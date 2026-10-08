> Revision note (rev0452): read this pilot order now beneath `design/benchmark-evidence-execution-blueprint-2026Q1.md`; the proving goal is lane/baseline/comparability honesty before wider policy or hosted-product expansion.

# Design: Benchmark Evidence Pilot Program (`cargo benchpack pilot`, `benchmark-pilot-pack/v0`)

## Goal
Turn the archive’s benchmark-evidence idea into a ranked rollout instead of a permanently plausible layer sitting between testing and performance.

A worthy contribution here is not a rewrite of Cargo benchmarking, Criterion, Divan, Iai-Callgrind, nextest, or CodSpeed.
It is a staged proof that Rust can publish **benchmark-native evidence** across unlike harnesses, runners, profiler lanes, and hosted adapters before broader compare/gate layers try to absorb them.

## Why this needs a pilot layer
The current ecosystem already has all the ingredients needed to drift into confusion:
- Cargo’s benchmark foundation is still partly unstable and partly custom-harness-driven.
- Criterion native baselines and `cargo-criterion` JSON export are already different lanes.
- Divan makes counter semantics explicit.
- nextest adds a runner-import lane.
- Iai-Callgrind adds deterministic profiler metrics and raw attachments.
- CodSpeed adds hosted compatibility layers and measurement modes on top.

That means the boundary only becomes real if it survives actual cross-lane adoption.

Sources:
https://doc.rust-lang.org/cargo/commands/cargo-bench.html
https://nexte.st/docs/features/benchmarks/
https://bheisler.github.io/criterion.rs/book/user_guide/command_line_options.html
https://bheisler.github.io/criterion.rs/book/cargo_criterion/cargo_criterion.html
https://docs.rs/divan/latest/divan/counter/index.html
https://docs.rs/iai-callgrind/latest/iai_callgrind/
https://codspeed.io/docs/benchmarks/rust
https://codspeed.io/docs/reference/codspeed-rust/cargo-codspeed

## Ranked pilot order

### Pilot 1 — Stable local harness pair
Use two materially different stable local benchmark lanes, such as Criterion native and Divan.

Must prove:
- benchmark subjects can be named consistently across suites/groups/cases;
- Criterion-native baseline posture stays explicit;
- Divan-style counter semantics stay explicit;
- one portable `benchmark-pack/v0` can carry results from unlike stable lanes without forcing a fake common denominator.

Why first:
- it reaches ordinary Rust libraries quickly;
- it stress-tests subject, baseline, and lane schemas before runner imports complicate them;
- it prevents the pack from becoming “Criterion JSON with extra steps”.

### Pilot 2 — Runner-import lane
Use `cargo nextest bench` as the first serious runner import.

Must prove:
- benchmark-specific timeout/setup/wrapper posture can be preserved;
- imported runner semantics stay explicit instead of becoming native benchmark truth;
- benchmark packs can point back to generic run evidence without flattening into it;
- custom-harness protocol users remain representable.

Why second:
- it tests the most live benchmark-runner seam in today’s ecosystem;
- it proves that benchmark truth can survive an import boundary.

### Pilot 3 — Deterministic profiler lane
Use Iai-Callgrind or another Valgrind-backed benchmark family.

Must prove:
- deterministic instruction/callgrind/cache/heap lanes can live beside statistical timer lanes without semantic collapse;
- raw attachments such as callgrind or DHAT outputs can be linked cleanly;
- native differential reports can be imported without claiming they are the whole benchmark policy layer.

Why third:
- it proves the design works for serious CI-facing lanes;
- it keeps deterministic profiler evidence from being backfilled awkwardly later.

### Pilot 4 — Hosted adapter lane
Use CodSpeed with at least one compatibility layer.

Must prove:
- hosted/imported baselines can be recorded honestly;
- `simulation`, `walltime`, and `memory` modes remain explicit measurement lanes;
- compatibility-layer passthrough behavior is visible;
- hosted orchestration does not destroy benchmark subject truth or erase the local harness family.

Why fourth:
- it tests the boundary where local benchmark code meets hosted-service workflow;
- it is strategically important but should not define the base schema by itself.

### Pilot 5 — Perf Labs handoff lane
Use benchmark packs as inputs to broader performance review.

Must prove:
- benchmark-native packs can feed compare/gate consumers without losing lane/counter/baseline nuance;
- compile-workflow or service-scenario performance review can remain distinct from benchmark-native evidence;
- the import boundary between Benchmark Evidence Kit and Perf Labs is smaller and cleaner than raw tool re-parsing.

Why fifth:
- it validates the stack architecture rather than just the leaf kit;
- it is where the contribution becomes clearly ecosystem-wide.

## Shared schema discipline
Every pilot must keep these pairs distinct:
1. **Cargo launch truth** vs **benchmark-engine semantics**
2. **native benchmark semantics** vs **generic run recording**
3. **measurement lane/counter semantics** vs **compare/gate policy**
4. **native baseline** vs **imported/hosted baseline**
5. **portable summary** vs **tool-native raw attachments**

## Immediate archive consequences
Read this together with:
- [`design/benchmark-evidence-lane-map.md`](./benchmark-evidence-lane-map.md)
- [`design/benchmark-evidence-kit.md`](./benchmark-evidence-kit.md)
- [`design/harness-protocol-kit.md`](./harness-protocol-kit.md)
- [`design/test-run-evidence-kit.md`](./test-run-evidence-kit.md)
- [`design/perf-labs.md`](./perf-labs.md)
- [`proposals/epic-benchmark-evidence-kit.md`](../proposals/epic-benchmark-evidence-kit.md)

The archive should now prefer:
- **benchmark evidence importers before new runners**,
- **lane and baseline honesty before universal performance scores**,
- and **benchmark-native packs before hosted-dashboard abstractions**.

## What should wait
Do **not** start with:
- another benchmark harness,
- one hosted benchmark service pretending to be the standard,
- a fake universal benchmark score,
- or a plan to merge all performance evidence into one mega-pack immediately.

Those may become consumers later. They are not the missing substrate.
