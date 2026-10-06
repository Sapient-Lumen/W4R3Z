# Deterministic redaction transforms (privacy as evidence)

Logs, traces, audit records, crash dumps, and replay traces frequently contain:

- credentials
- identifiers (emails, tokens, UUIDs)
- business secrets

DeriveBSD already treats *authority* as explicit.
It should also treat *privacy filtering* as explicit and auditable.

## Goal

Make redaction:

- **deterministic** (same input + same transform → same output)
- **hashable** (outputs are referenced by digest)
- **reviewable** (transforms are signed artifacts, not ad-hoc scripts)

## Model

### 1) A redaction transform is a first-class artifact

A **`redaction.transform`** defines a profile/module used to sanitize data.
It can be:

- declarative rules (allowlists + simple value masking)
- a sandboxed module (policy-as-Wasm runtime reuse)

Schema: `spec/redaction.transform.schema.json`

### 2) Applying redaction produces a receipt

A **`redaction.receipt`** binds:

- `input_digest`
- `output_digest`
- `transform_digest`

This makes “what was removed/changed” an attachable, verifiable fact.

Schema: `spec/redaction.receipt.schema.json`

## Where it plugs in

- UI data transfer (clipboard / drag&drop) can bind a redaction profile by digest so “safe paste paths” are reviewable: `docs/205-data-transfer-portals-clipboard-and-dnd.md`.
- `trace.stream.grant.constraints.redaction_profile_digest`
- `debug.record.grant.constraints.redaction_profile_digest`
- `trace.capsule.redaction` and `debug.replay.capsule.redaction`
- Export policies and receipts bind deterministic redaction at share time: `export.policy.rules[].redaction_transform_digest` and `export.receipt.redaction.receipt_digest` (see `docs/251-export-policies-and-support-bundle-portal.md`).
- Packet-capture normalization for stronger imported artifacts uses the same generic redaction lane: the official safe-open import receipt points at a constrained packet-capture `redaction-transform` / `redaction-receipt` pair rather than treating `strip-metadata` as tool folklore (`docs/512-packet-capture-normalization-redaction-receipt-boundary.md`, `spec/redaction.transform.packet-capture.schema.json`, `spec/redaction.receipt.packet-capture.schema.json`).

## Invariants

- Prefer allowlist-first rules (“keep these fields”) over denylist guessing.
- Redaction configuration is versioned and signed.
- Forensics mode is explicit and requires additional grants.

See also:
- `docs/186-policy-modules-wasm.md`
- `docs/192-observability-as-capability.md`
- `docs/194-debugging-by-lease-and-replay-capsules.md`

Last updated: 2026-03-09r241
