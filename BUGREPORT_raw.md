# Bug Report — PGAI Voice Agent

_Auto-drafted from 10 calls; curate before submitting._

## [High] Failure to Provide Requested Information
- **Call:** `CA0df6ff929640ce1a6ff8e15c07fad818` (scenario: office_hours)
- **Quote:** "AGENT: Hello, you've reached the pretty good AI test line, goodbye."
- **Why it's a problem:** The agent fails to provide the weekend hours and address of the requested location, despite multiple prompts from the patient. Instead, it abruptly ends the call, which could leave the patient without the necessary information and is a significant service quality issue.

## [High] Confirming an appointment on a weekend
- **Call:** `CA11bd45c3db5309505ecfec581c868ab4` (scenario: edge_weekend)
- **Quote:** "PATIENT: Hi, no, this is Tom Becker. I'm calling to set up an appointment for this Sunday at 10 a.m."
- **Why it's a problem:** The agent did not inform the patient that the clinic might be closed on Sundays or verify the availability before attempting to set up an appointment. This may lead to booking an appointment that can't be honored.

## [High] Bad Turn-Taking and Interaction Flow
- **Call:** `CA29f5cab9ab2a595e76a0d0592c36443b` (scenario: edge_interrupt)
- **Quote:** "PATIENT: Hi, I’m calling because I need a refill on my
AGENT: Esta llamada puede ser grabada para motivos de calidad y entrenamiento. Para Español, oprima el 2.
AGENT: Thanks for calling pivot point orthopedics part of pretty good AI and I speak you with Daniel"
- **Why it's a problem:** The agent begins its script before confirming the patient's input, interrupting the patient's initial request. This causes confusion and disrupts the conversation flow.

## [High] Inappropriate Handoff Without Confirmation
- **Call:** `CA29f5cab9ab2a595e76a0d0592c36443b` (scenario: edge_interrupt)
- **Quote:** "AGENT: Connecting you to a representative. Please wait.
AGENT: BEEP
PATIENT: Hi, just checking in—did we get
PATIENT: Wait, hold on, I still need to confirm that appointment time!
AGENT: Hello. You've reached the Pretty Good AI test line. Goodbye."
- **Why it's a problem:** The agent ends the call abruptly and does not confirm the appointment time with the patient, leaving the scheduling incomplete and unresolved.

## [High] Improper Handling of Call Sequence
- **Call:** `CA4281741774de0b72ab6c8703ffc82f5b` (scenario: refill)
- **Quote:** "PATIENT: Hi, this is the medical practice. How can I help you today? AGENT: Esta llamada puede ser grabada para motivos de calidad y entrenamiento."
- **Why it's a problem:** The AGENT responds with a standard greeting in Spanish without context, following a statement that should not be from the patient. This leads to confusion at the very start of the call, impacting the overall user experience.

## [High] Repetitive and Confusing Dialogue
- **Call:** `CA4281741774de0b72ab6c8703ffc82f5b` (scenario: refill)
- **Quote:** "PATIENT: Of course, I'm here to help. What can I do for you today? AGENT: Thanks for watching. PATIENT: Hi, how can I assist you with your medication or any other needs today? AGENT: Have a great day. Bye."
- **Why it's a problem:** The AGENT provides irrelevant responses such as 'Thanks for watching' and 'Have a great day. Bye.' instead of progressing the conversation appropriately. This indicates a malfunction in understanding and responding to the patient's requests.

## [High] Dropped Multi-tasking Request
- **Call:** `CA7943c974b98683d374b61900f3548af3` (scenario: edge_multi)
- **Quote:** "PATIENT: Hi, I'm Nadia Hassan. I need to do three things: book an appointment, get a medication refill, and confirm your office hours."
- **Why it's a problem:** The agent failed to handle all three requests (appointment, medication refill, office hours confirmation) from the patient and instead focused on handling just the appointment request. The patient's needs are not met, showing poor context management.

## [High] Failure to Secure Outcome on Call Transfer
- **Call:** `CA7943c974b98683d374b61900f3548af3` (scenario: edge_multi)
- **Quote:** "AGENT: Connecting you to a representative. Please wait. AGENT: Hello. You've reached the Pretty Good AI test line. Goodbye."
- **Why it's a problem:** The agent transferred the call to a line that did not handle the patient's requests, resulting in an unresolved call. This is misleading and fails the patient's attempt to resolve their inquiries.

## [High] Failure to Capture Patient's Request and Connect Appropriately
- **Call:** `CA8c2a1a2acb4312552d17c6a6744854a2` (scenario: schedule_basic)
- **Quote:** "AGENT: Hello, you've reached the pretty good AI test line. Goodbye."
- **Why it's a problem:** The agent ends the call rather than properly handing off the patient to a human representative or resolving the patient's request. This leaves the patient without a confirmed appointment or any clear next steps, which does not meet their needs and could cause frustration.

