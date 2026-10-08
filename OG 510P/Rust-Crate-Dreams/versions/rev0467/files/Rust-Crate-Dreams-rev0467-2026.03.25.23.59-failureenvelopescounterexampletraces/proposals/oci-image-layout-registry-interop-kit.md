---
id: P-0204
title: OCI Image Layout + Registry Interop Kit (reproducible images, diffs, redaction, conformance)
status: idea
domains: [containers, interoperability, supply-chain, packaging, tooling, testing]
last_reviewed: 2026-03-05
evidence:
  - https://specs.opencontainers.org/image-spec/image-layout/
  - https://specs.opencontainers.org/distribution-spec/?v=v1.0.0
  - https://docs.rs/oci-spec
  - https://termoshtt.github.io/ocipkg/ocipkg/index.html
---

# Problem

Rust has *pieces* for working with OCI (types, registries, tar layers), but teams repeatedly re‑implement a **coherent, reproducible, inspectable** workflow for:
- reading/writing an **OCI Image Layout** directory,
- producing *deterministic* layers and manifests,
- pushing/pulling via the **OCI Distribution** API,
- generating **minimal diffs** between images,
- creating **redacted evidence bundles** that are safe to share in CI or bug reports.

The ecosystem lacks a well‑tested “one crate you reach for” that turns OCI specs into a practical, reliable, reproducible pipeline.

# Non-goals

- Replacing mature full registries or runtimes.
- Competing with Docker/Podman UX.
- Being opinionated about SBOM/signing formats (instead: provide adapters).

# What the crate provides (for other people)

## 1) A stable *artifact model*
- `OciLayout` (filesystem) + `Ref` model (tags, digests, indexes)
- Zero-copy reads when possible, but **canonicalization** functions to produce deterministic outputs.

## 2) Deterministic build blocks
- `LayerBuilder` with canonical tar ordering, normalized mtimes/uid/gid, reproducible gzip (optional), and content hashing.
- `ManifestBuilder` / `IndexBuilder` with canonical JSON serialization.
- “Repro check” API: compute digest from bytes and compare to recorded descriptor digests.

## 3) Registry interop with conformance hooks
- Client for Distribution Spec endpoints (pull/push, blob upload, manifests, referrers when applicable).
- Pluggable auth: basic, bearer (token), and user-provided hook.
- **Conformance runner**: a small suite that exercises the spec paths against registries in CI.

## 4) Image diff & explain
- `diff(layout_a, layout_b)` producing:
  - blob-level delta,
  - manifest/index differences,
  - “why did digest change?” report (timestamps, tar order, compression, JSON canonicalization).

## 5) Evidence bundles
- `*.ocibundle.zip` capturing:
  - minimal OCI layout subset (or manifest+blobs),
  - redaction map (paths/tags scrubbed),
  - diff report and reproduction metadata (tool versions, hash seeds),
  - optional network transcript (request/response headers redacted).

# Architecture sketch

Crate layout:
- `oci-kit-core`: canonicalization, hashing, tar/layer utilities, JSON canonical forms.
- `oci-kit-layout`: read/write OCI Image Layout; efficient blob store.
- `oci-kit-registry`: Distribution Spec client; auth; retry/backoff; concurrency.
- `oci-kit-diff`: semantic diff and explain.
- `oci-kit-bundle`: bundle format + redaction + CLI helpers.

# MVP (4–8 weeks)

1. Read/write OCI Image Layout + validate digests.
2. Deterministic layer builder for common use cases (tar + gzip optional).
3. Pull/push (blob + manifest) against a reference registry in CI.
4. Minimal `ocibundle` format + “repro report”.

# De-risking plan

- Start with the layout spec + deterministic layer building (no network).
- Add registry interop behind a feature flag; test against a local registry in CI.
- Provide “escape hatches” early (custom tar writer, custom JSON ser, custom auth).

# Prior art / overlaps

- `oci-spec` provides spec types but not the end-to-end reproducible toolchain.
- `ocipkg` demonstrates OCI layout navigation, but the missing piece is **deterministic writes + diffs + evidence bundles**.

