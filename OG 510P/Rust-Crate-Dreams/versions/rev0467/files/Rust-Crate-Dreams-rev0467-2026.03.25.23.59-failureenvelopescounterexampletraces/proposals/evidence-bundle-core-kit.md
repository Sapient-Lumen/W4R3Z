---
id: P-0256
title: Evidence Bundle Core Kit — deterministic, signed, redactable, diffable bundle substrate for Rust tooling
status: idea
domains: [tooling, reproducibility, forensics, conformance, security, interoperability]
last_reviewed: 2026-03-21
evidence:
  - https://in-toto.io/docs/specs/
  - https://github.com/in-toto/attestation/blob/main/spec/v1/envelope.md
  - https://docs.sigstore.dev/about/bundle/
  - https://github.com/sigstore/sigstore-go/blob/main/docs/signing.md
  - https://datatracker.ietf.org/doc/draft-ietf-scitt-architecture/
  - https://oras.land/docs/concepts/reftypes/
  - https://github.com/opencontainers/distribution-spec/blob/main/spec.md
  - https://www.rfc-editor.org/rfc/rfc8785
  - https://www.rfc-editor.org/rfc/rfc9052.html
  - https://docs.rs/sigstore/latest/sigstore/
  - https://docs.rs/coset/latest/coset/
  - https://docs.rs/serde_jcs/latest/serde_jcs/
  - https://docs.rs/zip/latest/zip/
---

# P-0256 — Evidence Bundle Core Kit

**Codename:** `evidencekit`

**Primary surface:** one small crate workspace plus `cargo evidence`.

**Canonical artifact:** `*.evidencebundle.zip`

## Problem

This archive now contains a large family of proposals that want to emit portable artifacts:

- conformance failure bundles,
- interoperability repro bundles,
- verification campaign bundles,
- safety review packs,
- and Cargo/build/debugging receipts.

That pattern is healthy.
What is unhealthy is letting every domain invent its own private answer to the same boring questions:

- how is the bundle packed deterministically,
- what gets hashed and where,
- how do redaction policies work,
- how are signatures attached,
- how do two bundles diff cleanly,
- what metadata is core versus domain-specific,
- and how does a verifier explain failure instead of just returning `invalid`?

Rust does not mainly lack the idea of an evidence bundle anymore.
It lacks a **boring shared substrate** for evidence bundles.

## Main judgment

A worthy crate contribution here would not be “one more attestation format”, “one more signed zip helper”, or “a magical publication layer that silently handles registries and transparency logs”.

It would be a compact Rust-first substrate that lets other crates say:

> “This tool emits an `Xbundle.zip`, but the hard parts — deterministic packing, entry lineage, share-safe export, attestation import, publication routing, semantic diffing, and explainable verification — come from one common core.”

The sharper `0.1` shape is therefore a receiver-facing contract around five review objects:

1. **container basis** — exactly why the bundle claims deterministic packing;
2. **entry lineage** — whether each entry is raw, projected, imported, generated, or redacted;
3. **attestation lane** — which DSSE / COSE / Sigstore / unsigned lane is actually in play;
4. **publication route** — whether the bundle stays local, is attached through OCI subject/referrers, is mirrored elsewhere, or is prepared for SCITT-style publication later;
5. **share-safety posture** — whether the pack is private, redacted-shareable, encrypted, or still manual-review-only.

That makes the whole archive smaller, sharper, and more interoperable.

## Why now

The ecosystem pressure is stronger now than when this archive started:

- the in-toto Attestation Framework now explicitly distinguishes **predicate, statement, envelope, and bundle** layers,
- Sigstore now has a documented **bundle format** for carrying everything required to verify a signature,
- SCITT is clarifying the external transparency/publication layer,
- and the Rust ecosystem already has usable substrate for ZIP packaging, COSE, Sigstore verification, and JSON canonicalization.

That means the missing crate is increasingly **above** those pieces, not below them.

## What the crate should provide other people

### 1. A core bundle contract
A stable container contract that separates:

