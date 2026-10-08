# Design: Resource Evidence Pilot Program (`cargo perf pilot`, `cargo footprint pilot`, `resource-evidence-pack/v0`)

## Goal
Make the archive treat **Perf Labs** and **Footprint Kit** as a shared **Resource Evidence Stack** without flattening them into one mega-tool.

The missing contribution is not another dashboard, another benchmark harness, another size-shrinker, or another one-off CI recipe.
It is a reviewable substrate that lets teams publish, compare, and gate **resource claims** across four related but distinct lanes:
- **compile-workflow cost** (clean / incremental / rebuild / relink-sensitive time),
- **build-state and storage cost** (`target` growth, cache churn, retention pressure, GC candidates),
- **artifact footprint** (binary bytes, section layout, Wasm retained size, stack budgets),
- **runtime resource posture** (allocation and memory evidence, and their relation to performance).

## Why this needs its own design layer
The archive already had strong separate ideas for performance evidence and footprint evidence. Current official Rust signals now make the shared frontier clearer:

1. **The pain is explicitly bundled as "resource usage".** The 2025 State of Rust survey says resource usage — especially slow compile times and storage usage — remains one of the biggest productivity problems. That means the ecosystem pain is not only “make benchmarks better”; it is also “make build/storage/resource costs legible enough to govern.”
   https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
2. **The previous annual survey already named disk usage and binary size as distinct pain surfaces.** The 2024 State of Rust survey calls out high disk usage of compiler artifacts, and the full annual-survey reporting around that cycle also highlighted compiled-artifact size pressure. That is strong evidence that storage and shipped-artifact budgets should not live only as footnotes to runtime benchmarking.
   https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
3. **Cargo is actively restructuring the build directory around storage and cache realities.** The Cargo build-dir-layout goal explicitly ties the new layout to GC of target directories and a future cross-workspace shared build cache. That is a direct signal that build/storage evidence is strategically important, not merely an implementation detail.
   https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
4. **Cargo build-analysis/report work is creating machine-facing inputs for resource review.** The build-analysis goal and the 1.94 Cargo update make `cargo report timings`, `cargo report rebuild`, and `cargo report sessions` increasingly real. That improves the inputs for compile-workflow evidence, but does not by itself define a shared policy/review boundary above them.
   https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
   https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
5. **The compiler-performance effort keeps stressing workflow diversity.** The 2025 compiler-performance survey results say build experience differs wildly across users and workflows, and explicitly foreground the need to understand why builds are slow. That argues for lane-aware evidence rather than one score.
   https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
6. **Rust is also explicitly legitimizing size-sensitive standard-library builds.** The build-std goal names code-size optimization and target-/hardware-specific standard-library builds as real use cases. That makes artifact and section-budget evidence more central, especially for embedded and constrained environments.
   https://rust-lang.github.io/rust-project-goals/2025h2/build-std.html

## Working thesis
A worthy contribution should let a reviewer answer all of these without opening five unrelated tools and three tribal-knowledge docs:
- Which resource lane is being discussed?
- Which configuration, target, and collector produced the evidence?
- Which baseline is in force, and how fresh is it?
- Which dimensions are actually comparable here?
- If a gate fired, was it about time, storage, artifact bytes, stack, or allocation?
- If the result is advisory or inconclusive, why?

## Design principles
1. **Keep time, storage, footprint, and allocation distinct.** They may correlate; they are not one metric.
2. **Build workflows are first-class subjects.** Clean, incremental, rebuild, relink-sensitive, and cold-cache workflows should be named explicitly.
3. **Storage evidence is not a side effect.** `target` size, cache churn, duplication, and GC posture deserve attachable artifacts, not screenshots from a CI cache bill.
4. **Artifact footprint remains multi-dimensional.** Native bytes, section layout, Wasm retained size, stack, and heap evidence must stay explicit.
5. **Collector and tool identity stay first-class.** Cargo reports, Criterion, Iai-Callgrind, `cargo-bloat`, `twiggy`, `cargo-call-stack`, allocator profilers, and custom scripts should compose without pretending they measured the same thing.
6. **Baselines and freshness are part of the evidence.** A stale or mismatched baseline is not hidden metadata.
7. **Adapters come before replacement.** The archive should first unify evidence from the tools Rust already has.

## Shared artifact posture
The stack should preserve two neighboring but distinct pack families:
- **`perf-pack/v0`** for measurement lanes, collectors, comparisons, and policy verdicts.
- **`footprint-pack/v0`** for budgets, measurement coverage, deltas, and resource-specific caveats.

