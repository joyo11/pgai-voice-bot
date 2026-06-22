# Test Plan

How this bot tests the PGAI medical-practice voice agent at +1-805-439-8008. Our bot
calls them, role-plays a patient across 10 scenarios, records and transcripts both
sides, and we read the transcripts to find bugs in their agent.

## What "a good call" looks like

A call is usable as evidence only if:

- It runs the full conversation, roughly 1 to 3 minutes, not a 15-second hang-up.
- Our patient stays in character: human-sounding, short turns, never reveals it's an AI.
- The patient actively steers toward the scenario goal instead of passively answering.
  If the agent stalls, our side re-asks or pushes for a concrete outcome.
- The call reaches a clear endpoint: a confirmed time, a confirmation number, a
  refusal, or a hallucinated answer we can point at. "We talked and nothing happened"
  is a weak call; re-run it.
- Both transcript files (`transcripts/<callSid>.json` and `.txt`) and the dual-channel
  recording (`recordings/<callSid>.mp3`) exist and contain both speakers.

If a call dies early or the patient breaks character, throw it out and re-run that
scenario. We want 10+ good calls, not 10 attempts.

## The 10 scenarios

Keys map 1:1 to `scenarios.py`. Run all with `python call.py --all`, or one with
`python call.py --scenario KEY`.

### Happy-path scenarios

| Key | What it probes |
| --- | --- |
| `schedule_basic` | Core booking flow. Can it take a routine check-up request and confirm a specific day and time next week? Does it actually pin a slot or leave it vague? |
| `reschedule` | Moving an existing appointment. Does it find/assume the old appointment, release it, and confirm the new time without double-booking? |
| `cancel` | Full cancellation. Does it confirm the cancellation clearly and ideally give a confirmation, or does it leave the patient unsure it took? |
| `refill` | Medication refill (lisinopril). Does it handle a clinical request safely: route to pharmacy, set expectations on timing, or correctly punt to a human/provider? |
| `office_hours` | Factual Q&A: hours (esp. weekends), address, parking. Tests whether it knows real practice facts or invents them. |
| `insurance` | Insurance Q&A (BCBS PPO) and coverage. Tests whether it states accepted plans accurately or hallucinates coverage it can't know. |

### Edge cases (the bug-finders)

| Key | What it stresses |
| --- | --- |
| `edge_weekend` | Booking a closed-day slot. Patient insists on "this Sunday at 10am." Good agent catches the office is closed and offers a weekday. Bug: it confirms a slot on a closed day. |
| `edge_ambiguous` | Vague intent ("I need to come in for the thing"). Good agent asks clarifying questions before acting. Bug: it guesses and books/answers the wrong thing. |
| `edge_interrupt` | Barge-in and mid-thought topic switch (starts refill, flips to scheduling). Tests turn-taking and whether it follows the switch or gets stuck on the dropped topic. |
| `edge_multi` | Three asks in one call: book, refill, hours. Tests whether it tracks all three or silently drops one. Bug: a request goes unanswered with no acknowledgement. |

## Edge cases to stress (and what counts as a bug)

- Weekend / closed booking: agent confirms an appointment on a day the office is
  closed instead of catching it. (`edge_weekend`)
- Ambiguous request: agent acts on a guess instead of asking what the patient needs.
  (`edge_ambiguous`)
- Interruptions / barge-in: agent talks over the patient, ignores the interruption,
  or loses the thread after a mid-sentence switch. (`edge_interrupt`)
- Multiple requests in one call: agent answers one and drops the rest without saying
  so. (`edge_multi`)
- Hallucination: agent states specific insurance plans, hours, addresses, prices, or
  provider availability it cannot actually know, stated as fact. Watch `insurance` and
  `office_hours` especially, but flag it anywhere it appears.

Cross-cutting things to note in any call: confident wrong answers, no read-back of the
booked time, no confirmation on cancel, unsafe handling of the medication request,
collecting PHI carelessly, dead air or long latency, and failure to gracefully hand off
to a human when it should.

## How I iterate

This is not one-and-done. The loop:

1. Place a few early calls (`schedule_basic`, then one edge case) and listen to the
   recordings and read the transcripts end to end.
2. Tune our side, not the target:
   - VAD / barge-in: if the patient cuts the agent off too eagerly or sits silent too
     long, adjust server VAD sensitivity and the barge-in cancel timing in `server.py`.
   - Persona / steering: if a call wanders or ends too soon, tighten the goal and the
     shared STYLE rules in `scenarios.py` (shorter turns, push harder toward the
     outcome, wrap up at ~2 to 3 min).
3. Re-run the affected scenario(s) until the calls are consistently "good calls" by the
   bar above.
4. Once the patient is reliably lucid, run the full set (`--all`, optionally `--repeat`
   for the flaky edge cases), then `python analyze_bugs.py` to draft `BUGREPORT.md` and
   curate it against the transcripts by hand.

Keep the early throwaway runs as evidence of iteration; the point is to show the patient
got more lucid and the bug findings got sharper across runs.
