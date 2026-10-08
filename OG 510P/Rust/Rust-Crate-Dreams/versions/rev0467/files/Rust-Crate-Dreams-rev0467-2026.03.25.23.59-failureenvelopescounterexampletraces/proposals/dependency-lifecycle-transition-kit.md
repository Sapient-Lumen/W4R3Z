---
id: P-0535
title: Dependency Lifecycle Transition Kit — criticality lanes, abstraction seams, replacement-readiness, and lifecycle drift bundles
status: idea
domains: [cargo, dependencies, safety-critical, enterprise, maintenance, architecture, supply-chain]
last_reviewed: 2026-03-22
evidence:
  - https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
  - https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  - https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  - https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
  - https://doc.rust-lang.org/cargo/commands/cargo-tree.html
  - https://doc.rust-lang.org/cargo/reference/resolver.html
  - https://doc.rust-lang.org/cargo/reference/rust-version.html
  - https://doc.rust-lang.org/cargo/reference/overriding-dependencies.html
  - https://doc.rust-lang.org/cargo/reference/config.html
  - https://doc.rust-lang.org/cargo/reference/source-replacement.html
  - https://doc.rust-lang.org/cargo/guide/cargo-toml-vs-cargo-lock.html
---

# Problem

Rust teams increasingly have a real **dependency lifecycle**, but almost no shared artifact for it.

The January 2026 safety-critical write-up finally says the quiet part plainly: teams often **use crates early, track them carefully, and then shrink or replace them for higher-criticality parts**; other teams avoid third-party crates entirely in the highest-assurance lanes, or hide them behind abstraction layers and plan to replace them later.
That is not a fringe workflow anymore. It is an ecosystem reality.

The substrate around that reality is much better than it used to be:

- Cargo can expose machine-readable workspace and resolved-dependency structure through `cargo metadata`.
- `cargo tree` can show the graph people actually have, not the graph they think they have.
- the resolver and `Cargo.lock` already provide a concrete dependency-selection and freezing surface,
- `rust-version` now participates in dependency selection and `cargo add` can already bias toward versions compatible with the declared Rust floor,
- Cargo patch/replace/path overrides already give maintainers the escape hatches they use during migration,
- Cargo config docs now make it explicit that config-file patches are often local or generated and can override manifest patches,
- Cargo source replacement is now documented clearly enough to say when a vendor or mirror route is still supposed to be the *same code* rather than a divergent fork,
- Cargo.toml vs Cargo.lock docs keep broad dependency intent distinct from the exact realized graph,
- and crates.io now publishes stronger trust substrate like a Security tab, Trusted Publishing Only Mode, source lines of code, and `pubtime`.

But those pieces still do **not** answer the questions product teams, platform teams, and regulated adopters actually ask:

- which dependencies are allowed in which product or criticality lane,
- which ones are direct in the core versus isolated behind a trait / process / FFI / protocol seam,
- which ones are intentionally temporary,
- which ones are pinned, vendored, forked, or slated for internal replacement,
- which exceptions were consciously accepted,
- and whether the latest release quietly moved a third-party crate into a more sensitive part of the system.

That means the missing crate is **not** another vulnerability scanner, **not** another crate-ranking site, **not** another graph visualizer, and **not** a universal “best dependencies” recommender.

The sharper missing contribution is a **Dependency Lifecycle Transition Kit**: a crate and Cargo-adjacent tool that turns dependency use over time into a reviewable contract with explicit **criticality lanes**, **abstraction seams**, **replacement readiness**, and **lifecycle drift**.

# Main judgment

A worthy crate here should let another team answer four boring but decisive questions without reading issue trackers and architecture folklore by hand:

1. **Where may third-party crates live today?**
2. **What containment or abstraction seam makes later replacement realistic?**
3. **Which dependencies are expected to freeze, fork, vendor, internalize, or disappear as criticality rises?**
4. **What changed between releases that widened or tightened that posture?**

That is more valuable than another score-only trust tool.

# Sharper reading after the latest 2026 signals

The strongest recent signals line up unusually well:

