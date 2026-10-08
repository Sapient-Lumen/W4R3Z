# Proposal: Epic Proc-Macro Exit Stack

## Goal
Give Rust one reviewable transition layer over proc-macro burden so maintainers can reduce unnecessary proc-macro dependence without pretending all proc macros should disappear.

## Why now
Official Rust signals have become unusually aligned:
- macro improvements explicitly aim to cover more proc-macro use cases with declarative macros for faster builds and smaller dependency supply chains;
- reflection/comptime now explicitly frames proc-macro derives as hard to debug and bootstrap;
- 2026 flagship work includes prototype reflection;
- compiler-performance work says some language features could remove proc macros and calls out derive-proc-macro expansion as a remaining incremental-build pain point;
- proc macros still run during compilation with build-script-like authority concerns.

Sources:
- https://rust-lang.github.io/rust-project-goals/2025h1/macro-improvements.html
- https://rust-lang.github.io/rust-project-goals/2025h2/reflection-and-comptime.html
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- https://doc.rust-lang.org/reference/procedural-macros.html

## Stack reading
This epic composes:
- `design/macro-workflow-kit.md`
- `design/compile-time-capabilities-kit.md`
- `gaps/macro-workflows-and-proc-macro-migration.md`
- `gaps/reflection-transition-lane-comparison-macro-burden-and-core-reflection-migration.md`

It should be read as a **transition-planning** and **handoff** layer, not as a replacement for those lower layers.

## MVP
Ship a thin `cargo macro-exit` / `macro-exit-pack/v0` layer that can:
1. import macro inventory/cost/debug evidence;
2. classify burden slices into candidate targets (`stay proc macro`, `declarative`, `language`, `reflection/comptime`, `visit-only`, `schema-tracing`);
3. record blockers, benefit classes, and confidence levels;
4. emit one bounded maintainer/review/build summary.

## Milestones
### M1 — subject + import lane
- `macro-exit-subject/v0`
- `macro-exit-imports/v0`
- import `macro-inventory/v0`
- optional import of macro cost/debug reports

### M2 — transition-target lane
- `macro-exit-targets/v0`
- explicit candidate classes
- explicit “stay proc macro” outcome to avoid false optimism

### M3 — planning lane
- `macro-exit-plan/v0`
- blocker classes
- confidence levels
- expected benefit classes

### M4 — diff and handoff lane
- `macro-exit-diff/v0`
- maintainer/build/review/assistant handoffs
- one real release-planning or roadmap consumer

## Non-goals
- no automatic rewrite engine;
- no universal reflection substrate;
- no hosted leaderboard of “good” or “bad” macros;
- no silent takeover of Macro Workflow or Compile-Time Capabilities.

## Why this is worthy
It gives Rust a way to convert macro-roadmap progress into maintainable ecosystem action.
That is a much more realistic contribution than waiting for language progress and hoping the migration folklore sorts itself out later.
