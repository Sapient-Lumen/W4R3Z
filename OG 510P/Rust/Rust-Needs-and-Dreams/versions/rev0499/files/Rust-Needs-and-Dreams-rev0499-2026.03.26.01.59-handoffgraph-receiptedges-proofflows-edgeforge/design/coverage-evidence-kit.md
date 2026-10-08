# Design: Coverage Evidence Kit (`cargo cov`, `coverage-pack/v0`)

## Goal
Create a Cargo-native, criterion-aware coverage evidence layer that makes it easy to define what “coverage” means for a project, attach execution truth, collect results from existing tools, merge them honestly, and attach portable review artifacts to CI, pull requests, releases, and later safety-critical consumers. This layer should stay explicitly **lane-aware**: the archive should keep official LLVM baseline coverage, Cargo-native LLVM orchestration, nextest+doctest merges, external/FFI imports, Tarpaulin contrast, and future decision/MC/DC imports distinct instead of compressing them into one verdict.

This should **converge** the ecosystem rather than replace it: the official `-C instrument-coverage` flow, `cargo-llvm-cov` as the likely reference UX for source-based coverage, Tarpaulin where its workflow remains useful, and existing output formats such as LCOV/Cobertura/JSON.

## References (signals)
- rustc codegen docs: `-C instrument-coverage` is stable, but the produced profile data is not promised to work with tools other than those shipped with the compiler.
  https://doc.rust-lang.org/rustc/codegen-options/index.html#instrument-coverage
- rustc coverage chapter: the official workflow exists, includes doc-test handling details, and exposes the low-level mechanics a kit needs to absorb honestly.
  https://doc.rust-lang.org/rustc/instrument-coverage.html
- Rust’s 2026 flagship roadmap explicitly includes **MC/DC coverage support** under **Safety-Critical Rust** and **better test tooling** under **Building blocks**.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The January 2026 safety-critical adoption post says industry participants are organizing around upstream MC/DC support.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- `cargo-llvm-cov` already provides a practical wrapper around the official flow with JSON/LCOV/Cobertura/Codecov export, proc-macro support, external-test support, optional doctest / branch coverage paths, `cargo nextest`, and C/C++ coverage merging.
  https://github.com/taiki-e/cargo-llvm-cov
- nextest’s coverage docs explicitly say doctest coverage must be merged separately because nextest does not currently support doctests.
  https://nexte.st/docs/integrations/test-coverage/
- Tarpaulin remains a widely used Cargo coverage tool with a materially different engine model and platform story; its 0.35.0 changelog also says delta coverage should not be reported when configuration changes would make a comparison meaningless.
  https://github.com/xd009642/tarpaulin
  https://docs.rs/crate/cargo-tarpaulin/latest/source/CHANGELOG.md
- The 2025 State of Rust survey still shows that users care a lot about tooling productivity and that documentation remains canonical; a coverage kit should therefore optimize for explainability and CI trust, not just percentages.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

Read this together with `design/coverage-evidence-lane-map.md`, which now names the concrete coverage lanes the kit must preserve.

## Core components

### 1) `coverage-manifest/v0`
A manifest for project coverage intent:
- targets to include: `lib`, `bins`, `examples`, `tests`, `doctests`, `benches`
- allowed engines: `llvm`, `tarpaulin`, `external`
- include / exclude rules
- merge policy
- per-path or per-module policy classes

Design rule: coverage starts from **declared intent**, not accidental defaults.

### 2) `coverage-criterion-profile/v0`
Explicit definition of what criterion the result is allowed to claim:
- criterion class (`line`, `region`, `branch`, `decision`, `mcdc`, `mixed`, `watch-only`)
- direct-measurement vs imported or future-facing posture
- engine/toolchain support expectations
- known blind spots
- comparability expectations

Design rule: the criterion ladder must be explicit before any percentage is reviewed.

### 3) `coverage-execution-import/v0`
Portable reference to what execution produced the raw coverage inputs:
- execution source (`cargo-test`, `cargo-nextest`, `cargo-run`, `external`, `runner-recording-import`, `other`)
- imported `test-exec-pack/v0`, runner-native recording, or raw-artifact pointers
- subset / shard selection notes
- known lossiness
- authoritative vs advisory posture

Design rule: coverage cannot quietly redefine what ran.

