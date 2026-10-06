# Storage-lane quarantine operation replay-key collision slice

Task: `scheduler:storage-lane-quarantine-operation-replay-key-collision-proof`

This release-light slice covers a timeout-quarantine data-loss risk in the storage-lane maintenance path. Earlier quarantine replay work added `operationEpoch` / `operationReplayKey`, but the live quarantine maps still keyed rows by visible `opId`. A merged handoff ledger with the same visible `opId` from two distinct operation epochs could therefore collapse or reject rows that should remain separately reviewable.

The proof imports a synthetic timeout-quarantine ledger with two successful timed-out rows that deliberately share the same visible `opId` but carry distinct `operationReplayKey` values. It verifies both rows survive import, duplicate operationReplayKey rows fail closed, clearance receipt validation permits repeated visible `opId` only when replay keys differ, and stale exact / single-row replay are rejected after reviewed clearance.

Non-claims: this is not provider cancellation, rollback, no-mutation-on-timeout, exactly-once semantics, cryptographic attestation, durability, quota/eviction survival, throughput, latency, or production-readiness evidence.
