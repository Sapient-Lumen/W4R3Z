# Cube audit rev0039

Current revision: rev0055

Rev0037 adds a composed overload-governance model slice and audits the cube around that slice.

## Audit/refactor work

- Added `StorageLaneOverloadGovernanceModelOracle` as a distinct runtime noun.
- Added proof and contract-audit tasks for `scheduler:storage-lane-overload-governance-model-proof`.
- Updated runtime exports, IPC exports, type declarations, boot-report executable proof flags, manifest, impact map, surface inventory, research registry, validation index, receipt, context pack, and non-claims charter.
- Kept broad release browser-light.
- Refactored release economics: carried-forward semantic proofs still run in release, but older per-rung contract audits now live in audit/full unless they are the current slice. This keeps future sessions from confusing stale carry-forward audit failures with runtime regressions.
- Preserved carried-forward admission-history, provider-resilience, retry-budget, circuit-breaker, persisted-spill, and OPFS/browser non-claims.
- Fixed `tools/package_release.py` to freeze package file bytes before manifest hashing/zip writing, after audit exposed a possible manifest/zip hash skew from late-settling proof artifacts.

## What future sessions should not miss

This revision composes existing fake-provider governors; it does not replace their individual proofs. The new oracle is a bridge toward future provider spending, not a production overload controller.
