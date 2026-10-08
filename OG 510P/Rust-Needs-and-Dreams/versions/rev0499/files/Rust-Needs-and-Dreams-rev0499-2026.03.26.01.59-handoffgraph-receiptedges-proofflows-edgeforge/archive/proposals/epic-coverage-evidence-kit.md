# Epic Proposal: Coverage Evidence Kit (`cargo cov`, `coverage-pack/v0`)

## One-sentence pitch
Give Rust projects a standard way to declare, collect, merge, and review criterion-aware coverage evidence so coverage becomes an auditable CI artifact instead of an opaque badge or flattened percentage, while preserving the lane that produced each result.

## Deliverables
- lane map: `design/coverage-evidence-lane-map.md`
- `cargo cov` reference tool
- Ranked rollout in [`design/coverage-evidence-pilot-program.md`](../design/coverage-evidence-pilot-program.md)
- Schemas:
  - `coverage-manifest/v0`
  - `coverage-criterion-profile/v0`
  - `coverage-execution-import/v0`
  - `coverage-report/v0`
  - `coverage-policy/v0`
  - `coverage-pack/v0`
- Adapters / publishers for:
  - `cargo-llvm-cov`
  - Tarpaulin
  - external test harnesses and merged LCOV/Cobertura/JSON inputs
- Docs:
  - coverage intent design guide
  - CI gating recipes
  - engine/provenance caveat guide

## Why now (signals)
- Rust has a stable source-based coverage compiler flag, but the official workflow still exposes enough raw mechanics that most teams rely on wrappers and bespoke CI glue.
  https://doc.rust-lang.org/rustc/codegen-options/index.html#instrument-coverage
  https://doc.rust-lang.org/rustc/instrument-coverage.html
- Rust’s 2026 flagship roadmap now includes **MC/DC coverage support** and **better test tooling**, and the January 2026 safety-critical adoption writeup says industry participants are organizing around upstream MC/DC support.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- `cargo-llvm-cov` has already proven that a Cargo-native wrapper around the official coverage pipeline is valuable and broadly useful, including `cargo nextest`, external tests, and C/C++ coverage merging.
  https://github.com/taiki-e/cargo-llvm-cov
- nextest’s own docs say doctest coverage must be merged separately, which is exactly the kind of execution/merge truth a shared artifact layer should expose.
  https://nexte.st/docs/integrations/test-coverage/
- Tarpaulin’s continuing popularity, plus its different engine/platform model and new refusal to report meaningless delta coverage when run configuration changes, is evidence that the ecosystem still needs convergence at the artifact/policy layer rather than yet another replacement engine.
  https://github.com/xd009642/tarpaulin
  https://docs.rs/crate/cargo-tarpaulin/latest/source/CHANGELOG.md
- Coverage review in practice still fractures across badges, Codecov-only conventions, raw LCOV uploads, and handwritten CI thresholds; Rust has the pieces, but not one portable review surface.

## Non-goals
- Replacing `cargo-llvm-cov` or Tarpaulin
- Pretending coverage percentages are interchangeable across unlike criteria, engines, execution plans, and targets
- Building a hosted SaaS as a prerequisite for adoption
- Claiming coverage alone proves correctness

## Strategic value
This is a worthy contribution because it upgrades a very common quality signal from **percentage theater** into **portable lane-aware evidence**:
- “What criterion did this percentage actually reflect?”
- “What exactly counted toward this result?”
- “Did changed code lose branch coverage or just workspace-wide line coverage?”
- “Are doctests and examples part of the gate, and if so, how were they merged?”
- “Can we merge black-box integration or FFI coverage honestly?”
- “Can reviewers audit how this result was produced?”

That is high leverage because coverage sits at the intersection of testing, documentation, CI, library maintenance, and regulated or assurance-heavy environments.

## Milestones
1. **v0 ranked pilot path + core schemas**
   - criterion/execution/report/policy/pack formats
   - LLVM baseline and nextest+doctest merge path
2. **v0.2 CI gates + comparability honesty**
   - fail/warn/inconclusive/not-comparable policy
   - explicit engine/criterion/import caveats
3. **v0.3 plural-engine and external-run imports**
   - Tarpaulin contrast lane
   - external / black-box / FFI merge lane
4. **v1 ecosystem convergence**
   - adapters for mainstream Rust coverage tools
   - safety-critical criterion imports and Cargo report-style plumbing where practical
