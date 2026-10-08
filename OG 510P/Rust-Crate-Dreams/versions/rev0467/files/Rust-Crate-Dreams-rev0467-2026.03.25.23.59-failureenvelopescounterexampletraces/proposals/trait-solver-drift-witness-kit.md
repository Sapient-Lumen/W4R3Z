---
id: P-0442
title: Trait Solver Drift Witness Kit — solver-lane receipts, obligation-class reports, diagnostic-normalization receipts, and minimized witness bundles
status: idea
domains: [compiler, language, types, diagnostics, testing, ci, devtools]
last_reviewed: 2026-03-22
evidence:
  - https://rust-lang.github.io/rust-project-goals/2025h2/next-solver.html
  - https://doc.rust-lang.org/beta/releases.html
  - https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
  - https://rustc-dev-guide.rust-lang.org/solve/significant-changes.html
  - https://rustc-dev-guide.rust-lang.org/solve/proof-trees.html
  - https://docs.rs/ui_test
  - https://crates.io/crates/trybuild
  - https://crates.io/crates/compiletest_rs
---

# Problem

Rust now has enough *real* trait-solver transition surface that “run trybuild on nightly and eyeball stderr” is no longer a serious ecosystem answer.

Fresh primary-source signals line up:

- the active project goal is explicitly about stabilizing `-Znext-solver=globally`, moving more lints and rustdoc to the new solver, and asking people to test it;
- stable Rust 1.84 already enabled the next-generation trait solver for coherence by default, which means the ecosystem is already living in a mixed-lane world rather than a clean old/new flip;
- the compiler-dev documentation now describes specific semantic and diagnostic differences in the new solver, including canonicalization-heavy behavior, proof-tree-based diagnostics, and different handling of nested goals;
- nightly/compiler docs still expose concrete lane differences such as overflow behavior under `-Znext-solver`;
- and the GSoC witness-generation work for `cargo-semver-checks` showed that “generate a witness crate and let rustc decide” is now a proven pattern for hard type-level questions.

That combination creates a missing middle.

Existing tools are useful, but incomplete for this job:

- `ui_test`, `trybuild`, and `compiletest_rs` can preserve compile-pass/compile-fail expectations;
- witness-generation work proves we can force rustc itself to arbitrate difficult type questions;
- the compiler has proof-tree and tracing substrate for its own needs;
- but ordinary crate authors still lack a **portable, reviewable support contract** for solver drift.

The missing crate is not a new trait solver.
The missing crate is not a generic compiler-fuzzing harness.
The missing crate is a **trait-solver drift witness kit** that can tell another engineer:

1. which solver lane actually ran,
2. which class of obligation changed,
3. whether the change is semantic, diagnostic, or scope-only,
4. how a minimized witness relates to the original corpus,
5. and where the evidence stops.

# Main judgment after the 2026-03-22 implementation refresh

This proposal is now sharper than its original “run two toolchains and diff them” framing.

A worthy crate contribution here should **not** just emit old/new stderr snapshots.
It should freeze a small set of first-class artifacts:

- one **`comparison-lane.receipt.json`** for which solver mode and compiler lane actually produced the result;
- one **`corpus-authority.receipt.json`** for where each case came from and how trustworthy its expectations are;
- one **`obligation-class.report.json`** for what kind of solver question changed;
- one **`diagnostic-normalization.receipt.json`** for what was normalized away before calling something “diagnostic-only”;
- one **`minimization-lineage.receipt.json`** for how a reduced repro maps back to the original case;
- one **`solver-drift.diff.json`** for the conservative comparison result;
- and one **`solver-support-bundle.manifest.json`** joining those pieces.

That is the point where this stops being compile-fail folklore and becomes a receiver-facing crate others can build workflows around.

# What it provides