- **bundle container** semantics,
- **core manifest** semantics,
- **domain profile** semantics,
- **embedded attestation/signature lanes**, and
- optional **publication / transparency / review** layers.

The crate should make it obvious which facts are universal and which belong to a profile like `conformbundle@1`, `verifybundle@1`, or `reprobuildbundle@1`.

### 2. Deterministic packing rules
The core must provide one boring answer to reproducibility questions:

- stable entry ordering,
- normalized timestamps,
- normalized permissions and compression settings,
- stable path rules,
- hash algorithm policy,
- and a manifest that can be reproduced byte-for-byte from the same logical inputs.

### 3. Artifact references and projections
Many tools need both raw artifacts and normalized views of those artifacts.
The crate should support:

- raw file entries,
- structured “projection” entries (decoded traces, normalized JSON/CBOR, summaries),
- subject/artifact references by digest,
- and cross-links between raw evidence and derived reports.

That keeps the bundle useful for both machines and humans.

### 4. Redaction as a first-class policy surface
Redaction must not be an afterthought.
The crate should provide:

- a redaction policy schema,
- path and field selectors,
- common secret/PII presets,
- a redaction receipt recording what changed,
- and a way to preserve stable digests or placeholders when content is removed.

### 5. Signing and verification lanes
The crate should be agnostic but opinionated.
A good default stack would be:

- **DSSE-style envelopes** for signed statements,
- optional **COSE-backed** lanes for compact binary profiles,
- optional **Sigstore bundle imports/attachments** where an ecosystem already uses Sigstore material,
- and explicit support for **unsigned local bundles** where signatures are not yet part of the workflow.

Verification must be explainable: policy mismatch, missing digest, signature failure, unsupported profile, redaction mismatch, and unknown external trust roots should be different verdicts.

### 6. Semantic diffing
Bundle diffs should not be raw zip diffs.
The crate should offer:

- manifest-level semantic diffing,
- artifact add/remove/change classification,
- policy changes,
- signature / attestation changes,
- and optional profile-specific diff hooks.

### 7. A small CLI that other crates can lean on
The MVP CLI should support:

- `cargo evidence pack`
- `cargo evidence verify`
- `cargo evidence explain`
- `cargo evidence diff`
- `cargo evidence redact`
- `cargo evidence inspect`

## Persona / who it’s for

- maintainers building bundle-first tooling
- teams shipping support artifacts across org boundaries
- conformance/interop tool authors who need shared artifact rules
- security/reliability engineers who need explainable verification
- higher-layer crates in this archive that should not each reinvent packaging and signing

## Users & user stories

- **Conformance tool author:** “I want to define the suite and reports, not reinvent deterministic zip packing and signing.”
- **Maintainer:** “Give me one diffable bundle I can attach to an issue without leaking secrets.”
- **Security reviewer:** “Tell me exactly why verification failed instead of forcing me to reverse-engineer bundle internals.”
- **Higher-assurance team:** “Let us reuse the same bundle substrate from build evidence through verification campaigns and assurance packs.”

## Prior art scan (and why it’s insufficient)

### in-toto / DSSE
The in-toto Attestation Framework already gives the ecosystem an important layering story:

- a **statement/predicate** model,
- a **DSSE envelope** layer,
- and a **bundle** layer for grouping attestations.

That is valuable substrate, but it does not by itself answer the full Rust-tooling problem:

- deterministic local packing of mixed artifacts,
- redacted support bundles,
- profile-specific semantic diffs,
- raw + normalized artifact co-packaging,
- and human-oriented review material.

### Sigstore bundles
Sigstore bundles are an important example of “everything required to verify a signature on an artifact”.
That is excellent for signature-verification material.
But many Rust support and repro workflows need to carry more than a signature bundle:

- raw failing inputs,
- normalized projections,
- redaction receipts,
- local machine environment notes,
- and domain reports that are not themselves signatures.

