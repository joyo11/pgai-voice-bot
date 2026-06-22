# Architecture

This is a voice bot that phone-calls the Pretty Good AI medical-practice agent, role-plays a
patient across scenarios, records and transcribes both sides of the call, and surfaces bugs in
their agent. The whole thing is three small Python pieces glued together by Twilio's Media
Streams and the OpenAI Realtime API.

## How a call flows

`call.py` uses the Twilio REST API to place an outbound call from `TWILIO_FROM_NUMBER` to the
target number, with `record=True` and `recording_channels="dual"` so each speaker lands on its
own channel. The call's `url` points at our own `GET /twiml?scenario=KEY`, which returns a
`<Connect><Stream>` pointing at `wss://PUBLIC_HOST/media`, carrying the scenario key as a
`<Parameter>`. Once the call connects, Twilio opens a bidirectional WebSocket to `/media`. There,
`server.py` opens a second WebSocket to the OpenAI Realtime API and relays audio both ways. Twilio
inbound audio (the PGAI agent speaking) is forwarded as `input_audio_buffer.append`; Realtime
output audio (our patient speaking) is sent back to Twilio as `media` frames. The scenario key
selects a patient persona and goal via `build_instructions()` in `scenarios.py`, sent once in
`session.update`.

```
                         outbound REST call (call.py)
   call.py  ──────────────────────────────────────────────►  PGAI agent
      │                                                       (+1 805 439 8008)
      │ fetches TwiML                                              │
      ▼                                                            │ phone audio
  GET /twiml ──► <Connect><Stream wss://PUBLIC_HOST/media>         │ (g711 u-law)
                                                                   ▼
                          Twilio Media Streams  ◄──────────────────┘
                                   │  ▲
                  agent audio in   │  │   patient audio out
                                   ▼  │
                         server.py  /media  (FastAPI WebSocket bridge)
                                   │  ▲
                  input_audio_     │  │   response.audio.delta
                  buffer.append    ▼  │
                          OpenAI Realtime API  (our "patient")
                                   │
                       transcripts (both sides) ──► transcripts/<callSid>.{json,txt}
                                                    recordings/<callSid>.mp3 (Twilio)
                                                              │
                                                              ▼
                                          analyze_bugs.py ──► BUGREPORT.md
```

## Why g711 u-law end to end

The phone network speaks 8 kHz g711 u-law, and Twilio Media Streams delivers exactly that. The
Realtime session is configured with `input_audio_format` and `output_audio_format` both set to
`g711_ulaw`, so the same encoding rides the whole path. Frames are just base64 strings copied from
one socket to the other with no transcoding. That means no resampling, no audio libraries in the
hot path, and the lowest latency we can get, which matters because the eval's #1 priority is a
lucid, natural conversation. Resampling or a different codec would add both processing delay and a
quality hit on already narrowband phone audio.

## Why OpenAI Realtime (speech-to-speech) over a STT->LLM->TTS pipeline

Realtime is a single speech-to-speech model, so turn-taking, interruption handling, and prosody
are decided by one model that hears the actual audio, not stitched across three services. The
brief's top eval criterion is whether the conversation sounds lucid and human, and a chained
STT->LLM->TTS pipeline pays serial latency on every turn (transcribe, then generate, then
synthesize) plus loses paralinguistic cues. We use Realtime's server-side VAD (`server_vad`) for
turn detection so we are not hand-rolling endpointing. A no-code voice platform (Vapi, Retell,
Bland) would have been faster to stand up, but it hides the audio path and the barge-in logic, and
the assessment explicitly wants working code and evidence of iteration, so owning the bridge is the
point.

## Transcripts and barge-in

Realtime gives us both sides of the conversation, which is the trick that makes a single model
double as a transcript recorder. The agent's speech (our input) comes back via
`input_audio_transcription` (`whisper-1`) on the
`conversation.item.input_audio_transcription.completed` event, and our patient's speech (our
output) comes back on `response.audio_transcript.done`. Both are appended to an in-memory list and
flushed to `transcripts/<callSid>.{json,txt}` when the call ends. Twilio's dual-channel recording
is the audio ground truth alongside that. Barge-in is handled on `input_audio_buffer.speech_started`:
when the agent starts talking while our patient is mid-sentence, we send Twilio a `clear` to drop
already-buffered patient audio and send Realtime a `response.cancel` to stop generating, so the bot
yields the floor instead of talking over the agent.

## Limitations and tradeoffs

This is honest about a few things. Barge-in is reactive, not perfect: there is a brief window where
buffered audio can still play before the `clear` lands, and a fast double-interruption can clip a
turn. The agent-side transcript uses `whisper-1` on 8 kHz phone audio, so it will occasionally
mis-hear names, dates, and numbers, which means `analyze_bugs.py` output is a draft to curate, not a
verdict. VAD thresholds (`threshold`, `silence_duration_ms`) are tuned by hand and a slow or
soft-spoken agent could trip early endpointing. The bridge holds transcript state in memory and only
writes on call end, so a crashed process loses that call's transcript (the Twilio recording still
survives). And `PUBLIC_HOST` assumes a stable public WSS endpoint (ngrok in dev), so a tunnel that
rotates mid-run breaks new calls. None of these block the core deliverable: real calls, real
two-sided transcripts, and recordings.
