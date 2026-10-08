---
id: P-0319
title: IIIF Image + Presentation Interop & Evidence Kit — compliance-aware manifests, image-request lockfiles, and portable library-tech bundles
status: idea
domains: [digital-libraries, iiif, image-processing, metadata, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://iiif.io/api/
  - https://iiif.io/api/image/3.0/
  - https://iiif.io/api/presentation/3.0/
  - https://iiif.io/api/image/validator/
  - https://iiif.io/api/presentation/validator/service/
  - https://crates.io/crates/iiif
  - https://crates.io/crates/i3f
---

# Problem

IIIF has become the de facto interoperability surface for image delivery and rich digital-object presentation across libraries, archives, museums, and scholarly tooling. Rust now has early IIIF substrate, but the operational pain is still in the same places:

- image-request URLs that are valid-ish but not truly compliant,
- manifests that parse but break viewers,
- drift between Image API capabilities and Presentation API assumptions,
- migration from 2.x to 3.x semantics,
- and support workflows that still rely on screenshots, copied manifests, and “works in viewer X” arguments.

The worthy crate contribution is not another monolithic DAMS or viewer. It is a **IIIF interop and evidence kit** that makes image and presentation behavior testable, diffable, and shareable.

# What it provides

- `iiif-ir` — canonical IR for Image API requests/responses, `info.json` capability declarations, Presentation manifests/collections/canvases, and annotation references.
- `iiif-profile` — lockfiles for Image API compliance level, Presentation API version, media/format assumptions, and migration expectations.
- `iiif-verify` — semantic checks for URI shape, `info.json` consistency, manifest structural correctness, and image/presentation cross-links.
- `iiif-diff` — explainable diffs: “manifest downgraded to 2.x semantics”, “service profile mismatch”, “canvas references missing image service capability”, “region/size request outside compliance profile”.
- `iiif-replay` — deterministic replay of viewer- and crawler-style request sequences.
- `cargo iiif` — emit `*.iiifbundle.zip` for collection migrations, bug reports, and interoperability labs.

# What the crate should provide other people

1. **A portable IIIF incident artifact** instead of screenshots plus raw JSON blobs.
2. **Compliance/profile lockfiles** that pin what a service or manifest claims to support.
3. **Cross-image/presentation diagnostics** grounded in IIIF concepts.
4. **Replayable request sequences** that reproduce viewer or crawler failures.
5. **A path from today’s Rust IIIF clients/servers to a conformance-first toolchain**.

# Users & user stories

- **Library platform teams**: “Show me whether this is an Image API compliance issue or a manifest modeling issue.”
- **Digital collections engineers**: “Diff our v2.x and v3.x manifests semantically before migration.”
- **Viewer authors**: “Replay a failing manifest and image-request sequence across versions.”
- **Consortia / integrators**: “Archive a passing evidence bundle for onboarding and regression tests.”

# Prior art (and why it’s insufficient)

- IIIF publishes stable API documentation plus validator services for Image and Presentation surfaces.
- Rust now has at least early client/server/model substrate (`iiif`, `i3f`).
- But there is not yet a strong Rust-native default for **compliance pinning, semantic diffs, replay, and shareable evidence bundles**.

# Design goals

1. **Image + Presentation together** — failures usually cross the boundary.
2. **Compliance-aware** — leverage the ecosystem’s explicit profile/compliance model.
3. **Migration-friendly** — v2.x → v3.x drift should be first-class.
4. **Small library-tech bundles** — fit into issue trackers, repositories, and preservation workflows.
5. **Implementation-neutral** — serve clients, servers, and validators.

# Non-goals

- Not a full viewer or DAMS.
- Not a giant image processing framework.
- Not a replacement for the official web validators.

# Architecture & API sketch

```rust
pub struct IiifReport {
    pub profile_id: String,
    pub verdicts: Vec<Verdict>,
    pub image_findings: Vec<ImageFinding>,
    pub presentation_findings: Vec<PresentationFinding>,
    pub crosslink_findings: Vec<CrossLinkFinding>,
}

pub fn verify_bundle(profile: &IiifProfile, bundle: &IiifBundle) -> IiifReport;
```

Bundle draft: `profile.toml`, `image/info.json`, `image/requests.jsonl`, `presentation/manifest.json`, `presentation/collection.json`, `verdicts.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Support redaction of collection-internal URLs, auth tokens, and unpublished metadata.
- Bound remote fetch and image-request expansion.
- Separate manifest summaries from optional fetched image bytes.
- Record exact validator/profile assumptions in every bundle.

# Maintenance & governance plan

- Pin exact IIIF API versions and compliance expectations in fixture packs.
- Publish synthetic/public fixtures for common failures: bad service blocks, broken canvas/image links, 2.x→3.x migrations, and compliance-level mismatches.
- Keep IR additive so auth/search/content-state overlays can remain optional later.

# Milestones

## 0.1
- Canonical IIIF IR
- Image/Presentation profile lockfiles
- Structural verification + bundle format

## 0.2
- Cross-link diagnostics
- Request replay
- Migration diffs

## 1.0
- Stable `*.iiifbundle.zip`
- Adapter layer for multiple Rust IIIF stacks
- CI-ready onboarding and regression workflows

# Open questions

- How much viewer-behavior simulation belongs in core?
- Should Auth/Search APIs remain future overlays rather than MVP scope?
- Can compliance-level modeling remain simple enough for human review?

# Sources

- IIIF API overview: https://iiif.io/api/
- IIIF Image API 3.0: https://iiif.io/api/image/3.0/
- IIIF Presentation API 3.0: https://iiif.io/api/presentation/3.0/
- IIIF Image API Validator: https://iiif.io/api/image/validator/
- IIIF Presentation API Validator: https://iiif.io/api/presentation/validator/service/
- `iiif` crate: https://crates.io/crates/iiif
- `i3f` crate: https://crates.io/crates/i3f