1. The safety-critical post explicitly asks for reusable **dependency lifecycle patterns** instead of more folklore.
2. The Vision Doc work says Rust should expand crate-side **supportive interfaces** and help users navigate the ecosystem better.
3. The 2025 State of Rust survey says online docs remain the preferred canonical reference, which means any lifecycle story should produce compact review artifacts, not just code hooks.
4. Crates.io is now publishing more trust-adjacent facts (`Security` tab, `Trusted Publishing Only Mode`, `pubtime`, SLOC), but those facts still do not tell you **where a dependency is allowed to live inside your system architecture**.

So the next worthwhile crate is not a raw signal source.
It is the contract layer above those signals.

# What it provides

Working build sketch: `meta/dependency-lifecycle-transition-product-plan-2026-03-22.md`.

- `dependency-lifecycle.toml` — declares lifecycle lanes, criticality classes, allowed third-party posture, transition goals, exception policy, and review zones.
- `dependency-lane.snapshot.json` — normalized map of workspace packages and resolved dependencies into lifecycle lanes such as `prototype`, `production_pinned`, `contained`, `replace_planned`, `vendor_frozen`, `owned_fork`, or `internal_only`.
- `criticality-boundary.report.json` — shows where third-party crates cross into higher-criticality packages, binaries, services, or firmware images.
- `abstraction-seam.receipt.json` — records the boundary that makes later replacement plausible: trait seam, process boundary, IPC/protocol seam, FFI seam, codegen seam, facade module, or `manual_review_required`.
- `replacement-readiness.report.json` — classifies whether a dependency is `direct_coupling`, `data_model_coupled`, `api_facade_present`, `protocol_seamed`, `process_isolated`, `fork_ready`, `vendor_ready`, or `manual_review_required`.
- `transition-plan.manifest.json` — concrete path from today’s lane to the intended next lane, including exit criteria, blockers, and owner notes.
- `override-authority.receipt.json` — records whether the current route is declared in checked-in manifest policy, checked-in config, generated config, local config, CI-only config, or manual process, and how reviewable that makes the transition.
- `dependency-exception.ledger.json` — typed waivers for cases where a high-criticality lane still imports an outside crate directly.
- `exception-reevaluation.report.json` — classifies whether those waivers are still active, approaching review, expired, stale, exit-ready, or manual-review-only.
- `lifecycle-drift.diff.json` — compares two snapshots or releases and classifies `criticality_crossing_added`, `seam_removed`, `replacement_improved`, `replacement_regressed`, `temporary_dependency_became_sticky`, `fork_or_vendor_posture_changed`, and `manual_review_required`.
- `imported-signal.receipt.json` — records which external trust/support facts were imported from crates.io or other adjacent tools and keeps them separate from architectural decisions.
- `signal-freshness.report.json` — records whether imported external facts are still fresh enough to support the current lifecycle decision.
- `selection-anchor.receipt.json` — records what currently makes the realized dependency route hold: lockfile, root patch, config-only patch, source replacement, git rev pin, or manual operator step, plus what would invalidate that anchor.
- `reresolution-risk.report.json` — classifies what happens on a clean resolve, lock refresh, or toolchain-floor change, including `current_lock_only`, `local_patch_not_shared`, `yanked_but_locked`, `rust_version_sensitive_selection`, or `manual_review_required`.
- `transition-summary.md` — short operator/reviewer-facing explanation of current posture and next planned moves.
- `cargo dep-lifecycle capture` — emit a lifecycle bundle from workspace policy plus current dependency graph.
- `cargo dep-lifecycle doctor` — flag direct third-party use in restricted lanes, missing seams, stale transition plans, lock-only routes, or local-only anchors being over-read as shared lifecycle policy.
- `cargo dep-lifecycle diff <old> <new>` — compare release or branch posture.
- `*.deplifecycle.zip` — portable artifact for design review, safety review, and release approval.

# What the crate should provide other people

1. **A way to separate crate choice from crate placement.**
   A crate may be acceptable in a prototype or peripheral service, but not in a control core or safety partition.
2. **A seam receipt, not a vague aspiration.**
   “We can replace it later” should mean there is a named trait/process/FFI/protocol seam with observable consumers.
