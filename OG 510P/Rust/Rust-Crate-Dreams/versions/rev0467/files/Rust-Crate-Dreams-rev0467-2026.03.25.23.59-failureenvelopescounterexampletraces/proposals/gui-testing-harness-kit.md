---
id: P-0092
title: GUI Testing & Snapshot Harness Kit (cross-GUI) — cargo-native render/snapshot/event playback with CI artifacts
status: idea
domains: [devtools, gui, testing, ci, a11y]
last_reviewed: 2026-03-05
evidence:
  - https://www.boringcactus.com/2025/04/13/2025-survey-of-rust-gui-libraries.html
  - https://lib.rs/crates/egui_kittest
  - https://crates.io/crates/egui-screenshot-testing
  - https://github.com/emilk/egui
---

# Problem
Rust GUI testing is fragmented. Some frameworks have their own screenshot/snapshot tools, but there is **no reusable harness layer** that standardizes:
- deterministic offscreen rendering
- synthetic event playback
- snapshot/golden workflows
- CI artifact formats (diffs, metadata, reproduction scripts)

That fragmentation makes GUI regression testing harder for app teams, and makes it harder for framework maintainers to ship conformance suites.

# What it provides
A “shared testing substrate” that both GUI frameworks and application teams can rely on:

- **Harness crate**: a stable API for `render(frame)->snapshot` and `dispatch(event)->state`.
- **Event script format**: a tiny DSL (JSON/YAML) describing inputs + time steps.
- **Snapshot formats**:
  - image snapshot (PNG)
  - optional accessibility tree snapshot (structured JSON)
  - optional layout metadata (DPI scale, font versions, renderer backend)
- **Artifact bundle**: `*.guitest.zip`
  - `events.json`
  - `snapshots/`
  - `diffs/`
  - `meta.json` (DPI, fonts, renderer, OS, GPU)
  - `repro.md` (exact commands)
- **Cargo UX**:
  - `cargo gui-test` (run)
  - `cargo gui-snap` (update goldens)
  - `cargo gui-diff` (open local HTML report)
  - `cargo gui-doctor` (determinism checks: fonts, DPI, backend)

# Users & user stories
- **GUI app teams**: “Catch visual regressions before release; reproduce CI failures locally.”
- **Framework maintainers**: “Publish a conformance suite that downstream apps can run.”
- **CI maintainers**: “Store compact artifacts and show diffs in PRs.”

# Prior art (and why it’s insufficient)
- egui’s testing helpers show the demand, but are **framework-scoped** and don’t generalize to the ecosystem. See evidence links.

# Design goals
- Determinism-first: stable snapshots across platforms where possible (especially with a software path).
- Artifact-first: every failure produces a shareable bundle.
- Cross-framework: define a minimal common denominator; allow per-framework adapters.

# Non-goals
- Full OS-level automation (that’s Playwright/Appium-like territory).
- Standardizing one GUI framework.

# Architecture & API sketch
- `gui_test_harness::Harness<Adapter>` where `Adapter` provides:
  - `fn step(&mut self, event: Event)`
  - `fn render(&mut self) -> Snapshot`
- Backends:
  - software backend (portable)
  - optional GPU backend (wgpu) behind feature flags

# Security / safety model
- No network by default in CI mode.
- Snapshot bundles should include only deterministic outputs (avoid capturing secrets).

# Maintenance & governance plan
- Keep the core harness minimal; push framework-specific integrations into adaptor crates.
- Conformance fixtures live in-repo with clear versioning for formats.

# Milestones
- 0.1: software rendering snapshots + event playback + HTML diff report
- 0.2: first two adaptors (e.g., egui + one other)
- 0.3: a11y tree snapshots (optional) + conformance pack
- 1.0: stable artifact format + compatibility guarantees

# Open questions
- How to define “deterministic enough” for GPU pipelines (metadata + opt-in).
- How much to standardize accessibility trees across frameworks.

# Sources
- See evidence links above.
