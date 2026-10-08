---
id: P-0512
title: Crate Guidance Pack Kit — supportive diagnostics, recovery recipes, and failure-path receipts for library authors
status: idea
domains: [crates, diagnostics, dx, docs, proc-macros, async, cargo, supportiveness]
last_reviewed: 2026-03-19
evidence:
  - https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  - https://doc.rust-lang.org/reference/attributes/diagnostics.html
  - https://doc.rust-lang.org/reference/attributes.html
  - https://doc.rust-lang.org/beta/releases.html
  - https://rust-lang.github.io/rfcs/3368-diagnostic-attribute-namespace.html
  - https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html
  - https://doc.rust-lang.org/rustdoc/unstable-features.html
  - https://docs.rs/trybuild/latest/trybuild/
  - https://docs.rs/ui_test/latest/ui_test/
  - https://docs.rs/miette/latest/miette/trait.Diagnostic.html
  - https://docs.rs/proc-macro-error2/latest/proc_macro_error2/
---

# Problem

Rust’s current ecosystem research is pointing at a supportiveness gap that sits **inside crates themselves**.

The December 2025 vision-doc work says Rust should “double down on extensibility” and explicitly calls out **supportive interfaces** — better diagnostics and guidance from crates — as an area where Rust is still weak. It also says the ecosystem’s extensibility can become an obstacle when people cannot tell which crate to use or how to recover from a mismatch once they have chosen one.

Meanwhile, the 2025 State of Rust survey says online documentation remains the preferred canonical reference and the code itself is the next place people study. That is a strong sign that a crate’s support surface is not a side issue; it is part of the product.

Rust now has real substrate for better compile-time guidance:

- the `#[diagnostic]` namespace is stable,
- `#[diagnostic::on_unimplemented]` is stable,
- `#[diagnostic::do_not_recommend]` is in the Reference,
- and the Reference explicitly documents that these are compiler-facing hints for compile-time errors.

But those pieces are still just fragments.
Library authors still lack a boring workflow for questions like:

- which failure paths deserve first-class guidance,
- whether compile-fail fixtures still emit the guidance we think they do,
- which docs/example anchors are the intended recovery paths,
- how a proc-macro crate, trait-heavy crate, or feature-rich crate records its “good next step” advice,
- and how downstream tools import that support surface without scraping prose.

The missing crate is therefore **not** another diagnostic renderer and **not** another crate-ranking engine.
It is a **Crate Guidance Pack Kit**: a crate that helps maintainers author, test, diff, and export a receiver-facing support surface for their crates.

# Main judgment

A worthy crate here should provide a receiver-facing answer to:

1. **What are this crate’s common failure modes?**
2. **Which ones have exact compiler-supported diagnostics versus advisory guidance only?**
3. **What recovery recipe should another person follow next?**
4. **Which guidance paths are verified by fixtures, and which still require manual review?**
5. **What changed in the support surface across releases?**

That is more valuable than another pretty error renderer.

# What it provides

