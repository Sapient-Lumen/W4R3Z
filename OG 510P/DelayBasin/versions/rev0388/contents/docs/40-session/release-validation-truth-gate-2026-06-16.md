# Release-validation truth gate — 2026-06-16

`rev0370` resolves `OQ-0261` via `RS-0269`, but only as a release-validation truth repair. The risky defect was concrete: a fresh lint run from the packaged `rev0369` ZIP failed at `tools/check_package_identity_witness_contract.py` because static root currentness surfaces still carried stale revision/current-revision tokens while the receipt claimed `make lint` and `make package-release` had passed.

## What was wrong

The failure was not semantic disagreement about the Priority-0 external replay mission. It was a release-integrity breach: the archive could present a full-validation receipt while the citable ZIP did not survive a fresh lint path. That is more urgent than adding another external-replay doctrine surface, because every later handoff relies on the package being truthfully reproducible.

The observed drift class was static currentness spillover across `CANARY-PROTOCOL.json`, `LINK-INTEGRITY-POLICY.json`, `WITNESS-VOCABULARY.json`, `WITNESS-FAMILY-HANDLES.json`, `PATH-ALIAS-LEDGER.json`, and `ALIAS-RETENTION-POLICY.json`.

## What changed

- Resynchronized the static package-identity/currentness surfaces to `rev0370` and added `assays/release-validation-truth-gate-2026-06-16.json` plus `tools/check_release_validation_truth_gate_contract.py` so the same class of stale root-currentness drift fails closed.
- Historicalized `tools/check_priority_zero_clean_response_admission_gate_contract.py` so the rev0369 custody-admission gate remains citable evidence without locking the current tail or forcing stale current additions.
- Refactored `tools/score_priority_zero_external_replay_response.py` with `--summary-out`, allowing the future clean-response score to emit a citable JSON summary instead of relying on copied stdout.
- Kept the actual clean response plus custody evidence absent. The compact gate remains narrowed until `OQ-0262` has a frozen response, separate custody record, and post-response score.

## Scored posture

| Variant | Score | Operator cost | Meaning |
|---|---:|---:|---|
| Released rev0369 fresh-lint regression | 4 / 16 | 2 min | Real defect: receipt/check claims outran fresh package validation. |
| Static currentness resync | 14 / 16 | 4 min | Stale root currentness fields repaired and scanned by package identity audit. |
| Release-claim truth gate | 15 / 16 | 8 min | Checker added to the validation toolchain and historical checker lock-in removed. |
| Clean response plus custody evidence | 0 / 16 | 0.5 min | Correctly absent; no clean external/operator-independent response exists yet. |

## Non-takes

This is not clean external replay success, not independent certification, not deletion authority, not compact-cue confirmation, not a benchmark authority, not a minimality proof, and not a review court.

## Next action

`OQ-0262` remains the live frontier: hand only `handoffs/priority-zero-custody-hardened-external-replay-submission-kit-2026-06-16.zip` or the contained responder bundle to a clean responder, freeze the response, complete `assays/priority-zero-clean-external-response-evidence-record-template-2026-06-16.json`, then score with `make score-external-response RESPONSE=<response.json> EVIDENCE=<custody-record.json>` or the scorer tool's `--summary-out` path.
