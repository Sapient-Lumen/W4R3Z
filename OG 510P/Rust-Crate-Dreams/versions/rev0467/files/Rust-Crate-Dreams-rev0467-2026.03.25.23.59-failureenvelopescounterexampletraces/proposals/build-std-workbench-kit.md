---
id: P-0430
title: Build-Std Workbench Kit — stage-aware sysroot recipes, locks, and review receipts
status: idea
domains: [cargo, toolchains, embedded, safety-critical, build, cross-compilation]
last_reviewed: 2026-03-16
evidence:
  - https://rust-lang.github.io/rust-project-goals/2025h2/build-std.html
  - https://blog.rust-lang.org/2025/10/28/project-goals-2025h2/
  - https://blog.rust-lang.org/inside-rust/2025/11/19/program-management-update--october-2025/
  - https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
  - https://doc.rust-lang.org/cargo/reference/unstable.html#build-std
  - https://doc.rust-lang.org/cargo/CHANGELOG.html
  - https://crates.io/crates/cargo-sysroot
  - https://crates.io/crates/cargo-xbuild
---

# Problem

Rust now has a much clearer official story for `build-std`, but ordinary teams still lack a boring crate that makes those workflows **reviewable, diffable, and handoff-friendly**.

The upstream movement is real:

- Rust’s 2025H2 goals explicitly target stabilizing a core MVP of `build-std`.
- The July 2025 goals update split the work into explicit stages: manual enablement, explicit `core`/`alloc`/`std` dependencies, target-modifier / codegen customization, and then automatic rebuild behavior.
- The October 2025 program-management update says the `build-std` RFCs were posted, including context, always-on rebuild configuration, and explicit standard-library dependencies.
- Cargo’s unstable docs already define today’s operational constraints: nightly Cargo, nightly rustc, `rust-src`, and passing `-Z build-std` on every invocation.

That means the missing crate is no longer “some way to rebuild the sysroot.”
It is the **stage-aware workbench** that can tell other people:

- what exactly was rebuilt,
- under which stage assumptions,
- how host/target/sysroot/source choices were pinned,
- whether the recipe was directly observed or partially inferred,
- and what changed between two sysroot builds.

# Main judgment

The worthy contribution here is not another ad hoc wrapper around nightly flags.
It is a **portable recipe / lock / receipt / diff layer** above Cargo’s evolving std-aware substrate.

This crate should help people ship one compact bundle containing:

1. one recipe for how the sysroot should be rebuilt,
2. one lock for which toolchain/std sources/options were actually used,
3. one receipt for what was directly observed during the build,
4. one stage report saying whether the workflow reflects manual `-Z build-std`, explicit std-dependency posture, target-modifier/codegen posture, or automatic-rebuild assumptions,
5. one diff report between two sysroot builds,
6. and one evidence-source receipt that keeps direct facts separate from normalization or imported context.

# What it provides

- `sysroot.recipe.toml` — desired target, requested std crates, profile, panic mode, target JSON / target triple, codegen and target-modifier flags, source overrides, patch overlays, and export policy.
- `sysroot.lock` — exact toolchain, `rust-src` identity, std workspace source identity, enabled std features, build mode, Cargo/Cargo-config inputs, and output digests.
- `sysroot.receipt.json` — direct observations from one build: commands, target/host facts, produced artifacts, warnings, skipped units, and unstable features used.
- `sysroot-stage.report.json` — classifies the workflow as `manual_build_std`, `explicit_std_dependency_transition`, `target_modifier_profile`, `automatic_rebuild_policy`, or `manual_review_required`.
- `sysroot-diff.report.json` — compares two locked builds and classifies `same_recipe_new_toolchain`, `same_toolchain_changed_std_source`, `target_modifier_drift`, `stage_posture_changed`, `build_std_feature_set_changed`, and `manual_review_required`.
- `evidence-source.receipt.json` — says which facts came from direct Cargo output, local configuration inspection, imported bundle metadata, or manual annotation.
- `cargo sysroot recipe` — validate and normalize a build-std recipe.
- `cargo sysroot capture` — run or import one build-std workflow and emit receipt + lock artifacts.
- `cargo sysroot diff` — compare two captured sysroot bundles.
- `cargo sysroot bundle` — emit `*.sysrootbundle.zip` containing recipe, lock, receipts, and notes.

# What the crate should provide other people

