# Design: Release Pipeline Kit (`cargo ship`, `release-pack/v0`)

## Goal
Define a portable release contract for Rust projects so that **crate publishing, binary distribution, installers, signatures, SBOMs, provenance, and attached evidence packs** can compose into one reviewable release boundary.

This should **not** replace `release-plz`, `cargo-release`, `cargo-dist`, `cargo-packager`, or `cargo-binstall`. It should give them a better shared surface.

## References (signals)
- Publishing on crates.io is permanent, which raises the bar for release evidence beyond “the workflow passed”.
  https://doc.rust-lang.org/cargo/reference/publishing.html
- `cargo publish` starts from a concrete `.crate` package boundary and upload flow.
  https://doc.rust-lang.org/cargo/commands/cargo-publish.html
- crates.io now supports GitLab CI/CD Trusted Publishing, TP-only mode, and blocking risky GitHub Action triggers.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- Cargo is exploring explicit final-artifact uplift from build scripts, which sharpens the need for a real artifact/release boundary rather than ad hoc target-dir scraping.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- Cargo’s unstable `sbom` support already emits SBOM precursor files beside uplifted compiled artifacts.
  https://doc.rust-lang.org/beta/cargo/reference/unstable.html
- `release-plz` automates changelog generation, release PRs, registry publishing, and release creation, with semver-check inputs.
  https://github.com/release-plz/release-plz
- `cargo-release` still fills the “extend `cargo publish` with validation, tagging, version management, and push semantics” niche.
  https://crates.io/crates/cargo-release
- `cargo-dist` already emits a machine-readable release manifest with a published schema crate.
  https://docs.rs/cargo-dist-schema/latest/cargo_dist_schema/
- `cargo-dist` also supports SBOM output and OmniBOR artifact IDs.
  https://github.com/axodotdev/cargo-dist/blob/main/CHANGELOG.md
- `cargo-binstall` already consumes prebuilt binary metadata and supports signature verification, but it requires explicit metadata rather than magical auto-discovery.
  https://github.com/cargo-bins/cargo-binstall/blob/main/SIGNING.md
- The infrastructure side has stated that crates.io package format decisions are not necessarily final for all Rust use cases, especially around precompiled material.
  https://blog.rust-lang.org/2025/11/25/interview-with-jan-david-nose/

## Stack boundaries
This kit should be treated as the orchestration layer inside a shared **Release Truth Stack**:
- [`design/publish-set-kit.md`](./publish-set-kit.md) owns source-package publication subject, packaged payload, publish-time checks/waivers, authority/registry-path facts, and upload/index receipts.
- [`design/release-pipeline-kit.md`](./release-pipeline-kit.md) owns the broader release subject, release intent, release manifest, release policy, and `release-pack/v0`.
- [`design/signed-binaries-kit.md`](./signed-binaries-kit.md) owns `binpack/v0` and `binverify-report/v0` for installable binary verification.
- [`design/repro-build-kit.md`](./repro-build-kit.md) owns independent rebuild evidence and diff reasons.

Design rule: **the release boundary is broader than source publication, signatures, or reproducibility, but it must not swallow them**.

## Boundary relative to Distribution Contract Stack
The **Release Truth Stack** ends at producer-side publication and release description.
It owns what the producer published, where it was hosted, and what artifacts/evidence belong to that release.

The downstream **Distribution Contract Stack** begins when a consumer actually chooses among channels, hosts, mirrors, installers, source-build fallback, and verification options.
That stack should import `release-pack/v0`; it should **not** force Release Pipeline Kit to pretend that a published artifact was necessarily the artifact or path a consumer actually installed.

## Core components

### 1) `release-subject/v0`
Canonical identity for the release being described:
- workspace / package selection
- version(s)
- git commit / tag / source snapshot
- registry target(s)
- CI run / issuer identity when available
- comparison / previous-release pointer when relevant

Design rule: release facts need a stable subject before they can be attached, mirrored, or verified.

### 2) `release-intent/v0`
A design-time declaration of what this project intends to ship:
- publish targets: crates.io / alt registry / GitHub Release / static hosting / mirrors / package managers
- artifact kinds: `.crate`, archives, installers, app bundles
- target triples
- signing / attestation / rebuild strategy
- required attached evidence packs
- update channels / rollout classes
- optional “library-only” or “source-only” modes