- `guidance-pack.toml` — versioned declaration of common failure paths, guidance classes, docs anchors, recipe references, and manual-review zones.
- `compile-guidance.receipt.json` — observed compile-time guidance surface: `#[diagnostic::on_unimplemented]`, `#[diagnostic::do_not_recommend]`, proc-macro diagnostics, and other captured compile-fail hints.
- `recovery-recipe.manifest.json` — minimal runnable or compileable examples showing the intended “good path” after a failure.
- `guidance-check.report.json` — verifies that fixtures still trigger the expected guidance, docs anchors resolve, and recovery recipes still build or compile as promised.
- `guidance-diff.report.json` — compares two crate releases and classifies `guidance_added`, `guidance_removed`, `recipe_changed`, `anchor_changed`, `manual_review_required`, and `diagnostic_hint_drift`.
- `guidance-authority.policy.json` — explicit meaning for compiler-backed versus fixture-observed versus advisory guidance claims.
- `recovery-origin.receipt.json` — provenance for each recovery hint, such as diagnostic attributes, compile-fail fixtures, rustdoc examples, `miette` metadata, or maintainer-authored anchors.
- `recipe-fidelity.report.json` — explicit statement of how much of the advertised recovery path was actually checked across features, editions, targets, docs parity, and proc-macro invocation shape.
- `message-stability.report.json` — explicit statement of whether the crate promises exact wording, code-only stability, shape-level stability, failure-only proof, or manual review.
- `guidance-channel.receipt.json` — receiver-facing record of whether support is delivered through compiler diagnostics, snapshot-tested stderr, proc-macro emission, `miette` metadata, docs anchors, or a mixed path.
- `support-path.summary.md` — short human-facing summary of the most important supported failure/recovery paths.
- `cargo guidance-pack check` — run compile-fail/runtime-light fixtures and emit a report.
- `cargo guidance-pack capture` — capture the current crate guidance surface.
- `cargo guidance-pack diff <old> <new>` — show how the support surface changed.
- `cargo guidance-pack summary` — render the user-facing summary from the pack.

# What the crate should provide other people

1. **A receiver-facing support contract** above raw type errors, feature mismatches, and macro failures.
2. **A verified guidance layer** for trait-heavy, proc-macro-heavy, and configuration-heavy crates.
3. **Recovery recipes** that turn “something failed” into “here is the smallest known good path”.
4. **A diffable support surface** so maintainers can review whether a release became easier or harder to use.
5. **A message-stability contract** so downstream teams know whether exact wording is supported or only the broader error/help shape is.
6. **A guidance-channel contract** so users know whether help arrives through compiler output, snapshot-tested stderr, proc-macro emission, `miette`, docs anchors, or manual review.
7. **Importable guidance vocabulary** for docs portals, editors, pathfinder-style tools, and support bots.
8. **A narrow bridge** between official compiler diagnostic hooks and crate-authored usability work.

# Persona / who it’s for

- library authors with trait-heavy APIs
- proc-macro authors
- framework maintainers whose users regularly hit configuration or feature mismatches
- app teams maintaining internal foundational crates
- docs/tool authors who want structured “what now?” surfaces

# Users & user stories

- **Trait-heavy library maintainer**: “Prove that our most common bound errors produce clear guidance and link to the right fix path.”
- **Proc-macro maintainer**: “Record the expected diagnostics and recovery recipes for the three most common misuse cases.”
- **Framework team**: “Diff the support surface across releases so we do not quietly remove helpful guidance.”
- **Editor/docs author**: “Import machine-readable recovery steps instead of scraping prose examples from README files.”
- **Platform team**: “Keep internal crate guidance reviewable in CI just like public API or semver drift.”

# Prior art (and why it’s insufficient)

- The Rust Reference now documents the `#[diagnostic]` namespace and `#[diagnostic::on_unimplemented]` as stable compile-time guidance hooks.
- The Reference also lists `#[diagnostic::do_not_recommend]`, which lets authors keep misleading impls out of compiler suggestions.
- RFC 3368 exists because crates with complex type hierarchies can emit large, incomprehensible errors and authors need tools to improve them.
- rustdoc `compile_fail` examples make failure-path documentation testable, but explicitly warn that code failing today may compile in a future release.
- rustdoc’s nightly-only error-code checking for `compile_fail` doctests is useful, but the rustdoc book also says emitted codes are not guaranteed to be the only thing a snippet emits from version to version, so that feature is unlikely to stabilize.
- `trybuild` and `ui_test` already make compiler stderr a testable surface for misuse cases.
- `miette` already exposes diagnostic code, help text, and URL metadata that crates can reuse.
- `trybuild` and `ui_test` already make message shape and stderr snapshots testable, but those harnesses still do not define what exact wording another team may treat as contractual.
- `proc-macro-error2` already provides a structured path away from `panic!`-based proc-macro errors.
- Generic renderer crates such as `miette`, `ariadne`, and `codespan-reporting` help tools present diagnostics well.
- The latest survey and vision-doc work show that supportiveness and documentation are a major part of how people successfully learn and use Rust.

