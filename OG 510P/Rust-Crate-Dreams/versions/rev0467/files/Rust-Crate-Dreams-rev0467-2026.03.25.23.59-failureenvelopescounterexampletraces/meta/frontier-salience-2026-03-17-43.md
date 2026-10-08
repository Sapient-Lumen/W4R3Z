# Frontier salience snapshot — 2026-03-17 (43)

This pass did **not** promote a new lane.
It sharpened an existing high-ranked cross-cutting proposal:

- **P-0517 Crate Performance Envelope Pack Kit** — because the archive still lacked a good release-grade artifact for the maintainer question that sits between “we have benchmarks” and “downstream users can actually trust our performance story”: *which workloads matter, which metric rules, under what conditions, and with what confidence?*

## Main judgment

The next worthy move in this frontier was **not** another benchmark runner, another profiler, or another hosted regression dashboard.
Those pieces already exist in partial form.

The sharper missing layer is the **performance-envelope contract** above them:

- metric-authority policy,
- environment-fidelity receipts,
- noise-class reports,
- budget reports,
- workload recipes,
- and release-to-release performance diffs.

That move is now better grounded because:

- the Rust vision-doc explicitly argues for more supportive interfaces from crates,
- the 2025 State of Rust survey says docs and code remain the main learning surfaces while resource usage and debugging stay visible pain,
- Cargo already documents that `cargo bench` defaults to the `bench` profile and that stable benchmarking often means custom harnesses,
- Cargo profile docs explicitly warn that optimization settings can have surprising results and should be re-evaluated over time,
- Cargo’s 1.84 development-cycle notes make the release-fidelity versus profiling-ease tradeoff explicit,
- Criterion already offers a statistically-driven wall-time surface,
- Iai-Callgrind already offers CI-stable instruction/cache-oriented measurement,
- Divan already offers a modern stable benchmarking surface,
- and CodSpeed compatibility layers already show teams trying to reuse local suites in hosted CI while preserving imports and most behavior.

So the gap is no longer “Rust has no benchmarking tools”.
The gap is that maintainers still rarely publish a **reviewable workload / metric / fidelity / confidence contract** above that substrate.

## Broad portfolio ranking after this pass

1. **P-0520 Crate Lifecycle Surface Pack Kit** — still one of the clearest implementation-ready support-truth lanes.
2. **P-0484 Toolchain & Target Support Contract Kit** — still one of the strongest support-drift lanes for real users on real machines.
3. **P-0451 Cfg Availability Ledger Kit** — still a highly leverageful way to make conditional API truth reviewable.
4. **P-0521 Crate Resource Surface Pack Kit** — now one of the best capacity/support contracts in the frontier.
5. **P-0517 Crate Performance Envelope Pack Kit** — now a much more believable `0.1` crate for workload/metric honesty.
6. **P-0472 Docs.rs Build Parity Evidence Kit** — critical adjacent lane, but narrower than the full performance/support contract.
7. **P-0121 FFI Boundary & Bindings Conformance Kit** — still a high-value bridge for Rust↔foreign adoption.

## Why this won over adjacent candidates right now

- It beat **more observability follow-ons** because emitted telemetry still does not tell users which performance metric they should trust.
- It beat **more resource follow-ons** because boundedness and saturation are not the same lane as workload choice and benchmark honesty.
- It beat **more configuration follow-ons** because setup recipes still do not answer what tradeoff a chosen mode buys.
- It beat several strong **authority/runtime** candidates because this lane multiplies value across CLI, parser, async, embedded-ish, and framework crates rather than one integration domain at a time.

## What changed in the archive

Added:
- `meta/crate-performance-envelope-product-plan-2026-03-17.md`
- `meta/frontier-salience-2026-03-17-43.md`
- `entries/2026-03-17-223.md`
- `fixtures/crate-performance-envelope-pack-kit/metric-authority.policy.schema.json`
- `fixtures/crate-performance-envelope-pack-kit/environment-fidelity.receipt.schema.json`
- `fixtures/crate-performance-envelope-pack-kit/noise-class.report.schema.json`
- `fixtures/crate-performance-envelope-pack-kit/release_claim_measured_with_bench_profile/`
- `fixtures/crate-performance-envelope-pack-kit/instruction_count_ci_authoritative_not_walltime/`
- `fixtures/crate-performance-envelope-pack-kit/compat_layer_skips_local_benchmark_semantics/`

Updated:
- `proposals/crate-performance-envelope-pack-kit.md`
- `README.md`
- `INDEX.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/known-existing.md`
- `meta/llm-hygiene.md`

## What this pass deliberately did not do

It did **not** collapse:

- setup/configuration scenarios,
- profiling bundles,
- benchmark frameworks,
- hosted perf services,
- observability surfaces,
- resource contracts,
- and receiver-facing performance-envelope contracts

into one fake “better benchmarking” story.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://doc.rust-lang.org/cargo/commands/cargo-bench.html
- https://doc.rust-lang.org/cargo/reference/profiles.html
- https://blog.rust-lang.org/inside-rust/2024/12/13/this-development-cycle-in-cargo-1.84/
- https://docs.rs/criterion/latest/criterion/
- https://docs.rs/iai-callgrind/latest/iai_callgrind/
- https://docs.rs/crate/divan/latest
- https://docs.rs/crate/codspeed-criterion-compat/latest
- https://docs.rs/crate/codspeed-divan-compat/latest
