# Gap: Build performance diagnosis and actionable guidance are still too fragmented

## Summary
Rust is getting better raw build telemetry, better caching plans, and better documentation. But the ecosystem still lacks a **portable diagnosis-and-guidance layer** that can answer, with evidence:
- which workflow is actually hurting (`cargo check`, incremental rebuild, IDE annotations, clean CI build, debugger-oriented dev build),
- what the dominant bottleneck class is (workspace fanout, link time, proc-macro expansion, debuginfo, cache thrash, lock contention, dependency bloat, build-script churn, check-vs-build duplication),
- which changes are worth trying next,
- and what trade-offs those changes buy or impose.

That missing layer is not another benchmark engine, not just more JSON from Cargo, and not a blog post full of generic tips.
It is a **reviewable build-doctor substrate** that consumes existing observations, classifies bottlenecks, and emits evidence-backed suggestions tied to the workflow the user actually cares about.

## Why now
- The Rust compiler performance survey says build performance still materially limits productivity, and around 45% of respondents who stopped using Rust cited long compile times as at least one reason. It also says the most painful workflows are incremental rebuilds, editor/IDE type-check latency, and clean/CI builds.
  https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- The same survey says `cargo check` / `cargo build` cache non-sharing is a real pain point, around 33% of users find waiting for inline editor diagnostics a big blocker, more than 35% view IDE/Cargo blocking one another as a big problem, and very few users use profiling tools because the existing surfaces are hard to interpret.
  https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- The survey also says users want tooling that can explain which code had to be recompiled, which macros are costly, and what actionable suggestions follow from the data.
  https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- Cargo’s accepted/proposed work is converging on exactly the raw ingredients a doctor layer would need: user-wide build cache, build-dir relayout, reduced lock contention, and `cargo report` build-analysis commands with rebuild reasons, timing history, and future actionable suggestions.
  https://rust-lang.github.io/rust-project-goals/2024h2/user-wide-cache.html
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- The Cargo 1.94 development-cycle report says structured logging work has added `cargo report rebuild`, `cargo report sessions`, and more timing support. That is real progress on observation plumbing, but it is still not the same thing as stable diagnosis artifacts or tradeoff-aware recommendations.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- The Cargo book now has an official “Optimizing Build Performance” chapter with concrete recommendations such as reducing debuginfo, trying Cranelift, enabling the parallel frontend, using alternate linkers, and resolving features for the whole workspace — and it repeatedly emphasizes trade-offs and workflow-specific evaluation. That is strong evidence the missing contribution is a reusable decision layer over evidence, not just another tip list.
  https://doc.rust-lang.org/nightly/cargo/guide/build-performance.html
- That guidance chapter is tracked as an explicit Cargo issue, which further shows this is an active product surface rather than off-to-the-side folklore.
  https://github.com/rust-lang/cargo/issues/16119

## Concrete missing pieces
1. **Workflow-aware diagnosis**
   - distinguish `cargo check` latency from `cargo build` latency,
   - distinguish incremental edit-build loops from clean CI builds,
   - distinguish debugger-heavy dev workflows from backtrace-only workflows.
2. **Portable bottleneck classifications**
   - link-dominated builds,
   - workspace rebuild fanout,
   - proc-macro / build-script churn,
   - cache-miss / target-dir / lock-contention pathologies,
   - debug-info dominated builds,
   - feature/dependency bloat,
   - check/build duplication.
3. **Evidence-backed suggestions with tradeoffs**
   - not “use mold” in the abstract,
   - but “linker dominates this workflow; alternate linker or debuginfo reduction is likely high leverage here, with stated debugger / C-interop tradeoffs”.
4. **History and comparison artifacts**
   - compare today’s build to last week’s,
   - explain why a workspace became slower,
   - and keep raw observations attached instead of reducing everything to one score.
5. **Composability with current Cargo direction**
   - consume `cargo report` outputs,
   - import timing / rebuild / session context,
   - stay above build-cache and build-dir-layout work instead of competing with it.

## Why this matters
1. **The ecosystem is moving from “no data” to “too many partial data surfaces.”**
   The next missing piece is not more raw telemetry by itself; it is a stable way to turn observations into useful, reviewable advice.
2. **Build-performance advice is full of trade-offs.**
   The official Cargo guide makes this explicit: faster builds often trade off runtime performance, debug fidelity, target coverage, or bug-finding posture. Those trade-offs need first-class artifacts.
3. **This is leverage, not niche tooling.**
   Better build diagnosis helps application teams, library maintainers, CI owners, IDE integrations, and Cargo itself.
4. **The archive already has adjacent layers but not this one.**
   Cargo Report Kit handles raw reports; Build Cache Kit handles reuse; Build Interop Kit handles discovery/plan/event contracts; Perf Labs handles runtime/perf evidence. None of those is the portable diagnosis-and-recommendation surface for compile/build latency.

## A worthy contribution here would
- define versioned workflow and bottleneck vocabularies,
- ingest Cargo report data plus optional richer attachments,
- attach rule- and evidence-based suggestions with explicit tradeoffs,
- make “inconclusive” or “mixed signals” a first-class result,
- and give CI, editors, and humans one shared artifact for “why are my Rust builds slow, and what should I try next?”

## Distinction from nearby archive entries
- **Cargo Report Kit** owns portable raw timing/rebuild/session artifacts; this gap is about interpreting those artifacts into diagnoses and suggestions.
- **Build Cache Kit** owns cache reuse and GC policy; this gap is about diagnosing when cache behavior is the bottleneck and what to try next.
- **Build Interop Kit** owns discovery/graph/plan/event contracts; this gap is about workflow-aware build-latency diagnosis above those contracts.
- **Perf Labs** owns runtime/performance workload evidence; this gap is about compile/build feedback loops.
- **Compile Guidance Kit** owns developer-facing compile diagnostics and lint/help surfaces emitted by crates/tools; this gap is about diagnosing Cargo/rustc build behavior itself.
