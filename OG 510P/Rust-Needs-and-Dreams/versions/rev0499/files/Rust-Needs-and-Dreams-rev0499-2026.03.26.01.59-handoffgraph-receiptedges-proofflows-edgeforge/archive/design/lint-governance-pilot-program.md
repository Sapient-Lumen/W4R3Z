# Design: Lint Governance Pilot Program

## Purpose
Turn the broader **Lint Governance Stack** into an executable rollout instead of leaving it as a good but underspecified contract idea.

The archive already had the right broad thesis: Rust needs versioned lint profiles, baselines, reports, and fix packs.
What it did **not** yet answer clearly enough is:
- which lint-governance exports should be standardized first,
- how stable manifest lint policy should relate to observed reports,
- when fix packs become governed edit waves instead of raw suggestions,
- how Cargo-native warning/report lanes fit without swallowing the stack,
- and what counts as a successful pilot instead of just a nicer lint CI job.

A worthy contribution here is not just `cargo lintpack check`.
It is a ranked pilot plan that proves lint artifacts survive real workspace inheritance, debt rollouts, fix review, Cargo imports, and policy handoff without flattening intent, findings, and edits into one blob.

## References (signals)
- Rust’s 2026 flagships keep safety-critical lints in Clippy on the roadmap, which means lint posture is now tied to assurance-oriented consumers rather than only convenience.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo’s manifest and workspace docs make `[lints]` and `[workspace.lints]` stable review surfaces as of Rust 1.74, with explicit inheritance via `[lints] workspace = true`.
  https://doc.rust-lang.org/cargo/reference/manifest.html#the-lints-section
  https://doc.rust-lang.org/cargo/reference/workspaces.html
- Cargo’s unstable features already include `[lints.cargo]`, meaning Cargo-native lint families are being designed for the same configuration plane rather than an entirely separate one.
  https://doc.rust-lang.org/cargo/reference/unstable.html#lintscargo
- `cargo report` already standardizes a machine-usable report path for future incompatibilities. That means Cargo-side warning families already have a report consumer lane even though the broader lint-governance stack does not yet exist.
  https://doc.rust-lang.org/cargo/commands/cargo-report.html
  https://doc.rust-lang.org/cargo/reference/future-incompat-report.html
- `cargo fix` is still single-configuration and edition migrations often require multiple passes across features, targets, or packages; the Cargo 1.90 development report says its current architecture also makes selective or interactive application hard. That is direct evidence that fix suggestions need a governed handoff layer rather than assuming “autofix” is the whole solution.
  https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
  https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/

## Design principles
1. **Manifest intent first, CI failure second.** Start with exportable selected policy, not just observed breakage.
2. **Baselines are debt, not invisibility cloaks.** Debt must stay reviewable, expirable, and diffable.
3. **Fixes stay separate from findings.** Suggested edits, selected edits, and verified edits are different artifacts.
4. **Cargo-native warning lanes are imported companions.** Future incompatibility and Cargo-native lints should join the evidence story without swallowing it.
5. **Consumers must stay explicit.** CI, release, migration, and safety consumers should declare what they import and what they may conclude.
6. **Graduation requires a real handoff.** A pilot succeeds only when another workflow consumes the artifacts without bespoke scraping.

## Artifact family

### 1. `lint-pilot-brief/v0`
Why a lint-governance lane is being piloted.

Should record:
- pilot id and summary
- subject family (`profile-lock`, `baseline-drift`, `fixpack-review`, `cargo-import`, `consumer-handoff`)
- why this lane matters now
- intended consumers and action paths
- why the pilot is tractable now

### 2. `lint-policy-lock/v0`
The selected lint intent for the pilot.

Should record:
- manifest/workspace sources of truth
- expanded group locks and engine versions
- inheritance posture and override rules
- package/path/target selectors
- whether Cargo-native lint families are in scope

Design rule: **this is not an observed finding report**.
It records intended policy and its locked expansion.

### 3. `lint-consumer-handoff/v0`
How a downstream consumer uses lint artifacts.

Should record:
- imported report/baseline/fixpack artifacts
- whether policy or human review is also required
- what local thresholds or waivers the consumer adds
- what conclusions the consumer must not claim

### 4. `lint-pilot-scorecard/v0`
Decides whether the pilot works.

