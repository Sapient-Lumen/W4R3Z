# Storage-lane quarantine review replay-key scope contract-audit slice

Task: `facility:storage-lane-quarantine-review-replay-key-scope-contract-audit`

This facility audit keeps the replay-key-scoped review boundary wired through runtime, proof, browser proof, docs, manifest, impact map, surface inventory, and first-read package surfaces.

The audit specifically looks for `operationReplayKeys` review manifests, ambiguous opId clear rejection, row-level stale replay protection, and the current managed Chromium proof. It is intended to prevent the cube from regressing to visible-`opId`-only maintenance clearing after timeout-quarantine identity has moved to `operationReplayKey`.

Non-claims: audit only; it does not launch Chromium and does not prove durability, provider cancellation, rollback, no-mutation-on-timeout, cross-browser behavior, cryptographic attestation, throughput, latency, or production readiness.
