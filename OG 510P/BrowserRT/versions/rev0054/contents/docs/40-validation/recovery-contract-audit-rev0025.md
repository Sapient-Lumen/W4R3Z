# Recovery contract audit — rev0028

Manifest id: `facility:recovery-contract-audit`.

## Purpose

This carry-forward audit keeps the rev0023 persisted-spill recovery contract coherent while rev0028 works on scheduler model-walks. It verifies source, docs, manifest, impact map, surface inventory, proof artifact, research registry, and non-claim boundaries for the fake-provider recovery model.

The audit is intentionally a coherence guard, not a new recovery feature. It prevents future sessions from losing the persisted-spill boundary while they refactor scheduler or testing surfaces.

## Command

```bash
node tools/persisted_spill_recovery_probe.mjs --json artifacts/validation/REV0044-PERSISTED-SPILL-RECOVERY-PROBE.json
node tools/recovery_contract_audit.mjs --json artifacts/audit/REV0044-RECOVERY-CONTRACT-AUDIT.json
```

## What it checks

- `ipc:persisted-spill-recovery-proof` remains release-tier and browser-light.
- `facility:recovery-contract-audit` remains release-tier and browser-light.
- The proof artifact is current for rev0028.
- The docs still state fake-provider, at-least-once, pending redelivery, and no exactly-once boundaries.
- The source/probe/manifest/impact/surface inventory stay aligned.

## Non-claims

- No OPFS persisted-spill proof.
- No browser Worker persisted-spill proof.
- No exactly-once delivery claim.
- No fsync, flush, quota, eviction, or durability claim.
- No browser reload/crash recovery proof.