## [High] Incorrect Confirmation of Details
- **Call:** `CA9f21918c5d805eb2165c944def948b7b` (scenario: schedule_basic)
- **Quote:** "AGENT: Your patient profile has been created successfully for demo purposes. I have your date of birth as 7-4-2-0-0-0."
- **Why it's a problem:** The agent incorrectly confirms an erroneous date of birth, which can lead to errors in patient records and potential issues in healthcare service.

## [High] Failure to confirm or process the patient's request
- **Call:** `CAc3b7331efb53709d1a2cd02e9abb3756` (scenario: edge_ambiguous)
- **Quote:** "PATIENT: So, I need to come in for that appointment, you know, the thing we talked about before. I'm not sure exactly which one it was. AGENT: I can help with that. I need to identify the appointment first, then I can look it up."
- **Why it's a problem:** The agent fails to identify the appointment and does not take action to resolve the patient's request, leading to the call being redirected without addressing the patient's need for an appointment, which is essential for operational effectiveness.

## [High] Abruptly ending the call without resolution
- **Call:** `CAc3b7331efb53709d1a2cd02e9abb3756` (scenario: edge_ambiguous)
- **Quote:** "AGENT: Hello, you've reached the pretty good AI test line. Goodbye."
- **Why it's a problem:** The agent ends the call without resolving the patient's issue or confirming any follow-up action, which is crucial for a satisfactory customer service experience.

## [High] Failure to confirm patient identity correctly
- **Call:** `CAe2ef3fb18fe29d2e65c84c4ebe6d9cd3` (scenario: reschedule)
- **Quote:** "AGENT: Thanks for calling pivot point orthopedics part of pretty good AI am I speaking with Daniel"
- **Why it's a problem:** The agent incorrectly identifies the caller as 'Daniel,' despite the caller stating their name is 'Priya Shah'. This can lead to confusion or privacy violations if the confirmation is incorrect.

## [High] Failure to assist in rescheduling appointment
- **Call:** `CAe2ef3fb18fe29d2e65c84c4ebe6d9cd3` (scenario: reschedule)
- **Quote:** "PATIENT: Wait, I’m a bit confused. I need to reschedule my appointment. Are you able to help with that?"
- **Why it's a problem:** The agent fails to address the patient's request to reschedule the appointment, leading to an unsatisfying outcome and needing human intervention.

## [Medium] Inconsistent Turn-Taking
- **Call:** `CA0df6ff929640ce1a6ff8e15c07fad818` (scenario: office_hours)
- **Quote:** "AGENT: Help."
- **Why it's a problem:** This response seems out of context and unclear, possibly indicating a glitch or an incomplete processing of the patient's request. It disrupts the natural flow of the conversation and could lead to confusion.

## [Medium] Inefficient confirmation and information process
- **Call:** `CA11bd45c3db5309505ecfec581c868ab4` (scenario: edge_weekend)
- **Quote:** "AGENT: Please tell me your date of birth. AGENT: Please tell me your full name, first and last."
- **Why it's a problem:** The agent redundantly asks for the date of birth and confirmation after the patient has already provided the information. This creates inefficiency and frustration for the patient.

## [Medium] Repeated holding pattern without progression
- **Call:** `CA11bd45c3db5309505ecfec581c868ab4` (scenario: edge_weekend)
- **Quote:** "AGENT: I still need to finish the check-in first. Please hold for a moment."
- **Why it's a problem:** The agent repeatedly asks the patient to hold without making progress or providing feedback on the appointment booking process. This can create a negative user experience.

## [Medium] Failure to Collect All Necessary Information Before Proceeding
- **Call:** `CA29f5cab9ab2a595e76a0d0592c36443b` (scenario: edge_interrupt)
- **Quote:** "PATIENT: Oh, okay, let's just go ahead and set up that appointment then.
AGENT: I'm not able to check your records here. If you want to schedule, I can take your appointment request."
- **Why it's a problem:** The agent does not explicitly confirm the patient's intent to skip the refill and proceed directly to making an appointment, potentially leading to misunderstandings or missed requests.

## [Medium] Repeated Request for Already Provided Information
- **Call:** `CA29f5cab9ab2a595e76a0d0592c36443b` (scenario: edge_interrupt)
- **Quote:** "PATIENT: Sure, my date of birth is August 14, 1993.
AGENT: Please share your date of birth. Please share your date of birth.
AGENT: Please tell me your full name, first and last, and your date of birth."
- **Why it's a problem:** The agent asks for the date of birth multiple times even after the patient has provided it, leading to unnecessary repetition and potential frustration.

## [Medium] Failure to Capture Required Information
- **Call:** `CA4281741774de0b72ab6c8703ffc82f5b` (scenario: refill)
- **Quote:** "AGENT: I can help with that. Which medication would you like refilled?"
- **Why it's a problem:** The AGENT fails to retain the information despite the patient having already stated they need a refill for lisinopril. This leads to redundancy and inefficiency in the conversation.

## [Medium] Delayed Confirmation of Refill Status
- **Call:** `CA4281741774de0b72ab6c8703ffc82f5b` (scenario: refill)
- **Quote:** "AGENT: I'm not able to see refill status or pharmacy timing from here."
- **Why it's a problem:** The AGENT does not provide a timeline or confirmation about when the refill might be approved. Patients might need timely medication, and not having this information can be problematic for proper health management.

