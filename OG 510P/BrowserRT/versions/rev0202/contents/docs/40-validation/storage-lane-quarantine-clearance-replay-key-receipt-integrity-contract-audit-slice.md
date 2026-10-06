# Storage-lane quarantine clearance replay-key receipt integrity contract audit

Current audit: `facility:storage-lane-quarantine-clearance-replay-key-receipt-integrity-contract-audit`.

This contract audit checks the runtime hooks, release-light probe, Managed Chromium proof, docs, manifest, impact map, surface inventory, scripts, changelog, and first-read currentness for the current slice.

Required anchors: `operationReplayKeys must match cleared row operationReplayKeys`, `cleared row operationReplayKey mismatch`, missing/extra replay keys, and current slice.

## Non-claims

Audit only; no browser execution, provider cancellation, rollback, durability, quota/eviction survival, cryptographic attestation, or production readiness claim.
