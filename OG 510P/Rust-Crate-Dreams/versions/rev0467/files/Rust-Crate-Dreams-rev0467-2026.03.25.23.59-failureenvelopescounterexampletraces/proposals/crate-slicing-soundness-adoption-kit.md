---
id: P-0462
title: Crate Slicing Soundness & Adoption Kit — slice-eligibility ledgers, predicted-benefit receipts, and fallback-aware review bundles above `cargo-slicer` and rustc-native slicing work
status: idea
domains: [cargo, compiler, performance, build, ci, static-analysis, adoption]
last_reviewed: 2026-03-07
evidence:
  - https://rust-lang.github.io/rust-project-goals/2026/crate-slicing.html
  - https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  - https://github.com/yijunyu/cargo-slicer
  - https://crates.io/crates/cargo-slicer
  - https://blog.rust-lang.org/2023/11/09/parallel-rustc.html
---

# Problem

Rust now has an explicit 2026 project goal around **crate slicing for faster fresh builds**. That goal is intentionally not “ship `cargo-slicer` to everyone as-is.” Instead, it uses `cargo-slicer` and PRECC-Rust as proof that a meaningful separate-compilation gap exists, while stressing that real production support must be rustc-native and must handle soundness constraints like trait coherence, blanket impls, proc macros, and `build.rs` fallbacks.

That leaves a very practical ecosystem gap for ordinary teams:

- the existing proof-of-concept is useful for demonstrating opportunity, but not for producing a conservative **adoption decision artifact**,
- maintainers still lack a boring way to say *which crates or targets are slicing candidates*,
- they cannot easily record *why a dependency must fall back to full compilation*,
- and they do not have a compact receipt for the tradeoff between predicted benefit, analysis overhead, and soundness risk.

The missing crate is not a new slicer.

The missing crate is a **soundness-and-adoption kit** that helps teams review whether slicing is worth trying, where it is unsafe to assume, and how to report the result back upstream.

# What it provides

- `slice-profile.toml` — declares workspace targets, toolchains, fallback policy, sensitivity to proc macros / `build.rs`, and acceptable analysis overhead.
- `slice-candidates.json` — inventory of crates or units that appear slice-eligible, slice-hostile, or unknown.
- `slice-soundness.json` — conservative findings like `blanket_impl_risk`, `proc_macro_boundary`, `build_rs_generated_code`, `trait_coherence_unknown`, and `manual_review_required`.
- `slice-benefit.json` — predicted gap, observed compile-time deltas, and overhead classes.
- `slice-fallbacks.json` — records why full-crate compilation was retained for a unit.
- `slice.receipt.json` — exact toolchain, slicer/prototype version, flags, dataset, and caveats.
- `cargo slice-adopt plan` — inventory candidate units and expected review burden.
- `cargo slice-adopt rehearse` — run a conservative dry-run without changing the build pipeline permanently.
- `cargo slice-adopt diff` — compare two adoption runs or two workspaces.
- `*.slicebundle.zip` — shareable artifact for team review, CI triage, or compiler-team issue filing.

# What the crate should provide other people

1. **A boring review artifact** for “should we even try slicing here?”
2. **A soundness vocabulary** above research prototypes.
3. **A fallback ledger** that makes unsliceable crates visible instead of silently excluded.
4. **A predicted-benefit receipt** that separates real wins from wishful compile-time folklore.
5. **A bridge** between experimental slicing tools and future rustc-native support.

# Persona / who it’s for

- performance-minded maintainers of large Rust workspaces
- compiler-adjacent build engineers
- CI owners trying to justify experimentation on fresh-build bottlenecks
- contributors preparing evidence for rustc-native slicing design discussions

# Users & user stories

- **Workspace maintainer**: “Tell me which of our dependencies are plausible slicing candidates and which ones should stay full-crate because of macros or generated code.”
- **Compiler contributor**: “Show me a minimized bundle where slicing looked attractive but trait/coherence concerns forced fallback.”
- **CI engineer**: “Compare predicted and observed benefit for two candidate services before we invest in deeper tooling.”
- **Research adopter**: “Keep a record of what this prototype did, what it skipped, and why we still consider the results informative.”

# Prior art (and why it’s insufficient)

- The 2026 crate-slicing goal explicitly positions `cargo-slicer` and PRECC-Rust as proof-of-concept evidence, not production workflow.
- `cargo-slicer` itself proves there is opportunity, but it is intentionally outside rustc and cannot fully model coherence or all language features.
- The parallel-rustc work shows idle cores are real, but it does not answer whether a given workspace is a good slicing candidate.

What remains missing is a **maintainer-facing adoption layer**: the thing that records slice eligibility, fallback reasons, predicted benefit, and soundness caveats as a reviewable artifact.

# Design goals