3. **A transition plan, not a static score.**
   Teams need to say whether a dependency is being retained, pinned, frozen, forked, vendored, or designed out.
4. **A drift report for architecture posture.**
   It should be easy to see when a release accidentally moved a dependency into a more sensitive lane.
5. **A clean boundary between imported trust facts and local policy.**
   Security tabs, publishing posture, and SLOC can inform a decision without becoming the decision.
6. **A way to tell what currently anchors the posture.**
   A checked-in lockfile, a root manifest patch, a local config patch, and a source replacement are not the same kind of transition anchor.
7. **A way to tell whether the transition is really shared.**
   A local config patch, a generated config override, and a checked-in manifest declaration are not the same lifecycle claim.
8. **A way to tell whether the current green build survives re-resolution.**
   Yanks, lock refreshes, and `rust-version`-sensitive selection can change posture later even when today still builds.
9. **A way to tell whether the supporting context is still current.**
   Imported signals and typed waivers need explicit refresh and reevaluation posture, not silent carry-forward.
10. **A review bundle suitable for long-lived products.**
   The output should survive CI, design review, and handoff to downstream users or auditors.

# Persona / who it’s for

- maintainers of mixed-criticality Rust workspaces
- platform architects planning “use now, replace later” dependency strategy
- safety-critical and regulated adopters
- enterprise teams trying to shrink direct dependency exposure over time
- reviewers who need one honest artifact instead of folklore

# Users & user stories

- **Platform architect:** “Show me which third-party crates still reach our high-criticality core directly.”
- **Safety lead:** “Tell me which external crates are contained behind process or FFI boundaries and which are not.”
- **Maintainer:** “We forked this crate for stability. Record that as a lifecycle move, not just a git URL accident.”
- **Reviewer:** “This release added a new dependency in the diagnostics binary. Fine. Did it also leak into the control daemon?”
- **Downstream integrator:** “Give me one document that says what is temporary, what is pinned, and what is planned for replacement.”

# Prior art (and why it’s insufficient)

- Cargo already exposes dependency graphs and resolved workspace structure via `cargo tree` and `cargo metadata`.
- Cargo resolver and lockfiles already give teams a real freezing surface.
- `rust-version` gives packages a support floor and can influence dependency selection.
- Cargo patch/replace/path overrides already let teams test fixes, use unpublished versions, or temporarily redirect sources.
- crates.io now offers stronger trust/support context such as security advisories, trusted publishing posture, SLOC, and publication time.
- The archive already has adjacent lanes:
  - **P-0036 MSRV Workspace Lab** for version-floor truth,
  - **P-0017 Trust Lens** for trust/risk signals,
  - **P-0515 Crate Offramp Pack Kit** for leaving one crate,
  - **P-0011 Crate Health Contract Kit** for maintenance/support posture.

What remains missing is the **architecture-level transition contract** that says how dependencies are supposed to move through a system over time.

# Design goals

1. **Lifecycle-first** — focus on movement over time, not just one static risk snapshot.
2. **Architecture-aware** — a dependency’s meaning depends on where it lives.
3. **Seam-explicit** — replacement plans must name a real seam.
4. **Policy/import split** — keep imported external signals distinct from local architectural policy.
5. **Diffable** — the release-to-release change story is as important as the current state.
6. **Cargo-adjacent** — import Cargo graph facts instead of replacing Cargo.
7. **Conservative** — prefer `manual_review_required` over fake certainty about replaceability.

# MVP surface

- Minimal types: `DependencyLifecyclePolicy`, `DependencyLaneSnapshot`, `CriticalityBoundaryReport`, `AbstractionSeamReceipt`, `ReplacementReadinessReport`, `TransitionPlanManifest`, `DependencyExceptionLedger`, `LifecycleDriftDiff`, `ImportedSignalReceipt`, `TransitionSummary`
- Minimal functions:
  - `load_dependency_lifecycle_policy()`
  - `capture_dependency_lane_snapshot()`
  - `classify_criticality_boundaries()`
  - `capture_abstraction_seams()`
  - `classify_replacement_readiness()`
  - `diff_lifecycle_posture()`
  - `write_deplifecycle_bundle()`
