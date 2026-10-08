# Gap: reproducible benchmarking and performance regression review are still too fragmented

## Summary
Rust has strong benchmarking and profiling pieces, but most teams still have to hand-assemble the answers to basic performance-review questions:
- what workload was actually run,
- what kind of measurement it was,
- what machine / collector configuration produced it,
- what baseline it is being compared against,
- and whether the result is comparable, noisy, or genuinely regressed.

That fragmentation means the ecosystem has **benchmark engines** and **profilers**, but still lacks a shared **performance evidence boundary**.

The missing piece is not “yet another benchmark crate”. It is a Cargo-native, reviewable layer for **workload identity, measurement-lane identity, configuration-aware comparison, and attachable regression evidence**.

## Why now
- The newest State of Rust survey still lists **resource usage** among the biggest productivity problems. That is a durable signal that performance pain remains ecosystem-wide rather than niche.  
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The compiler team’s `rustc-perf` work is now explicitly about **multiple collectors**, **multiple configurations**, and making comparisons **within a configuration, not across configurations**. That is a very strong signal that performance evidence needs first-class configuration identity instead of one global “faster/slower” number.  
  https://rust-lang.github.io/rust-project-goals/2025h2/rustc-perf-improvements.html
- The rustc dev guide already frames perf runs as comparisons across concrete workflow configurations like **fresh builds** and **incremental compilation**. That is direct evidence that “what was measured?” is a structured subject, not a blog-post footnote.  
  https://rustc-dev-guide.rust-lang.org/tests/perf.html
- Rust’s 2025H2 Cranelift goal says the backend is expected to matter especially for **local development**, e.g. `cargo test` or `cargo run`, and reports roughly a 20% reduction in codegen time with around a 5% total clean-build speedup on some projects. That makes workflow-specific measurement more important, not less: dev builds, release builds, compile-only flows, and end-to-end runtime benchmarks should not be flattened together.  
  https://rust-lang.github.io/rust-project-goals/2025h2/production-ready-cranelift.html
- Cargo’s 1.94 development-cycle report says `cargo report timings`, `cargo report rebuild`, and `cargo report sessions` are advancing together. That is a strong signal that Cargo is becoming more machine-facing and more capable of feeding review artifacts rather than only terminal text.  
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Stable benchmarking is still fragmented today:
  - Cargo’s official docs still say `#[bench]` is unstable and nightly-only, even though `cargo bench` can also run custom harnesses with `harness = false`.  
    https://doc.rust-lang.org/cargo/commands/cargo-bench.html  
    https://doc.rust-lang.org/rustc/tests/index.html
  - Criterion has strong statistical benchmarking, but its own docs say machine-readable output is routed through `cargo-criterion --message-format=json`, while CSV output is being deprecated.  
    https://bheisler.github.io/criterion.rs/book/cargo_criterion/external_tools.html  
    https://bheisler.github.io/criterion.rs/book/user_guide/csv_output.html
  - `iai-callgrind` explicitly positions itself as accurate and consistent enough for CI and can run other Valgrind tools like Cachegrind or DHAT, which means the ecosystem already spans multiple serious measurement lanes rather than one canonical engine.  
    https://docs.rs/iai-callgrind

## Concrete missing pieces
1. **Performance subject identity**
   - which crate / package / binary / scenario / request shape / benchmark group is being discussed,
   - and whether the subject is runtime, compile, memory, or service-level.
2. **Measurement-lane identity**
   - statistical wall-time,
   - instruction/callgraph/callgrind,
   - cache-simulation,
   - allocation / heap,
   - compile clean,
   - compile incremental,
   - end-to-end service scenario,
   - and any custom lane that should remain explicit.
3. **Collector / configuration identity**
   - CPU / virtualization / runner class,
   - target triple, profile, linker, codegen backend,
   - benchmark engine and version,
   - container / image / host policy,
   - and whether results are actually comparable.
4. **Baseline provenance**
   - what revision, release, or tagged baseline was used,
   - whether the baseline is stale,
   - whether the comparison is branch-local, release-over-release, or PR-vs-main,
   - and whether multiple baselines are allowed.
5. **Reviewable verdicts**
   - `improved`, `regressed`, `unchanged`, `inconclusive`, `not-comparable`, `baseline-stale`,
   - with attached reason codes instead of screenshots or freeform PR comments.
6. **Shareable performance packs**
   - summary metrics,
   - raw measurement references,
   - optional profiler / flamegraph / callgrind / heap / Cargo-report attachments,
   - and one portable bundle that CI, PR review, releases, or dashboards can all consume.

## Desired properties
- Build on existing tools instead of replacing them.
- Compare **within a declared configuration class** by default.
- Make `inconclusive` and `not-comparable` first-class outcomes.
- Preserve raw measurement lineage instead of only exporting one pretty chart.
- Work for applications, libraries, CI pipelines, and hosted benchmark services.
- Keep compile-time evidence and runtime evidence distinct while allowing both to live in one ecosystem substrate.

## Distinction from nearby archive entries
- **Cargo Report Kit** standardizes Cargo report surfaces broadly; this gap is about a shared **performance evidence and comparison** boundary.
- **Build Doctor Kit** diagnoses slow build workflows and suggests actions; this gap is about **performance workloads, measurement lanes, compare verdicts, and policyable evidence**.
- **Build Cache Kit** explains reuse and cache posture; this gap explains whether a performance claim or regression result is reviewable.
- **Replay Kit** captures correctness/debugging failures; this gap captures repeatable performance evidence.
- **Footprint Kit** owns binary/resource-size budget truth; this gap owns **measured performance comparisons**.
