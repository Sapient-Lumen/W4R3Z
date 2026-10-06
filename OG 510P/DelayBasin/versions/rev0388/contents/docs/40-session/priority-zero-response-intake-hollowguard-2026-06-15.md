# Priority-0 response-intake hollow guard — 2026-06-15

## Risk burned

`rev0366` made the external replay lane physically runnable: a responder-only ZIP existed, scorer material stayed outside the bundle, and the compact gate stayed narrowed while completed response evidence remained absent. The still-risky gap was smaller and more operational: a future scorer could receive a custody-clean response with correct hashes and labels but empty packet answers, then accidentally treat the file as a completed response.

That would be wasteful in exactly the way this cube is trying to escape. The archive would create a bundle, a manifest, a scorer intake, and a checker, yet still fail at the moment where substantive evidence should enter.

## Change made

This revision resolves `OQ-0258` narrowly by adding an intake-hardened handoff lane:

- `assays/priority-zero-intake-hardened-external-replay-responder-only-2026-06-15.json`
- `assays/priority-zero-intake-hardened-external-replay-response-template-2026-06-15.json`
- `handoffs/priority-zero-intake-hardened-external-replay-responder-bundle-2026-06-15.zip`
- `handoffs/priority-zero-intake-hardened-external-replay-handoff-manifest-2026-06-15.json`
- `assays/priority-zero-intake-hardened-external-replay-scorer-intake-2026-06-15.json`
- `assays/priority-zero-intake-hardened-external-replay-shape-pass-canary-2026-06-15.json`
- `assays/priority-zero-intake-hardened-external-replay-hollow-response-canary-2026-06-15.json`
- `assays/priority-zero-intake-hardened-external-replay-leak-response-canary-2026-06-15.json`
- `assays/priority-zero-response-intake-hollowguard-2026-06-15.json`
- `tools/check_priority_zero_response_intake_hollowguard_contract.py`
- `tools/build_priority_zero_intake_hardened_handoff_bundle.py`
- `tools/score_priority_zero_external_replay_response.py`

The scorer now rejects hollow responses before any manual scoring can matter. A response must carry the expected bundle hash, expected packet hash, scorer-key separation attestation, no-full-archive-before-response attestation, positive operator cost, exact packet labels, and non-empty substantive fields for every packet answer.

## Audit / refactor

`tools/check_priority_zero_current_tail_external_bundle_contract.py` is now historical evidence for `rev0366` rather than current-tail authority. The new checker owns the live `rev0367` invariants, and the scoring tool owns reusable response-intake completeness rules. This cuts duplicated current-tail assumptions and prevents stale rev0366 handoff readiness from being mistaken for the live completed-response test.

## Scores

| Variant | Score | Operator cost | Interpretation |
|---|---:|---:|---|
| Pre-hardening scorer hollow-risk | 8 / 16 | 3 min | Hashes/labels/order could pass while blank answers still slipped through. |
| Hardened intake scorer | 15 / 16 | 4 min | Rejects hollow or leaked responses and keeps the absent-response boundary explicit. |
| Hollow-response negative canary | 16 / 16 | 1 min | Correctly fails before scoring; this is the proof point for the change. |
| Completed external-response evidence | 0 / 16 | 0.5 min | Still absent. No independent response is claimed. |

## Non-takes

This is not an external replay result, not independent certification, not deletion authority, not a minimality proof, not benchmark authority, and not a review court. It is an intake hardening and hollow-response guard.

## Next action

Hand only `handoffs/priority-zero-intake-hardened-external-replay-responder-bundle-2026-06-15.zip` to a responder who has not seen scorer-only material or the full archive. After they fill the response template with substantive answers, score the completed response with `assays/priority-zero-intake-hardened-external-replay-scorer-intake-2026-06-15.json`. That successor is `OQ-0259`.