What remains missing is a **crate-authored guidance pack workflow** above those pieces:

- author one guidance surface,
- verify it against fixtures,
- export it in stable artifacts,
- and diff it over time.

# Design goals

1. **Receiver-facing first** — optimize for the person blocked by an error, not just the maintainer emitting it.
2. **Exact versus advisory honesty** — distinguish compiler-backed hints from prose-only or recipe-only guidance.
3. **Compile-time and runtime separation** — keep compile-fail guidance separate from runtime troubleshooting receipts.
4. **Recipe-backed support** — the best guidance paths should point to a minimal good example, not only words.
5. **Docs/editor friendly** — exported artifacts should be easy for docs sites and tooling to import.
6. **Import, don’t absorb** — ranking, capability contracts, interop profiles, and renderer crates remain separate lanes.
7. **Narrow enough to ship** — first stabilize a tiny failure/guidance vocabulary before supporting many adapters.

# MVP surface

- Minimal types: `GuidancePack`, `FailureCase`, `CompileGuidanceReceipt`, `RecoveryRecipeManifest`, `GuidanceCheckReport`, `GuidanceDiffReport`, `SupportPathSummary`
- Minimal functions:
  - `load_guidance_pack()`
  - `capture_compile_guidance()`
  - `check_failure_cases()`
  - `validate_recovery_recipes()`
  - `diff_guidance_bundles()`
  - `render_support_summary()`
- Feature flags:
  - `serde`
  - `cargo`
  - `compile-fail`
  - `proc-macro`
  - `docs-links`
  - `markdown`

# Compatibility story

- Works above stable compiler diagnostic attributes rather than replacing them.
- Should remain useful for crates that do **not** use `#[diagnostic]` yet, because they can still export recipe-backed advisory guidance.
- Must preserve which guidance came from exact compiler hooks, fixture-observed stderr, or maintainer-authored recovery notes.
- Should interoperate with docs portals, pathfinder-style ecosystem tools, and future support bots by exporting small machine-readable artifacts.
- Must stay honest when the crate’s guidance is intentionally incomplete and still requires manual review.

# 0.1 failure families

1. `trait_bound_mismatch`
   - expected `on_unimplemented` / `do_not_recommend` guidance if present
   - recovery recipe points at the smallest correct impl or adapter path
2. `feature_or_runtime_mismatch`
   - expected help when a crate is used without the required feature/runtime profile
   - recipe shows the supported feature set or runtime-neutral alternative
3. `proc_macro_usage_mismatch`
   - expected diagnostic and smallest corrected invocation
4. `unsupported_target_or_cfg_path`
   - expected guidance for unsupported target/platform/cfg combinations
   - recipe points to supported target or fallback adapter path

# Conformance & fixtures

- one trait-bound fixture with explicit `on_unimplemented` guidance
- one fixture proving a misleading impl is hidden by `do_not_recommend`
- one proc-macro misuse fixture with an expected corrective note
- one feature/runtime mismatch fixture with a minimal “good path” recipe
- goldens for `guidance_present`, `guidance_missing`, `recipe_missing`, `anchor_missing`, `diagnostic_hint_drift`, and `manual_review_required`

# Path to boring stability

- Stabilize the pack/check/diff schema before growing fancy editor integrations.
- Start with a tiny failure vocabulary and a small number of built-in result classes.
- Treat docs anchors and recipes as first-class tested assets, not README decoration.
- Keep advisory guidance clearly labeled so it does not masquerade as guaranteed compiler behavior.
- Add runtime troubleshooting only after compile-time guidance receipts prove useful.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 27/30**

# Minimum lovable MVP

A crate and cargo subcommand that load one `guidance-pack.toml`, run a small compile-fail fixture set, record observed diagnostic guidance plus recipe anchors, and emit a `guidance-check.report.json` together with a short `support-path.summary.md`.

