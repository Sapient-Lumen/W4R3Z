---
id: P-0136
title: Localization Pipeline Kit — modern Rust i18n with ICU4X + Fluent, extraction, testing, and shipping workflows
status: idea
domains: [i18n, ux, tooling, productivity]
last_reviewed: 2026-03-05
evidence:
  - https://github.com/unicode-org/icu4x
  - https://docs.rs/icu
  - https://discourse.mozilla.org/t/high-level-fluent-rust-apis/123688
  - https://lib.rs/internationalization
needs:
  - Rust apps (CLI/desktop/server) need a **high-level** localization story that is:
    - ergonomic for developers,
    - workable for translators/localizers,
    - testable in CI,
    - and consistent across UI stacks.
  - The ecosystem has powerful primitives (ICU4X, Fluent), but “end-to-end product i18n” still requires a lot of bespoke glue.
non_goals:
  - Replacing ICU4X or Fluent.
  - Solving every translation platform integration out of the gate.
what_it_provides:
  - A unified message runtime:
    - Fluent-compatible message formatting with ICU4X-backed locale data where appropriate.
    - Strongly-typed “message keys” generation (optional) to reduce runtime missing-key surprises.
  - Extraction and build integration:
    - `cargo l10n extract` (scan Rust sources for message keys and parameters).
    - `cargo l10n compile` (validate bundles, generate optimized runtime assets).
  - Testing and QA tools:
    - Pseudolocalization mode (accenting/expansion) to catch layout issues early.
    - `cargo l10n doctor` for missing keys, unused keys, and parameter mismatches.
    - Locale-fallback simulations to ensure predictable behavior.
  - Shipping workflows:
    - A versioned `*.l10nbundle.zip` artifact containing the compiled catalogs + metadata + diagnostics output for CI caching and reproducibility.
mvp_plan:
  - MVP (3–5 weeks):
    - Minimal runtime + extraction + validation; `doctor`; integrate with common app patterns (anyhow/logging).
  - v1 (2–3 months):
    - Better typing story (derive macro generating enums/structs for keys), plural rules/fallback policy, pseudo-l10n, bundle artifact spec.
design_notes:
  - Separate “translation format” from “developer API”:
    - Keep Fluent (or Fluent-like) as an interchange format, while providing a Rust-native ergonomic surface.
  - Make i18n failures visible:
    - Prefer explicit diagnostics over silent fallback; emit actionable reports.
  - Keep data footprint controllable:
    - Offer features/profiles for “tiny CLI” vs “desktop app” vs “server”.
testing_conformance:
  - Fixture corpora across scripts/locales (LTR/RTL, complex plurals).
  - Golden tests for formatting outputs and fallback behavior.
  - Fuzz keys/params in extraction and compilation steps.
adoption_path:
  - Start with app teams that already want Fluent but lack tooling.
  - Provide adapters for popular UI crates (egui/iced/slint) as optional layers, not core dependencies.
---

(Proposal details are encoded in the YAML front matter for machine-checkable indexing.)
