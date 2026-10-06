# Cube audit rev0036

Current revision: rev0055

Audit/refactor focus: make the new admission-history model oracle legible without leaving duplicate or stale model surfaces behind.

Findings and actions:

- Added `StorageLaneAdmissionHistoryModelOracle` as the canonical model companion to `StorageLaneAdmissionHistoryRunner`.
- Removed the stale duplicate `src/storage-lane-admission-history-model.mjs` path during refactor and kept `src/storage-lane-admission-model.mjs` canonical.
- Added `scheduler:storage-lane-admission-model-proof` and `facility:storage-lane-admission-model-contract-audit`.
- Updated current metadata so future sessions see rev0036 as an earned fake-provider model rung, not an OPFS/browser step.
- Preserved broad release as browser-light.

Next earned stair: OPFS prerequisite factoring or richer admission-history model expansion only after this fake-provider model surface remains stable.

## Rev0036 release-facility refactor

Broad release now keeps the current admission-history proof/audit plus the new admission-model proof/audit in release, while older detailed contract audits remain runnable by explicit id or `audit`/`full` tier. This keeps future-session release windows cheaper without deleting carry-forward surfaces.

