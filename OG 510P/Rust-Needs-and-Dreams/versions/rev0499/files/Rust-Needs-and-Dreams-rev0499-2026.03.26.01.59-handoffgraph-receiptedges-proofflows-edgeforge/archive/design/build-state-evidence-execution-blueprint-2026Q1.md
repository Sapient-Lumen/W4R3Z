# Design: Build-State Evidence execution blueprint (2026 Q1)

## Goal
Turn the archive's strongest **one-project** answer into a sharper **buildable program**.

The missing contribution is not another build dashboard, another cache wrapper, another editor-only workaround page, or another universal Cargo control plane.
It is a disciplined companion layer that lets Rust teams carry **portable build review truth** across local loops, editor/CLI contention, CI, and future change-impact work.

Read this note when the question is narrower than the broad ladder:

> if a serious Rust team only builds the archive's current top one-project bet, what should that contribution actually ship in theory and practice?

Read with:
- `design/worthy-contribution-shortlist-2026Q1.md`
- `design/strategic-territory-map-2026Q1.md`
- `design/build-state-evidence-stack.md`
- `design/build-state-evidence-pilot-program.md`
- `proposals/epic-build-state-evidence-stack.md`

## Why this note is needed now
The archive already knew that **Build-State Evidence** was strategically strong.
What it still lacked was a crisper answer to **what the winning project should look like**.

Fresh official signals sharpen that answer:
- Rust's March 2026 challenges writeup says compilation performance is a universal productivity tax, not a niche complaint.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey says resource usage (especially slow compile times and storage usage) remains one of the biggest non-trivial productivity problems.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The 2025 compiler-performance survey says around 87% of respondents use inline editor annotations as their main way of inspecting errors, around 33% consider waiting for them a big blocker, and more than 35% say IDE/Cargo blocking is a big problem.
  https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- The Cargo build-analysis goal is explicitly about recording build metadata across invocations and exposing rebuild reasons and timings through `cargo report`.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- The build-dir-layout goal is explicitly about smaller units, finer-grained locking, GC, and a cross-workspace shared cache.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- The March 2026 call for testing says many projects still rely on unspecified build-dir details because Cargo is missing higher-level features, which is a strong hint that the ecosystem needs an honest review layer above those internals.
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Rust Analyzer's documented `cargo.targetDir` workaround avoids lock contention by separating target directories, but explicitly duplicates artifacts to do so. That is useful evidence, not a durable explanation layer by itself.
  https://rust-analyzer.github.io/book/configuration.html
- The **Relink don't Rebuild** goal makes it even clearer that future Cargo work will need a place to express **observed rebuilds** separately from **rebuilds that could have been avoided**.
  https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html

Taken together, those signals say the archive should stop describing the winner only as a theme.
It should describe a real contribution shape.

## Headline answer
If one serious team wants to build the archive's strongest broad contribution, the answer should now be:

> Build a **Build-State Evidence reference layer** that imports Cargo-native evidence, preserves topology / impact / diagnosis as separate truths, and emits reviewable packs and briefs for humans, CI, editors, and downstream tools.

That answer is deliberately narrower than “fix Rust build times”.
It is also deliberately stronger than “show timings”.

## What this contribution should be in theory

### Core thesis
A build-state system becomes ecosystem infrastructure when it can answer all of these from one reviewable pack:
1. **what subject and workflow lane were built;**
2. **what build-state units existed beforehand;**
3. **what was reused, blocked, duplicated, or pruned;**
4. **what changed and which rebuilds were observed;**
5. **which additional work was merely conservative or avoidable;**
6. **what diagnosis or next-step advice is justified by the evidence.**

If a project cannot answer those questions without raw logs, it is not yet the contribution the archive is pointing at.

### Boundary rule
The contribution should stop at **portable build review**.

It should include:
- topology and reuse facts;
- lock/contention and duplication facts;
- rebuild-cause and change-impact imports;
- workflow-aware diagnosis;
- consumer-specific summaries.

It should not become:
- a replacement Cargo;
- a universal scheduler;
- a remote-execution platform;
- or the new unofficial interface for every build backend on earth.

### Separation rule
The contribution must preserve at least four distinct truth classes:
- **observed facts** — what Cargo / rustc / the local run actually did;
- **imported facts** — what first-party or trusted companion tools reported;
- **derived judgments** — bounded classifications and diagnoses;
- **hypothetical opportunities** — e.g. relink-sensitive or policy-change opportunities that did not actually happen.

This is the biggest theory/practice guardrail in the whole design.
Without it, every report turns into a confidence soup.

## What this contribution should be in practice

### Reference tool shape
A serious v0 should probably look like a thin companion tool and schema family:
- `cargo build-state capture`
- `cargo build-state explain`
- `cargo build-state diff`
- `cargo build-state doctor`
- `cargo build-state export --consumer <pr|ci|ide|support|perf>`

The tool should **import** first-party surfaces when available rather than replacing them.

### Public artifact spine
Keep the current stack-level family and make the public outputs more explicit:

#### Imported/internal families
- `build-state-pack/v0`
- `impact-pack/v0`
- `build-doctor-pack/v0`
- `report-pack/v0`

#### Public review families
- `build-state-evidence-brief/v0`
- `build-state-evidence-pack/v0`
- `build-state-evidence-diff/v0`
- `build-state-evidence-handoff/v0`
- `build-state-consumer-slice/v0`

