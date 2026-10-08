# Gap: build-state truth still lacks one portable topology → impact → diagnosis boundary

## Summary
Rust’s build tooling is finally gaining enough first-party signal that the missing problem is no longer “collect more timing data somehow”.
What is still missing is the **portable review boundary** that keeps three truths distinct while letting them compose:
- **build-state topology / reuse / locking truth**,
- **change-impact / rebuild-scope / relink-opportunity truth**,
- **workflow-aware diagnosis / suggestion truth**.

The ecosystem can already answer fragments such as:
- “this build session rebuilt crate X because inputs changed,”
- “`cargo check` and `cargo build` blocked or duplicated one another,”
- “the build-dir layout makes CI caching awkward,”
- or “this edit probably should not have forced downstream recompiles.”

What it still struggles to answer cleanly is:
- which facts came from Cargo’s own recorded build state versus later inference,
- whether a rebuild was semantically required or merely conservative,
- where contention or duplication was intentional policy versus accidental layout fallout,
- which diagnoses are grounded in imported evidence rather than folklore,
- and what changed between two build-review moments without diffing raw logs and HTML by hand.

That missing layer is not another cache wrapper, not another timings dashboard, and not a fake universal build score.
It is a **portable build-state evidence boundary** that keeps topology facts, impact facts, and diagnostic conclusions separate.

## Why now
Recent official Rust/Cargo signals make this much more concrete than it used to be:
- the 2025 State of Rust survey still lists compile times and storage usage among major productivity problems;
- the 2025 compiler-performance survey says users want better explanations of slow builds, highlights editor latency, and notes Cargo / IDE blocking as a real pain point;
- Cargo’s build-analysis experiment now records JSONL build logs and exposes `cargo report sessions`, `cargo report timings`, and `cargo report rebuilds`;
- the `build-dir` layout goal explicitly targets finer-grained locking, reduced Cargo / rust-analyzer contention, and a cross-workspace shared build cache;
- the **Relink don’t Rebuild** goal explicitly targets avoiding downstream rebuilds when a crate’s public interface did not change;
- Cargo’s build-cache docs now separate final artifacts in `target-dir` from intermediate artifacts in `build-dir`;
- Cargo 1.93 says build-dir work is being organized around build units so Cargo can lock them individually.

Sources:
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- https://doc.rust-lang.org/cargo/reference/unstable.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
- https://doc.rust-lang.org/cargo/reference/build-cache.html
- https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/

## The current seam is awkward
Today, teams often improvise build understanding from incompatible materials:
- `cargo --timings` HTML,
- unstable `cargo report` output,
- ad hoc CI cache stats,
- rust-analyzer target-dir workarounds,
- perf screenshots,
- build-log spelunking,
- public-API diffs or semver checks,
- and human guesses about which rebuilds were “really necessary”.

That usually leads to one of five failures:
1. cache/layout facts get flattened into one crude hit/miss story;
2. semantic change and observed rebuild scope get conflated;
3. build-doctor advice overclaims what the evidence actually proved;
4. editor/CLI coexistence pain becomes target-dir folklore instead of reviewable reports;
5. CI/shared-cache experiments cannot explain why reuse failed or why duplication was chosen.

## Why this matters
This gap affects more than compiler-performance specialists.
It matters to:
1. **everyday developers** — because slow edit-debug cycles need explanations, not only optimism;
2. **editor and IDE integrators** — because Cargo/rust-analyzer coexistence is still a real source of friction;
3. **CI and remote-cache operators** — because artifact exchange and retention decisions need better evidence than tarball size and hope;
4. **Cargo evolution itself** — because structured report/plumbing work benefits from a portable consumer boundary above unstable raw data;
5. **downstream stacks** — because Tooling Contract, Perf/Resource Evidence, Release review, and support workflows all benefit from an honest build-state import.

## What “good” looks like
A worthy contribution here is a thin composition layer above Build Cache Kit, Change Impact Kit, and Build Doctor Kit, with at least:
- `build-state-evidence-brief/v0` — why this build-review subject exists and which workflow/lane it covers;
- `build-state-evidence-pack/v0` — linked topology, impact, and diagnosis artifacts with explicit missing-data posture;
- `build-state-evidence-diff/v0` — what changed between two review points and why;
- `build-state-evidence-handoff/v0` — bounded imports for CI, IDEs, support, perf/resource, and release/policy consumers;
- and a coordinating CLI/layer that validates these attachments without absorbing the underlying cache, impact, or doctor tools.

The winning version should keep these distinctions visible:
- **topology/reuse/locking truth** versus **impact/rebuild truth**,
- **observed rebuilds** versus **relink opportunities**,
- **workflow identity** (`check`, `build`, editor, CI, release) versus generic build folklore,
- **imported facts** versus **derived suggestions**,
- and **canonical linked packs** versus compressed consumer views.

The bar is not a prettier build dashboard.
The bar is a durable, explainable, importable evidence boundary for build reality.
