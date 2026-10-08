# Run-definition hash-lock refactor — rev0332

## Problem

A local result receipt can be privacy-safe and still be scientifically useless if the intervention it
summarizes is not the intervention the owner reviewed. Before rev0332, the owner-review stop record
did not hash-lock all run-defining files. `COACH-PROMPT.md`, `RUN-CHECKLIST.md`, `CYCLE-RUN-SHEET.md`,
and the discovery card could change after packet generation or after review without the result
recorder noticing.

## Refactor

`tools/score_teacher_tutor_micro_pilot_readiness.py` now includes the entry check
`run-definition-hash-stable`. It requires:

- `DISCOVERY-FIRST-CONTACT.md`, `COACH-PROMPT.md`, `RUN-CHECKLIST.md`, `MEASURE-CARD.md`, and
  `CYCLE-RUN-SHEET.md` to match the hashes recorded in `PACK-MANIFEST.json`;
- `COACH-PROMPT.md` to match the prompt-card SHA-256 recorded in `OWNER-PLAN.md`;
- the owner plan to confirm the prompt card stayed unchanged, with regeneration required if it changed.

`tools/record_teacher_tutor_micro_pilot_owner_review.py` now includes those run-defining files in the
owner-review packet hash scope. `tools/record_teacher_tutor_micro_pilot_result.py` already refuses a
result when any owner-reviewed packet hash changes, so the result path now inherits the stronger
hash-lock without a new recorder.

## Smoke scenario

A fresh generated packet still reports `NOT_READY` until the owner plan is completed. A synthetic dry
run with unchanged run-definition files reaches `SYNTHETIC_READY_SMOKE_NOT_EVIDENCE`. If
`COACH-PROMPT.md` is edited after generation, readiness remains blocked and reports prompt hash drift.
If the prompt is edited after owner review, the result recorder refuses the packet as changed after
owner review.

## Boundary

Hash stability is provenance, not evidence. It does not contact an educator, run a cycle, estimate
efficacy, prove learning, support a public claim, authorize service use, or close `FT-0181`.
