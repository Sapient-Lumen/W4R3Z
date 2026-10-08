# Design: Build Doctor Kit (`cargo builddoctor`, `build-doctor-pack/v0`)

## Goal
Define a portable contract for identifying, validating, diffing, and reviewing **Rust build-performance diagnoses and actionable suggestions** across the workflows people actually use: incremental rebuilds, `cargo check`, IDE feedback, clean CI builds, and debugger-oriented development builds.

This should sit **above** Cargo’s raw report/plumbing surfaces and **below** ad hoc blog posts, dashboards, and one-off advice.
It should not replace Cargo, rustc, rust-analyzer, Criterion, or profiler tools.
It should make build-performance troubleshooting reviewable.

## References (signals)
- 2025 compiler performance survey: long compile times remain a major pain point; the hardest workflows are incremental rebuilds, IDE/type-check latency, and clean/CI builds.
  https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- The same survey explicitly calls for tooling that explains what was recompiled, what macros are costly, and what suggestions follow.
  https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- Cargo build-analysis goal: record timing/rebuild metadata across invocations and eventually offer richer insights and actionable suggestions.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Cargo 1.94 development cycle: `cargo report rebuild`, `cargo report sessions`, and improved timings are landing as real observation surfaces.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Cargo build performance guide: official recommendations already exist, but they are workflow-dependent and full of trade-offs.
  https://doc.rust-lang.org/nightly/cargo/guide/build-performance.html
- Cargo build-dir relayout and user-wide cache work make cache/locking/build-layout diagnosis an ecosystem-level concern rather than private expert knowledge.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
  https://rust-lang.github.io/rust-project-goals/2024h2/user-wide-cache.html

## Design principles
1. **Diagnose by workflow, not by one global score.**
   A fix that helps `cargo build` may hurt `cargo check` or debugger workflows.
2. **Keep observation separate from interpretation.**
   Raw timings, rebuild reasons, lock waits, and configuration state should remain attachable evidence, not disappear into one opaque heuristic.
3. **Suggestions must declare trade-offs.**
   Every recommendation should say what it may worsen: debuggability, runtime performance, target coverage, CI reproducibility, or bug-finding power.
4. **Make inconclusive results first-class.**
   Many slow builds are mixed-cause or noisy; the right answer should sometimes be “collect more evidence.”
5. **Prefer convergence over replacement.**
   Reuse Cargo reports, self-profile-like data, linker timings, rust-analyzer coordination facts, and official guidance instead of inventing a rival universe.

## Artifact family

### 1) `build-workflow-profile/v0`
Describes the workflow being optimized.

Fields should include:
- workflow id (`incremental-rebuild`, `cargo-check-loop`, `ide-annotations`, `clean-ci`, `debug-dev`, `release-ci`, etc.)
- user goals (fastest feedback, lowest disk usage, debugger-ready artifacts, stable CI throughput, etc.)
- acceptable trade-offs
- target/profile/toolchain context
- selection rationale

This prevents advice from pretending there is one universal “fast build” mode.

### 2) `build-observation-pack/v0`
Portable raw observations and attachments.

Fields should include:
- Cargo session ids / run ids where available
- timings and critical-path data
- rebuild reasons
- link-time observations
- target-dir / cache / lock-contention observations when available
- CLI/config/profile/environment metadata relevant to build behavior
- optional richer attachments:
  - self-profile outputs
  - proc-macro timing attachments
  - rust-analyzer / editor coordination observations
  - CI cache stats

This is the source-truth layer for later diagnosis.

### 3) `build-bottleneck-profile/v0`
A normalized vocabulary for bottleneck classes and confidence.

Example classes:
- `WORKSPACE_REBUILD_FANOUT`
- `LINK_DOMINATED`
- `DEBUGINFO_DOMINATED`
- `CHECK_BUILD_DUPLICATION`
- `PROC_MACRO_EXPANSION_HEAVY`
- `BUILD_SCRIPT_CHURN`
- `FEATURE_THRASH`
- `DEPENDENCY_BLOAT`
- `LOCK_CONTENTION`
- `CACHE_MISS_CHURN`
- `CLEAN_BUILD_HEAVY_DEP_GRAPH`
- `INSUFFICIENT_EVIDENCE`