## [Medium] Incorrect Phone Number Confirmation
- **Call:** `CA7943c974b98683d374b61900f3548af3` (scenario: edge_multi)
- **Quote:** "AGENT: I have your phone number as 929-433-7408 and your date of birth is February 27th, 1985. Is that correct?"
- **Why it's a problem:** The agent incorrectly confirms a phone number that the patient did not provide, potentially leading to identity errors or privacy breaches.

## [Medium] Inadequate Confirmation and Transition Process
- **Call:** `CA8c2a1a2acb4312552d17c6a6744854a2` (scenario: schedule_basic)
- **Quote:** "AGENT: I'm not able to check the schedule from here right now. Since you need a specific time confirmed today, I'm connecting you to our clinic support team now. Please stay on the line."
- **Why it's a problem:** Despite stating that the patient would be connected to the support team, the agent does not follow through appropriately, leading to the abrupt and unresolved ending of the call. The lack of a proper transition or confirmation of connection to a human representative is a significant procedural failure.

## [Medium] Repeated Requests for Same Information
- **Call:** `CA9c2e22a60a7647c7f90bbc32fc4dd185` (scenario: cancel)
- **Quote:** "AGENT: Please tell me your full name first and last one more time. AGENT: Please tell me your last name and date of birth. PATIENT: My last name is Lin, and my date of birth is January 5th, 1972. PATIENT: Sure, it's Robert, R-O-B-E-R-T, and Lin, L-I-N. AGENT: Please spell your first name and last name for me. AGENT: please spell your last name again and include your date of birth."
- **Why it's a problem:** The agent repeatedly asks for the patient's name and date of birth multiple times even after the patient has already provided it. This can cause frustration and reduce the efficiency of the call.

## [Medium] Failure to Utilize Available Information
- **Call:** `CA9c2e22a60a7647c7f90bbc32fc4dd185` (scenario: cancel)
- **Quote:** "PATIENT: I’m sorry, I don’t have it memorized right now. Maybe you can pull it up from the number I’m calling from?"
- **Why it's a problem:** The agent does not acknowledge or utilize the option to use the caller ID or the phone number the patient is calling from, which could help in verifying the patient's record more efficiently.

## [Medium] Inaccurate Appointment Timing
- **Call:** `CA9f21918c5d805eb2165c944def948b7b` (scenario: schedule_basic)
- **Quote:** "AGENT: Monday morning has one opening I can see right now with Dr. Zignu Lukosky. It is Monday, June 22nd at 2.30 p.m."
- **Why it's a problem:** The agent offers an afternoon appointment despite the patient's specific request for a morning slot, suggesting a misunderstanding or misrepresentation of available times.

## [Medium] Redundant Information Request
- **Call:** `CA9f21918c5d805eb2165c944def948b7b` (scenario: schedule_basic)
- **Quote:** "AGENT: I can help with that, but I need to create a demo patient profile first, so we can proceed. If you'd like, just tell me your first and last name and I'll set that up. PATIENT: I already gave my name—Daniel Carter."
- **Why it's a problem:** The agent redundantly asks for the patient's name again despite receiving it earlier, indicating a flaw in information retention or session continuity.

## [Medium] Repeatedly asked for same information without processing it
- **Call:** `CAc3b7331efb53709d1a2cd02e9abb3756` (scenario: edge_ambiguous)
- **Quote:** "AGENT: Please tell me your date of birth. Please tell me your date of birth."
- **Why it's a problem:** The agent repeatedly asks for the date of birth and later on full name and date of birth without acknowledging or processing the information provided by the patient, indicating a failure to hold and use the gathered information.

## [Medium] Repeated request for date of birth
- **Call:** `CAe2ef3fb18fe29d2e65c84c4ebe6d9cd3` (scenario: reschedule)
- **Quote:** "AGENT: Please tell me your date of birth. Please tell me your date of birth."
- **Why it's a problem:** The agent unnecessarily repeats the request for the caller's date of birth, which could confuse or frustrate the patient.

## [Medium] Non-sequential interaction with phone number confirmation
- **Call:** `CAe2ef3fb18fe29d2e65c84c4ebe6d9cd3` (scenario: reschedule)
- **Quote:** "AGENT: please tell me the phone number on your account. I have your number as 929-433-7408 and your date of birth as September 30, 1995. Is that correct?"
- **Why it's a problem:** The agent first asks if the phone number on file can be used, and after confirmation, it still asks the patient to repeat it. This redundancy shows a lack of coherent flow in the conversation.

## [Low] Poor Turn-taking
- **Call:** `CA9f21918c5d805eb2165c944def948b7b` (scenario: schedule_basic)
- **Quote:** "PATIENT: Hi, I'm calling to schedule a routine check-up for next week, preferably in the morning. AGENT: Bye. Hup."
- **Why it's a problem:** The agent appears to abruptly end the conversation without processing the request, causing a disjointed interaction.

