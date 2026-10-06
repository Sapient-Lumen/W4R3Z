# Recovery contract audit rev0028

Revision: rev0028

Manifest id: `facility:recovery-contract-audit`

Tool: `tools/recovery_contract_audit.mjs`

Artifact: `artifacts/audit/REV0044-RECOVERY-CONTRACT-AUDIT.json`

## Purpose

Carry forward the persisted-spill recovery contract while rev0028 adds retention/compaction. The audit still checks source, docs, manifest, impact map, surface inventory, validation index, proof artifact, research registry, and non-claim surfaces for the recovery rung.

## Current boundary

Recovery is fake-provider-only. Pending entries redeliver at-least-once. Recovery plus compaction does not imply OPFS durability, browser reload/crash recovery, quota/eviction behavior, or exactly-once delivery.
