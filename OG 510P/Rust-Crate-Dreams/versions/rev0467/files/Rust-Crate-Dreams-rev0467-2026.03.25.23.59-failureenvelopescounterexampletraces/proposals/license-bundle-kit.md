---
id: P-0014
title: License Bundle Kit — deterministic third‑party license + notice bundles for Rust artifacts
status: idea
domains: [compliance, licensing, cargo, release-engineering]
last_reviewed: 2026-03-01
evidence:
  - https://users.rust-lang.org/t/missing-good-tools-for-bundling-third-party-licenses/93172
  - https://github.com/EmbarkStudios/cargo-about
  - https://github.com/sstadick/cargo-bundle-licenses
  - https://opensource.google/documentation/reference/thirdparty/rust
---

# Problem
Rust teams shipping binaries frequently need to **bundle third‑party license texts and attribution**. Existing Cargo tools help, but users report:
- outputs that depend on fuzzy “license detection thresholds” rather than *copying authoritative texts*,
- missing control over build target / cfg / features,
- and common failure modes where license files are not included in packaged workspace crates.

The result is repeated bespoke scripts and compliance risk.

# Users & user stories
- **App teams**: “When we cut a release, produce a `THIRDPARTY` bundle for *this exact build* (target, features, profile) and fail CI if anything is missing.”
- **Legal/compliance**: “Show the exact license texts and copyright notices shipped.”
- **Distros/packagers**: “Generate a machine-readable bill of licenses + a human-friendly bundle.”

# Prior art (and why it’s insufficient)
- `cargo-about`: great for generating a license listing, but users report surprises around threshold-based detection and want a “copy all authoritative texts” mode.
- `cargo-bundle-licenses`: bundles licenses, but users cite limited configurability and output ergonomics, and real projects hit missing-license-file packaging issues.

# Design goals
- Deterministic output for a **specific build plan** (target triple, cfg, features, workspace members).
- Prefer **authoritative license texts** (from the crate package contents), not reconstructed templates.
- Produce both:
  - **human** bundle (`THIRDPARTY.*` + folder of license texts),
  - **machine** bundle (JSON) with stable schema.
- CI-friendly failure modes (missing license file, unknown license expression, changed license since last release).

## Non-goals
- Replacing `cargo-deny` (this complements it: `cargo-deny` decides *allowed*, this bundles *what you ship*).

# Architecture & API sketch
Split into a library + cargo plugin:

## Library (`license_bundle_core`)
- `BuildPlan` (target, features, resolve graph)
- `ResolvedDep { package_id, source, selected_features, cfg }`
- `LicenseArtifact { spdx_expr, texts: Vec<TextFile>, notices: Vec<Notice>, provenance }`
- Extract texts from:
  1) the `.crate` tarball / packaged workspace output (preferred),
  2) repo fallback (optional, explicit opt-in).

## CLI (`cargo license-bundle`)
- `cargo license-bundle --target x86_64-unknown-linux-gnu --features ... --format thirdparty`
- `--fail-on missing-text|unknown-spdx|changed-license`
- `--bundle-dir target/license-bundle/` (stable location)

# Security / safety model
- **No network by default**; only reads local Cargo registry cache / packaged artifacts.
- If repo fetch is enabled, require pinned commit + checksum and mark provenance.

# Maintenance & governance plan
- Keep dependencies small (std + cargo metadata parsing).
- Conformance tests with fixture workspaces:
  - workspace include/exclude pitfalls,
  - multiple license files,
  - license changes across versions.

# Milestones
- **0.1**: resolve graph + copy license texts from `.crate` + output JSON
- **0.2**: stable `THIRDPARTY` renderer + dedupe + notices
- **0.3**: “license-change gate” (store baseline file + diff)
- **1.0**: conformance suite + integration docs for CI + release tooling

# Scorecard (0–5)
- Impact: 4
- Neglectedness: 4
- Feasibility: 4
- Adoptability: 5
- Sustainability: 4
- Differentiation: 4

# Open questions
- Best canonical output format for `THIRDPARTY` (Debian-style vs custom)?
- How should we treat crates that declare SPDX but ship no license text?

# Sources
- https://users.rust-lang.org/t/missing-good-tools-for-bundling-third-party-licenses/93172
- https://github.com/EmbarkStudios/cargo-about
- https://github.com/sstadick/cargo-bundle-licenses
- https://opensource.google/documentation/reference/thirdparty/rust
