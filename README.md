# pgai-voice-bot

An automated voice bot for the Pretty Good AI (pgai.us) AI Engineer take-home. It phone-calls
their test medical-practice voice agent, role-plays a patient across 10 scenarios, records and
transcribes both sides of every call, and surfaces bugs in their agent.

All calls go to the PGAI test agent at **+1-805-439-8008**.

> Note: do NOT call the number shown on the pgai.us/athena confirmation screen. That account
> exists only to give context on the agent's intended behavior. Every call this bot places goes
> to +1-805-439-8008 (already set as `TARGET_NUMBER`).

## How it works

- `server.py` is a FastAPI media-stream bridge. `/twiml` returns TwiML that opens a
  `<Connect><Stream>` to `wss://PUBLIC_HOST/media` with the chosen scenario. The `/media`
  WebSocket bridges Twilio audio to the OpenAI Realtime API: the PGAI agent's audio becomes
  Realtime input, our patient voice becomes Twilio output. Both sides use 8kHz g711 u-law, so
  there is no resampling. Server VAD handles turn-taking and basic barge-in. Both sides'
  transcripts are written to `transcripts/<callSid>.{json,txt}`.
- `call.py` places outbound calls via the Twilio REST API and downloads dual-channel recordings.
- `scenarios.py` defines the 10 patient personas and builds the Realtime system prompt.
- `analyze_bugs.py` reads the transcripts and drafts `BUGREPORT.md` for you to curate.

## Prerequisites

- Python 3.11
- [ngrok](https://ngrok.com/) (to expose the local server to Twilio)
- A Twilio account with a phone number (voice-capable)
- An OpenAI API key with Realtime API access
- A pgai.us/athena test account (for context on the agent's intended behavior only)

## Install

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configure

```bash
cp .env.example .env
```

Fill in `.env`:

- `OPENAI_API_KEY` your OpenAI key with Realtime access
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER` from your Twilio console
- `PUBLIC_HOST` left blank for now, set after ngrok is up (see below)
- `TARGET_NUMBER` already set to +18054398008, leave as is
- `REALTIME_MODEL`, `REALTIME_VOICE`, `ANALYZE_MODEL`, `MAX_CALL_SECONDS` defaults are fine

## Run

### 1. Start the server

```bash
uvicorn server:app --port 8000
```

### 2. Start ngrok and set PUBLIC_HOST

In a second terminal:

```bash
ngrok http 8000
```

Copy the forwarding host (the part after `https://`, e.g. `abc123.ngrok-free.app`) and set it in
`.env`:

```
PUBLIC_HOST=abc123.ngrok-free.app
```

`call.py` reads `PUBLIC_HOST` at call time, so no server restart is needed.

### 3. Place calls

Single scenario:

```bash
python call.py --scenario schedule_basic
```

All 10 scenarios:

```bash
python call.py --all
```

Useful flags: `--repeat N` (run the selection N times), `--gap S` (seconds between calls).

Scenario keys: `schedule_basic`, `reschedule`, `cancel`, `refill`, `office_hours`,
`insurance`, `edge_weekend`, `edge_ambiguous`, `edge_interrupt`, `edge_multi`.

## Output

- Transcripts (both sides): `transcripts/<callSid>.json` and `transcripts/<callSid>.txt`
- Recordings (dual-channel mp3): `recordings/<callSid>.mp3`

## Draft the bug report

After the calls complete:

```bash
python analyze_bugs.py
```

This reads `transcripts/*.json`, flags agent bugs with the analysis model, and writes a draft
`BUGREPORT.md`. Curate it by hand before sharing: confirm each flagged issue against the matching
transcript and recording, drop false positives, and keep the strongest, clearly-reproducible bugs.

## Cost

A full run of 10 calls (Twilio voice + recording plus OpenAI Realtime audio) typically costs under
$20.
