# Store

## Minimum properties

- **Immutable artifacts:** new builds produce new objects (no mutation-in-place).
- **Strong integrity:** digests always verified; signatures/attestations supported.
- **Efficient GC:** explicit roots define reachability.
- **Introspectable closures:** “show me everything needed at runtime.”

## Identity model (two digests)

DeriveBSD separates two identities:

1) **Plan digest** (what we intended to build)
- hash of Lock + policy decision record + fully evaluated DAG (+ normalized env)

2) **Object digest** (what we actually got)
- hash of serialized output objects as stored (tree serialization; see `adrs/ADR-0024-tree-serialization-dar.md`)

The store is keyed by **object digests** (hash agility is a requirement; see ADR-0013). platform identity is carried in typed metadata rather than encoded into store paths; the archive now treats cross-build truth as explicit `build_platform` / `host_platform` / optional `target_platform` data. See `docs/701-cross-compilation-platform-identity-stays-build-host-target-shaped-and-not-store-path-encoded.md`.

## Store paths (recommended shape)

`/derive/store/<digest>-<name>/...`

- `<digest>` is authoritative (content-addressed identity)
- `<name>` is a human hint only (non-authoritative)
- target triples, `TARGET`/`TARGET_ARCH`, or other platform selectors do **not** become path authority

See: `docs/56-store-layout-and-digests.md` (RFC-0033, ADR-0013).

## Metadata index (v1)

Need a queryable index for:

- object → inputs (Plan digest, sources, toolchain id)
- object → runtime refs (closure edges)
- build logs + sandbox policy summary
- provenance/attestation pointers (if present)

v1 recommendation: **SQLite index** keyed by object digest/store path.

Platform role metadata belongs in that index too, but as typed fields attached to objects and plans rather than as path parsing rules.

Last updated: 2026-03-23r432
