"""
Media-stream bridge: Twilio phone call  <-->  OpenAI Realtime API (the patient).

Flow per call:
  1. Twilio places the outbound call (see call.py) and fetches TwiML from
     GET /twiml?scenario=<key>. We return a <Connect><Stream> that opens a
     bidirectional WebSocket to /media.
  2. On /media we open a second WebSocket to OpenAI's Realtime API and relay
     audio both ways (both are 8kHz g711 u-law, so no resampling needed):
        Twilio inbound audio (the PGAI agent talking)  -> Realtime input
        Realtime output audio (our patient talking)    -> Twilio
  3. Realtime emits transcripts for BOTH sides, which we log to
     transcripts/<callSid>.{json,txt}.
  4. Basic barge-in: if the agent starts talking while our patient is talking,
     we cancel our response and clear Twilio's audio buffer.

Run:  uvicorn server:app --port 8000   (then expose with ngrok)
"""
from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import PlainTextResponse
from fastapi.websockets import WebSocketState
import websockets

from scenarios import build_instructions

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
REALTIME_MODEL = os.environ.get("REALTIME_MODEL", "gpt-realtime")
REALTIME_VOICE = os.environ.get("REALTIME_VOICE", "alloy")
PUBLIC_HOST = os.environ.get("PUBLIC_HOST", "localhost:8000")

app = FastAPI()


@app.get("/")
def health():
    return {"ok": True, "service": "pgai-voice-bot"}


@app.api_route("/twiml", methods=["GET", "POST"])
async def twiml(request: Request):
    """Return TwiML that connects the call to our media WebSocket.
    The scenario key is passed through as a Stream <Parameter> so the socket
    knows which patient persona to use."""
    scenario = request.query_params.get("scenario", "schedule_basic")
    ws_url = f"wss://{PUBLIC_HOST}/media"
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Connect>
    <Stream url="{ws_url}">
      <Parameter name="scenario" value="{scenario}" />
    </Stream>
  </Connect>
</Response>"""
    return PlainTextResponse(content=xml, media_type="text/xml")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M:%S")


@app.websocket("/media")
async def media(ws: WebSocket):
    await ws.accept()
    scenario = "schedule_basic"
    call_sid = "unknown"
    stream_sid = None
    transcript = []          # [{t, speaker, text}]
    response_active = False   # is the patient currently generating a response?

    oai_url = f"wss://api.openai.com/v1/realtime?model={REALTIME_MODEL}"
    oai_headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}  # GA API: no beta header

    try:
        async with websockets.connect(oai_url, additional_headers=oai_headers, max_size=None) as oai:

            async def configure(scn: str):
                # GA Realtime shape: audio nested under session.audio.input/output,
                # g711 u-law = "audio/pcmu" (matches Twilio Media Streams exactly).
                await oai.send(json.dumps({
                    "type": "session.update",
                    "session": {
                        "type": "realtime",
                        "instructions": build_instructions(scn),
                        "audio": {
                            "input": {
                                "format": {"type": "audio/pcmu"},
                                "turn_detection": {
                                    "type": "server_vad",
                                    "threshold": 0.5,
                                    "prefix_padding_ms": 300,
                                    "silence_duration_ms": 600,
                                },
                                "transcription": {"model": "whisper-1"},
                            },
                            "output": {
                                "format": {"type": "audio/pcmu"},
                                "voice": REALTIME_VOICE,
                            },
                        },
                    },
                }))

            # ---- Twilio -> OpenAI ----
            async def from_twilio():
                nonlocal scenario, call_sid, stream_sid
                async for raw in ws.iter_text():
                    data = json.loads(raw)
                    ev = data.get("event")
                    if ev == "start":
                        start = data["start"]
                        stream_sid = start["streamSid"]
                        call_sid = start.get("callSid", "unknown")
                        params = start.get("customParameters", {}) or {}
                        scenario = params.get("scenario", scenario)
                        await configure(scenario)
                        print(f"[start] call={call_sid} scenario={scenario}")
                    elif ev == "media":
                        await oai.send(json.dumps({
                            "type": "input_audio_buffer.append",
                            "audio": data["media"]["payload"],
                        }))
                    elif ev == "stop":
                        print(f"[stop] call={call_sid}")
                        break

            # ---- OpenAI -> Twilio ----
            async def from_openai():
                nonlocal response_active
                async for raw in oai:
                    msg = json.loads(raw)
                    t = msg.get("type", "")

                    if t == "response.created":
                        response_active = True
                    elif t == "response.done":
                        response_active = False

                    if t == "response.output_audio.delta" and stream_sid:
                        # our patient's voice -> back into the call
                        await ws.send_text(json.dumps({
                            "event": "media",
                            "streamSid": stream_sid,
                            "media": {"payload": msg["delta"]},
                        }))

                    elif t == "input_audio_buffer.speech_started":
                        # the agent started talking -> barge-in: stop our audio,
                        # and only cancel if a patient response is actually active.
                        if stream_sid:
                            await ws.send_text(json.dumps({"event": "clear", "streamSid": stream_sid}))
                        if response_active:
                            response_active = False
                            try:
                                await oai.send(json.dumps({"type": "response.cancel"}))
                            except Exception:
                                pass

                    # --- transcripts ---
                    elif t == "conversation.item.input_audio_transcription.completed":
                        # what the PGAI agent said (our input)
                        text = (msg.get("transcript") or "").strip()
                        if text:
                            transcript.append({"t": _now(), "speaker": "AGENT", "text": text})
                            print(f"AGENT: {text}")

                    elif t == "response.output_audio_transcript.done":
                        # what our patient said (our output)
                        text = (msg.get("transcript") or "").strip()
                        if text:
                            transcript.append({"t": _now(), "speaker": "PATIENT", "text": text})
                            print(f"PATIENT: {text}")

                    elif t == "error":
                        print("[oai error]", msg.get("error"))

            # run both directions; when EITHER ends (Twilio "stop" or OpenAI
            # closes), cancel the other so we fall through to save the transcript.
            t1 = asyncio.create_task(from_twilio())
            t2 = asyncio.create_task(from_openai())
            done, pending = await asyncio.wait({t1, t2}, return_when=asyncio.FIRST_COMPLETED)
            for p in pending:
                p.cancel()
                try:
                    await p
                except asyncio.CancelledError:
                    pass

    except Exception as e:
        print("[media error]", repr(e))
    finally:
        save_transcript(call_sid, scenario, transcript)
        if ws.client_state != WebSocketState.DISCONNECTED:
            await ws.close()


def save_transcript(call_sid: str, scenario: str, transcript: list):
    if not transcript:
        print(f"[transcript] nothing to save for {call_sid}")
        return
    os.makedirs("transcripts", exist_ok=True)
    base = f"transcripts/{call_sid}"
    with open(base + ".json", "w") as f:
        json.dump({"call_sid": call_sid, "scenario": scenario, "turns": transcript}, f, indent=2)
    with open(base + ".txt", "w") as f:
        f.write(f"Call: {call_sid}\nScenario: {scenario}\n" + "=" * 50 + "\n")
        for turn in transcript:
            f.write(f"[{turn['t']}] {turn['speaker']}: {turn['text']}\n")
    print(f"[transcript] saved {base}.txt ({len(transcript)} turns)")
