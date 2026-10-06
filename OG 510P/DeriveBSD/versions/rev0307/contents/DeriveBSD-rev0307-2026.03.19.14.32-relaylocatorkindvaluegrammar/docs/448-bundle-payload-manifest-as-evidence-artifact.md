# Bundle payload manifest as an evidence artifact

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** reproducibility, supply-chain, operability
**Patterns:** Capsule, Bundles, Plan→Apply→Receipt

When DeriveBSD exports an incident/support bundle, we want two truths to be simultaneously easy:

1) **Human truth:** “what did we share?”
2) **Machine truth:** a deterministic, replayable binding between *plan → bytes → members*.

`bundle.build.receipt` binds `bundle.plan` to the produced payload digest, but that still leaves a practical forensic question:

> “What *members* were in the payload, and what are their digests?”

This doc introduces a minimal, typed answer: `bundle.payload.manifest`.

## Artifact: `bundle.payload.manifest`

`bundle.payload.manifest` is a deterministic, stable-ordered member listing for an exported bundle payload.

It records:
- the `bundle.plan` digest used for selection + transforms
- the payload digest + format (tar.zst/zip)
- optional transform bindings (redaction transform / export policy)
- a stable-ordered list of payload members with per-member digests

See:
- Schema: `spec/bundle.payload.manifest.schema.json`
- Example: `spec/examples/bundle.payload.manifest.json`

## Why this matters (pillars)

- **Operability / forensics UX:** support and incident workflows can answer “what exactly was in the bundle?” without unpacking bytes or trusting ad-hoc scripts.
- **Supply-chain / provenance:** exported evidence becomes self-describing; receipts can bind “bundle payload digest” to a verifiable member list.
- **Reproducibility:** the manifest is deterministic-by-default and becomes a stable join key for re-exports/replays.

## Wiring (how it composes)

### Plan → Apply → Receipt

- `bundle.plan` declares selection + transforms.
- `bundle.payload.manifest` records the concrete payload member set.
- `bundle.build.receipt` binds plan digest + payload digest and (optionally) the payload manifest digest.

### Capsule / Bundles

The payload manifest is *metadata evidence* that belongs inside the support-bundle story:
- `incident.bundle` can reference the build receipt (preferred)
- the build receipt can reference `bundle.payload.manifest`

This keeps exports replayable without forcing a specific payload format.

## Determinism rules (stable diff surface)

To keep the manifest a stable review surface:
- member paths must be normalized (forward slashes)
- ordering must be deterministic (lexicographic by `path`)
- per-member digests must be over the exact member bytes as written
- optional `category` and `source` fields exist for UX and traceability, but must not require non-deterministic discovery

## Tier / profile placement

- **Tier B (Base):** emitting a payload manifest is “boring but high leverage” for operability.
- **Profiles A–D:** no shape is forced to export bundles, but when exports happen the manifest keeps the evidence UX deterministic.

## References

This is conceptually similar to content-addressed member manifests used by OCI and other artifact formats (digest-first indexing).

See curated pointers:
- OCI image spec (digest model for manifest/index objects): `docs/32-curated-references.md`

Last updated: 2026-02-28r169
