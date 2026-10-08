# Epic Proposal: SBOM Evidence Kit (`cargo inventory`)

## One-sentence pitch
Turn Rust dependency inventory into a first-class evidence artifact: capture Cargo-native build facts, preserve scope and artifact linkage, project into standards like CycloneDX/SPDX with explicit lossiness notes, and attach the result as one portable pack.

## Deliverables
- `cargo-inventory` reference implementation
- Schemas:
  - `inventory-subject/v0`
  - `inventory-capture-report/v0`
  - `inventory-graph/v0`
  - `artifact-inventory-report/v0`
  - `inventory-projection-report/v0`
  - `inventory-diff-report/v0`
  - `inventory-pack/v0`
- Commands / adapters:
  - Cargo SBOM precursor ingestion
  - Cargo metadata / lockfile fallback lane
  - `cargo-auditable` / binary-recovery ingestion
  - CycloneDX / SPDX exporters and crosswalks
- Docs:
  - maintainer workflow for build/release/inventory capture
  - scope-model reference (runtime/build/proc-macro/dev/host-target)
  - exporter caveat and lossiness reference
  - policy / incident / release integration patterns

## Why now (signals)
- Rust’s 2026 roadmap explicitly includes **stabilizing Cargo SBOM precursor** support and names **SBOM generation** as part of the flagship supply-chain theme.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo’s unstable docs already expose a concrete Rust-native precursor format with dependency kind, features, target, compiler identity, and per-artifact output placement.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo’s tracking issue says the remaining work includes demonstrating end-to-end generation of an industry-standard SBOM from this data source and explicitly scopes non-Rust dependency tracking out of the precursor feature.
  https://github.com/rust-lang/cargo/issues/16565
- RFC 3553 explicitly positions Cargo’s output as a Cargo-specific intermediate that external tooling can transform into SPDX or CycloneDX.
  https://github.com/rust-lang/rfcs/pull/3553
- `cargo-cyclonedx` proves demand for standardized SBOM exports, but its issue tracker also shows current data sources can misclassify build-only dependencies as runtime dependencies under resolver v2.
  https://github.com/CycloneDX/cyclonedx-rust-cargo/blob/main/README.md
  https://github.com/CycloneDX/cyclonedx-rust-cargo/issues/760
- `cargo-auditable` proves that binary-embedded dependency evidence is practical and reproducible-build-friendly, while also making clear that SBOMs are not themselves trust or incident-impact verdicts.
  https://github.com/rust-secure-code/cargo-auditable

## Non-goals
- Claiming complete system inventory for every native or foreign dependency in v0
- Replacing CycloneDX, SPDX, or container-image standards
- Turning inventory into a trust score
- Pretending workspace-level dependency graphs automatically prove shipped-artifact content
- Using SBOMs as a substitute for advisories, trust review, or reproducible-build verification

## Strategic value
The first design rule is now explicit: read this epic together with [`design/sbom-evidence-lane-map.md`](../design/sbom-evidence-lane-map.md).
A worthy implementation must keep **Cargo-native precursor capture, source-project standards export, embedded binary recovery, release-attached standards documents, scanner/import views, and downstream consumer handoffs** distinct instead of narrating one universal SBOM lane.

This kit has high leverage because it connects:
- Cargo’s emerging upstream SBOM support
- release engineering and artifact publication
- trust / policy / incident tooling that needs normalized inventory input
- binary/container scanners and downstream packagers
- supply-chain review that must distinguish runtime, build, and proc-macro exposure honestly

## Milestones
1. **v0**
   - ingest Cargo SBOM precursor files
   - emit `inventory-pack/v0`
   - export CycloneDX / SPDX with explicit projection reports
   - support structured diffs across releases / baselines
2. **v0.2**
   - binary-recovered inventory lane via `cargo-auditable` or similar adapters
   - artifact-link cross-checks and mismatch reporting
   - workspace aggregation and filter presets for runtime/build/proc-macro review
3. **v1**
   - deeper Cargo integration
   - richer native/foreign supplement lanes
   - stronger container/image handoff and attachment workflows

## What success looks like
- A maintainer can attach one pack that answers “what did we inventory, how did we capture it, what ended up in which artifact, and what changed?”
- A release or CI system can consume the same pack for CycloneDX/SPDX export, policy checks, and incident preparation without re-scraping bespoke tool output.
- Downstreams can distinguish observed Cargo build truth, binary-recovered truth, and approximated metadata truth instead of treating them as interchangeable.


## Stack role
This kit should now be read as the inventory-truth keystone inside the broader [`design/inventory-evidence-stack.md`](../design/inventory-evidence-stack.md).
It owns capture provenance, scope-aware graphs, artifact linkage, export-lossiness reports, and inventory packs; Package Admission, Release Truth, Distribution Contract, Trust, Policy, and Incident workflows should import those artifacts rather than replace them.
