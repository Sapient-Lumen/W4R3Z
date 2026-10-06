# ADR-0001: Spec encoding

- Status: **accepted**
- Date: 2026-02-22

## Context

DeriveBSD needs a typed, diff-friendly Spec format that:
- supports stable merging
- provides great error messages
- keeps the default surface “data-first”
- can be hashed/signature-bound deterministically

## Decision

1) **Canonical form is JSON** (UTF-8), validated by **JSON Schema**.
2) Any human-friendly frontend (e.g., HuJSON) MUST compile to canonical JSON.
3) All digests/signatures are computed over **JCS-canonical JSON** bytes.

This keeps the “Spec surface” simple and toolable (editors, schemas, tooling), while enabling deterministic hashing/signing.

See:
- canonical JSON hashing: ADR-0022 (`adrs/ADR-0022-canonical-json-jcs.md`)
- spec-as-data frontends: ADR-0023 (`adrs/ADR-0023-spec-as-data-frontends.md`)

## Consequences

- The evaluator can remain minimal (no Turing-complete spec language required).
- Specs become a stable API boundary for:
  - `derive explain` output
  - policy evaluation inputs
  - evidence objects
- We must invest in good schema ergonomics (defaults, error paths, examples).

