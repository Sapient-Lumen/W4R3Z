# Schema evolution rules (Spec/Lock/Plan/Manifest/Bundle)

Stable contracts enable safe automation and long-lived archives.

## Versioning
- Major bumps can break compatibility.
- Minor bumps are additive and backward compatible.

## Rules (v1)
- Never change the meaning of existing fields in a minor bump.
- Add fields with explicit defaults.
- Deprecations require:
  - a warning period
  - a migration tool (`derive migrate`)

## Required field
All machine-readable contracts include `schema_version`.

See RFC-0022.
Last updated: 2026-02-23

## Canonical JSON pointer

Canonical hashing rules live in `docs/80-canonical-json-hashing-jcs.md` (RFC-0053, ADR-0022).
