# ADR-0043: MicroVM plan digest is `sha256(JCS(plan))`

- Status: **accepted**
- Date: 2026-03-04

## Context

`microvm.*.plan` objects are the **input** side of the host-local `derive-vmmd` authority boundary.
Receipts bind outcomes to the executed plan via `plan_id` + `plan_digest`.

DeriveBSD already standardizes JCS (RFC 8785) as the canonicalization step for “hashable JSON” (`docs/80-canonical-json-hashing-jcs.md`), and multiple core artifacts define digests as:

- `sha256( JCS(json) )` (e.g., runtime manifests and microVM bundles)

However, the new microVM lifecycle artifacts did not yet make the digest algorithm explicit.
Leaving it implicit invites drift:

- different backends or tools pick different algorithms
- examples stop being mechanically checkable
- operators lose a stable join key (“is this the same plan?”)

We want a rule that is:

- implementable across languages with minimal dependencies
- consistent with existing DeriveBSD hashing rules
- strict enough to enable drift checks

## Decision

For microVM lifecycle plans:

- `plan_digest = "sha256:" + hex( sha256( utf8( JCS(plan_json) ) ) )`

Where:

- `JCS(plan_json)` is the RFC 8785 canonical JSON encoding
- hashing uses raw UTF-8 bytes of the canonical encoding
- hex is lower-case

This applies to:

- `microvm.launch.plan` → `microvm.launch.receipt.plan_digest`
- `microvm.stop.plan` → `microvm.stop.receipt.plan_digest`

## Consequences

- Receipts across A–D have a single, stable “same plan” join key.
- We can mechanically validate that receipt examples actually match plan examples.
- If DeriveBSD later standardizes a different plan-digest algorithm, that change MUST be explicit (new plan/receipt versions + an ADR), and callers should treat it as a compatibility boundary.

See: `docs/455-microvm-launch-plans-and-receipts.md`, `spec/microvm.launch.receipt.schema.json`, `spec/microvm.stop.receipt.schema.json`.
