# Priority-0 clean-response admission gate — 2026-06-16

`rev0369` resolves `OQ-0260` narrowly via `RS-0268`: the cube still lacks a clean external/operator-independent response, but the admission path now refuses to treat responder self-attestation as enough. A completed-looking response must be accompanied by a separate custody evidence record before strict scoring can count it as clean external evidence.

## Risk burned

The risky gap after `rev0368` was not lack of another doctrine surface. It was that the lane could accept a future response too cheaply: correct packet hashes, non-empty answers, and self-attested no-key/no-archive booleans could be mistaken for clean custody. The scoring tool also needed to stop relying on a frozen historical default scorer and instead resolve the live scorer from `FRONTIER-BACKLOG.json`.

## Concrete changes

- Added the custody-hardened responder bundle `handoffs/priority-zero-custody-hardened-external-replay-responder-bundle-2026-06-16.zip` and submission kit `handoffs/priority-zero-custody-hardened-external-replay-submission-kit-2026-06-16.zip`.
- Added `assays/priority-zero-clean-external-response-evidence-record-template-2026-06-16.json` so custody must be recorded outside the responder's own claims.
- Added `assays/priority-zero-custody-hardened-external-replay-scorer-intake-2026-06-16.json`, whose OQ-routing metric now points from `OQ-0260` to `OQ-0261` and whose strict mode requires a custody evidence record.
- Added `assays/priority-zero-custody-hardened-external-replay-self-attested-cleanlike-canary-2026-06-16.json`, a complete-looking self-attested response that must fail before manual scoring.
- Refactored `tools/score_priority_zero_external_replay_response.py` so the default scorer is `auto:frontier` and current strict scoring can require `--evidence-record`.
- Refactored `tools/run_lint_suite.py` so every checker runs in an isolated subprocess with `PYTHONDONTWRITEBYTECODE=1`; this cuts `runpy` state leakage, bytecode residue, and temp-tree inheritance without weakening the admission suite.

## Scored posture

| Variant | Score | Cost | Meaning |
|---|---:|---:|---|
| Pre-custody submit strict path | 8 / 16 | 4 min | Useful contamination guard, but still too self-attestation-friendly. |
| Custody-hardened current admission gate | 14 / 16 | 7 min | Current scorer and bundle are ready, but successor response is still absent. |
| Self-attested cleanlike negative canary | 16 / 16 | 1 min | Correctly rejects clean-looking self-attestation without custody record. |
| Clean response plus custody evidence | 0 / 16 | 0.5 min | Correctly absent. |

## Non-takes

This is not a clean external replay result, not independent certification, not deletion authority, not benchmark authority, not compact-cue confirmation, not a minimality proof, and not a review court. The compact gate remains narrowed until `OQ-0261` has a completed response plus custody evidence record scored after response freeze.

## Next action

Give only `handoffs/priority-zero-custody-hardened-external-replay-responder-bundle-2026-06-16.zip` to a responder. Freeze their completed response. Fill a custody evidence record from `assays/priority-zero-clean-external-response-evidence-record-template-2026-06-16.json` before opening `assays/priority-zero-custody-hardened-external-replay-scorer-intake-2026-06-16.json`. Then score with `tools/score_priority_zero_external_replay_response.py --evidence-record <record> <response>` and confirm, narrow, or reverse compact reentry based on the result.