### 3) `release-manifest/v0`
The produced release graph:
- source crate publish records
- git tag / commit
- CI run identifiers
- artifact list with checksums, sizes, target triples, and URLs or relative paths
- signature references
- attestation references
- SBOM references
- installer / updater / mirror metadata
- raw imported manifests (for example `dist-manifest.json`) when available

Design rule: this should **ingest existing machine-readable manifests** instead of competing with them blindly.

### 4) `release-policy/v0`
A project or org policy artifact:
- required signatures
- required attestations or CI issuers
- required evidence packs (`api`, `policy`, `sbom`, `repro`, `safety`, etc.)
- allowed artifact kinds and hosting classes
- fail / warn / informational / inconclusive semantics

Design rule: policy is about **release readiness**, not merely build success.

### 5) `release-pack/v0`
Bundle format:
- `release-subject/v0`
- `release-intent/v0`
- `release-manifest/v0`
- optional `release-policy/v0`
- pointers or attachments for domain-specific packs:
  - `binpack/v0`
  - `binverify-report/v0`
  - `repro-pack/v0`
  - `api-pack/v0`
  - `policy-pack/v0`
  - `sbom-evidence-pack/v0`
  - `safety-pack/v0`
- optional raw inputs (`dist-manifest.json`, attestation bundles, updater metadata, SBOM precursor files)
- verification summary with explicit incompleteness markers

### 6) `cargo ship`
Reference UX:
- `cargo ship plan`
- `cargo ship collect`
- `cargo ship verify`
- `cargo ship gate`
- `cargo ship pack`
- `cargo ship diff --against <pack|tag|path>`

`cargo ship` should start as an **adapter/orchestrator and validator**, not as a giant replacement release tool.

## What the kit should provide to others
- **Library maintainers:** one release boundary that ties crate publishing, semver/API evidence, and policy together.
- **CLI and app teams:** a portable description of archives, installers, mirrors, updater channels, and signatures.
- **Security/compliance teams:** one place to require signed artifacts, provenance, SBOMs, rebuild evidence, and explicit waivers.
- **Tool authors:** stable attachment points so `release-plz`, `cargo-dist`, `cargo-packager`, `cargo-release`, and `cargo-binstall` stop inventing incompatible release vocabularies.

## Integration points
- **Signed Binaries Kit:** attach `binpack/v0` and `binverify-report/v0`; do not re-specify signature semantics inside the core release schema.
- **Repro Build Kit:** attach `repro-pack/v0`; do not treat provenance or signatures as a proxy for rebuild equivalence.
- **SBOM Evidence Kit:** attach SBOM or precursor-derived evidence without flattening it into one yes/no release bit.
- **Public API / Coverage / Perf / Policy / Safety:** optional or required attachments for org policy.
- **Trust Signals / Lifecycle / Incident / Stewardship:** consume release packs for approval, audit, incident response, and support routing.

## Hard problems (explicitly scoped)
1. **Not every project ships binaries**
   - crate-only release packs must stay first-class and small.
2. **Hosted pages are not enough**
   - GitHub Releases, package-manager pages, or registries may mirror the release, but should not be the only reconstructible source of truth.
3. **Release artifacts are not one thing**
   - `.crate` packages, installer bundles, archives, app bundles, and updater feeds may all belong to one release while having different verification rules.
4. **Do not overclaim reproducibility**
   - attach `repro-pack/v0` when available; do not silently equate provenance, signatures, and rebuild verification.
5. **Avoid umbrella bloat**
   - the core contract should attach domain-specific packs rather than absorbing them.

## Evaluation plan
Use the ranked rollout in [`design/release-pipeline-pilot-program.md`](./release-pipeline-pilot-program.md):
1. crate-only publish lane,
2. CLI binary lane,
3. signed-install lane,
4. independent rebuild lane,
5. multi-channel / installer / mirror lane.

Success bar:
- the same release can be described without bespoke CI parsing,
- offline verification is practical,
- policy can explain why a release is blocked,
- and existing tools can emit/consume the format incrementally.