# De-risk plan

1. Start with compile-time guidance and recipe validation before runtime troubleshooting.
2. Validate on one trait-heavy library, one proc-macro crate, and one feature-rich async crate.
3. Freeze exact-vs-advisory result classes early.
4. Keep the first version import-friendly for docs/editor tooling instead of chasing bespoke UIs.

# Non-goals

- Not another terminal diagnostic renderer.
- Not a crate picker or ranking engine.
- Not a generic documentation site generator.
- Not a semver checker.
- Not a full support bot or issue tracker replacement.

# Architecture & API sketch

```rust
pub enum GuidanceClass {
    TraitBoundMismatch,
    FeatureOrRuntimeMismatch,
    ProcMacroUsageMismatch,
    UnsupportedTarget,
}

pub enum EvidenceClass {
    CompilerHint,
    FixtureObserved,
    AdvisoryRecipe,
}

pub fn load_guidance_pack(path: &std::path::Path) -> Result<GuidancePack>;
pub fn capture_compile_guidance(root: &std::path::Path) -> Result<CompileGuidanceReceipt>;
pub fn check_failure_cases(root: &std::path::Path, pack: &GuidancePack) -> Result<GuidanceCheckReport>;
pub fn validate_recovery_recipes(root: &std::path::Path, pack: &GuidancePack) -> Result<RecoveryRecipeManifest>;
pub fn diff_guidance_bundles(old: &GuidanceBundle, new: &GuidanceBundle) -> GuidanceDiffReport;
```

Bundle draft: `guidance-pack.toml`, `compile-guidance.receipt.json`, `recovery-recipe.manifest.json`, `guidance-check.report.json`, `guidance-diff.report.json`, `support-path.summary.md`, `notes.md`.

# Security / safety model

- Never hide the original compiler failure behind a prettier message.
- Keep exact compiler-backed guidance distinct from maintainer-authored advice.
- Support redaction of local file paths in exported receipts.
- Treat recipe execution as opt-in and minimal.
- Warn when docs anchors or examples become stale instead of silently dropping them.

# Maintenance & governance plan

- Track the stable diagnostic attribute surface and any future expansion in the Reference.
- Keep schemas compact and versioned.
- Maintain a public fixture corpus for trait-bound, proc-macro, feature/runtime, and target-support cases.
- Encourage other tools to import the guidance vocabulary rather than inventing bespoke per-crate scraping.
- Publish a brief compatibility note whenever the compiler changes observable diagnostic behavior in a way that affects receipts.

# Milestones

## 0.1
- pack schema
- compile-guidance receipt
- fixture checker
- support summary

## 0.2
- recipe validation
- diff report
- docs/editor import notes

## 1.0
- stable schemas
- curated corpus across at least four failure families
- importer guidance for docs portals, editors, and pathfinder-style tools

# Open questions

- What is the smallest useful failure vocabulary that still travels well across domains?
- How much compiler stderr matching is needed before the tool becomes brittle?
- Which guidance surfaces belong in the crate versus downstream ecosystem tools?

# Sources

- Rust vision-doc post, including “supportive interfaces” and ecosystem-orientation recommendations: https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey results, including documentation/code as primary learning surfaces: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust Reference, diagnostic attribute namespace and `on_unimplemented`: https://doc.rust-lang.org/reference/attributes/diagnostics.html
- Rust Reference built-in diagnostics index including `diagnostic::do_not_recommend`: https://doc.rust-lang.org/reference/attributes.html
- Rust 1.78.0 release notes stabilizing `#[diagnostic]` and `#[diagnostic::on_unimplemented]`: https://doc.rust-lang.org/beta/releases.html
- RFC 3368 on the diagnostic attribute namespace and crate-authored compile-time guidance: https://rust-lang.github.io/rfcs/3368-diagnostic-attribute-namespace.html
