# Frontier salience snapshot — 2026-03-19 (82)

This pass did **not** add another benchmark runner, another profiler UI, another performance dashboard, or another hosted regression service.
It sharpened a top-ranked support-surface lane:

- **P-0517 Crate Performance Envelope Pack Kit** — because Rust now has real benchmark/profile/CI substrate, but still lacks one boring receiver-facing contract for **metric authority**, **execution intent**, **workload lineage**, **profile identity**, and **noise class**.

## Main judgment

The next worthy move here was **not** more benchmarking substrate.
That substrate already exists.

The sharper missing layer is the **joined performance-support contract** above today’s substrate, especially once five facts stay explicit:

- **metric-authority truth** — which number rules a scenario,
- **execution-intent truth** — whether the run was measuring, smoke-checking, replaying, or merely importing evidence,
- **workload-lineage truth** — where the input shape came from and whether it is representative,
- **profile-identity truth** — which Cargo profile / harness / optimizer story actually produced the evidence,
- **noise-class truth** — what trust level the result deserves.

That move is better grounded now because:

- the Rust vision-doc work explicitly calls for **supportive interfaces from crates**;
- the 2025 State of Rust survey still says online docs and code are the main learning surfaces and still names resource usage as a recurring pain point;
- Cargo’s current `cargo bench` docs still make `bench`-profile defaults and `harness = false` boundaries explicit;
- Cargo profiles still make custom profiles and profile-specific optimizer/debug-symbol choices explicit;
- Criterion is still strong stable-compatible wall-time measurement substrate;
- Iai-Callgrind is still especially useful for CI-friendly instruction-count evidence;
- Divan still exposes throughput counters and allocation profiling substrate;
- CodSpeed compatibility layers still preserve suite structure without guaranteeing that every environment produced a real measurement;
- `cargo-nextest` now makes the measurement-vs-test-mode boundary explicit for Criterion benchmarks.

So the gap is no longer “Rust lacks perf tools”.
The gap is that teams still rarely get a **reviewable crate-authored performance promise** above those pieces.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually use?”
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because start/stop truth is so often missing.
3. **P-0522 Crate Persistence Surface Pack Kit** — still one of the sharpest support-surface lanes now that durable-state promises are specific.
4. **P-0521 Crate Resource Surface Pack Kit** — still a strong support lane because waiting-room truth is concrete now.
5. **P-0524 Crate Example Surface Pack Kit** — still a strong first-success lane.
6. **P-0523 Crate Test Surface Pack Kit** — now much stronger because support-level and evidence-lineage truth are concrete.
7. **P-0517 Crate Performance Envelope Pack Kit** — now much stronger because measurement intent and workload lineage are finally explicit rather than implied.
8. **P-0525 Crate Diagnosis Surface Pack Kit** — still a strong first-diagnosis lane.
9. **P-0484 Toolchain & Target Support Contract Kit** — still crucial for real machines and real targets.
10. **P-0483 Public API Readiness Bundle Kit** — still a strong joined release-review lane.
11. **P-0519 Crate Authority Surface Pack Kit** — still one of the strongest adoption-trust lanes.
12. **P-0027 text-input-kit** — still one of the clearest end-user product-engineering opportunities.

## Why this won over adjacent candidates right now

- It beat a deeper **P-0518** pass because the support stack still needed a more concrete answer for “was this actually a performance measurement, or only a benchmark-sanity run?” before another observability-support refinement.
- It beat a deeper **P-0519** pass because trust about ambient authority matters, but today’s benchmark/profile substrate makes performance-support contracts unusually buildable right now.
- It beat more **foreign-package shipping** work because the archive already has many fresh release-contract passes and still needed a stronger core supportiveness lane.
- It beat more **pathfinder** work because ecosystem choice is already strong enough that the archive now benefits more from tightening what happens *after* a crate is chosen and somebody asks “what performance claim should I trust?”

## What changed in the archive

Added:
- `entries/2026-03-19-262.md`
- `meta/frontier-salience-2026-03-19-82.md`
- `meta/crate-performance-envelope-product-plan-2026-03-19.md`
- `fixtures/crate-performance-envelope-pack-kit/README.md`
- `fixtures/crate-performance-envelope-pack-kit/execution-intent.report.schema.json`
- `fixtures/crate-performance-envelope-pack-kit/workload-lineage.receipt.schema.json`
- `fixtures/crate-performance-envelope-pack-kit/nextest_criterion_test_mode_checks_compile_and_panic_not_budget/`
- `fixtures/crate-performance-envelope-pack-kit/custom_profile_changes_benchmark_story/`
- `fixtures/crate-performance-envelope-pack-kit/codspeed_unknown_environment_checks_suite_without_measurement/`
- `fixtures/crate-performance-envelope-pack-kit/captured_trace_sets_authoritative_workload_lineage/`
- `fixtures/crate-performance-envelope-pack-kit/divan_alloc_budget_metric_overrules_wall_time/`

Updated:
- `README.md`
- `INDEX.md`
- `proposals/crate-performance-envelope-pack-kit.md`
- `meta/known-existing.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/epic-crate-portfolio-2026-03-18.md`
- `meta/llm-hygiene.md`