- `solver-profile.toml` — pins toolchains, channels, target, edition, crate flags, corpus adapters, and comparison policy.
- `comparison-lane.receipt.json` — records whether the compared run was `legacy_only`, `coherence_default_only`, `global_preview`, or `mixed_unknown`, plus the exact rustc/cargo/rustdoc/lint command families involved.
- `corpus-authority.receipt.json` — records whether a case came from `ui_test`, `trybuild`, `compiletest`, handwritten source, generated witness code, or a reduced repro; whether it was imported exactly or adapted; and which expectations are normative versus advisory.
- `obligation-class.report.json` — classifies what changed for each case: trait-bound satisfaction, alias normalization, higher-ranked reasoning, coherence overlap, overflow/fixpoint behavior, opaque-type handling, or `manual_review_required`.
- `diagnostic-normalization.receipt.json` — records path remapping, span elision, note filtering, proof-tree/provenance differences, and whether a “diagnostic-only” verdict is still trustworthy.
- `minimization-lineage.receipt.json` — maps one reduced witness back to the original case, fixture family, feature set, and dropped context.
- `solver.results.json` — normalized outcomes per case and run.
- `solver-drift.diff.json` — categories such as `accepted_to_rejected`, `rejected_to_accepted`, `overflow_behavior_changed`, `coherence_only_lane_changed`, `diagnostic_only`, `scope_changed`, and `manual_review_required`.
- `solver-support-bundle.manifest.json` — the shareable bundle manifest joining the review artifacts.
- `cargo solver-witness run` — execute one corpus under one or more solver lanes.
- `cargo solver-witness diff` — produce the conservative drift report.
- `cargo solver-witness reduce` — minimize one changed case while preserving lineage.
- `cargo solver-witness pack` — emit a portable `*.solverbundle.zip`.

# What the crate should provide other people

1. **A boring way to ask “which solver lane did this actually exercise?”**
2. **A shared vocabulary** for obligation classes instead of one-off compiler-log interpretation.
3. **A receiver-facing distinction between semantic drift and diagnostic drift.**
4. **A minimized witness bundle** that still preserves where it came from.
5. **A stable-on-top workflow** above `ui_test`, `trybuild`, witness generation, and future compiler substrate.
6. **An issue-ready handoff artifact** that upstream teams can actually inspect.
7. **A truthful uncertainty layer** whenever mixed-lane behavior or diagnostic normalization make strong claims unsafe.

# Persona / who it’s for

- maintainers of trait-heavy libraries
- maintainers of proc-macro and derive-heavy ecosystems
- CI / release engineers comparing stable, beta, and nightly
- Rust team contributors triaging next-solver regressions
- tooling authors building semver, lint, rustdoc, or migration workflows above rustc behavior

# Users & user stories

- **Library maintainer**: “Compare our compile-fail corpus on stable and nightly `-Znext-solver=globally`, but tell me which differences are semantic and which are only diagnostics.”
- **Release engineer**: “Attach one small bundle to a nightly-regression issue instead of raw stderr blobs.”
- **Compiler contributor**: “Take this minimized case, but keep the lineage to the original corpus and flags.”
- **Tool author**: “Import solver-drift artifacts instead of reimplementing compiler-side heuristics.”
- **SemVer maintainer**: “When witness generation says a type-level compatibility question changed, preserve whether the drift was actually rooted in solver-lane behavior or only in normalization/diagnostics.”

# Prior art (and why it’s insufficient)

- `ui_test`, `trybuild`, and `compiletest_rs` are good corpus runners, but they do not standardize solver-lane truth, obligation classes, diagnostic normalization, or minimization lineage.
- `cargo-semver-checks` witness-generation work proves the *pattern* of using rustc as the decider, but it is aimed at SemVer breakage, not general solver-lane drift review.
- The compiler’s proof-tree and tracing substrate is powerful, but it is internal/compiler-facing and not itself a downstream workflow contract.
- The next-solver goal page and dev-guide notes explain why behavior can differ, but they do not give crate authors one portable artifact format for those differences.

What remains missing is a **solver-drift support bundle** above those ingredients.

# Design goals

1. **Lane-explicit** — every comparison must say which solver configuration actually ran.
2. **Outcome-first** — semantic result classes matter more than raw text diffs.
3. **Diagnostic-honest** — only call something diagnostic-only if normalization rules are recorded.
4. **Corpus-honest** — preserve whether a case was imported, adapted, generated, or reduced.
5. **Minimization-with-lineage** — reduced repros must stay connected to their source context.
6. **Stable-on-top** — avoid requiring internal rustc proof-tree APIs for the MVP.
7. **Import-friendly** — be able to ingest `ui_test`, `trybuild`, and witness-generation style corpora.

