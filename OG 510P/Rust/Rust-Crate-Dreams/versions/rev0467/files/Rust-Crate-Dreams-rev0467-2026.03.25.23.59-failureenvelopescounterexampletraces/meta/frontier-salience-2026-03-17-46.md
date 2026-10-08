# Frontier salience snapshot — 2026-03-17 (46)

This pass did **not** promote a new lane.
It sharpened an existing cross-cutting proposal:

- **P-0084 Memory Observability Kit** — because the archive still lacked a good implementation-ready artifact for the ordinary question that sits between “we know memory is weird here” and “we can hand another engineer one reviewable bundle explaining what moved, what was measured, and how trustworthy the evidence is”.

## Main judgment

The next worthy move in this frontier was **not** another allocator, another one-off profiler wrapper, another pretty flamegraph helper, or another hosted dashboard.
Those pieces already exist in partial form or answer a narrower layer.

The sharper missing layer is the **memory-evidence contract** above them:

- capture-scope policies,
- symbolization-fidelity reports,
- backend-capability receipts,
- regression-gate policies,
- redaction posture,
- and release-to-release memory diffs.

That move is now better grounded because:

- the Rust vision-doc work explicitly treats supportive interfaces from crates as part of Rust’s product experience,
- the 2025 State of Rust survey still reports resource usage as a recurring productivity problem while debugging remains notable,
- `leaktracer` is explicit that plug-and-play allocator interception is already feasible,
- `dhat` is explicit that heap profiling in Rust already exists as a scoped global-allocator workflow with a clear profile lifetime,
- `tikv-jemalloc-ctl` is explicit that allocator statistics and heap dumps already have a Rust-facing control surface,
- and `jemalloc_pprof` shows that allocator-side heap profiling can already be exported into a widely-used profile format.

So the gap is no longer “Rust has zero ways to look at memory”.
The gap is that teams still rarely get a **reviewable capture / fidelity / gate artifact** above today’s tools.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually reach for?”
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still one of the best support-truth lanes once a crate is chosen.
3. **P-0484 Toolchain & Target Support Contract Kit** — still one of the strongest “real machines, real targets” support lanes.
4. **P-0519 Crate Authority Surface Pack Kit** — still one of the most believable ambient-power review lanes.
5. **P-0451 Cfg Availability Ledger Kit** — still a highly leverageful way to make conditional API truth reviewable.
6. **P-0521 Crate Resource Surface Pack Kit** — still one of the best capacity/support contracts in the frontier.
7. **P-0517 Crate Performance Envelope Pack Kit** — still a strong workload/metric honesty lane.
8. **P-0084 Memory Observability Kit** — now a much more believable `0.1` crate for heap evidence, capture boundaries, and regression review.
9. **P-0472 Docs.rs Build Parity Evidence Kit** — still a critical build-surface lane, but narrower than the cross-runtime memory-evidence need.

## Why this won over adjacent candidates right now

- It beat **more performance-envelope follow-ons** because a trusted metric is different from a trusted memory investigation bundle.
- It beat **more resource-surface follow-ons** because steady-state capacity promises are different from dynamic attribution and regression evidence.
- It beat **more observability-surface follow-ons** because emitted signals are different from heap evidence collected under explicit profiling scope.
- It beat several strong **domain workbenches** because memory investigation pain cuts across services, CLIs, async systems, libraries, and constrained deployments rather than one protocol family at a time.

## What changed in the archive

Added:
- `meta/memory-observability-product-plan-2026-03-17.md`
- `meta/frontier-salience-2026-03-17-46.md`
- `entries/2026-03-17-226.md`
- `fixtures/memory-observability-kit/README.md`
- `fixtures/memory-observability-kit/capture-scope.policy.schema.json`
- `fixtures/memory-observability-kit/symbolization-fidelity.report.schema.json`
- `fixtures/memory-observability-kit/regression-gate.policy.schema.json`
- `fixtures/memory-observability-kit/alloc_count_flat_but_peak_rss_regresses/`
- `fixtures/memory-observability-kit/dhat_scope_guard_ends_before_background_phase/`
- `fixtures/memory-observability-kit/jemalloc_stats_present_but_callsite_attribution_missing/`

Updated:
- `proposals/memory-observability-kit.md`
- `README.md`
- `INDEX.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/known-existing.md`
- `meta/llm-hygiene.md`

## What this pass deliberately did not do

It did **not** collapse:

- crate-authored resource-surface contracts,
- performance-envelope metric authority,
- general observability signal design,
- allocator choice/tuning crates,
- jemalloc-specific tooling,
- or hosted profiler products

into one fake “memory profiling solved” story.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://docs.rs/leaktracer/latest/leaktracer/
- https://docs.rs/dhat/latest/dhat/
- https://docs.rs/dhat/latest/dhat/struct.Profiler.html
- https://docs.rs/tikv-jemalloc-ctl/latest/tikv_jemalloc_ctl/
- https://docs.rs/jemalloc_pprof/latest/jemalloc_pprof/
