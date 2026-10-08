## Addendum (rev0474)
For questions about **what ideal Rust should actually build next in concrete library, tool, pack, commons, or program form once the archive's comparative maps are already known**, read this note immediately after:
- `design/territory-priority-refresh-2026Q1.md`
- `design/epic-contribution-scorecards-2026Q1.md`
- `design/epic-contribution-learning-clock-map-2026Q1.md`

Interpretation rule:
- this note does **not** rerank the broad ladder;
- it owns the **practical build menu** and the **wrong-shape kill list** for broad “what should we build?” questions;
- keep **Build-State Evidence** as the strongest one-team first build;
- keep **Feedback Loop / Debuggability Acceptance** as the clearest second serious build;
- keep **Adoption Navigation + Ecosystem Atlas + renewal receipts** as the strongest consumer-facing widener;
- keep **Tooling Contract**, **Semantic Context**, and **Shared Spine** as hidden multipliers that should stay thinner than the public builds they enable;
- keep **Package Intake Gateway** as the clearest urgent boundary bridge; and
- keep **Safety-Critical Readiness Commons** as the clearest high-value program seam.

# Design: Practical epic-contribution briefs (2026 Q1)

## Goal
The archive already has ranking notes, execution blueprints, scorecards, and comparative maps.
What it still needed was one tighter answer to a different question:

> if a serious team asked “what should we actually go build for ideal Rust right now — as a library, Cargo subcommand, report/pack family, commons, or program?”, what should the answer be?

This note is that answer.
It is a **practical build menu + elimination pass**.
It is meant to keep the repo from answering broad strategy questions with either pure abstraction or one more framework fantasy.

Read with:
- `design/territory-priority-refresh-2026Q1.md`
- `design/ideal-rust-worthy-contributions-2026Q1.md`
- `design/epic-contribution-scorecards-2026Q1.md`
- `design/build-state-evidence-execution-blueprint-2026Q1.md`
- `design/feedback-loop-debuggability-execution-blueprint-2026Q1.md`
- `design/adoption-navigation-execution-blueprint-2026Q1.md`
- `design/tooling-contract-execution-blueprint-2026Q1.md`
- `design/package-intake-gateway-execution-blueprint-2026Q1.md`
- `design/safety-critical-readiness-commons-execution-blueprint-2026Q1.md`
- `meta/LATEST_REVISION_FILESET.md`

## Why this pass is merited
The archive already knew the broad answers.
The newest public Rust signals make the **practical shape** harder to dodge.

Signals that matter most:
- The March 2026 challenges writeup says the recurring pain is not only syntax or beginner friction; it explicitly names **async difficulty**, **choice paralysis / tacit knowledge**, and **immature domain support** in places like embedded and safety-critical Rust.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey says **resource usage** remains one of the biggest non-trivial problems, **debugging** remains major friction, and docs remain the canonical reference even as editor or LLM-mediated learning rises.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo's build-analysis and build-dir-layout goals say the ecosystem now wants **rebuild explanation**, **historical build analysis**, **user-wide/shared-cache truth**, and less lock contention between Cargo and tools.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- The 2026 debugging survey says Rust still lacks consistently strong multi-debugger, multi-OS support, visualizers, async debugging, and Rust-expression evaluation.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- The 2026 goals page still treats **public/private dependencies**, **SBOM precursor support**, **Wasm Components**, **sanitizers**, **Rust for Linux**, and **cargo-script** as active stabilization work, which means ideal-Rust contributions should complement real upstream motion instead of pretending upstream is static.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The safety-critical synthesis says the remaining gaps are operational and evidentiary: readiness checklists, dependency-lifecycle playbooks, better target onramps, safety-case-friendly async requirements, and interop guidance.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- The “what people love about Rust” writeup reinforces why these contributions should stay supportive and reviewable: people explicitly value Rust's **supportive tooling**, error messages, reliability, and extensibility.
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- Rust's contributor-funding work is a reminder that some of these bets want durable steward support, not just one clean v0.
  https://blog.rust-lang.org/2025/12/08/making-it-easier-to-sponsor-rust-contributors/

Taken together, the missing contribution is usually **not** “one more framework”.
It is a better **artifact family**, **acceptance commons**, **review boundary**, or **stewarded program**.

