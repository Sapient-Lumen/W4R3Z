---
id: P-0244
title: SemVer API Diff Evidence Kit — witness plans, public-API snapshots, and publish-ready breakage evidence
status: idea
domains: [cargo, semver, release, api-design, devtools, reliability]
last_reviewed: 2026-03-16
evidence:
  - https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
  - https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
  - https://doc.rust-lang.org/cargo/reference/semver.html
  - https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  - https://github.com/obi1kenobi/cargo-semver-checks
  - https://github.com/cargo-public-api/cargo-public-api
---

# Problem

The archive’s older framing for this proposal was too narrow.
The missing value is not just a stable diff-friendly public-API IR.
By early 2026, the sharper frontier is a **portable SemVer evidence layer** that can sit beneath Cargo integration work.

Official Rust signals now make that concrete:

- `cargo-semver-checks` is on an explicit path toward the `cargo publish` workflow.
- The Rust project is treating **breaking-change detection** as part of the 2026 “Secure your supply chain” theme.
- Current blockers are not merely cosmetic lint additions; they include **type-precision problems**, **cross-crate item identity**, and the need for witness-based checking when syntactic diffs are not enough.
- The Rust project has now publicly described **witness program generation** as the plan for many hard type-related cases, and a 2025 GSoC project delivered a proof-of-concept that supports multiple crate origins and multiple rustdoc JSON formats.

That changes what a worthy crate should do.
The missing crate is no longer “one more semver checker.”
It is the boring, reviewable artifact that says:

1. what the old and new public surfaces were,
2. which items were matched across versions,
3. which potential breaks required a witness program,
4. what Cargo / rustdoc / compiler facts were imported,
5. and which verdicts are solid evidence versus still-manual review.

The missing crate is a **SemVer API Diff Evidence Kit**.

# Sharper reading after the 2025H2 / 2026 updates

The 2025H2 goal work and later 2026 framing make this proposal stronger and more concrete than when it first entered the archive.

1. Cargo wants semver checks on the publish path, which raises the bar from “useful linter” to “trustworthy release evidence.”
2. The blockers explicitly include cases where syntactic API diffs are insufficient because implied bounds and type semantics matter.
3. The current plan for those hard cases is to generate **witness programs** and let `cargo check` / rustc answer the compatibility question.
4. The GSoC witness-generation work shows this will need to survive real-world crate origins (`crates.io`, path, git) and multiple rustdoc JSON versions.
5. That means the ecosystem still needs a small stable contract above evolving internal formats and publish-flow UX.

So the missing contribution is not a Cargo replacement.
It is the **witness plan / evidence bundle / result vocabulary** that other tools, release bots, and humans can share.

# Main judgment

A worthy crate here should provide a receiver-facing answer to:

1. **What public items were compared, and how were they matched across versions?**
2. **Which possible breakages were decided by direct rule evaluation versus generated witness programs?**
3. **What exact compiler/Cargo/rustdoc inputs produced the verdict?**
4. **Which verdicts are confident enough for automation, and which still need review?**
5. **What source identity did each compared crate actually have (registry, git, path, revision)?**

That is more durable than another bespoke semver report format.

# What it provides

- `semver-policy.toml` — declares baseline/new crate locations, selected semver profile, allowed waivers, witness-generation posture, and redaction rules.
- `public-api.snapshot.json` — normalized snapshot of one version’s public surface: item identity, visibility, reexports, type-shape summaries, and source-origin metadata.
- `api-match.report.json` — how old and new items were paired, split, renamed, or left ambiguous.
- `witness-plan.json` — every candidate compatibility question that should be decided by witness compilation rather than syntax alone.
- `witness-result.json` — compile results, selected toolchains, environment facts, and whether the witness provided decisive evidence.
- `semver-judgment.report.json` — final rule/witness verdicts with severity, rationale, confidence, and required manual review.
- `semver.receipt.json` — exact tool versions, imported substrate (`cargo-semver-checks`, rustdoc JSON, `cargo-public-api`, direct rustc/Cargo checks), and schema versions.
- `semver-waivers.toml` — structured owner/rationale/expiry data for intentional breakage or temporarily accepted ambiguity.
- `cargo semver-evidence capture` — freeze old/new snapshots, witness plans, and judgment reports into one bundle.
- `cargo semver-evidence plan-witnesses` — explain which candidate breaks need witness compilation and why.
- `cargo semver-evidence replay-witness` — rerun one witness case deterministically enough for review.
- `cargo semver-evidence diff <old> <new>` — compare two evidence bundles and classify rule drift, witness drift, or source-identity drift.
- `*.semverbundle.zip` — portable artifact for PR review, release approval, or future cargo-publish integration experiments.

