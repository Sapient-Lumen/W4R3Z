# Revision 0403 — contract-bound replay proof

Date: 2026-03-22
Revision: 0403

## What changed

- added `src/vhk/project/macro_proof_contract.py`
- runner now records `macro_proof_contract` on `run_start`
- `macro-latest-run-json` and replay-board health now compare current source/recorder state against the recorded proof contract
- replay posture now has `stale_contract`
- selected-macro replay tickets now route stale proof to `rerun_after_contract_change`
- added tests covering stale replay proof after macro edits and stack routing for that condition

## Why it matters

VHK is supposed to optimize for **record -> cleanup -> replay -> inspect -> refine** on a warm X11/i3 runtime. Old healthy logs are useful evidence, but they should not keep counting as current replay proof after the operator or a private LLM edits the macro or its recorder context. This revision makes replay truth stricter and more honest.