## Headline answer
If the archive had to answer in one paragraph, it should now say:

> The best first Rust ecosystem contribution is still a **portable build-state evidence layer**.
> The best second serious contribution is a **feedback-loop / debuggability acceptance commons**.
> The best widener is a **reviewable adoption-navigation and defaults layer**.
> The key multipliers remain **Tooling Contract**, **Semantic Context**, and **Shared Spine**.
> The most urgent narrow bridge remains **Package Intake Gateway**.
> The highest-value program seam remains **Safety-Critical Readiness Commons**.

That is the practical build menu.

## Practical ranking and build shapes

### 1) Build-State Evidence
**Portfolio class:** broad first build

**What is missing**
Rust still lacks one honest, portable family for answering:
- what rebuilt,
- why it rebuilt,
- where time and memory went,
- what cache or lock contention mattered,
- and what changed between two runs.

**What the contribution should look like in practice**
Ship a **report/pack family**, not a dashboard empire:
- `cargo report build-state`
- `cargo report rebuild`
- `cargo report sessions`
- one `build-state-pack/v0` attachment family with lineage receipts
- one doctor flow that keeps explicit unknowns and lossiness visible

**Why this is worthy**
It hits broad recurring pain, aligns with real Cargo motion, and composes with debugging, CI, support, native-edge, and recommendation layers.

**Wrong shapes to refuse**
- cache-wrapper empire
- hosted build-score portal
- daemonized universal build control plane
- `target/` archaeology pretending to be stable substrate

### 2) Feedback Loop / Debuggability Acceptance
**Portfolio class:** second serious build

**What is missing**
Rust still lacks one portable answer for “can I inspect, explain, and hand off debugging truth across debugger tuples, async cases, and support/export consumers?”

**What the contribution should look like in practice**
Ship an **acceptance commons + session pack**:
- debugger-tuple capability and acceptance corpus
- visualizer acceptance lanes
- async-debug acceptance lanes
- portable session exports that import build-state evidence instead of starting from scratch
- issue/support/docs/editor handoff packs that preserve unsupported or unknown states

**Why this is worthy**
The ecosystem is now openly naming debugger inconsistency as a major gap, and it is the clearest daily-experience seam that still lacks a disciplined evidence layer.

**Wrong shapes to refuse**
- one debugger fork sold as the answer
- IDE-only session magic
- a “developer experience” portal with weak exports

### 3) Adoption Navigation + Ecosystem Atlas + renewal receipts
**Portfolio class:** strongest consumer-facing widener

**What is missing**
Rust still lacks a bounded, renewable answer to “which lane, stack, or crate family fits this project, and how fresh is that recommendation?”

**What the contribution should look like in practice**
Ship a **reviewable recommendation layer**:
- lane definitions and slot maps
- conservative defaults with explicit local-fit overlays
- imported build, maintenance, support, compatibility, and learning evidence
- renewal receipts and drift budgets
- project-scoped decision reviews rather than universal winner tables

**Why this is worthy**
The challenge signal is choice paralysis and tacit knowledge, not just search failure.
That makes this a real top-band contribution once the stronger evidence layers exist beneath it.

**Wrong shapes to refuse**
- “best crates for Rust” portal
- leaderboards and trust scores posing as guidance
- assistant-memory canon with no freshness receipts

### 4) Tooling Contract
**Portfolio class:** hidden multiplier / machine-facing substrate

**What is missing**
Cargo still lacks one clean machine-facing contract from discovery through evidence handoff.
Tools still assemble their own partial truths from metadata, message streams, unstable or lossy surfaces, and local inference.

**What the contribution should look like in practice**
Ship a **contract pack + adapter/import corpus**:
- separate subject, discovery/scope, graph/plan, execution/evidence, stability posture, and adapter lossiness
- import Cargo-native surfaces first
- produce bounded adapters for rust-analyzer, CI, docs/release tooling, outer-build systems, and assistants

**Why this is worthy**
It makes many other contributions more honest without trying to become Cargo itself.

**Wrong shapes to refuse**
- Cargo daemon
- BSP-only story
- monorepo/workspace-control platform
- build-dir scraping presented as canon

### 5) Package Intake Gateway
**Portfolio class:** urgent operational bridge

