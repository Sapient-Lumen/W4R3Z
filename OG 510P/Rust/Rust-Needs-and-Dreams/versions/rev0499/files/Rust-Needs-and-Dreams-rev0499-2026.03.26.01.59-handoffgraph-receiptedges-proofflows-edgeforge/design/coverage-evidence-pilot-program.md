# Design: Coverage Evidence Pilot Program (`cargo cov pilot`, `coverage-pilot-pack/v0`)

Read this together with `design/coverage-evidence-lane-map.md`: the ranked pilots below are now explicitly the archive's first pass through the named coverage lanes rather than just a generic implementation order.

## Goal
Make **Coverage Evidence Kit** executable as a ranked rollout instead of leaving `coverage-pack/v0` as a good schema idea with no agreed proving path.

The missing contribution is not another badge, dashboard, or hosted service integration.
It is a disciplined pilot path that proves Rust projects can publish **criterion-aware coverage intent, imported execution truth, honest merge provenance, diffable gate results, and bounded safety-critical handoffs** across materially different coverage lanes without pretending they already mean the same thing.

## Why this now
- Rust’s 2026 flagship roadmap now makes coverage criteria strategically visible again: **Safety-Critical Rust** includes implementing **MC/DC coverage support**, and **Building blocks** includes **better test tooling**.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The January 2026 safety-critical adoption writeup says industry participants are organizing around upstream MC/DC support instead of treating it as a forever-out-of-tree need.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- The rustc coverage docs already describe a real LLVM source-based workflow, but they also show how much low-level process still leaks into ordinary use: profiler runtime requirements, `profraw` / `profdata`, doc-test-specific flags, and caveats around additional compiler options.
  https://doc.rust-lang.org/rustc/instrument-coverage.html
- `cargo-llvm-cov` is now the clearest Cargo-native execution lane: line/region/branch coverage, `cargo test` / `cargo run` / `cargo nextest`, proc-macro support, external tests, C/C++ coverage, and explicit doctest handling.
  https://github.com/taiki-e/cargo-llvm-cov
- nextest’s own coverage docs make the merge problem concrete: nextest does not currently support doctests, so doctest coverage must be merged separately.
  https://nexte.st/docs/integrations/test-coverage/
- Tarpaulin remains live and materially unlike LLVM instrumentation. Its README still says Linux defaults to `ptrace` on `x86_64`, while macOS and Windows default to LLVM instrumentation; its 0.35.0 changelog also says delta coverage should not be reported when run-configuration changes would make the comparison meaningless.
  https://github.com/xd009642/tarpaulin
  https://docs.rs/crate/cargo-tarpaulin/latest/source/CHANGELOG.md

The proposal-layer candidate that should absorb successful pilots remains [`proposals/epic-coverage-evidence-kit.md`](../proposals/epic-coverage-evidence-kit.md).

## Why this needs its own design layer
Without a pilot design, Coverage Evidence keeps drifting toward four failure modes:
1. **percentage theater** — one number stands in for unlike criteria, workloads, and merge paths;
2. **runner amnesia** — coverage is treated as if the execution substrate were obvious, even when doctests, nextest, external harnesses, or black-box binaries are merged later;
3. **engine flattening** — Tarpaulin and LLVM-instrumented results get merged or compared without explicit comparability claims;
4. **assurance inflation** — line/region/branch outputs are imported into safety-critical review as if decision or MC/DC meaning had already been established.

A worthy contribution should prove the smaller and stronger claim:
> Rust coverage lanes can emit enough shared structure that humans and downstream systems can review what criterion was measured, what execution produced it, how merges happened, and where comparisons or gates are not honest.

## Design principles
1. **Criterion identity comes before percentages.** A pilot should name line, region, branch, decision, and future MC/DC posture explicitly.
2. **Execution imports are first-class.** Coverage without run-subject and runner/import truth is not reviewable enough.
3. **Merge provenance is part of the result.** “Combined coverage” must say from what, and with what caveats.
4. **Comparability must be explicit.** Different engines, targets, and execution plans are allowed; silent equivalence is not.
5. **Changed-code gates matter more than headline totals.** A portable policy layer must express why a gate failed.
6. **Safety-critical imports come later.** Ordinary line/region/branch lanes should harden before decision/MC/DC-oriented consumers widen the claim.

## Artifact family

### 1) `coverage-pilot-brief/v0`
Why a coverage slice is being piloted.

Should record:
- pilot id and summary
- subject family (`llvm-default`, `llvm-nextest-doctest-merge`, `llvm-external-ffi`, `tarpaulin-contrast`, `criterion-import`, `safety-import`)
- why this slice matters now
- intended consumers
- why the slice is tractable now

### 2) `coverage-subject-profile/v0`
The scoped thing being covered.

Should record:
- workspace/package/binary/test identity
- target/profile/features/toolchain identifiers
- included and excluded workload kinds (`unit`, `integration`, `doctest`, `example`, `bench`, `external`, `ffi`)
- whether the slice is illustrative, CI-gating, release-facing, or watch-only

### 3) `coverage-criterion-profile/v0`
What “coverage” means for this slice.

Should record:
- criterion class (`line`, `region`, `branch`, `decision`, `mcdc`, `mixed`, `watch-only`)
- whether the criterion is directly measured, derived, imported, or future-facing
- toolchain and engine support expectations
- known blind spots or caveats
- whether cross-run comparison is expected or advisory only

### 4) `coverage-execution-import/v0`
How execution truth is attached.