A later **`resource-evidence-pack/v0`** can bundle references to both when a review genuinely needs cross-lane conclusions. It should not replace them.

That bundle should only summarize:
- subject identity,
- shared configuration ids,
- baseline ids,
- linked perf and footprint reports,
- optional resource-level verdicts,
- and reason-coded cross-links such as `RSC:BUILD-STORAGE-GROWTH`, `RSC:TEXT-GROWTH-CORRELATED`, or `RSC:ALLOC-LANE-MISSING`.

## Recommended pilot order

### Pilot 1 — Compile-workflow + build-storage lane
Use Cargo-native inputs to attach compile-time and storage evidence for everyday developer workflows.

Must prove:
- clean / incremental / rebuild-sensitive workflows can be named explicitly;
- `cargo report timings` / `rebuild` / `sessions` can feed one review boundary;
- build-dir or target-dir growth can be recorded alongside time results without collapsing them into one score;
- reviewers can see whether a change regressed time, storage, or both;
- GC or retention follow-up work has a durable artifact to point at.

Why first:
- this is where official Cargo motion is strongest right now;
- it directly matches the survey pain around compile time and storage;
- it composes with Build Cache / Change Impact / Build Doctor.

### Pilot 2 — Native release-artifact lane
Use a CLI or service binary to combine runtime/compile evidence with shipped-artifact budgets.

Must prove:
- `.text`, `.rodata`, symbol hot spots, and debug-info policy can be compared against explicit release baselines;
- time regressions can point to footprint evidence without pretending footprint *caused* them;
- release reviews can attach one pack family rather than bespoke markdown tables.

Why second:
- it reaches a broad set of Rust users;
- it helps connect “slow builds” and “big binaries” without conflating them.

### Pilot 3 — Constrained-target lane (embedded / Wasm)
Use one embedded firmware or Wasm project where size, stack, and code-size-oriented std/profile choices matter.

Must prove:
- section budgets, stack evidence, Wasm retained-size, and target/profile/sysroot assumptions stay explicit;
- code-size-optimized stdlib or target-specific profile choices can be recorded honestly;
- unsupported coverage remains visible instead of silently omitted.

Why third:
- this is where resource truth is often most operationally important;
- it stress-tests the schema against non-hosted, non-CLI assumptions.

### Pilot 4 — Runtime allocation lane
Use one service or long-running binary with allocator/runtime memory evidence.

Must prove:
- heap/allocation evidence can link to performance and artifact packs without becoming the same artifact;
- allocator-specific, sampled, or partial coverage is visible;
- policy can say “allocation lane missing” without claiming the whole resource review failed.

Why fourth:
- it exercises the hardest “resource” lane without letting it dominate the model too early.

### Pilot 5 — Federated resource-review lane
Use multiple collectors/platforms/targets and prove the review boundary remains honest.

Must prove:
- results default to within compatible collector / target / footprint-coverage classes;
- summary bundles can represent conflicting or non-comparable evidence without forced aggregation;
- dashboards and release systems can ingest linked packs without redefining the schema.

Why fifth:
- strategically valuable, operationally heavy;
- only worth doing after the earlier lanes prove the artifact family is actually useful.

## Shared discipline rules
Every pilot must keep these pairs distinct:
1. **build time** vs **build storage**
2. **artifact footprint** vs **runtime allocation evidence**
3. **observed result** vs **policy verdict**
4. **portable summary** vs **large raw attachments**
5. **correlation** vs **causation claim**

## Immediate archive consequences
Read this file together with:
- [`design/perf-labs.md`](./perf-labs.md)
- [`design/perf-pilot-program.md`](./perf-pilot-program.md)
- [`design/footprint-kit.md`](./footprint-kit.md)
- [`design/build-cache-kit.md`](./build-cache-kit.md)
- [`design/change-impact-kit.md`](./change-impact-kit.md)
- [`design/build-doctor-kit.md`](./build-doctor-kit.md)
- [`design/config-set-kit.md`](./config-set-kit.md)
- [`design/release-pipeline-kit.md`](./release-pipeline-kit.md)

The archive should now prefer:
- **compile/storage resource pilots first**,
- **adapter-heavy evidence convergence before new engines**,
- **shared configuration and baseline ids across perf + footprint lanes**,
- and **cross-linked review artifacts** over all-in-one dashboards or fake universal resource scores.

## What should wait
Do **not** start with:
- one universal “resource score”,
- a hosted service that tries to own every benchmark and size report,
- automatic causal claims from time changes to size changes,
- or a plan to replace Criterion / Iai / Cargo reports / size tools all at once.

Those are possible consumers or later layers. They are not the missing substrate.
