# Mirror kit manifest as an evidence artifact

**Tier:** C (Optional lane)
**Profiles:** A, B, C, D
**Pillars:** supply-chain, operability
**Patterns:** Plan→Receipt, Bundles

Mirror kits are deliberately **boring**: a removable carrier with content-addressed bytes that become trusted only after verification.
To keep offline workflows explainable, resumable, and supportable, a kit should be **self-describing**.

This doc introduces a small, typed artifact that makes mirror kits inspectable without bespoke scripts.

## Artifact

- Kind: `mirror.kit.manifest`
- Schema: `spec/mirror.kit.manifest.schema.json`
- Example: `spec/examples/mirror.kit.manifest.json`

The manifest is **not** a trust root.
It is a structured index of what the kit *claims* to carry so that verification and operator UX can be deterministic and repeatable.

## What it enables

### Deterministic “what’s on this kit?” UX

`derive mirror verify <path>` can print:
- which channels are present,
- which snapshot ids are present (when known),
- how many objects/deltas/sources are included,
- which policy/provenance bindings the kit claims.

This is especially useful for air-gapped environments where operators must decide whether to import/promote without internet lookups.

### Receipt binding (evidence spine)

When importing a kit into quarantine:
- the importer SHOULD record the digest of the kit’s `mirror.kit.manifest` in the import receipt (`mirror.import.receipt.source.kit_manifest_digest`).

That digest becomes a stable join key for:
- support bundles,
- incident timelines,
- “what did we import when?” queries.

### Resume/replay ergonomics

A manifest lets an importer:
- resume partially-imported kits idempotently,
- detect missing objects early,
- avoid re-walking large directory trees when a kit is re-inserted.

## Where it fits

This artifact is part of the mirror-kit lane:
- `docs/273-airgap-mirror-kits-and-sneakernet-updates.md`

It also fits the evidence posture described in:
- `docs/229-evidence-spine-overview.md`

## Design constraints

- Deterministic ordering (stable diff surfaces): arrays in the manifest SHOULD be emitted in a stable order.
- Content-addressed identity: objects are referenced by digest; carrier paths are hints only.
- No forks: profiles can require/forbid kit manifests by policy, but the base lane remains optional.

Last updated: 2026-02-28r168