# What the crate should provide other people

1. **One portable SemVer evidence bundle** instead of ephemeral CLI output.
2. **A witness-plan vocabulary** that lets reviewers see why a case needed compilation-based checking.
3. **A stable import layer** above multi-version rustdoc JSON and evolving tool internals.
4. **A source-identity receipt** so path/git/registry comparisons stay honest.
5. **A conservative publish-facing judgment report** that can say `manual_review_required` without pretending to know more than it does.
6. **A reusable substrate** for future Cargo integration, release bots, and public-API readiness bundles.

# Persona / who it’s for

- maintainers of widely used public crates
- semver stewards and release engineers
- tooling authors building publish guards or release review bots
- ecosystem researchers studying accidental breakage
- workspace owners who need durable compatibility evidence, not just one CI log

# Users & user stories

- **Library maintainer**: “Show me the concrete evidence for why this release is minor-safe or major-breaking.”
- **Release reviewer**: “Point me at the few cases that needed witness compilation and tell me how they ended.”
- **Tool author**: “Consume one stable receipt instead of scraping semver-check logs and unstable rustdoc details.”
- **Researcher**: “Compare breakage evidence across releases without reverse-engineering old tool outputs.”
- **Cargo contributor**: “Experiment with publish-path SemVer gating using one compact bundle rather than re-running every analyzer ad hoc.”

# Prior art (and why it’s insufficient)

- `cargo-semver-checks` is the most important substrate in this space and is on an explicit path toward Cargo integration.
- `cargo-public-api` is useful for public-surface inventory and diffs.
- Cargo’s SemVer guidance is the policy baseline many people already reason from.
- The Rust project’s witness-generation work is creating a path through hard type-shape cases.

What remains missing is a **stable, receiver-facing evidence layer** that joins those pieces.
That is not the same as replacing `cargo-semver-checks`, and it is not the same as the broader release-review bundle in **P-0483**.
This crate is narrower: it is the foundational **SemVer evidence substrate**.

# Design goals

1. **Evidence-first** — optimize for reviewable proof, not just pass/fail UI.
2. **Witness-aware** — treat witness generation as a first-class lane, not an implementation detail.
3. **Source-identity-honest** — registry/path/git provenance must stay explicit.
4. **Importer-friendly** — prefer importing existing tool outputs over reimplementing everything.
5. **Confidence-explicit** — a real `manual_review_required` lane is part of the design.
6. **Bundle-small** — preserve high-value facts, not giant raw compiler dumps by default.
7. **Not a release dashboard** — stay separate from docs debt / public dependency / waiver aggregation bundles.

# MVP surface

- Minimal types: `SemverPolicy`, `PublicApiSnapshot`, `ApiMatchReport`, `WitnessPlan`, `WitnessResult`, `SemverJudgmentReport`, `SemverReceipt`, `SemverBundle`
- Minimal functions:
  - `capture_public_api_snapshot()`
  - `match_public_items()`
  - `plan_witness_cases()`
  - `run_witness_case()`
  - `judge_semver_candidates()`
  - `write_semver_receipt()`
  - `diff_semver_bundles()`
- Feature flags:
  - `cargo`
  - `serde`
  - `cargo-semver-checks`
  - `cargo-public-api`
  - `nightly-rustdoc`
  - `witnesses`
  - `redaction`

# Compatibility story

- Stable-first mode should still work by importing available public-API and semver outputs.
- Higher-fidelity mode may use nightly rustdoc JSON and witness generation when available.
- Must preserve which verdicts came from direct lint/rule imports and which came from generated witness programs.
- Must remain useful whether compared crates come from `crates.io`, a local path, or a git revision.
- Should stay valuable even if `cargo-semver-checks` merges into Cargo, because the evidence bundle remains a distinct coordination artifact.

# Conformance & fixtures

- `impl_trait_parameter_witness` — syntactic diff is not enough; witness compilation decides compatibility.
- `implied_bound_precision` — old/new public API appears similar until implied `'static` / `?Sized` semantics are considered.
- `cross_crate_item_identity` — item matching must preserve the real crate/version/source identity for reexport-heavy graphs.
- Goldens for `major_break_confirmed`, `compatible_after_witness`, `precision_gap_manual_review`, and `source_identity_ambiguous`.

