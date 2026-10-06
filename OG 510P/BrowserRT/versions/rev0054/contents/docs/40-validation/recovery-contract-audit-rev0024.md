# Recovery contract audit rev0028

Revision: rev0028

Manifest id: `facility:recovery-contract-audit`

Tool: `tools/recovery_contract_audit.mjs`

Artifact: `artifacts/audit/REV0044-RECOVERY-CONTRACT-AUDIT.json`

## Purpose

Rev0023 adds a real recovery-oriented runtime primitive. This audit/factor checks that the new proof is not floating alone. The source, docs, manifest, impact map, surface inventory, validation index, and non-claim surfaces must agree about what was earned and what was not.

## Checks

- `PersistedSpillMailbox` source contains checkpoint, journal, recovery, ack, and pending-redelivery events.
- `ipc:persisted-spill-recovery-proof` exists in `test/manifest.json` and remains release-tier friendly.
- `tools/persisted_spill_recovery_probe.mjs` writes the current artifact path.
- The proof artifact is current, passed, and contains key observations.
- The related-work registry includes durable queue / stream / browser-storage sources.
- The non-claims charter and future-session office manual mention persisted-spill non-claims.
- Browser-light release policy remains intact.

## Why this belongs

Future sessions see less context. A small audit/factor gives them a concrete office-respect surface: this rung is useful, but still fake-provider-only.