1. **Soundness-first** — prefer explicit fallback to optimistic misclassification.
2. **Prototype-friendly** — useful with today’s tools, not only after rustc-native slicing exists.
3. **Benefit-honest** — predicted wins and analysis overhead must both be visible.
4. **Fallback-explicit** — “could not slice safely” is first-class output.
5. **Upstream-useful** — exported bundles should help compiler discussions, not just local dashboards.

# MVP surface

- Minimal types: `SliceProfile`, `SliceCandidate`, `SliceSoundnessFinding`, `SliceBenefitReport`, `SliceFallback`, `SliceReceipt`, `SliceBundle`
- Minimal functions:
  - `inventory_candidates()`
  - `classify_soundness_risk()`
  - `estimate_benefit()`
  - `diff_receipts()`
  - `write_bundle()`
- Feature flags:
  - `cargo`
  - `serde`
  - `cargo-slicer`
  - `perf`
  - `ci`

# Compatibility story

- Must be useful before any rustc-native slicing lands by wrapping explicit prototype runs and conservative static inventory.
- Should remain useful after native slicing because teams will still need an adoption/fallback receipt.
- Must tolerate partial information and unknown categories.
- Should never imply that source-level slicing is semantically authoritative.

# Conformance & fixtures

- One macro-light workspace with likely benefit.
- One proc-macro-heavy workspace that mostly falls back.
- One `build.rs`-generated workspace with explicit “unknown / fallback” output.
- Goldens for `slice_candidate`, `fallback_due_to_proc_macro`, `benefit_overhead_negative`, and `manual_review_required`.
- A fixture comparing observed deltas on a small and large workspace.

# Path to boring stability

- Stabilize the receipt and fallback vocabulary before any automation beyond dry-run rehearsal.
- Start with candidate inventory and exported bundles.
- Keep the soundness taxonomy small and conservative.
- Add richer benefit prediction only after teams trust the basic receipts.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 27/30**

# Minimum lovable MVP

A library and cargo subcommand that inventory one workspace, classify each unit as slice-candidate / fallback / unknown, record conservative soundness reasons, and emit a `slice.receipt.json` plus compact review bundle.

# De-risk plan

1. Start with read-only inventory and receipt generation, not build rewriting.
2. Model only a handful of soundness/fallback classes first.
3. Validate on one real large workspace and one intentionally hostile macro-heavy workspace.
4. Keep prototype adapters thin so the crate does not become a hidden slicer implementation.

# Non-goals

- Not a replacement for rustc-native slicing work.
- Not a promise that source-level slicing is sound.
- Not a generic build-analysis platform.
- Not a benchmarking suite for every compile-performance question.

# Architecture & API sketch

```rust
pub enum SliceDisposition {
    Candidate,
    Fallback,
    Unknown,
}

pub fn inventory_candidates(root: &Path) -> Result<Vec<SliceCandidate>>;
pub fn classify_soundness_risk(candidate: &SliceCandidate) -> Vec<SliceSoundnessFinding>;
pub fn estimate_benefit(profile: &SliceProfile, root: &Path) -> Result<SliceBenefitReport>;
pub fn write_bundle(bundle: &SliceBundle, out: &Path) -> Result<()>;
```

Bundle draft: `slice-profile.toml`, `slice-candidates.json`, `slice-soundness.json`, `slice-benefit.json`, `slice-fallbacks.json`, `slice.receipt.json`, `notes.md`.

# Security / safety model

- Never claim semantic equivalence when only a prototype approximation was used.
- Treat proc macros, generated code, and coherence-sensitive patterns as explicit risk boundaries.
- Record exact toolchain and prototype versions.
- Support path redaction in exported bundles.

# Maintenance & governance plan

- Track the 2026 slicing goal and any rustc-native design evolution closely.
- Keep the risk taxonomy small and review-oriented.
- Maintain a fixture corpus spanning “good candidate” and “must fallback” workspaces.
- Publish guidance for interpreting predicted-benefit versus observed runtime/compile-time deltas.

# Milestones

## 0.1
- candidate inventory
- fallback taxonomy
- basic receipt export

## 0.2
- prototype adapters
- benefit estimation
- diffing across runs

## 1.0
- stable receipt schema
- CI adapters
- public fixture corpus

# Open questions

- What is the smallest useful taxonomy for slice-soundness concerns?
- How should predicted benefit be represented when prototype overhead dominates?
- Which classes of crates are most useful to classify early: proc macros, `build.rs`, blanket-impl-heavy libraries, or all three?

# Sources

- Crate slicing goal: https://rust-lang.github.io/rust-project-goals/2026/crate-slicing.html
- Rust in 2026 flagships: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- `cargo-slicer`: https://github.com/yijunyu/cargo-slicer
- crates.io entry for `cargo-slicer`: https://crates.io/crates/cargo-slicer
- Parallel rustc measurements: https://blog.rust-lang.org/2023/11/09/parallel-rustc.html