**What is missing**
Rust still lacks a first-class portable ingress boundary for extraction, quarantine, replay, waiver, and handoff truth.
Current security incidents keep proving the seam is real.

**What the contribution should look like in practice**
Ship a **local-first intake review layer**:
- extraction and ingress receipts
- quarantine / waiver / replay paths
- package-route identity and attachment posture
- synthetic proving grounds that teach before live fallout does

**Why this is worthy**
It is narrower than the broad first build, but current advisories keep showing that intake truth is not solved plumbing.

**Wrong shapes to refuse**
- vague trust-score dashboards
- universal security brands without route truth
- registry-specific fixes sold as general package-ingress canon

### 6) Compatibility Claims
**Portfolio class:** claim-routing spine

**What is missing**
The ecosystem still lacks one attachable answer to “what exactly is supported, on what evidence, with what drift posture, and for which consumers?”

**What the contribution should look like in practice**
Ship a **claims pack** built from imported layers:
- support-envelope facts
- public-API and release-boundary facts
- debugger / target / MSRV acceptance facts
- explicit claim families, evidence posture, drift status, and unknowns
- consumer-specific exports that stay lossy on purpose

**Why this is worthy**
Without it, support truth gets flattened into README text, badges, or assistant prose.

**Wrong shapes to refuse**
- badge farms
- one matrix pretending to settle everything
- one semver/MSRV result masquerading as total support truth

### 7) Safety-Critical Readiness Commons
**Portfolio class:** program / consortium seam

**What is missing**
Safety-critical teams still need shared readiness checklists, dependency lifecycle guidance, target-onramp truth, async-runtime qualification requirements, and FFI boundary discipline.

**What the contribution should look like in practice**
Ship a **stewarded commons**, not a one-crate fix:
- target-family readiness checklists
- dependency-lifecycle and replacement playbooks
- safety-case-friendly async requirement profiles
- attachable interop and toolchain evidence slots
- consortium-friendly maintenance and review posture

**Why this is worthy**
This is one of the clearest high-value proving grounds for whether the ecosystem can sustain stronger evidence and support discipline at all.

**Wrong shapes to refuse**
- “certified Rust” branding without evidence
- vendor-owned compliance theater
- one runtime or crate claiming the whole qualification story

## Hidden multipliers that should stay thin
These remain strategically real, but they should usually stay thinner than the public builds they enable.

### Semantic Context
Needed for cross-crate semantic import truth, public-API reasoning, docs/assistant derivations, and tool-to-tool semantic handoff.

### Shared Spine
Needed so multiple pack/report families can share lineage, verification, compatibility gates, and bounded assistant slices without silently diverging.

### Canonical Learning
Needed because docs remain canonical while editor/LLM mediation rises.
The worthy contribution is maintainer-authored canon plus derived overlays with explicit lossiness, not an assistant that becomes the canon.

## Outside-the-box bets worth watching
These do not outrank the top band, but they are worth keeping visible.

### Build authority and sandboxing
Sandboxed `build.rs` or proc-macro authority could materially improve determinism, security posture, and build explainability if it becomes practical.
It should be framed as **authority and evidence discipline**, not as novelty runtime work.

### Safety-case-friendly async requirements
The missing work may be less “build another runtime” and more “define the attachable quality/process artifacts and acceptance conditions a runtime would have to satisfy”.
That is a better first move.

### Target-readiness onramps
Short, target-focused readiness packs would help both safety-critical and mainstream teams translate raw tier policy into practical decisions.

## Kill list
The archive should now refuse these faster under broad “what should Rust build?” questions:
- generic crate-score sites
- “best stack” winner tables
- Cargo-daemon or universal workspace-manager dreams
- target-dir/build-dir scraping as stable substrate
- release-bot empires and badge theater
- framework winner-hunting as a portfolio answer
- assistant-owned repo memory that silently rewrites canon

## Practical evaluation rule
Before the archive promotes a new candidate after this pass, it should ask:
1. Is the pain explicitly named by current official Rust signals?
2. Does the proposal emit reviewable artifacts or only polished product behavior?
3. Can it begin as a thin companion layer?
4. Does it preserve distinct truths instead of flattening them?
5. Does it have a believable steward story?
6. Does it beat one of the current top-band entries, or is it really a child of one of them?

If the answer is weak, fold, watch, or refuse it.