1. **A stage-aware recipe language** that stays useful while upstream `build-std` evolves from manual flag-passing toward explicit std dependencies and later automatic rebuild behavior.
2. **A sharable sysroot lock** for teams that need to prove which std sources, features, flags, and toolchain revision were actually used.
3. **A reviewable boundary between direct evidence and guesswork** so support engineers and auditors can tell whether a fact was observed or reconstructed.
4. **A boring diff artifact** so two sysroot builds can be compared without spelunking shell scripts or Cargo internals.
5. **A migration bridge** for embedded, kernel-like, hardened, and qualification-heavy environments that need build-std now, before upstream stabilization is complete.

# Persona / who it’s for

- embedded and bare-metal maintainers
- Rust-for-Linux style integrators
- safety-critical / regulated-software teams
- custom distribution and toolchain engineers
- platform teams carrying patched std sources or custom target JSONs
- teams experimenting with sanitizer / hardening / debug-info sysroot variants

# Users & user stories

- **Embedded maintainer**: “Rebuild `core` and `alloc` for a custom target, freeze every assumption, and hand CI a compact bundle.”
- **Kernel/platform engineer**: “Track a patched std workspace, diff it across toolchain bumps, and keep review artifacts small.”
- **Safety engineer**: “Show me exactly which source tree, features, flags, and profile produced this sysroot.”
- **Toolchain adopter**: “Tell me whether this bundle represents today’s manual `-Z build-std` world, an explicit std-dependency transition, or something that assumes future automatic rebuild behavior.”
- **Support engineer**: “Explain whether this incompatibility came from toolchain drift, source drift, target-modifier drift, or recipe drift.”

# Prior art (and why it’s insufficient)

- Cargo’s unstable `build-std` support is the real substrate, but it is not yet a stable receiver-facing recipe/lock bundle.
- `cargo-xbuild` and `cargo-sysroot` show longstanding demand, but they do not define a neutral evidence bundle that survives across CI systems and later Cargo changes.
- Internal scripts in embedded/kernel/platform environments are often highly specific and rarely emit reviewable artifacts.
- The new RFC/staged planning is promising, but upstream Cargo is still deciding the final user-facing shape.

What remains missing is a **crate other people can build against today** that stays honest about stage posture and evidence sources.

# Design goals

1. **Stage-aware** — explicitly model the difference between manual `-Z build-std`, explicit std-dependency posture, target-modifier/codegen posture, and future auto-rebuild assumptions.
2. **Recipe-first** — keep the main authoring artifact small, portable, and diffable.
3. **Lock-and-receipt honest** — separate desired inputs from directly observed build facts.
4. **Host/target aware** — record target triple / target JSON, host assumptions, and std crate selection separately.
5. **Source-aware** — make `rust-src`, patched-std overlays, and source provenance first-class.
6. **Adoption-first** — help real teams use evolving `build-std`; do not try to replace Cargo.

# MVP surface

- Minimal types:
  - `SysrootRecipe`
  - `SysrootLock`
  - `SysrootReceipt`
  - `SysrootStageReport`
  - `SysrootDiffReport`
  - `EvidenceSourceReceipt`
  - `SysrootBundle`
- Minimal functions:
  - `load_recipe()`
  - `normalize_recipe()`
  - `capture_sysroot_build()`
  - `lock_sysroot()`
  - `classify_stage_posture()`
  - `diff_sysroots()`
  - `write_bundle()`
- Feature flags:
  - `build-std`
  - `patch-overlays`
  - `artifact-digests`
  - `import-existing-bundle`
  - `serde`

# Compatibility story

- Use Cargo/rustup/rustc as the actual builders.
- Accept that the upstream workflow is still changing; keep this crate’s recipe/lock schema stable earlier than the upstream substrate.
- Allow importing sysroot workflows captured outside Cargo when the evidence-source receipt marks them as imported or partially inferred.
- Treat missing `rust-src`, unstable-only requirements, and future-stage assumptions as first-class output, not hidden failure.

# Conformance & fixtures

This proposal now needs a real fixture corpus, not just prose.
The fixture pack should freeze:

- one minimal custom-target `core`/`alloc` rebuild,
- one patched-std overlay build,
- one target-modifier/profile variant,
- one “automatic rebuild assumed but not directly observed” scenario,
- and goldens for `manual_build_std`, `explicit_std_dependency_transition`, `target_modifier_profile`, and `automatic_rebuild_policy` stage classifications.

# Path to boring stability

