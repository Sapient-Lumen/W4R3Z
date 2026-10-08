# P0002-D010 reader-packet debias / response-gate audit — rev0037

## Finding

Rev0036 solved one problem and introduced two new risks.

First, the reader packet was disclosed-first, but it also named the hostile failure category — `graceful receipt object` — before the poem. That could make a future reader response measure packet priming rather than the poem.

Second, `tools/check_candidate_reader_packet.py` required the response log to be empty. That meant the recommended next action, recording a real reader response, would have made validation fail.

## Change

Rev0037 keeps machine/source/runtime disclosure before the poem, but moves hostile failure language into a separate evaluator rubric:

- reader packet: `anthology/candidates/P0002-D010_disclosed_reader_packet.md`
- evaluator rubric: `anthology/candidates/P0002-D010_evaluator_rubric.md`
- run sheet: `anthology/candidates/P0002-D010_reader_run_sheet.md`

The validator now allows either zero responses or real non-identifying responses, while still blocking admission/evidence leakage and personal-data collection.

## Research pulse used

- HHS/OHRP quality-improvement guidance reinforced the distinction between local improvement/editorial activity and research-purpose overclaim.
- Digital.gov plain-language guidance reinforced short, audience-first, testable reader surfaces.
- W3C WAI Easy Checks reinforced basic accessible HTML requirements such as language, title, headings, and no avoidable interaction burden.

## Non-claim

No external reader response is recorded in rev0037. D010 remains an internal anthology candidate, not admitted and not evidence-ready.
