> Revision note (rev0411): this gap is now promoted into the archive's explicit **performance-claim / compare-shaping** frontier.
> Keep reading it as a gap about **benchmark-native subject/lane/baseline/verdict truth**; do not let later Perf Labs policy or broad build-analysis work flatten it back into generic “performance results”.

# Gap: benchmark evidence is still scattered across harnesses, runners, profiler lanes, and hosted adapters

## Summary
Rust already has several real benchmarking lanes, but the ecosystem still lacks a shared contract for basic benchmark-review questions:
- what benchmark subject actually ran,
- which harness, runner, or hosted adapter path produced the result,
- what measurement lane and counter semantics applied,
- what baseline or prior run the result is being compared against,
- and whether the result is portable enough to hand off into broader performance review.

That means Rust has **benchmark harnesses, runner imports, profiler-backed lanes, and hosted services**, but still lacks a shared **benchmark evidence boundary**.

The missing piece is not another benchmark framework. It is a reviewable layer for **benchmark-native subject truth, lane/counter truth, baseline truth, runner/import truth, raw-result lineage, and bounded performance handoff**.

## Why this is real now
- Cargo’s own benchmark story is still explicitly plural. `cargo bench` can run the default libtest benchmark runner, `#[bench]` is still unstable/nightly-only, and targets can disable the harness and provide their own `main`. That means the foundation already spans nightly-first and custom-harness lanes rather than one settled built-in benchmark model.
  https://doc.rust-lang.org/cargo/commands/cargo-bench.html
- nextest now documents an experimental `cargo nextest bench` flow with support for Criterion.rs, the nightly libtest benchmark runner, and custom test-harness protocol users. That makes runner-import truth materially important.
  https://nexte.st/docs/features/benchmarks/
- Criterion’s native user guide still documents named baselines via `--save-baseline` and `--baseline`, but the `cargo-criterion` docs still say the Cargo extension provides machine-readable JSON and does **not** currently support baselines. That is strong evidence that machine-readable export and baseline truth are already split across lanes.
  https://bheisler.github.io/criterion.rs/book/user_guide/command_line_options.html
  https://bheisler.github.io/criterion.rs/book/cargo_criterion/cargo_criterion.html
- Divan makes throughput semantics first-class with bytes/chars/cycles/items counters. That widens the benchmark-review problem beyond “a wall-clock number in a table”.
  https://docs.rs/divan/latest/divan/counter/index.html
- Iai-Callgrind is explicitly a benchmark framework/harness using Valgrind Callgrind for extremely accurate and consistent measurements suited to CI, and it can also drive Cachegrind and DHAT-style lanes. That proves benchmark evidence already spans materially different metric families and raw attachments.
  https://docs.rs/iai-callgrind/latest/iai_callgrind/
- CodSpeed now publishes Rust compatibility layers for Divan, Criterion.rs, and bencher/libtest, while `cargo-codspeed` exposes distinct `simulation`, `walltime`, and `memory` measurement modes. That is another strong sign that benchmark ecosystems are converging through adapters rather than one runner or one collector.
  https://codspeed.io/docs/benchmarks/rust
  https://codspeed.io/docs/reference/codspeed-rust/cargo-codspeed
- rustc-perf’s multiple-collector direction explicitly warns against cross-configuration flattening by emphasizing comparison within a configuration, not across configurations. That is a direct design lesson for general Rust benchmark evidence as well.
  https://rust-lang.github.io/rust-project-goals/2025h2/rustc-perf-improvements.html

## Concrete missing pieces
1. **Benchmark subject identity**
   - package / target / benchmark binary / suite / group / case id,
   - parameterization or scenario identity,
   - and whether the subject is library microbench, binary scenario, compile benchmark, profiler lane, or hosted collector case.
2. **Measurement-lane and counter truth**
   - statistical wall-time,
   - nightly libtest/custom-harness execution,
   - explicit throughput counters,
   - deterministic instruction/cache/heap lanes,
   - hosted simulation/walltime/memory modes,
   - and explicit units.
3. **Baseline truth**
   - native Criterion saved baseline,
   - prior run without native baseline support,
   - hosted/imported baseline,
   - absent/unsupported baseline,
   - and freshness/staleness posture.
4. **Runner/import posture**
   - direct harness execution,
   - `cargo bench`,
   - `cargo nextest bench`,
   - hosted-service adapters,
   - sharding/filtering/timeouts,
   - and explicit lossiness.
5. **Raw-result lineage**
   - statistical summaries,
   - deterministic profiler outputs,
   - counter-bearing summaries,
   - raw attachments such as callgrind or heap reports,
   - and change metrics imported from native tools when present.
6. **Portable handoff to broader performance review**
   - one benchmark-native pack that Perf Labs, CI, release review, or hosted dashboards can import without pretending the benchmark engine’s native format is the whole answer.

## Desired properties
- Converge current tools instead of replacing them.
- Keep benchmark-native semantics explicit before broader compare/gate layers import them.
- Make runner/import lossiness first-class.
- Make missing baselines or non-comparable runs explicit instead of silently falling back.
- Preserve metric-family and counter semantics instead of flattening them into one score.
- Work for stable and nightly benchmark lanes without pretending those have the same maturity.

## Distinction from nearby archive entries
- **Harness Protocol Kit** owns capability/discovery/adapter truth before execution. This gap is about **benchmark-native result, lane, and baseline evidence**.
- **Test Run Evidence Kit** owns generic execution/run truth. This gap is about **benchmark semantics that remain special even when a runner can execute them**.
- **Perf Labs** owns broader workload comparison and gating. This gap is about the benchmark-native layer that Perf Labs should import instead of re-describing every harness/runner/collector format itself.
- **Coverage Evidence Kit** and **Sanitizer Battery Kit** own specialized evidence families above execution. This gap is about benchmark-native evidence before those specialized or broader consumers import it.