- Stabilize `sysroot.recipe.toml`, `sysroot.lock`, `sysroot.receipt.json`, `sysroot-stage.report.json`, and `evidence-source.receipt.json` before anything fancier.
- Start with capture + diff + review bundles, not broad orchestration.
- Prefer `manual_review_required` over false certainty when stage posture or source identity is ambiguous.
- Keep target-family adapters and exotic target JSON semantics optional.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A library and cargo subcommand that can capture one build-std workflow into a portable recipe, lock, receipt, stage report, and diffable bundle.

# De-risk plan

1. Start with direct capture and imported-bundle normalization.
2. Freeze the stage vocabulary early so future upstream churn does not scramble downstream artifacts.
3. Keep source-provenance and evidence-source receipts mandatory.
4. Grow target-modifier and patched-source support through fixture packs instead of one-off flags.

# Non-goals

- Not a replacement for Cargo, rustup, or rustc.
- Not a promise that every build-std environment is stable today.
- Not a generic ABI-flag, sanitizer, or debugger-support crate.
- Not a binary distribution or remote-cache service.
- Not a fake “stable std-aware Cargo before Cargo stabilizes it.”

# Architecture & API sketch

```rust
pub struct SysrootRecipe {
    pub target: String,
    pub crates: Vec<String>,
    pub profile: String,
    pub build_std_features: Vec<String>,
    pub rustflags: Vec<String>,
    pub stage_hint: StageHint,
}

pub fn load_recipe(path: &std::path::Path) -> Result<SysrootRecipe>;
pub fn capture_sysroot_build(recipe: &SysrootRecipe, cx: &BuildContext) -> Result<SysrootReceipt>;
pub fn classify_stage_posture(lock: &SysrootLock, receipt: &SysrootReceipt) -> SysrootStageReport;
pub fn diff_sysroots(a: &SysrootLock, b: &SysrootLock) -> SysrootDiffReport;
pub fn write_bundle(bundle: &SysrootBundle, out: &std::path::Path) -> Result<()>;
```

Bundle draft:

- `sysroot.recipe.toml`
- `sysroot.lock`
- `sysroot.receipt.json`
- `sysroot-stage.report.json`
- `sysroot-diff.report.json`
- `evidence-source.receipt.json`
- `toolchain.toml`
- `notes.md`

# Security / safety model

- Preserve source provenance for `rust-src`, patched std overlays, and target-definition inputs.
- Make ABI/hardening/codegen differences first-class diff outputs.
- Support path redaction without erasing target/source identity.
- Never imply two sysroots are interchangeable when stage posture or source identity differs.

# Maintenance & governance plan

- Version the recipe/lock/report schema independently of Cargo’s current unstable implementation details.
- Maintain a small but diverse fixture corpus across hosted, embedded, custom-target, and patched-source scenarios.
- Keep target-modifier and source-overlay adapters additive.
- Update stage vocabulary whenever upstream `build-std` stages materially change.

# Milestones

## 0.1
- `sysroot.recipe.toml`
- `sysroot.lock`
- `sysroot.receipt.json`
- `sysroot-stage.report.json`

## 0.2
- imported-bundle normalization
- `evidence-source.receipt.json`
- sysroot diff bundles
- patched-source fixtures

## 1.0
- stable core schema
- target-modifier profile support
- narrow compatibility matrix and CI adapters

# Open questions

- Which parts of stage posture can be inferred reliably versus requiring explicit annotation?
- How much patched-source detail belongs in portable locks versus local/private overlays?
- What is the smallest target-modifier vocabulary that still helps real users?
- How should the crate represent sysroot builds that only rebuild `core`/`alloc` and never `std`?

# Sources

- Build-std goal: https://rust-lang.github.io/rust-project-goals/2025h2/build-std.html
- Project goals for 2025H2: https://blog.rust-lang.org/2025/10/28/project-goals-2025h2/
- Program management update — October 2025: https://blog.rust-lang.org/inside-rust/2025/11/19/program-management-update--october-2025/
- Project goals update — July 2025: https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
- Cargo unstable `build-std` docs: https://doc.rust-lang.org/cargo/reference/unstable.html#build-std
- Cargo changelog (`-Zbuild-std`, `build-std-features`, target-spec probing): https://doc.rust-lang.org/cargo/CHANGELOG.html
- `cargo-sysroot`: https://crates.io/crates/cargo-sysroot
- `cargo-xbuild`: https://crates.io/crates/cargo-xbuild
