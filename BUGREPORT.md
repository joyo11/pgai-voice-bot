# Bug Report , PGAI Voice Agent

Found by an automated patient-simulator bot across 10 calls to +1-805-439-8008.
Each bug is verified against the matching transcript (in `transcripts/`) and
recording (in `recordings/`). Issues are curated: the auto-draft
(`BUGREPORT_raw.md`) flagged 31 candidates; the ones below are the genuine,
reproducible agent-side problems after listening to the calls. Items caused by
the test simulator itself (early-call warmup overlap) were excluded.

---

## [High] Reads back a wrong / garbled date of birth as confirmed
- **Call:** `CA9f21918c5d805eb2165c944def948b7b` (schedule_basic), ~00:12:44
- **What happened:** Patient: "my name's Daniel Carter, and my date of birth is April 12, 1989." Agent: "Your patient profile has been created successfully... I have your date of birth as 7-4-2-0-0-0."
- **Why it matters:** The agent confirmed an incorrect, garbled DOB and even created a profile with it. In a medical setting, a wrong DOB on the record is a real patient-safety / identity issue. It should echo the DOB it actually heard and re-confirm on mismatch.

## [High] Cannot complete core tasks; dead-ends to "goodbye"
- **Calls:** `CA0df6ff929640ce1a6ff8e15c07fad818` (office_hours), `CA8c2a1a2acb4312552d17c6a6744854a2` (schedule_basic), `CA4281741774de0b72ab6c8703ffc82f5b` (refill)
- **What happened:** Across scheduling, refills, and office-hours questions, the agent repeatedly says it cannot access the schedule / refill status and either punts ("I'll let the clinic support team know") or ends the call: "Hello, you've reached the Pretty Good AI test line. Goodbye."
- **Why it matters:** The three most common patient intents (book, refill, hours) do not reach a resolved outcome. The agent cannot actually act, and the fallback is a dead end rather than a real handoff or a concrete next step.

## [High] Drops most requests when a caller has several
- **Call:** `CA7943c974b98683d374b61900f3548af3` (edge_multi), ~01:21:00
- **What happened:** Patient: "I need to do three things: book an appointment, get a medication refill, and confirm your office hours." After some back-and-forth on only the appointment, the agent ended with "Hello. You've reached the Pretty Good AI test line. Goodbye.", handling none of the three.
- **Why it matters:** No tracking of a multi-item request. The agent should acknowledge all three, work them in order, and confirm what was and was not completed.

## [High] Gets stuck in a repeated "please hold" loop, then abandons the call
- **Call:** `CA11bd45c3db5309505ecfec581c868ab4` (edge_weekend), 01:09:25 to 01:10:09
- **What happened:** During check-in the agent said "Please hold for a moment" six times in a row, never addressed the caller's actual request (a Sunday 10am appointment), and finished with "I can't proceed further right now."
- **Why it matters:** A stuck repetition loop is a clear breakdown. Separately, it never caught or addressed the weekend request (the clinic's hours were never checked against the asked-for Sunday slot).

## [Medium] Promises a transfer that does not happen
- **Calls:** `CA29f5cab9ab2a595e76a0d0592c36443b` (edge_interrupt), `CA7943c974b98683d374b61900f3548af3` (edge_multi)
- **What happened:** Agent: "Connecting you to a representative. Please wait." immediately followed by "Hello. You've reached the Pretty Good AI test line. Goodbye." No actual transfer occurs.
- **Why it matters:** Telling a patient they are being connected and then hanging up is worse than saying it cannot help. Either complete the transfer or set a clear, honest expectation.

## [Medium] States a phone number "on file" the caller never provided
- **Call:** `CA11bd45c3db5309505ecfec581c868ab4` (edge_weekend), ~01:09:12
- **What happened:** Agent: "I have your phone number as 555-234-7890 and your date of birth as June 6th, 1990. Is that correct?" The caller never gave that phone number in the call.
- **Why it matters:** Possible hallucinated/placeholder PII read back as fact. Worth verifying against whatever lookup the agent is doing; if there is no record, it should not invent one.

---

### Notes on method (for honesty)
- The first ~10 seconds of several calls contain overlap between the clinic's
  bilingual IVR ("Para Espanol, oprima el 2") and the caller, plus a few
  short mis-transcriptions on the agent side ("Thanks for watching"). Those are
  transcription/IVR artifacts, not counted as agent bugs.
- The "can't complete tasks / goodbye" pattern is the single most consistent
  finding and shows up across most scenarios, so it is the highest-value fix.
