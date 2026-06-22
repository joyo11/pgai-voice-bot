# Loom Scripts

Two recordings for the PGAI AI-Engineer take-home. Keep both under 5 minutes. Talk like a person, show the terminal and the files, let one real call play. Do not read these scripts word for word, use them as beats.

Before you hit record:
- Server already running: `uvicorn server:app --port 8000`
- ngrok up, `PUBLIC_HOST` set in `.env`
- At least one finished call in `transcripts/` and `recordings/`
- A couple terminal tabs ready: one for `call.py`, one for `analyze_bugs.py`, one with the repo open in an editor

---

## Video 1: Main walkthrough (target 4:30, hard cap 5:00)

### Beat 1: The problem (0:00 to 0:30)
- One line on the task: "PGAI has a medical-practice voice agent on a phone number. The job is to find its bugs. So I built a second bot that calls it, role-plays a patient, records both sides, and surfaces the agent's failures."
- Why a bot and not me dialing manually: "I need 10+ consistent, repeatable conversations across scenarios, transcribed both sides. Manual dialing does not scale and is not reproducible."
- Frame the goal: "Lucid patient voice in, structured evidence out."

### Beat 2: Architecture (0:30 to 1:45)
- Open the repo, point at the four files as you talk. Keep it to the data flow.
- `call.py`: "Twilio places an outbound call to the PGAI number from my Twilio number. It points Twilio at my `/twiml` endpoint with a `scenario` parameter, records in dual channel, waits for the call to finish, then downloads the mp3."
- `server.py`: "This is the bridge. `/twiml` returns a `<Connect><Stream>` to my `/media` WebSocket. That socket sits between Twilio and the OpenAI Realtime API."
  - Call out the one design choice that matters: "Both sides are 8kHz g711 u-law, so I pass audio straight through, no resampling. Twilio inbound, which is the PGAI agent, goes into Realtime as input. Realtime output, my patient voice, goes back to Twilio."
  - "Turn-taking is server VAD. Barge-in: when the agent starts talking over me, I send Twilio a `clear` and Realtime a `response.cancel`."
  - "Both transcripts get logged: the agent via Realtime input audio transcription, my patient via the response audio transcript event. They land in `transcripts/<callSid>` as json and txt."
- `scenarios.py`: "Ten patient personas, from a basic scheduling call to edge cases like a weekend request, an ambiguous date, and a deliberate interrupt. `build_instructions` builds the Realtime system prompt: stay human, short turns, never reveal it's an AI, steer to the goal, wrap up in 2 to 3 minutes."
- `analyze_bugs.py`: "Reads the transcripts, asks gpt-4o to flag the agent's bugs, writes a BUGREPORT.md draft that I then curate."

### Beat 3: Run it / play a real call (1:45 to 3:15)
- Show the single run: "End to end it is install requirements, fill `.env`, start uvicorn, start ngrok, then `python call.py --all`."
- Optionally kick off one live: `python call.py --scenario schedule_basic`. If time is tight, do not wait, cut to a finished one.
- Open `recordings/<callSid>.mp3` and play 20 to 30 seconds of a real conversation. Pick a clip where my patient voice sounds natural and the back and forth is clean. This is the single most important moment in the video, since lucid voice is the top eval criterion.
- While it plays, pull up the matching `transcripts/<callSid>.txt` so they can read both sides as they hear it.

### Beat 4: Show a found bug (3:15 to 4:15)
- Open `BUGREPORT.md` and pick one concrete, real bug. Read the transcript snippet that proves it, not just the summary.
- Good candidates to highlight (use whatever actually showed up):
  - Agent offers an appointment slot outside stated office hours, or on a weekend after saying it is closed.
  - Agent loses the date when I give it ambiguously ("next Tuesday") and confirms the wrong day.
  - Agent talks over the patient and does not recover after an interrupt.
  - Agent fails to confirm back critical details (name, DOB, reason) before booking.
- Say why it matters in a medical context: "Booking the wrong day or a closed-hours slot is a real patient-harm bug, not cosmetic."

