# DeriveBSD rev0590 review

Generated for version: `2026-06-18r616`

## Priority focus

The riskiest unfinished seam after rev0589 was proof identity for the new executable runtime path. The same spec and stamp produced different runtime evidence when the local workspace path changed, so local cloudtainer paths were leaking into semantic proof identity.

## Substantive changes

- Added the `derive-runtime-v0-content-identity-no-local-locators` runtime identity profile.
- Made lock, plan, artifact, activation, rollback, explanation, and run-summary digests path-independent while preserving semantic inputs, authorities, blast radius, artifact content, target intent, and upstream digest bindings.
- Added upstream digest verification before downstream runtime stages: plan checks lock, build checks plan, activate checks artifact, rollback checks activation receipt, and explain checks the live chain.
- Strengthened `tools/check_runtime_golden_thread.py` with same-spec/same-stamp cross-workspace stability and stale lock/plan digest tamper rejection.
- Refreshed stale cube-cut constants and generated examples for schema-audit, schema-refactor, hygiene-checkset, host-smoke, host-proof-bundle, and real-host work-order surfaces.
- Regenerated the current dry-run runtime evidence workspace and current release-critical ledger.
- Kept the front door within its byte/line budget by compacting the r616 index entry instead of raising budgets.

## Honest boundary

This remains dry-run local runtime evidence. No real FreeBSD host proof was imported, no `bectl` activation happened, and no bhyve VM was launched.

## Validation

- Release-critical hygiene: 52/52 passed, 0 failed, 0 timed out.
- Schema-cube-audit hygiene: 3/3 passed, 0 failed, 0 timed out.
- Spec examples: 469 examples validated.