### 4) `coverage-report/v0`
Portable result artifact:
- producing lane (`llvm-baseline`, `cargo-llvm-cov`, `nextest-doctest-merge`, `external-ffi-import`, `tarpaulin-contrast`, `decision-mcdc-watch`, or later registered lane ids)
- engine and version
- coverage model (`line`, `region`, `branch`, `mixed`)
- linked `coverage-criterion-profile/v0`
- linked `coverage-execution-import/v0` when applicable
- toolchain / target / profile metadata
- per-file and per-module summaries
- changed-files summary
- provenance of merged inputs
- explicit caveats (`doctest-merge`, `mixed-engine-merge`, `external-run`, `criterion-watch-only`)

### 5) `coverage-policy/v0`
CI gate description:
- global thresholds
- changed-code thresholds
- critical-path stricter rules
- allowlisted low-value/generated paths
- `fail` / `warn` / `informational` / `inconclusive`

Design rule: policy must be more expressive than “overall line coverage >= N”.

### 6) `coverage-pack/v0`
Bundle format:
- coverage manifest
- one or more coverage reports
- optional raw references (`profraw`, `profdata`, tarpaulin json, lcov, cobertura)
- HTML report link or attachment metadata
- CI summary / compare results

### 7) `cargo cov`
The reference UX should make lane identity impossible to miss. One report should always say which coverage lane produced it, what criterion it measured, what executions were imported, and whether merged results remained comparable.

Reference UX:
- `cargo cov record`
- `cargo cov merge`
- `cargo cov diff`
- `cargo cov gate`
- `cargo cov pack`

`cargo cov` should be schema validation and orchestration first, and an engine only where necessary.

## What the kit should provide to others
- **Library authors:** portable coverage evidence attached to releases and PRs.
- **Application teams:** one place to declare whether examples, doctests, integration tests, and external black-box tests count.
- **CI/review systems:** machine-readable coverage diffs and gate results rather than brittle badges or scraped text.
- **Tool authors:** a shared schema for publishing results from `cargo-llvm-cov`, Tarpaulin, nextest-backed flows, or custom integration harnesses.
- **Safety-critical consumers:** criterion-aware imports that can distinguish ordinary coverage from future decision/MC/DC-oriented lanes.

## Integration points
- **Test Execution Evidence Stack:** import shared run identity instead of re-owning what executed.
- **Perf Labs:** combine changed-code coverage and regression evidence when a test suite expansion also affects cost.
- **Safety Evidence Kit:** import coverage artifacts as one assurance input, especially around unsafe-heavy modules, while preserving criterion identity.
- **FuzzPack Kit:** account for fuzz and property-testing runs as optional coverage-producing inputs.
- **Cargo Report Kit:** reuse report-oriented plumbing where Cargo grows more machine-readable build/test/session surfaces.

## Hard problems (explicitly scoped)
1. **Coverage is not one number**
   - line, region, branch, decision, and future MC/DC criteria are different signals; do not collapse them silently.
2. **Execution imports matter**
   - nextest, doctest, external, and black-box execution lanes change what raw coverage means; import them explicitly.
3. **Engine heterogeneity**
   - v0 must preserve engine provenance rather than pretending Tarpaulin and LLVM instrumentation are identical.
4. **Doctest weirdness**
   - doctests matter, but the artifact must carry caveats when fidelity is imperfect or separately merged.
5. **Monorepo and workspace policy**
   - thresholds often vary by crate and by path; do not force a single workspace-wide scalar.
6. **Hosted-service gravity**
   - the kit should work with hosted services, but not require them as the source of truth.

## Evaluation plan
Pilot on the ranked rollout in [`design/coverage-evidence-pilot-program.md`](./coverage-evidence-pilot-program.md):
1. LLVM default-harness baseline,
2. nextest + doctest merge,
3. external / black-box / FFI merge,
4. Tarpaulin contrast,
5. criterion-aware safety import.

Success bar:
- teams can declare coverage intent once,
- criterion identity stays explicit,
- CI can explain *why* a coverage gate failed or became inconclusive,
- merged results remain auditable,
- and the artifact is useful even without a hosted dashboard.

## Safety-critical stack note
Treat this kit as the **coverage-criterion layer** inside the shared **Safety-Critical Evidence Stack** in [`design/safety-critical-evidence-stack.md`](./safety-critical-evidence-stack.md).
That means ordinary line/region/branch reporting still matters, but decision and MC/DC lanes must remain explicit rather than being flattened into one “coverage” score.
Use [`design/coverage-evidence-pilot-program.md`](./coverage-evidence-pilot-program.md) to harden ordinary criterion-aware coverage first, then [`design/safety-critical-pilot-program.md`](./safety-critical-pilot-program.md) to keep later release-facing and MC/DC-capable imports separate from earlier library-review pilots.