Should record:
- execution source (`cargo-test`, `cargo-nextest`, `cargo-run`, `external`, `runner-recording-import`, `other`)
- imported artifact pointers (`test-exec-pack/v0`, runner-native recording, raw logs, profraw/profdata refs)
- selected subset / shard notes
- known lossiness in the import
- whether the import is authoritative, advisory, or watch-only

### 5) `coverage-merge-report/v0`
How distinct runs became one result.

Should record:
- merged input identities
- engine/criterion compatibility posture
- config/target/profile differences
- doctest/example/external/FFI merge notes
- reasons a merge is comparable, advisory, or not comparable

### 6) `coverage-gate-report/v0`
Portable policy outcome.

Should record:
- gate scope (`global`, `path`, `changed-code`, `critical-slice`, `watch-only`)
- thresholds and rationale
- outcome (`pass`, `warn`, `fail`, `inconclusive`, `not-comparable`)
- cited inputs and caveats
- required human review followups

### 7) `coverage-pilot-scorecard/v0`
Decides whether a lane is worth widening.

Should ask:
- did the pilot preserve criterion identity honestly?
- did it preserve execution-import truth honestly?
- did merged inputs remain auditable?
- were non-comparable or inconclusive states preserved?
- did at least one real downstream consumer import it?
- does widening the pilot still look justified?

### 8) `coverage-pilot-pack/v0`
Bundle for review and reuse:
- pilot brief
- subject profile
- criterion profile
- execution import
- merge report
- linked `coverage-pack/v0`
- gate report
- scorecard

## Ranked first pilots

### 1) Official LLVM baseline lane
**Why first**
- It aligns with the official rustc coverage workflow and the dominant Cargo-native wrapper.
- It gives the archive one clean baseline before merge/import complexity widens.

**Must prove**
- criterion identity is explicit (`line` / `region`, optional `branch`)
- unit/integration workload selection is reviewable
- raw report plus gate summary are both useful
- changed-code gates can be expressed without a hosted service

### 2) Cargo-native LLVM orchestration + nextest/doctest merge lane
**Why second**
- nextest coverage is real, but nextest’s own docs say doctests must be merged separately.
- This is the smallest pilot that proves execution imports and merge provenance belong in the contract.

**Must prove**
- imported `test-exec-pack/v0` or runner-native execution can attach cleanly
- doctest coverage is recorded as a distinct merged input
- one combined report can preserve merge caveats
- gate outcomes can distinguish “good enough” from “not comparable enough”

### 3) External / black-box / FFI import lane
**Why third**
- `cargo-llvm-cov` already supports external tests and C/C++ coverage, which makes this a live seam rather than a speculative one.
- It forces the pack to record non-Cargo execution and linked-language inputs honestly.

**Must prove**
- execution imports can cite external binaries or harnesses
- merged FFI/native coverage does not silently become “all Rust coverage”
- include/exclude policy remains explicit
- downstream CI can still reason about the result

### 4) Tarpaulin contrast lane
**Why fourth**
- Tarpaulin remains important precisely because it is not the same lane as LLVM instrumentation.
- This pilot tests whether the archive can preserve engine diversity without pretending away comparability limits.

**Must prove**
- engine family is explicit in the result
- delta and compare posture can become `not-comparable` when configuration changes matter
- line-only or backend-specific limitations remain visible
- policy consumers can import the result without mistaking it for LLVM-equivalent evidence

### 5) Decision / MC/DC watch-and-import lane
**Why fifth**
- The roadmap pressure around MC/DC means coverage will increasingly be consumed by safety-critical reviewers.
- The archive should test that import boundary after ordinary coverage hardens, not before.

**Must prove**
- line/region/branch results can be imported without overclaiming decision or MC/DC meaning
- future decision/MC/DC lanes can attach as distinct criterion profiles
- Safety Evidence consumers can state what they may and may not conclude
- the boundary stays thin instead of absorbing all assurance logic

## Shared schema discipline
Every pilot must keep these truths separate:
1. **coverage criterion** vs **percentage outcome**
2. **execution truth** vs **coverage aggregation**
3. **portable coverage reports** vs **tool-native raw artifacts**
4. **engine identity** vs **comparability claims**
5. **policy threshold** vs **gate outcome**
6. **ordinary quality review** vs **safety-critical import**
7. **raw merged inputs** vs **derived diff/gate summaries**
8. **watch-only signals** vs **release/CI gating signals**

## Immediate archive consequences
Read this together with:
- [`design/coverage-evidence-kit.md`](./coverage-evidence-kit.md)
- [`design/test-execution-evidence-stack.md`](./test-execution-evidence-stack.md)
- [`design/test-run-evidence-kit.md`](./test-run-evidence-kit.md)
- [`design/config-set-kit.md`](./config-set-kit.md)
- [`design/fuzzpack-kit.md`](./fuzzpack-kit.md)
- [`design/sanitizer-battery-kit.md`](./sanitizer-battery-kit.md)
- [`design/safety-evidence-kit.md`](./safety-evidence-kit.md)
- [`design/safety-critical-evidence-stack.md`](./safety-critical-evidence-stack.md)

The archive should now prefer:
- **criterion-aware packs before another percentage badge**,
- **execution imports before coverage-only summaries**,
- **honest merge reports before one-number dashboards**,
- and **coverage gates that explain themselves before hosted-service conventions**.

## What should wait
Do **not** start with:
- a universal hosted Rust coverage service,
- a fake cross-engine single score,
- a claim that line or branch coverage already solves MC/DC needs,
- or a demand that all coverage tools emit the same raw format.

Those may become consumers or adapters later.
They are not the missing substrate.
