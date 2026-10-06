# Recovery contract audit rev0033

Revision: rev0033

Manifest id: `facility:recovery-contract-audit`

Tool: `tools/recovery_contract_audit.mjs`

Artifact: `artifacts/audit/REV0044-RECOVERY-CONTRACT-AUDIT.json`

## Purpose

Carry forward the persisted-spill recovery contract while rev0033 adds retention/compaction. The audit still checks source, docs, manifest, impact map, surface inventory, validation index, proof artifact, research registry, and non-claim surfaces for the recovery rung.

## Current boundary

Recovery is fake-provider-only. Pending entries redeliver at-least-once. Recovery plus compaction does not imply OPFS durability, browser reload/crash recovery, quota/eviction behavior, or exactly-once delivery.


## Rev0028 carry-forward note

This is a current-revision carry-forward audit document for `recovery`. It keeps the source, docs, manifest, impact map, surface inventory, proof artifact, and non-claim boundaries visible while rev0033 adds storage-lane model and retry surfaces.


This audit remains release tier and browser-light; it carries fake-provider recovery semantics forward without OPFS/browser spending.


## rev0033 carry-forward note

This current-revision carry-forward document keeps the older proof/audit boundary visible while rev0033 adds the circuit-breaker/bulkhead model oracle. It does not upgrade any OPFS, browser, production, performance, durability, or formal-verification claim.
