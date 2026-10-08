# Epic Proposal: Perf Labs (`cargo perf`, `perf-pack/v0`)

## One-sentence pitch
Give Rust projects a standard way to publish **configuration-aware performance evidence** so regressions become reviewable artifacts with explicit workload, metric, baseline, and comparability truth instead of folklore and screenshots.

## Deliverables
- `cargo perf` reference implementation
- Schemas:
  - `perf-subject/v0`
  - `perf-workload/v0`
  - `perf-measurement-profile/v0`
  - `perf-collector-profile/v0`
  - `perf-baseline-record/v0`
  - `perf-compare-report/v0`
  - `perf-policy/v0`
  - `perf-pack/v0`
- Adapters / importers for:
  - `benchmark-pack/v0` imports from Benchmark Evidence Kit
  - Criterion / cargo-criterion JSON output where direct import still matters
  - Iai-Callgrind and adjacent Valgrind-backed lanes
  - Cargo timing / rebuild / session report attachments
  - custom benchmark harnesses and service-scenario lanes
- Docs:
  - workload-design playbook
  - CI gating patterns
  - runner/collector hygiene guidance
  - baseline lifecycle guidance

## Why now (signals)
- Rust users still identify resource usage as a major productivity problem.  
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The compiler team’s current `rustc-perf` roadmap is explicitly about multiple collectors and configuration-aware comparison.  
  https://rust-lang.github.io/rust-project-goals/2025h2/rustc-perf-improvements.html
- The rustc dev guide already treats fresh and incremental builds as distinct performance configurations, which is exactly the kind of subject identity other Rust projects also need.  
  https://rustc-dev-guide.rust-lang.org/tests/perf.html
- The Cranelift goal sharpens the importance of measuring concrete developer workflows such as local `cargo run` / `cargo test` style iteration.  
  https://rust-lang.github.io/rust-project-goals/2025h2/production-ready-cranelift.html
- Cargo’s newer `cargo report *` commands make structured performance attachments more realistic than they used to be.  
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Stable benchmarking remains fragmented between unstable `#[bench]`, custom harnesses, Criterion/cargo-criterion, and Iai-Callgrind-style lanes.  
  https://doc.rust-lang.org/cargo/commands/cargo-bench.html  
  https://bheisler.github.io/criterion.rs/book/cargo_criterion/external_tools.html  
  https://docs.rs/iai-callgrind

## Non-goals
- Replacing Criterion, Iai-Callgrind, profiler tools, or rustc-perf
- Pretending different metric families are directly comparable
- Claiming results from different collector classes are automatically apples-to-apples
- Requiring a hosted dashboard service before the format is useful
- Turning performance review into one global benchmark score

## Strategic value
Current posture: **companion kit / evidence substrate** for imported `benchmark-pack/v0` lanes, Cargo reports, profiler outputs, hosted benchmark services, and release/policy workflows.

This is a worthy contribution because it would let Rust projects answer performance questions with **portable evidence**:
- “What workload regressed?”
- “Was this wall-time or instruction-count evidence?”
- “Are these results comparable or did the runner/config drift?”
- “Which baseline are we using, and is it stale?”
- “Why did CI fail the performance gate?”

That is high leverage because performance work spans compilers, libraries, services, CI systems, release engineering, and hosted benchmarking infrastructure — but today the evidence boundary is still mostly bespoke.

## Milestones
1. **v0 compile-workflow pilot**
   - prove build-performance subjects and Cargo report attachments
   - baseline-vs-candidate compare with reason codes
   - explicit collector profiles and baseline freshness
2. **v0.2 runtime and deterministic CI pilots**
   - library microbench lane
   - instruction/count or simulator-style CI lane
   - thresholding, waivers, stale-baseline handling, inconclusive state
3. **v0.3 service / scenario pilot**
   - end-to-end workload manifests
   - large-trace / flamegraph / heap attachment conventions
4. **v1 ecosystem convergence**
   - adapters for common engines and harnesses
   - stronger workspace aggregation
   - federated collector / hosted-service publishing patterns

See [`design/perf-pilot-program.md`](../design/perf-pilot-program.md) for the ranked rollout logic.

## What success looks like
- A maintainer can attach one `perf-pack/v0` to a release or pull request.
- A reviewer can tell exactly what was measured, how, against what baseline, and whether the comparison is trustworthy.
- CI can gate on stable reason codes instead of scraping freeform benchmark output.
- Existing engines remain viable while becoming easier to compare and consume together.
