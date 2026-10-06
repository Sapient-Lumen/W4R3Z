# Store layout, digests, and closure computation

Define store identity and closure verification.

## Store object identity

- Store objects are **content-addressed** by a digest over a deterministic serialization of their contents.
- Digests must be **hash-agile** (algorithm is policy-selectable / upgradeable).

See: `adrs/ADR-0013-content-addressed-store-hash-agility.md` (proposed) and `adrs/ADR-0024-tree-serialization-dar.md`.

## Path shape (convention)

`/derive/store/<digest>-<name>/...`

- digest is the authoritative identity
- name is human-friendly only (non-authoritative)

## Closures

Closures are transitive dependency sets. Deployment verifies:

- required objects exist
- digests match expected
- refuse on mismatch (`adrs/ADR-0009-artifact-verification.md`)

To make closures auditable and policy-verifiable, DeriveBSD emits a small **closure manifest** and (typically) a **closure proof** signature.

See: `docs/90-closure-proof.md` and `spec/closure.manifest.schema.json`.

Last updated: 2026-02-23
