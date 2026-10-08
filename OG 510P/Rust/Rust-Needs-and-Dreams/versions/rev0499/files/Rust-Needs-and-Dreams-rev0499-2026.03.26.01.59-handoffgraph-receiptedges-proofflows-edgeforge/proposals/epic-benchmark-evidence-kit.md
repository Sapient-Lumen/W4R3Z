> Revision note (rev0452): read this proposal now as the execution path beneath the archive's explicit **Benchmark Evidence execution blueprint**. Keep it benchmark-native: do not let broader Perf Labs policy, release gating, or one engine/adaptor story silently re-own comparability truth.

> Revision note (rev0411): read this proposal now as the concrete execution path beneath the archive's explicit **Benchmark Evidence Contract** frontier.
> Keep it benchmark-native: do not let broader Perf Labs policy, release gating, or one engine/adaptor story silently re-own the contract.

# Epic Proposal: Benchmark Evidence Kit (`cargo benchpack`, `benchmark-pack/v0`)

## One-sentence pitch
Give Rust a portable benchmark-native evidence layer so harnesses, runners, deterministic profiler lanes, and hosted services can exchange subject/lane/baseline/result truth without scraping output or flattening unlike benchmark models into one fake score.

## Deliverables
- `cargo-benchpack` reference implementation
- Schemas:
  - `benchmark-subject/v0`
  - `benchmark-lane-profile/v0`
  - `benchmark-run-import/v0`
  - `benchmark-baseline-import/v0`
  - `benchmark-result-report/v0`
  - `benchmark-pack/v0`
- Design docs:
  - `design/benchmark-evidence-lane-map.md`
  - benchmark-subject design playbook
  - measurement-lane and counter semantics guide
  - baseline-import and freshness guide
  - Perf Labs handoff guide
- Adapters/importers for:
  - `cargo bench`
  - Criterion native and `cargo-criterion` JSON
  - Divan result/counter lanes
  - `cargo nextest bench`
  - Iai-Callgrind and adjacent Valgrind-backed lanes
  - CodSpeed compatibility-layer imports

## Why now (signals)
- Cargo’s docs still define a plural benchmark surface: nightly libtest or custom harness, with `#[bench]` still unstable.
  https://doc.rust-lang.org/cargo/commands/cargo-bench.html
- nextest now documents an experimental `cargo nextest bench` flow with support for Criterion.rs, nightly libtest benches, and custom test-harness protocol users.
  https://nexte.st/docs/features/benchmarks/
- Criterion’s native user guide still has named baselines, while `cargo-criterion` still exports machine-readable JSON but lacks baseline support.
  https://bheisler.github.io/criterion.rs/book/user_guide/command_line_options.html
  https://bheisler.github.io/criterion.rs/book/cargo_criterion/cargo_criterion.html
- Divan and Iai-Callgrind prove benchmark semantics already span explicit throughput counters, deterministic profiler lanes, and raw attachment families.
  https://docs.rs/divan/latest/divan/counter/index.html
  https://docs.rs/iai-callgrind/latest/iai_callgrind/
- CodSpeed compatibility layers and measurement modes show that hosted/imported benchmark plurality is real.
  https://codspeed.io/docs/benchmarks/rust
  https://codspeed.io/docs/reference/codspeed-rust/cargo-codspeed
- rustc-perf’s multiple-collector direction reinforces the need for explicit benchmark lane and collector truth.
  https://rust-lang.github.io/rust-project-goals/2025h2/rustc-perf-improvements.html

## Non-goals
- Replacing Criterion, Divan, Iai-Callgrind, nextest, CodSpeed, or rustc-perf
- Declaring one benchmark harness or hosted service the winner
- Owning generic run-result truth or harness discovery truth
- Owning broad compare/gate policy for all performance workloads
- Collapsing metric families, baselines, and runner imports into one score

## Strategic value
This is a worthy contribution because it creates the missing portable layer between Rust’s growing benchmark reality and broader performance-review infrastructure.

It would let maintainers answer questions like:
- “What benchmark subject actually regressed?”
- “Was this nightly `cargo bench`, Criterion-native baseline evidence, Divan counters, nextest-imported execution, Iai-Callgrind profiler data, or a hosted adapter run?”
- “Did the result rely on a native saved baseline, a hosted baseline, or no baseline at all?”
- “Which raw artifacts exist if a reviewer wants deeper proof?”

That is strategically valuable because today those answers are split across per-tool formats, local directories, CI comments, and hosted dashboards.

## Milestones
1. **v0 stable local harness pilot**
   - Criterion native + Divan benchmark packs
   - explicit lane/counter/baseline truth
2. **v0.2 runner-import pilot**
   - `cargo nextest bench` import lane
   - benchmark-specific timeout/setup/wrapper truth
3. **v0.3 deterministic profiler pilot**
   - Iai-Callgrind / Valgrind-backed imports
   - deterministic metric-family support and raw attachment links
4. **v0.4 hosted compatibility pilot**
   - CodSpeed imports
   - hosted baseline and measurement-mode truth
5. **v1 ecosystem handoff**
   - clean Perf Labs import path
   - stronger CI/release/dashboard consumers

## What success looks like
- A benchmark run can be attached as one `benchmark-pack/v0` instead of a tool-native directory plus explanation comments.
- Reviewers can see benchmark subject ids, lane/counter semantics, baseline posture, runner/import posture, and raw-attachment refs without tool-specific archaeology.
- Hosted services and local harnesses can coexist without pretending they have the same semantics.
- Perf Labs can import benchmark packs instead of re-learning every benchmark tool’s native format.

## Execution order
For the ranked rollout order, see `design/benchmark-evidence-pilot-program.md`.
