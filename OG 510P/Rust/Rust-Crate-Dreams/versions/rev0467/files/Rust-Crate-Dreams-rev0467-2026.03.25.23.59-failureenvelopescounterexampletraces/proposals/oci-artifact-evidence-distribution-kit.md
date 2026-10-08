---
id: P-0131
title: OCI Artifact Evidence & Distribution Kit (cargo-native ORAS for bundles + referrer graphs)
status: idea
domains: [supply-chain, devtools, ci, oci, artifact-management, cargo]
last_reviewed: 2026-03-05
evidence:
  - https://oras.land/
  - https://oras.land/docs/client_libraries/rust/
  - https://crates.io/crates/oci-client
  - https://github.com/oras-project/rust-oci-client
  - https://learn.microsoft.com/en-us/azure/container-registry/container-registry-manage-artifact
---

# Problem

Rust has excellent crates for **building artifacts** (binaries, bundles, reports), but the ecosystem still lacks a widely adopted, ergonomic, *content-addressed distribution workflow* for arbitrary build artifacts that:

- works with existing infra (OCI registries),
- supports rich media types + “referrer” graphs (SBOMs, attestations, reports),
- and can be used in CI as a stable *artifact contract*.

Teams already treat OCI registries as generic artifact stores via ORAS, but Rust-first “cargo-native” UX is fragmented.

# What it should provide other people

## 1) Cargo-native workflows

A `cargo oci-artifact` subcommand (or `cargo-oci`) that supports:

- `cargo oci push <ref> <path>`: push an artifact (zip/tar/wasm/etc) with a declared media type.
- `cargo oci pull <ref> --out <dir>`: fetch + verify.
- `cargo oci attach <ref> --sbom <file> --attestation <file> ...`: attach supply-chain artifacts using the registry’s referrer model.
- `cargo oci ls <ref>`: show attached graph (SBOMs, scans, provenance, signatures).
- `cargo oci doctor`: auth + registry feature probing + policy checks.

Under the hood: build on `oci-client` (ORAS rust-oci-client) and optionally interop with ORAS concepts.

## 2) Standard “evidence bundle” conventions

Define a small set of conventions (not a new standard) so tools can interoperate:

- media type registry (strings) for common Rust artifacts (test bundles, crash bundles, policy reports, etc.)
- “attachment slots” (SBOM, provenance, scan report, signatures) with predictable names
- deterministic manifest JSON for local reproducibility (sha256, source provenance, tool versions)

## 3) Policy and verification hooks

- optional Sigstore verification (fulcio/rekor) and/or key-based verification
- policy profiles (dev vs CI vs release)
- stable JSON outputs: `oci-report.json` suitable for gating

# MVP scope

- pull/push blobs + OCI manifest
- media type + annotations
- `doctor` that checks auth, registry API capabilities, and warns on nonconformant registries
- minimal attachment support: attach SBOM and provenance as separate OCI artifacts

# v1 scope

- referrer graph UI (`cargo oci graph`)
- concurrency + resumable uploads/downloads
- pluggable auth providers (ECR/GHCR/ACR) without leaking registry-specific logic into core
- hermetic “artifact capture” mode: write a local OCI layout directory (for airgapped transfer)

# Conformance & testing

- a conformance corpus: known OCI layouts + expected behaviors
- golden tests against local registry (e.g., distribution/distribution) in CI
- fuzzing for manifest parsing and annotation handling

# Risks and constraints

- Registry capability variance: make `doctor` a first-class feature.
- Avoid reinventing ORAS CLI—focus on Rust library + cargo UX + artifact conventions.