So the core crate should be able to **carry or reference** Sigstore material, not pretend Sigstore already solves the whole receiver-facing support artifact.

### SCITT / transparency systems
SCITT sharpens the external publication and transparency side.
That matters for supply-chain and inter-org evidence flows.
But a large fraction of Rust bundle-first workflows are still local or semi-private.
The missing crate here is not a transparency service; it is the **portable local bundle substrate** that can optionally publish outward later.

### Current Rust substrate
Rust already has meaningful building blocks:

- `zip` for reading/writing ZIP archives,
- `coset` for COSE types,
- `sigstore` for Sigstore capabilities,
- and `serde_jcs` for RFC 8785 JSON canonicalization.

That is exactly why the missing value now looks like a **coordination artifact crate** rather than a missing crypto primitive.

## Design goals

1. **Small core, many profiles** — keep the universal layer compact.
2. **Deterministic by default** — reproducibility should be normal, not heroic.
3. **Redaction-first** — safe sharing is a core feature.
4. **Explainable trust** — verification must say *why* something passed or failed.
5. **Human + machine friendly** — raw evidence, structured projections, and review summaries must coexist.
6. **Profile-extensible** — conformance, verification, build evidence, and assurance packs should all fit.
7. **Publication-optional** — local/private bundles should still be first-class.

## Proposed architecture

```text
evidencekit-core/      # bundle model, manifest types, profile registry
evidencekit-pack/      # deterministic zip writer/reader, path and timestamp normalization
evidencekit-redact/    # redaction policies, receipts, preset profiles
evidencekit-sign/      # DSSE helpers, optional COSE and sigstore integration
evidencekit-diff/      # semantic manifest/artifact diffing + profile hooks
evidencekit-cli/       # cargo evidence subcommands
```

### Core types

- `BundleProfileId`
- `BundleManifest`
- `SubjectRef`
- `BundleEntryRef`
- `ProjectionRef`
- `RedactionPolicy`
- `RedactionReceipt`
- `VerificationPolicy`
- `VerificationReport`
- `BundleDiff`
- `AttestationLane`

## 0.1 receiver-facing contract

The 0.1 bundle should be able to hand another person a compact, intelligible pack with these stable lanes:

```text
bundle.toml                               # core profile + version + hash/compression policy
manifest.json                             # canonical entry index, digests, kinds, relations
profiles/<id>.json                        # profile contract or imported profile declaration
subjects/subjects.json                    # bundle subjects and top-level digests
artifacts/...                             # raw files and byte payloads
projections/...                           # normalized decoded views and summaries
policies/redaction.json                   # redaction policy used for export
reports/container-basis.receipt.json      # why deterministic-pack claims are valid
reports/entry-lineage.report.json         # raw vs projection vs generated vs imported vs redacted truth
reports/share-safety.receipt.json         # who can safely receive this bundle and under what caveats
reports/redaction-receipt.json            # what changed during redaction
reports/verification-report.json          # explainable verification result
reports/diff-report.json                  # optional semantic diff against another bundle
reports/attestation-lane.receipt.json     # which attestation lane is present and how it was imported
reports/publication-route.receipt.json    # local-only vs OCI vs transparency/publication path
attestations/...                          # DSSE envelopes, COSE objects, sigstore material, or refs
review/README.md                          # generated summary for humans
```

This is enough to make a handoff useful without forcing every downstream profile to invent its own packing grammar.
It also keeps transport, attestation, and shareability from being silently laundered into the same success bit.

## Profile and transport boundaries

The proposal should now say these boundaries explicitly:

### The core *does* own
- deterministic container rules
- stable manifest vocabulary
- bundle entry kinds and subject references
- redaction receipts
- explainable verification reports
- semantic diff surface

### The core *does not* own
- the meaning of every domain-specific report
- a single universal attestation schema
- transparency-log operation
- key management or remote trust-root distribution
- registry / OCI / SCITT publication as a mandatory workflow