# Minimal artifact vocabulary (freeze early)

## 1. `comparison-lane.receipt`

This is the first missing truth.
A comparison should record:

- toolchain ids,
- channel (`stable`, `beta`, `nightly`),
- whether `-Znext-solver=globally` was used,
- whether the result is best classified as `legacy_only`, `coherence_default_only`, `global_preview`, or `mixed_unknown`,
- whether rustdoc/lints were in scope,
- target/edition/profile facts,
- and whether the lane is suitable for release gating versus preview-only testing.

## 2. `corpus-authority.receipt`

This answers where the case came from:

- imported from `ui_test`, `trybuild`, or `compiletest_rs`,
- handwritten case,
- generated witness crate,
- or minimized repro.

It also records whether expected stderr is authoritative, whether only pass/fail is authoritative, and whether the corpus was redacted or transformed.

## 3. `obligation-class.report`

This is the second missing truth.
A crate reviewer should not just see “case changed”.
They should see whether the change was about:

- trait-bound satisfaction,
- alias normalization,
- higher-ranked reasoning,
- coherence overlap,
- overflow / recursion / fixpoint behavior,
- opaque-type handling,
- or a still-unknown mixed bucket.

## 4. `diagnostic-normalization.receipt`

The dev guide is explicit that proof trees and canonicalization change how diagnostics are produced and interpreted.
So the crate must preserve:

- path remapping,
- note/help filtering,
- span elision,
- ordering normalization,
- and whether a “diagnostic-only” decision depends on those transforms.

## 5. `minimization-lineage.receipt`

This keeps reduced repros honest.
It should record:

- original case id,
- original corpus,
- reducers applied,
- dropped files/features/dependencies,
- preserved expectation class,
- and whether the minimized repro is still accepted as authoritative.

# Implementation shape in theory and practice

## Three evidence lanes

### 1. Corpus-run lane

Use `ui_test`, `trybuild`, or `compiletest_rs` style corpora and record normalized outcomes.
This is the stable-first default and the broadest adoption path.

### 2. Witness-generation lane

Use generated witness crates for hard type-level questions where direct surface diffs are insufficient.
This follows the pattern proven in `cargo-semver-checks` work, but here it remains one lane among several instead of the whole product.

### 3. Compiler-substrate lane

Optionally import extra debug substrate such as tracing or future proof-tree-facing diagnostics.
This is intentionally optional and should never be required for the MVP.

## Product shape

The crate should be two things:

1. a library for capturing, normalizing, classifying, and packaging solver-drift evidence;
2. a cargo subcommand for CI and issue-handoff workflows.

## Minimal types

```rust
pub enum SolverLaneKind {
    LegacyOnly,
    CoherenceDefaultOnly,
    GlobalPreview,
    MixedUnknown,
}

pub enum ObligationClass {
    TraitBound,
    AliasNormalization,
    HigherRanked,
    Coherence,
    OverflowOrFixpoint,
    OpaqueTypes,
    Unknown,
}

pub enum DriftClass {
    AcceptedToRejected,
    RejectedToAccepted,
    OverflowBehaviorChanged,
    DiagnosticOnly,
    ScopeChanged,
    ManualReviewRequired,
}
```

## Minimal functions

```rust
pub fn capture_comparison_lane(profile: &SolverProfile, run: &SolverRun) -> ComparisonLaneReceipt;
pub fn import_corpus_authority(corpus: &Path) -> CorpusAuthorityReceipt;
pub fn classify_obligation(case: &CaseObservation) -> ObligationClassReport;
pub fn normalize_diagnostics(raw: &RawDiagnostics, policy: &NormalizationPolicy) -> DiagnosticNormalizationReceipt;
pub fn diff_solver_runs(old: &SolverRun, new: &SolverRun) -> SolverDriftDiff;
pub fn reduce_case(case: &CaseObservation) -> MinimizationLineageReceipt;
```

