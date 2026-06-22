"""
Draft a bug report from the saved transcripts.

This reads every transcripts/*.json, asks an LLM to flag bugs / quality issues
in the AGENT's behavior (NOT the patient's), and writes BUGREPORT.md.

This is a DRAFT to speed you up — read the calls yourself and keep only the
real, well-described bugs. Useful bugs beat a long list of nitpicks.

Usage:  python analyze_bugs.py
"""
from __future__ import annotations

import glob
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
MODEL = os.environ.get("ANALYZE_MODEL", "gpt-4o")

RUBRIC = """You are QA-reviewing a medical-practice voice AI agent. You are given a
phone-call transcript between a PATIENT (a tester) and the AGENT (the AI under test).
Find concrete BUGS or quality issues in the AGENT's behavior only. Look for:
- Confirming things it shouldn't (e.g. booking a closed day/weekend, impossible times)
- Hallucinated facts (hours, addresses, insurance, policies) stated with false confidence
- Failing to ask for needed info (name, DOB, pharmacy) before acting
- Dropping one of several requests; losing track of context
- Unsafe medical advice, or refusing reasonable requests
- Bad turn-taking, talking over the patient, long awkward pauses (if visible)
- Not confirming/no callback on cancellations or refills

For each issue return: title, severity (High/Medium/Low), the exact transcript
quote that shows it, and why it's a problem. If the call looks clean, say so.
Return STRICT JSON: {"issues":[{"title","severity","quote","why"}]}"""


def analyze(call):
    convo = "\n".join(f"{t['speaker']}: {t['text']}" for t in call["turns"])
    resp = client.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": RUBRIC},
            {"role": "user", "content": f"Scenario: {call['scenario']}\nCall: {call['call_sid']}\n\n{convo}"},
        ],
    )
    try:
        return json.loads(resp.choices[0].message.content).get("issues", [])
    except Exception:
        return []


def main():
    files = sorted(glob.glob("transcripts/*.json"))
    if not files:
        print("No transcripts found. Make some calls first (python call.py --all).")
        return
    sev_rank = {"High": 0, "Medium": 1, "Low": 2}
    rows = []
    for fp in files:
        call = json.load(open(fp))
        print(f"analyzing {call['call_sid']} ({call['scenario']}) ...")
        for issue in analyze(call):
            issue["call"] = call["call_sid"]
            issue["scenario"] = call["scenario"]
            rows.append(issue)
    rows.sort(key=lambda r: sev_rank.get(r.get("severity", "Low"), 3))

    with open("BUGREPORT.md", "w") as f:
        f.write("# Bug Report — PGAI Voice Agent\n\n")
        f.write(f"_Auto-drafted from {len(files)} calls; curate before submitting._\n\n")
        for r in rows:
            f.write(f"## [{r.get('severity','?')}] {r.get('title','(no title)')}\n")
            f.write(f"- **Call:** `{r['call']}` (scenario: {r['scenario']})\n")
            f.write(f"- **Quote:** \"{r.get('quote','').strip()}\"\n")
            f.write(f"- **Why it's a problem:** {r.get('why','').strip()}\n\n")
    print(f"\nWrote BUGREPORT.md with {len(rows)} candidate issues. Now read the calls and keep the real ones.")


if __name__ == "__main__":
    main()