Should ask:
- did the pilot keep selected policy, observed findings, debt posture, and applied edits distinct?
- did at least one consumer use it without bespoke scraping?
- did workspace inheritance and group expansion remain reviewable?
- did fix suggestions stay reviewable instead of silently auto-applied?
- did the lane improve explainability without inventing a cleanliness score?
- does widening the pilot still look justified?

### 5. `lint-pilot-pack/v0`
Bundle for review and reuse:
- pilot brief
- policy lock
- lint report / baseline / diff attachments
- optional fixpack and apply receipt
- consumer handoff
- scorecard and references

## Ranked first pilots

### 1) Workspace/profile-lock lane
**Why first**
- Stable `[lints]` and `[workspace.lints]` already make selected policy reviewable.
- It proves that lint governance begins with declared posture and inheritance, not only with whatever CI emitted.
- It gives repos a durable subject for later baseline and consumer work.

**Core artifacts**
- `lint-profile/v0`
- `lint-policy-lock/v0`
- optional `lint-pack/v0`

**Primary consumers**
- workspace maintainers
- CI configuration review
- migration planning

### 2) Baseline-drift / debt-budget lane
**Why second**
- This is where lint governance becomes more than command-line flags.
- It proves the stack can distinguish new findings from accepted debt and can time-box or review debt.
- It is the first lane that policy and release consumers can import without bespoke heuristics.

**Core artifacts**
- `lint-baseline/v0`
- `lint-report/v0`
- diff report / summary
- `lint-pilot-pack/v0`

**Primary consumers**
- pull-request review
- rollout programs for stricter policies
- release readiness checks

### 3) Fixpack / apply-receipt lane
**Why third**
- Rust already has machine-applicable suggestions, but current workflows conflate “suggested” with “applied.”
- This lane proves reviewable edit waves can stay distinct from observed findings.
- It composes naturally with Edit Workflow instead of replacing it.

**Core artifacts**
- `lint-fixpack/v0`
- apply receipt from Edit Workflow
- verification summary
- consumer handoff for human review or staged apply

**Primary consumers**
- edition and cleanup waves
- large workspaces rolling out new lint profiles
- assistant/editor/CI review tools

### 4) Future-incompat / Cargo-lint import lane
**Why fourth**
- Cargo already has a report path for future incompatibility, and Cargo-native lints are an active unstable direction.
- This lane proves the governance stack can import Cargo-side warning families without pretending they are identical to rustc or Clippy findings.
- It also creates a clearer bridge between lint governance and migration planning.

**Core artifacts**
- import profile for Cargo-side report families
- normalized import notes in `lint-report/v0`
- consumer handoff to migration or policy lanes

**Primary consumers**
- upgrade and edition planning
- dependency-maintenance workflows
- release review

### 5) Safety-/release-consumer lane
**Why fifth**
- Only after the evidence lanes are stable should curated lint subsets drive higher-stakes consumers.
- This is where safety-critical lint subsets, documentation lint posture, or public-API hygiene profiles can become attachable imported evidence.
- It is a strong test of whether lint governance improves decisions without becoming the entire decision engine.

**Core artifacts**
- consumer handoff to Policy / Safety Evidence / Release Pipeline
- named imported profile slices
- scorecard showing what the consumer may and may not conclude

**Primary consumers**
- safety-heavy teams
- release and package-admission workflows
- support and migration review

## Honest partial outcomes
A pilot may still succeed if it only proves one of these:
- selected policy and group locks are much more valuable than raw lint output,
- baseline drift review matters more than another lint dashboard,
- fix packs should remain attachments while edit receipts belong elsewhere,
- Cargo future-incompat imports are useful even if Cargo-native lint normalization stays partial,
- safety/release consumers should import lint posture as one evidence family rather than letting it dominate the verdict.

## Failure modes to avoid
- turning lint governance into a universal repo-cleanliness score
- silently treating baselines as permanent suppression
- flattening authored lint catalogs, observed findings, fix suggestions, and final edits into one artifact
- pretending Cargo-side report families are identical to rustc/Clippy findings
- making `cargo lintpack` a stealth policy engine instead of an evidence/orchestration layer

## Archive policy
Future revisions should prefer:
- workspace/profile locks,
- explicit baseline debt and expiry,
- fixpack/apply-receipt separation,
- Cargo/future-incompat import notes,
- and real policy/release/safety handoff

over another Clippy preset, another autofix wrapper, or another lint dashboard.
