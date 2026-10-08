# Epic Proposal: Build-State Evidence Stack (`cargo build-state` + `build-state-evidence-pack/v0`)

## One-sentence pitch
Make Rust build review boring by standardizing a portable **topology → impact → diagnosis** boundary above Cargo’s emerging build-analysis/report work instead of leaving developers, editors, and CI systems to reconstruct build truth from HTML, raw logs, and folklore.

For the concrete execution shape, also read `design/build-state-evidence-execution-blueprint-2026Q1.md`.

## Deliverables
- `cargo build-state` reference tool
- schemas:
  - `build-state-evidence-brief/v0`
  - `build-state-evidence-pack/v0`
  - `build-state-evidence-diff/v0`
  - `build-state-evidence-handoff/v0`
- adapters/importers for:
  - `build-state-pack/v0`
  - `impact-pack/v0`
  - `build-doctor-pack/v0`
  - `report-pack/v0`
  - optional timing/self-profile/cache-exchange/raw-log attachments
- docs:
  - editor/CLI coexistence review recipe
  - private-change / relink-opportunity review recipe
  - workspace/CI cache-exchange review recipe
  - workflow-aware diagnosis and support handoff guide

## Why now (signals)
- The 2025 State of Rust survey still identifies compile times and storage usage as major productivity problems.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The 2025 compiler-performance survey says users want better explanations of slow builds, calls out editor latency, and says more than 35% of respondents who see CI/IDE blocking as a big problem report Cargo and the IDE blocking one another.
  https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- Cargo’s build-analysis experiment records JSONL session logs and exposes `cargo report sessions`, `cargo report timings`, and `cargo report rebuilds`, which means first-party raw evidence is now real enough to import.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- The Cargo build-analysis project goal explicitly aims to record build metadata across invocations and expose rebuild reasons and timing history.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- The build-dir-layout goal explicitly targets fine-grained locking, reduced Cargo / rust-analyzer contention, garbage collection, and a cross-workspace shared build cache.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- The **Relink don’t Rebuild** goal explicitly targets avoiding reverse-dependency rebuilds when a crate’s public interface did not change.
  https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
- Cargo’s build-cache docs now distinguish final artifacts in `target-dir` from intermediate artifacts in `build-dir`, and Cargo 1.93 says build-dir work is being organized around build units so Cargo can lock them individually.
  https://doc.rust-lang.org/cargo/reference/build-cache.html
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/

## Non-goals
- replacing Cargo internals, rust-analyzer, or `sccache`;
- inventing one universal build-health score;
- pretending relink opportunities are already-realized Cargo behavior;
- turning unstable raw report formats into a fake stable contract without explicit import posture;
- flattening topology facts, impact facts, and diagnostic conclusions into one mega-format.

## Strategic value
This deserves promotion because it gives the archive a **build-review-native composition point**.
With it:
- local developers can understand why work rebuilt, blocked, or duplicated;
- editor integrations can explain separate-target-dir tradeoffs instead of repeating folklore;
- CI/shared-cache operators can review reuse, rejection, and retention posture with bounded artifacts;
- relink-sensitive future Cargo work can attach opportunity reports without pretending the future has already landed;
- downstream Tooling Contract, Perf/Resource, Release, and support stacks can import build truth without screen-scraping HTML or raw logs.

The prize is not another build wrapper.
The prize is a reviewable build-state evidence boundary that other tools can import.

## Proposed shape
Ship a narrowly scoped stack-level layer:
1. import `build-state-pack/v0` as the topology / reuse / locking boundary;
2. import `impact-pack/v0` as the semantic-change / rebuild-scope / relink-opportunity boundary;
3. import `build-doctor-pack/v0` as the workflow-diagnosis boundary;
4. optionally attach `report-pack/v0` and raw timing/log/profile artifacts without making them canonical by themselves;
5. emit `build-state-evidence-handoff/v0` for IDE, CI, perf/resource, release, and support consumers;
6. provide diffing that preserves lane distinctions and `INCONCLUSIVE` posture.

## Critical design bet
The critical bet is that **build-state evidence should stop at portable build review**.
That means:
- cache/layout/reuse facts are included,
- rebuild-scope and relink-opportunity facts are included,
- workflow-aware diagnoses are attached,
- optional raw reports/traces can travel,
- but Cargo scheduling policy, editor architecture, and remote-cache backends stay outside the stack.

Without that boundary, the stack will either stay too weak to matter or bloat into a fake universal build platform.

## Milestones
1. **v0 schemas + editor/CLI lane**
   - `build-state-evidence-brief` / `build-state-evidence-pack`
   - import `build-state-pack/v0` and `build-doctor-pack/v0`
2. **v0.2 private-change / relink lane**
   - attach `impact-pack/v0`
   - preserve observed rebuilds vs relink opportunities
3. **v0.3 workspace / CI exchange lane**
   - attach cache-exchange / retention / rejection reports
   - keep local, shared, and CI lanes explicit
4. **v0.4 diagnosis + consumer handoff lane**
   - emit bounded handoffs for IDEs, support, perf/resource, and tooling-contract consumers
5. **v1 stable-ish import posture**
   - document stable-vs-experimental evidence imports
   - add diffing and consumer-view guidance without overclaiming stability

## Execution order
Use [`design/build-state-evidence-pilot-program.md`](../design/build-state-evidence-pilot-program.md) as the stack-level rollout:
1. editor/CLI coexistence and lock-scope lane,
2. private-change / relink-opportunity lane,
3. workspace / CI exchange lane,
4. workflow-aware diagnosis lane,
5. federated consumer lane.

Use [`proposals/epic-build-cache-kit.md`](./epic-build-cache-kit.md), [`proposals/epic-change-impact-kit.md`](./epic-change-impact-kit.md), and [`proposals/epic-build-doctor-kit.md`](./epic-build-doctor-kit.md) as the leaf-level execution guides beneath it.

## Success metrics
- humans can reconstruct build-review facts offline from one linked pack;
- topology, impact, and diagnosis truth remain visibly distinct in summaries and diffs;
- editor/CLI contention and duplication can be explained without target-dir folklore;
- relink opportunities remain explicit opportunity reports rather than fake success claims;
- downstream consumers can import build-state evidence without re-scraping unstable raw reports;
- the ecosystem gets one explainable build-review seam instead of scattered timing pages, CI logs, and ad hoc cache dashboards.