### Beat 5: Evidence of iteration (4:15 to 4:45)
- One honest sentence on what changed across runs: "First pass my patient barged in too aggressively and clipped the agent, so transcripts were garbage. I added the clear plus response.cancel on the agent's speech_started and the turns got clean."
- Point at `--repeat` and `--all`: "I can re-run the whole scenario set to confirm a bug is consistent and not a one-off."
- Close: "Code's in the repo, 10+ transcripts and recordings are attached, bug report is curated. The second video is me fixing one of these live with AI."

---

## Video 2: Prompting AI to debug (target 4:30, hard cap 5:00)

Goal: show genuine iterative AI-assisted debugging on a real bug. Pick ONE bug and actually fix it on camera. Below is barge-in not cancelling cleanly. Swap in transcript ordering if that is the more honest bug for your run (alt prompts at the end).

Pick the bug honestly: if barge-in already works, do not fake it. Choose whatever is actually broken.

### Beat 1: Name the symptom with evidence (0:00 to 0:45)
- Open a transcript where the bug shows. "Look at this call. The PGAI agent starts a sentence, my patient cuts in, but the agent's audio keeps coming and the two transcripts interleave wrong. Barge-in isn't actually cancelling the in-flight response."
- State the hypothesis out loud: "I think on `input_audio_buffer.speech_started` I clear Twilio but I'm not reliably cancelling the Realtime response, or I'm cancelling when there's nothing to cancel and the real one slips through."
- First prompt to type into the AI assistant:
  > Here's `server.py` (paste or @-attach it). On the `/media` socket, when the remote agent starts speaking I want true barge-in: stop my patient's current audio immediately. Walk me through exactly what my speech_started handler does today and where it can fail to cancel an in-flight Realtime response.

### Beat 2: Read the AI's diagnosis, push back (0:45 to 1:45)
- Let it explain. Then narrow it instead of taking it wholesale.
- Second prompt:
  > Two questions before we change anything. (1) Am I tracking whether a response is currently active? If I send response.cancel with no active response, does Realtime error or no-op? (2) After I send Twilio "clear", do I also need to drop the audio deltas already queued so stale audio doesn't play? Show me the minimal state I need to track.

### Beat 3: Make the change (1:45 to 2:45)
- Have it produce a focused diff. Show the edit landing in the file.
- Third prompt:
  > Give me a minimal patch: track an `assistant_speaking` / active-response flag, only send response.cancel when it's true, send Twilio "clear" plus stop forwarding queued audio deltas on barge-in, and reset the flag on response.done and response.cancelled. Show only the changed handlers, don't rewrite the file.
- As you paste it in, say what each line does so it reads as you understanding it, not blind copy-paste.

### Beat 4: Run it and verify (2:45 to 4:00)
- Restart uvicorn, place one targeted call: `python call.py --scenario edge_interrupt`.
- Watch the server logs. Call out the cancel firing only when the agent was mid-response.
- Open the fresh transcript: "Now the agent stops when I cut in, and the turns don't interleave."
- If it is not fixed yet, that is good footage. Show the follow-up:
  > Still seeing one stale chunk after the clear. Here are the new logs (paste). The cancel fires but Twilio plays ~200ms of old audio. Is the leftover in Twilio's buffer or mine? How do I flush both?

### Beat 5: Confirm and close (4:00 to 4:45)
- One more run, or re-point at clean logs: "Repeated `edge_interrupt` twice, clean both times."
- Honest close: "That's the loop I used throughout: reproduce from a transcript, hypothesize, have the AI narrow it, apply a minimal diff, re-run the exact scenario, confirm with logs and the new transcript."

### Alt narrative: transcript ordering bug
- Symptom: in `transcripts/<callSid>.txt` lines land out of order, or a turn is attributed to the wrong speaker, because agent transcription (input_audio_transcription) and patient transcription (response.audio_transcript.done) complete at different times.
- Opening prompt:
  > In server.py I write the agent's lines on input_audio_transcription completion and the patient's lines on response.audio_transcript.done. They finalize at different times so my transcript file ends up out of order. How should I order turns by actual speech time instead of completion time?
- Follow-up:
  > Give me a minimal change: buffer turns with a timestamp at speech start, sort on flush, and keep speaker labels correct. Show only the transcript-writing code.
- Verify the same way: re-run a call, open the txt, confirm the turns read in true chronological order with correct speakers.