### Minimum schema disciplines
Every public artifact should keep these fields first-class:
- **subject identity** — workspace, package set, target/profile/features/toolchain, lane, invocation class;
- **authority posture** — observed locally, imported from Cargo-native report lane, imported from another companion tool, or inferred;
- **coverage / completeness** — exact, partial, fallback-only, stale, mixed;
- **time and comparison anchors** — session IDs, prior sessions, compared packs;
- **raw attachments** — optional links to timings HTML, JSONL, traces, profiler outputs, cache stats, or logs;
- **reason-coded conclusions** — supported / partial / watch / inconclusive, with explicit ambiguity.

### Commands and what they should emit

#### `cargo build-state capture`
Purpose:
- gather one build-review subject;
- import Cargo-native reports when present;
- record workflow lane, build-dir/target-dir posture, and lock/contention context;
- emit `build-state-evidence-pack/v0`.

Important rule:
- if build-analysis or other first-party surfaces are unavailable, emit a **limited-authority** pack instead of pretending equivalence.

#### `cargo build-state explain`
Purpose:
- tell a human why crates rebuilt, why reuse failed, where lock contention occurred, and which evidence lane justified the answer;
- render the same evidence pack at different depths.

#### `cargo build-state diff`
Purpose:
- compare two packs while preserving the distinction between:
  - new observed rebuilds,
  - new reuse,
  - new duplication,
  - new contention,
  - and new hypothetical relink opportunities.

#### `cargo build-state doctor`
Purpose:
- attach bounded suggestions such as “separate rust-analyzer target dir”, “shared cache policy mismatch”, “build-dir layout assumptions detected”, or “private-change churn likely”.
- the tool should never hide the fact basis behind prose.

#### `cargo build-state export`
Purpose:
- emit smaller consumer slices for PR review, CI annotations, IDE panes, support issues, or perf triage without making those slices canonical by themselves.

## Ranked feature set

### P0 — required for a worthy v0
- import Cargo-native build-analysis / `cargo report` evidence where possible;
- keep `build-dir` and `target-dir` truth visibly separate;
- represent editor/CLI contention and duplicated-target-dir posture explicitly;
- preserve observed rebuilds versus hypothetical relink opportunities;
- emit one portable brief plus one portable pack;
- support raw attachment linkage instead of embedding giant artifacts;
- surface `inconclusive` / `partial` states honestly.

### P1 — strong near-term extensions
- CI/shared-cache exchange reports;
- PR-friendly diff rendering;
- explicit build-dir-layout compatibility notes for tools relying on internal layout details;
- richer private-change classifications;
- support handoffs for bug reports and “why is CI slow?” escalations.

### P2 — do later or fold elsewhere
- remote cache backends;
- cluster scheduling policy;
- editor-specific UX empires;
- hosted timing dashboards;
- predictive optimization advice that is weakly grounded in observed evidence.

## Pilot lanes that best prove the idea

### 1) Editor / CLI coexistence lane
Prove:
- which invocations contended;
- whether separate target directories were used;
- what duplication cost was incurred;
- whether the conclusion came from observed lock behavior, policy choice, or both.

This lane matters because both the build-dir-layout goal and the compiler-performance survey make it a real everyday pain point.

### 2) Private implementation change lane
Prove:
- what changed;
- what actually rebuilt;
- what would still rebuild under today's Cargo rules;
- what might become a relink-only or reduced-rebuild opportunity later.

This is the lane that keeps the stack relevant to **Relink don't Rebuild** without faking that future as already shipped.

### 3) Workspace / CI cache lane
Prove:
- what build-state units were reusable;
- what was duplicated or invalidated by policy;
- what the retention/exchange posture was;
- and what a support or perf reviewer may honestly conclude.

### 4) Build-dir layout migration lane
Prove:
- whether a project or library relied on internal layout assumptions;
- whether those assumptions broke under `-Zbuild-dir-new-layout`;
- and whether the break belonged to internal-path folklore, missing Cargo features, or a real regression.

This lane is especially important because the March 2026 call for testing says those internal assumptions are widespread.

## How this contribution should compose with the rest of the archive

### It strengthens, but does not replace, Rust inner-loop work
The inner-loop band still owns debugger/runtime/editor handoff.
Build-State Evidence should provide one of its strongest factual imports.

### It strengthens, but does not replace, Semantic Context
Semantic context is the hidden multiplier for type/API/doc-aware consumers.
Build-State Evidence is about build review, not semantic authority.

### It strengthens, but does not replace, Package Intake
The March 2026 Cargo extraction CVE is a reminder that package-ingress truth is a separate seam.
Build-state evidence begins **after** intake truth is established and should not pretend local extraction safety is already solved.
  https://blog.rust-lang.org/2026/03/21/cve-2026-33056/

### It strengthens, but does not replace, Public API / Migration
Observed rebuild scope and hypothetical relink opportunities can inform API and migration work, but those contracts still own release-boundary and change-program truth.

## Failure modes to avoid
Do not let this contribution become:
- a score-only product with weak provenance;
- a wrapper that depends on unstable Cargo internals but hides that fact;
- a pure timings viewer that cannot explain rebuild cause or duplication;
- a future-optimizations wish list with little observed evidence;
- or a local power-user tool that cannot emit portable packs.

## Ranking consequence
This note does **not** promote a new frontier.
It deepens the archive's current **one-project winner**.

The clearer execution answer is now:
- **Build-State Evidence** remains the strongest single-project answer overall;
- **Build-State Evidence execution blueprint** is now the canonical “what should it actually ship?” note;
- **Package Intake Gateway** remains the most underappreciated operational seam and should stay separate;
- **Native Edge Contract** remains the active specialist frontier;
- **Semantic Context Contract** remains the hidden multiplier.

That is a stronger repo answer than either of these extremes:
- “invent a whole new #1”; or
- “keep praising Build-State Evidence without ever describing the thing.”
