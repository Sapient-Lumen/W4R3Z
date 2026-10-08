# Design: Downstream Testing Kit (`cargo downstream`, downstream-report/v0)

## Goal
Provide a pragmatic, CI-friendly downstream testing workflow for library and tool authors:
- small enough to run regularly,
- standardized enough to compare results,
- extensible enough to scale toward Crater-like runs.

## References (signals)
- Crater repo: https://github.com/rust-lang/crater
- Ecosystem testing guide: https://rustc-dev-guide.rust-lang.org/tests/ecosystem.html
- Downstream testing (autopkgtest analogy): https://nesbitt.io/2026/03/01/downstream-testing.html

## Core UX: `cargo downstream`
Reference commands:
- `cargo downstream plan`  
  Produce a plan: selected downstream crates, versions, feature sets, and budgets.
- `cargo downstream run`  
  Execute the plan with standardized sandboxing + caching (composes with Hermetic/Cache Kits).
- `cargo downstream diff <A> <B>`  
  Compare two `downstream-report/v0` artifacts and emit reasoned deltas.
- `cargo downstream explain <crate>`  
  Explain a failure with “why chains”: toolchain/feature/build-dep differences, logs, minimal repro.

## Plan selection strategies
- `--top <N>` by reverse-dep count (from crates.io metadata via adapter)
- `--curated file.yml` (maintainer curated critical dependents)
- `--workspace` (internal downstreams in monorepo)
- `--risk-profile`:
  - `build-deps` / `proc-macros` / `runtime` separation
  - MSRV matrix (compose with MSRV kit)

## Cost controls
- Sharding by crate list and test phases
- Budgets:
  - max wall time
  - max crates
  - max retries
- Caching:
  - integrate with `cargo cache` / sccache wrapper
- Sandbox (optional):
  - integrate with `cargo safe`/capability policy

## Artifact: `downstream-report/v0`
A portable JSON report:
- subject crate@version (+ git commit)
- toolchain (rustc + cargo versions)
- plan hash (selection strategy + inputs)
- per downstream crate:
  - crate id, version, features
  - status: PASS/FAIL/SKIP
  - reason codes:
    - `API_BREAK`
    - `MSRV_BREAK`
    - `FEATURE_CONFLICT`
    - `BUILD_SCRIPT_FAIL`
    - `PROC_MACRO_FAIL`
    - `TEST_FLAKE`
    - `INFRA_TIMEOUT`
  - logs (content-addressed refs)
- summary:
  - pass rate
  - new failures vs baseline
  - confidence score (coverage, stability)

## Evaluation plan
- Pilot on 3–5 popular libraries with large rdep sets:
  - compare “curated” vs “top-N” selection efficiency
  - measure signal/noise
- Maintain a regression corpus:
  - known breaking changes with expected downstream failures