# MVP surface

- import one corpus family (`ui_test` or `trybuild`)
- compare two configured runs
- emit the six first-class artifacts
- support a minimal outcome taxonomy
- package one `*.solverbundle.zip`

# Path to boring stability

## 0.1

- one corpus adapter
- one toolchain-pair comparison mode
- narrow lane taxonomy
- narrow obligation taxonomy
- redaction-aware bundle export

## 0.2

- second corpus adapter
- witness-generation lane
- minimization helpers
- CI annotations / GitHub artifact export

## 1.0

- stable schemas for the first-class receipts
- strong lineage guarantees
- curated public corpus of representative solver-drift cases
- optional adapters for richer compiler substrate if it becomes practical

# Conformance & fixtures

The fixture set should include at least:

1. **coherence default is not global parity** — stable coherence lane changed, but full solver parity is not proven.
2. **overflow classification changes with next solver** — preserve that overflow behavior can move from eager fatal handling to classifiable outcome.
3. **diagnostic text shifts after normalization** — preserve that a “diagnostic-only” claim depends on recorded normalization policy.
4. **minimized repro keeps corpus lineage** — preserve which original UI/trybuild case was reduced.
5. **handwritten witness is not interchangeable with imported corpus authority** — preserve different trust posture.

# Security / safety model

- Never claim semantic equivalence from diagnostic similarity alone.
- Never claim “new solver everywhere” when only coherence-default behavior changed.
- Preserve exact toolchain ids and flags in every comparison.
- Support path and crate-name redaction for shared bundles.
- Mark reduced repros as derivative artifacts with explicit lineage.

# Maintenance & governance plan

- Version the lane taxonomy carefully.
- Freeze the normalization vocabulary before expanding obligation classes too far.
- Keep compiler-substrate adapters optional.
- Maintain a public example corpus spanning normalization, coherence, HRTBs, overflow, opaques, and derive-heavy cases.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 27/30**

# Minimum lovable MVP

A library and cargo subcommand that run one trait-heavy compile-fail corpus under two configured solver lanes, classify the differences conservatively, and emit:

- one `comparison-lane.receipt.json`,
- one `corpus-authority.receipt.json`,
- one `obligation-class.report.json`,
- one `diagnostic-normalization.receipt.json`,
- one `solver-drift.diff.json`,
- and one shareable `*.solverbundle.zip`.

# De-risk plan

1. Start with lane truth and obligation classes, not internal proof trees.
2. Support one corpus format first.
3. Keep semantic-vs-diagnostic-vs-scope buckets few and explainable.
4. Validate usefulness on one trait-heavy public crate before broadening the taxonomy.
5. Only add deeper compiler-substrate import once the first receipt family is trusted.

# Non-goals

- Not a trait solver implementation.
- Not a promise to explain every solver change root cause.
- Not a replacement for compiler issue triage.
- Not a generic rustc log parser.
- Not a borrow-checker or Polonius migration kit.
- Not a semver checker, though it should compose with semver witness workflows.

# Open questions

- What is the smallest useful obligation taxonomy that still helps real maintainers?
- How should mixed stable/nightly/coherence-default comparisons be summarized in CI without overclaiming?
- Which minimization invariants matter most for upstream issue filing?
- When proof-tree-facing substrate becomes more accessible, what is the least invasive way to import it?

# Sources

- Next-generation trait solver goal: https://rust-lang.github.io/rust-project-goals/2025h2/next-solver.html
- Rust release notes (1.84 coherence change and later next-solver fixes): https://doc.rust-lang.org/beta/releases.html
- GSoC 2025 witness generation in cargo-semver-checks: https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- rustc-dev-guide, significant changes and quirks: https://rustc-dev-guide.rust-lang.org/solve/significant-changes.html
- rustc-dev-guide, proof trees: https://rustc-dev-guide.rust-lang.org/solve/proof-trees.html
- `ui_test`: https://docs.rs/ui_test
- `trybuild`: https://crates.io/crates/trybuild
- `compiletest_rs`: https://crates.io/crates/compiletest_rs