### The core should support
- embedding or referencing **in-toto DSSE envelopes**,
- embedding or referencing **Sigstore bundles**,
- optional **COSE** lanes for compact profiles,
- and domain profiles that import those materials without being forced to re-specify them.

## MVP surface

### 0.1
- deterministic zip writer/reader
- stable bundle manifest model
- profile declaration model
- SHA-256-based subject/artifact references
- `container-basis`, `entry-lineage`, `attestation-lane`, `publication-route`, and `share-safety` receipts
- redaction policy schema + one conservative preset
- DSSE sign/verify helpers plus imported Sigstore-bundle handling
- `pack`, `verify`, `explain`, `inspect`, `classify-share-safety`, and `classify-publication-route`
- fixture bundles and JSON schemas that another language can read

### 0.2
- semantic diffing
- projection support
- profile registry API
- optional JCS helper for JSON-based profile reports
- optional Sigstore-bundle attachment/import helpers

### 0.3
- optional COSE-backed profile lane
- stronger redaction placeholders and provenance linking
- profile-specific validators generated from profile declarations
- interoperability examples in another language

## Adoption plan

1. Land the core bundle contract first.
2. Pilot it underneath 2–3 existing bundle-heavy proposals in this archive.
3. Freeze the minimal manifest and profile declaration before adding many adapters.
4. Publish tiny examples and golden bundles that other languages can read.
5. Prove that one bundle can be useful in three very different receiver contexts: support, conformance, and verification review.

## Path to boring stability

- Freeze deterministic packing and path rules early.
- Keep the mandatory manifest tiny.
- Make profile hooks explicit rather than magical.
- Ship readers and validators before optimizing for fancy authoring APIs.
- Treat explainable verification as part of the stable product, not a debug-only feature.
- Keep publication/transparency adapters optional and external-facing.

## Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 5/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 28/30**

## Minimum lovable MVP

A crate workspace that can deterministically pack a bundle, emit container-basis and entry-lineage receipts, classify share-safety posture, attach or reference DSSE-backed / Sigstore-backed attestations without reinterpreting them, optionally describe OCI/SCITT publication routes, verify the bundle with an explainable report, and diff two bundles semantically.

## De-risk plan

1. Pilot the core on three very different bundle families: one build-evidence bundle, one conformance bundle, and one verification bundle.
2. Keep signatures optional in local workflows, mandatory only where the profile says so.
3. Validate that a non-Rust reader can parse core manifests and reports.
4. Fuzz redaction and path-normalization logic aggressively.
5. Test that embedded Sigstore or DSSE materials can round-trip without the core pretending to reinterpret their semantics.

## Non-goals

- Not a universal provenance or attestation standard.
- Not a remote transparency log service.
- Not a secret manager or key-management platform.
- Not a domain-specific schema replacement for every protocol/tool.
- Not a mandatory online verification workflow.
- Not an excuse for every profile to ignore stable core rules.

## Open questions

- Should the canonical machine manifest be JSON-only for 0.1, or should a CBOR mirror also ship immediately?
- Which pieces should be required in every bundle versus only in signed/exportable profiles?
- How much of signature policy should be core versus adapter-specific?
- When should Sigstore material be embedded versus referenced?
- Which redaction placeholders preserve the most useful diffability without leaking too much?
- Should OCI publication receipts capture only `subject`/referrer linkage, or also retention and repository-scope caveats?
- How much entry-lineage truth can be inferred automatically versus declared by profile adapters?

## Sources

- https://in-toto.io/docs/specs/
- https://github.com/in-toto/attestation/blob/main/spec/v1/envelope.md
- https://docs.sigstore.dev/about/bundle/
- https://datatracker.ietf.org/doc/draft-ietf-scitt-architecture/
- https://www.rfc-editor.org/rfc/rfc8785
- https://www.rfc-editor.org/rfc/rfc9052.html
- https://docs.rs/sigstore/latest/sigstore/
- https://docs.rs/coset/latest/coset/
- https://docs.rs/serde_jcs/latest/serde_jcs/
- https://docs.rs/zip/latest/zip/
