---
id: P-0019
title: Cargo Transparency Bundle — SBOM + auditable + provenance + signatures
status: idea
domains: [cargo, supply-chain, security, devops]
last_reviewed: 2026-03-01
evidence:
  - https://docs.rs/crate/cargo-sbom/latest
  - https://crates.io/crates/cargo-cyclonedx
  - https://github.com/rust-secure-code/cargo-auditable
  - https://slsa.dev/spec/draft/build-provenance
  - https://crates.io/docs/trusted-publishing
  - https://docs.rs/sigstore/latest/sigstore/
  - https://internals.rust-lang.org/t/pre-rfc-using-sigstore-for-signing-and-verifying-crates/18115
  - https://axodotdev.github.io/cargo-dist/
needs:
  - Teams shipping Rust binaries need a one-command way to emit verifiable “what’s in this artifact?” metadata.
  - Security/ops want to verify provenance and dependency identity for binaries running in prod.
  - Existing tools cover parts, but not a coherent bundle + verification workflow.
risks:
  - Overlap with existing tools; success depends on being an integration layer with strong ergonomics.
  - Supply-chain formats (SLSA, in-toto, CycloneDX, SPDX) evolve; must version artifacts carefully.
---

# Problem

Rust has strong supply-chain building blocks, but producers and consumers still struggle to do the *end-to-end* workflow:

- **Produce**: generate SBOMs, provenance, and dependency identity for a build in CI.
- **Ship**: attach those artifacts to releases/containers.
- **Consume**: verify signatures/attestations and answer “what exactly is this binary?”

The gap is not a single missing primitive; it’s the lack of a **default bundle** + **verification toolchain** that stitches the ecosystem together.

# Users & user stories

- **App teams**: “When I tag a release, CI should emit a bundle (SBOM + provenance + dep identity) and sign it.”
- **Security**: “Given a binary in prod, I want to verify what it was built from and whether its deps have advisories.”
- **Distros / SREs**: “We need machine-readable provenance + checksums for fleet-wide verification and inventory.”

# Prior art (and why it’s insufficient)

- `cargo-sbom`, `cargo-cyclonedx`: produce SBOMs, but don’t define a standard *bundle* or signing/verifying workflow.
- `cargo-auditable`: embeds dep graph identity in binaries, but doesn’t cover SBOM/provenance/signatures.
- Sigstore crates: provide verification primitives, but remain “library-level” and can be hard to integrate.
- `cargo-dist`: unifies release engineering steps, but isn’t specifically a transparency/provenance framework.

# Design goals

- One command to produce a **portable bundle** per artifact.
- Deterministic output; stable artifact schema; strong backward-compat story.
- Works with and/or plugs into `cargo-dist`.
- Supports multiple SBOM formats (SPDX and CycloneDX) by conversion from a canonical internal model.
- Optional binary embedding (via `cargo-auditable`) when it helps post-deploy inventory.
- Verification command that is useful in CI and in production incident response.

# Non-goals

- Replacing crates.io registry trust or redesigning Cargo itself.
- Building a full vulnerability scanner (should integrate with RustSec/cargo-audit ecosystems).

# Architecture & API sketch

**Crates**
- `transparency_bundle_core` (library): canonical models + deterministic serializers.
- `cargo-transparency` (CLI): `cargo transparency bundle|verify|explain`.
- Optional feature crates:
  - `transparency_sigstore` (verify/sign via sigstore)
  - `transparency_auditable` (embed/extract dep data via cargo-auditable)
  - `transparency_sbom` (SPDX/CycloneDX emitters)

**Bundle layout (directory or tarball)**
- `manifest.toml` (schema version + list of artifacts + digests)
- `sbom/`:
  - `sbom.spdx.json`
  - `sbom.cdx.json`
- `provenance/`:
  - `build.slsa.json` (SLSA provenance predicate)
  - `in-toto.jsonl` (optional)
- `deps/`:
  - `cargo.resolved.json` (resolved dependency graph + features/targets)
  - `auditable.json` (optional copy of embedded metadata)
- `signatures/`:
  - `bundle.sig` (or Sigstore bundle)
  - `bundle.cert` (if applicable)

**CLI**
- `cargo transparency bundle --workspace --target ... --features ... --out dist/bundles/`
- `cargo transparency verify --artifact path/to/bin --bundle dist/bundles/...`
- `cargo transparency explain --bundle ...` (human-readable summary)

# Security / safety model

- No embedding of sensitive paths/secrets.
- Clear separation between “producer asserted” and “cryptographically verified”.
- Verification should check:
  - artifact digest matches manifest
  - signatures/attestations verify
  - provenance matches expected source/repo ref (when policy provided)

# Maintenance & governance plan

- Keep core dependency footprint small.
- Publish artifact schema with semantic versioning and a compatibility table.
- Add fixtures: sample workspaces (bin, cdylib, wasm) with golden bundle outputs.

# Milestones

## 0.1
- Deterministic manifest + resolved dependency graph capture (via `cargo metadata`).
- Emit SPDX and CycloneDX using existing SBOM crates where feasible.
- `bundle` command producing a directory bundle.

## 0.2
- Integrate `cargo-auditable` (embed + extract + compare).
- Add `verify` (digest + basic schema checks).

## 0.3
- Add Sigstore verification path (verify-only first), policy flags (expected repo, expected ref).

## 1.0
- Stable bundle schema v1, conversion tool, cargo-dist integration examples.

# Open questions

- Should the canonical internal model be “Cargo SBOM” compatible with the pre-RFC proposal?
- How should feature/target resolution be represented for multi-target releases?
- How far should we go in standardizing “policy” vs leaving it to org tooling?

# Sources

- https://docs.rs/crate/cargo-sbom/latest
- https://crates.io/crates/cargo-cyclonedx
- https://github.com/rust-secure-code/cargo-auditable
- https://slsa.dev/spec/draft/build-provenance
- https://crates.io/docs/trusted-publishing
- https://docs.rs/sigstore/latest/sigstore/
- https://internals.rust-lang.org/t/pre-rfc-using-sigstore-for-signing-and-verifying-crates/18115
- https://axodotdev.github.io/cargo-dist/