- Feature flags:
  - `serde`
  - `cargo-metadata`
  - `cargo-tree-import`
  - `html-summary`
  - `ci`

# Compatibility story

- Works above today’s Cargo graph and override substrate.
- Can import `cargo metadata` and `cargo tree` output instead of re-resolving dependencies itself.
- Can incorporate `rust-version`, lockfile posture, and yank/re-resolution risk as lifecycle facts without becoming another MSRV solver or update-policy engine.
- Can import crates.io or Trust-Lens-style signals as optional context while keeping architectural policy authoritative.
- Should remain useful even if Cargo later grows richer dependency-planning support, because the explicit **criticality lane / seam / replacement plan** layer would still be valuable.

# Conformance & fixtures

- One fixture where a prototype CLI uses many third-party crates but a flight-control or control-core package must keep them outside the restricted lane.
- One fixture where a crate is acceptable only behind a trait facade and the seam receipt must prove that facade exists.
- One fixture where a dependency moves from crates.io to an owned fork or vendored source as criticality rises.
- One fixture where a release accidentally adds a direct dependency into a restricted lane and the drift report flags it.
- Goldens for `criticality_crossing_added`, `seam_present`, `seam_missing`, `replacement_improved`, `replacement_regressed`, `vendor_or_fork_transition`, and `manual_review_required`.

# Path to boring stability

- Freeze the artifact vocabulary before trying to auto-infer clever architecture claims.
- Keep current placement, imported signals, and future transition plans separate.
- Treat seam capture as first-class from `0.1`.
- Prefer explicit owner notes and typed waivers over secret policy exceptions.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 3/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A crate and cargo subcommand that load one `dependency-lifecycle.toml`, import one workspace graph, emit one lane snapshot, one criticality-boundary report, one seam receipt set, and one lifecycle drift diff suitable for code review.

# De-risk plan

1. Start with policy + snapshot + diff, not automated “best replacement” recommendations.
2. Make seam capture explicit before attempting fancy graph heuristics.
3. Keep imported signal facts optional and visibly second-order.
4. Add fork/vendor/internalization lanes only after direct-vs-contained posture feels stable.

# Non-goals

- Not a vulnerability scanner.
- Not a global crate-ranking service.
- Not a full architecture modeling language.
- Not a promise to automatically rewrite or replace dependencies.
- Not a claim that “uses fewer crates” is always better.

# Architecture & API sketch

```rust
pub enum LifecycleLane {
    Prototype,
    ProductionPinned,
    Contained,
    ReplacePlanned,
    VendorFrozen,
    OwnedFork,
    InternalOnly,
    ManualReviewRequired,
}

pub enum SeamKind {
    TraitFacade,
    ProcessBoundary,
    FfiBoundary,
    ProtocolBoundary,
    FacadeModule,
    CodegenBoundary,
    ManualReviewRequired,
}

pub struct DependencyLifecyclePolicy {
    pub restricted_packages: Vec<String>,
    pub allowed_lanes_by_package: Vec<(String, Vec<LifecycleLane>)>,
    pub seam_expectations: Vec<(String, SeamKind)>,
}

pub fn capture_dependency_lane_snapshot(policy: &DependencyLifecyclePolicy) -> anyhow::Result<DependencyLaneSnapshot>;
pub fn classify_criticality_boundaries(snapshot: &DependencyLaneSnapshot) -> CriticalityBoundaryReport;
pub fn classify_replacement_readiness(snapshot: &DependencyLaneSnapshot) -> ReplacementReadinessReport;
pub fn diff_lifecycle_posture(old: &DependencyLaneSnapshot, new: &DependencyLaneSnapshot) -> LifecycleDriftDiff;
```

# Why this would count as an epic crate contribution

Because it would give other people a new kind of boring truth Rust teams do not currently share well:
**how third-party dependencies are supposed to mature, narrow, and exit as systems get more serious**.
That is a real ecosystem need, it reuses today’s Cargo/crates.io substrate instead of competing with it, and it fills a gap that current trust/MSRV/health/off-ramp tools only touch from the sides.