For each class:
- confidence
- supporting evidence ids
- affected workflows
- known caveats

### 4) `build-suggestion-catalog/v0`
Structured suggestions tied to bottlenecks and trade-offs.

Each suggestion should include:
- suggestion id
- applicable bottleneck classes
- expected benefit lanes (`link-time`, `incremental`, `check-loop`, `disk-usage`, `CI-cacheability`)
- expected trade-offs (`debug-quality`, `runtime-speed`, `nightly-only`, `target-coverage`, `C/C++-interop-risk`, `bug-masking-risk`)
- source of suggestion (`official-cargo-guide`, `cargo-team-goal`, `ecosystem-tool`, `project-local-policy`)
- required evidence threshold
- follow-up measurement plan

Examples:
- reduce debuginfo in `dev`
- use alternate linker
- try Cranelift in `dev`
- enable parallel frontend on nightly
- unify workspace feature resolution
- remove unused deps/features
- separate debugger profile from default dev profile
- split selected workspace crates or reduce high-fanout edit paths

### 5) `build-diagnosis-report/v0`
The review artifact users actually consume.

Fields should include:
- selected workflow profile
- top bottleneck classes, ranked
- evidence references
- suggestions with trade-off metadata
- expected-confidence statement
- “what to measure next” section
- comparison to baseline / previous report when available

### 6) `build-doctor-pack/v0`
Bundle of workflow profile, observations, diagnosis report, attached raw artifacts, and human-readable explanation.

## CLI shape
`cargo builddoctor` should start as an adapter/orchestrator.

Potential commands:
- `cargo builddoctor record`
- `cargo builddoctor diagnose --workflow <id>`
- `cargo builddoctor suggest --workflow <id>`
- `cargo builddoctor diff <old-pack> <new-pack>`
- `cargo builddoctor pack`

The first credible version should import existing Cargo surfaces and only then add deeper adapters.

## What the kit should provide to others
- **Developers:** a concrete answer to “why is this workflow slow?”
- **Maintainers:** reproducible build-latency reports attached to PRs and issues.
- **CI/infrastructure teams:** machine-readable suggestions instead of manually reading timing HTML and logs.
- **Cargo and tool authors:** one place to attach emerging diagnostics without freezing every upstream internal format.
- **Editors/IDEs:** a shared artifact for explaining build/check contention and feedback latency.

## Initial target scope
Start where the official signals are strongest:
1. `cargo report timings` + `cargo report rebuild`
2. workflow profiles for incremental rebuilds, `cargo check`, and clean CI
3. official Cargo build-performance-guide suggestions as structured suggestions
4. link-time, debuginfo, feature/dependency, and cache/lock-contention diagnosis

Later versions can add:
- proc-macro-heavy workflow diagnosis,
- rust-analyzer coordination adapters,
- richer self-profile and memory observations,
- project-specific heuristics.


## Shared stack role
This kit is now one leg of the archive’s shared **Build-State Evidence Stack**:
- [`design/build-state-evidence-stack.md`](./build-state-evidence-stack.md)
- [`design/build-state-evidence-pilot-program.md`](./build-state-evidence-pilot-program.md)

That means future revisions should treat Build Doctor Kit as the **diagnosis and suggestion** layer that imports build-cache and change-impact facts, not as a replacement for them.

## Boundaries with nearby archive proposals
- **Cargo Report Kit** owns raw report schemas and report packs; Build Doctor Kit consumes them and emits diagnoses.
- **Build Cache Kit** owns cache storage/reuse/GC/reporting; Build Doctor Kit explains when cache behavior is the problem.
- **Perf Labs** owns runtime performance evidence; Build Doctor Kit owns compile/build feedback-loop evidence.
- **Compile Guidance Kit** owns crate-authored compile-time diagnostics and lint/help surfaces; Build Doctor Kit owns diagnosis of the build pipeline itself.
- **Build Interop Kit** owns discovery/graph/plan/event contracts; Build Doctor Kit is a higher-level consumer of those contracts.

## Failure modes to avoid
- a fake single build score that ignores workflow differences,
- cargo-report parsing with no attached raw evidence,
- suggestions without trade-off declarations,
- overfitting to one OS/linker/toolchain,
- or pretending one diagnosis engine can replace upstream Cargo work.