Current implementation-shaping target:
- freeze `public-api.snapshot.json`, `witness-plan.json`, `witness-result.json`, and `semver-judgment.report.json`
- prove them on three scenario bundles before expanding the waiver and publish-gating surface

# Path to boring stability

- Freeze the evidence vocabulary before broad automation.
- Treat witness plans/results as first-class artifacts, not temporary debug files.
- Keep imported tool output and normalized bundle output distinct.
- Start with conservative judgments and explicit review-required paths.
- Delay changelog generation and policy bots until the evidence bundle feels trustworthy.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 5/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 27/30**

# Minimum lovable MVP

A library and cargo-adjacent tool that capture old/new public API snapshots, map matching items, generate witness plans for the cases rules cannot decide confidently, run those witnesses, and emit one portable SemVer evidence bundle with explicit confidence and source-origin facts.

# De-risk plan

1. Start by importing `cargo-semver-checks` and `cargo-public-api` outputs rather than replacing them.
2. Freeze witness-plan and witness-result schemas before trying to automate publish decisions.
3. Validate on one simple syntactic break, one witness-required type-shape break, and one cross-crate/reexport-heavy case.
4. Preserve exact/manual-review boundaries everywhere.

# Non-goals

- Not a replacement for `cargo-semver-checks`.
- Not a full release-readiness dashboard.
- Not a general behavioral compatibility tester.
- Not a promise to explain every breakage with zero ambiguity.
- Not a changelog generator.

# Architecture & API sketch

```rust
pub enum SemverDecision {
    Compatible,
    Breaking,
    ManualReviewRequired,
}

pub fn capture_public_api_snapshot(input: &CrateInput) -> Result<PublicApiSnapshot>;
pub fn plan_witness_cases(old: &PublicApiSnapshot, new: &PublicApiSnapshot) -> Result<WitnessPlan>;
pub fn run_witness_case(case: &WitnessCase, toolchain: &ToolchainRef) -> Result<WitnessResult>;
pub fn judge_semver_candidates(
    old: &PublicApiSnapshot,
    new: &PublicApiSnapshot,
    witness: Option<&WitnessResult>,
) -> Result<SemverJudgmentReport>;
```

Bundle draft: `semver-policy.toml`, `public-api.snapshot.old.json`, `public-api.snapshot.new.json`, `api-match.report.json`, `witness-plan.json`, `witness-result.json`, `semver-judgment.report.json`, `semver.receipt.json`, `semver-waivers.toml`, `notes.md`.

# Security / safety model

- Treat imported analyzer output as untrusted input.
- Preserve exact toolchain and origin information for every witness result.
- Support redaction of private paths and unreleased crate names without redacting semantic conclusions.
- Never claim a witness was decisive if the environment/toolchain facts make replay dubious.
- Keep manual-review results visible rather than collapsing them into optimistic “compatible” outcomes.

# Maintenance & governance plan

- Track Cargo integration work for `cargo-semver-checks`, witness-generation evolution, and rustdoc JSON changes.
- Keep schemas small, explanation-heavy, and versioned.
- Maintain fixtures for implied bounds, `impl Trait`, cross-crate identities, and multi-origin inputs.
- Publish clear compatibility-policy profiles rather than letting ad hoc waivers dominate.

# Milestones

## 0.1
- public API snapshot capture/import
- witness-plan schema
- semver judgment report

## 0.2
- witness execution + receipts
- source-origin handling for path/git/crates.io
- diffable bundles

## 1.0
- stable evidence schema
- curated fixture corpus
- release-bot / publish-flow adapters

# Open questions

- What is the smallest useful witness-plan taxonomy that still helps reviewers?
- Which source-identity facts are mandatory for trustworthy cross-crate item matching?
- How much raw compiler output should the default bundle retain versus reference indirectly?
- What is the sharpest boundary between this crate and **P-0483 Public API Readiness Bundle Kit**?

# Sources

- Continue resolving `cargo-semver-checks` blockers for merging into cargo: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- Google Summer of Code 2025 results (`cargo-semver-checks` witness generation work): https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- Cargo SemVer Compatibility reference: https://doc.rust-lang.org/cargo/reference/semver.html
- Rust in 2026 flagships: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- `cargo-semver-checks`: https://github.com/obi1kenobi/cargo-semver-checks
- `cargo-public-api`: https://github.com/cargo-public-api/cargo-public-api
