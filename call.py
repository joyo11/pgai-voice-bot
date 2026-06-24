"""
Place outbound test calls to the PGAI assessment line.

For each scenario it:
  1. Tells Twilio to call TARGET_NUMBER from your TWILIO_FROM_NUMBER, fetching
     TwiML from your running server (which bridges to OpenAI Realtime).
  2. Records BOTH sides (dual-channel).
  3. Waits for the call to finish, then downloads the recording to recordings/.

The server (server.py) writes the transcript to transcripts/<callSid>.{txt,json}.

Usage:
  python call.py --scenario refill         # one scenario
  python call.py --all                     # every scenario in scenarios.py
  python call.py --all --repeat 1          # run the full set once (10 calls)
"""
from __future__ import annotations

import argparse
import os
import time

import requests
from dotenv import load_dotenv
from twilio.rest import Client

from scenarios import SCENARIOS

load_dotenv()

SID = os.environ["TWILIO_ACCOUNT_SID"]
TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
FROM = os.environ["TWILIO_FROM_NUMBER"]
TARGET = os.environ.get("TARGET_NUMBER", "+18054398008")
PUBLIC_HOST = os.environ.get("PUBLIC_HOST", "").strip()
MAX_SECONDS = int(os.environ.get("MAX_CALL_SECONDS", "240"))

# Fail loudly before spending money on a call that would be silent: without a
# public host the TwiML URL has no host and Twilio can't reach the server.
if not PUBLIC_HOST:
    raise SystemExit(
        "PUBLIC_HOST is not set. Start ngrok, then set PUBLIC_HOST in .env to the "
        "forwarding host (e.g. abc123.ngrok-free.app) and try again."
    )

client = Client(SID, TOKEN)


def place_call(scenario: str) -> str:
    url = f"https://{PUBLIC_HOST}/twiml?scenario={scenario}"
    call = client.calls.create(
        to=TARGET,
        from_=FROM,
        url=url,
        method="POST",
        record=True,
        recording_channels="dual",       # both sides on separate channels
        time_limit=MAX_SECONDS,           # hard safety cap
    )
    print(f"\n=== {scenario} === call {call.sid}  ({SCENARIOS[scenario]['label']})")
    return call.sid


def wait_for_completion(call_sid: str, timeout: int = 360) -> str:
    deadline = time.time() + timeout
    status = ""
    while time.time() < deadline:
        try:
            call = client.calls(call_sid).fetch()
            status = call.status
            if status in ("completed", "busy", "failed", "no-answer", "canceled"):
                break
        except Exception as e:
            print(f"    (transient poll error, retrying: {type(e).__name__})")
        time.sleep(3)
    print(f"    status: {status}")
    return status


def download_recording(call_sid: str):
    # recordings may take a few seconds to finalize
    for _ in range(10):
        recs = client.recordings.list(call_sid=call_sid, limit=1)
        if recs:
            rec = recs[0]
            os.makedirs("recordings", exist_ok=True)
            out = f"recordings/{call_sid}.mp3"
            media_url = f"https://api.twilio.com/2010-04-01/Accounts/{SID}/Recordings/{rec.sid}.mp3"
            r = requests.get(media_url, auth=(SID, TOKEN))
            if r.ok:
                with open(out, "wb") as f:
                    f.write(r.content)
                print(f"    recording -> {out} ({len(r.content)//1024} KB)")
                return out
        time.sleep(3)
    print("    (no recording found yet — check Twilio console)")
    return None


def run(scenario: str):
    sid = place_call(scenario)
    wait_for_completion(sid)
    time.sleep(4)
    download_recording(sid)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", help="single scenario key (see scenarios.py)")
    ap.add_argument("--all", action="store_true", help="run every scenario")
    ap.add_argument("--repeat", type=int, default=1, help="times to repeat the --all set")
    ap.add_argument("--gap", type=int, default=8, help="seconds to wait between calls")
    args = ap.parse_args()

    if args.scenario:
        run(args.scenario)
    elif args.all:
        keys = list(SCENARIOS.keys())
        for _ in range(args.repeat):
            for k in keys:
                try:
                    run(k)
                except Exception as e:
                    print(f"    (scenario {k} errored, continuing: {type(e).__name__})")
                time.sleep(args.gap)
    else:
        print("Pick one:  --scenario <key>   or   --all")
        print("Scenarios:", ", ".join(SCENARIOS.keys()))


if __name__ == "__main__":
    main()
