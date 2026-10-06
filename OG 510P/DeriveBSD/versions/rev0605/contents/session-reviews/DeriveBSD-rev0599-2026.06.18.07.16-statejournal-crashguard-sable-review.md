# DeriveBSD rev0599 review

Generated for version: `2026-06-18r625`

## Priority focus

The riskiest unfinished seam after rev0598 was crash ambiguity around local state mutation. The prior cut had an exclusive writer lock and no-clobber generation receipts, but an interruption between generation receipt creation and the current-generation pointer update could still leave evidence that was locally valid while operationally ambiguous.

## Substantive changes

- Added a digest-bound `.derive-runtime-state-journal.json` precommit journal around dry-run activation and rollback.
- Activation and rollback now write the journal before changing `current-generation.json`, remove it only after the fsynced commit, and bind the journal digest into the resulting receipt.
- Pending journals fail closed before later activation or rollback, preserve the journal for operator review, and do not remove another writer's lock.
- Extended `tools/check_runtime_golden_thread.py` with stale-journal activation/rollback regressions plus cleanup assertions for successful commits and duplicate-generation refusal.
- Updated runtime golden-thread docs, start-here docs, r625 OS lesson, generated docs/current surfaces, FreeBSD proof-bundle/work-order surfaces, and the checked release ledger.
- Kept this as runtime crash-safety work, not a new schema-family expansion.

## Honest boundary

This remains dry-run local runtime evidence. No real FreeBSD host proof was imported, no `bectl` activation happened, no bhyve VM was launched, and resolver work remains fixture-based rather than authoritative FreeBSD package-index resolution.

## Validation

- Release-critical hygiene ledger: 52/52 passed, 0 failed, 0 timed out.
- Schema-cube-audit hygiene: 3/3 passed, 0 failed, 0 timed out.
- Spec examples: 469 examples validated.
