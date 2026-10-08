# Epic Proposal: Test Run Evidence Kit (`cargo testrun`)

## One-sentence pitch
Turn Rust test execution into a first-class attachable artifact boundary: enumerate test subjects, record runner semantics, capture machine-readable results, attach specialized evidence, and diff the outcome without forcing one runner to win first.

## Deliverables
- `cargo-testrun` reference implementation
- Schemas:
  - `test-subject/v0`
  - `test-binary-catalog/v0`
  - `test-list-report/v0`
  - `test-run-profile/v0`
  - `test-run-report/v0`
  - `flake-observation-report/v0`
  - `test-attachment-index/v0`
  - `test-pack/v0`
- Adapters:
  - libtest JSON lane
  - nextest machine-readable list/run lanes
  - JUnit import/export lane
  - attachment adapters for coverage / replay / fuzz / downstream / device / mutation results
- Docs:
  - CI/release attachment guide
  - runner-semantics reason-code reference
  - test-execution pilot-program guide

## Why now (signals)
- The libtest JSON goal says Cargo and custom runners need more programmatic test output, explicitly calling out `cargo nextest`, summaries, noisy output, and smarter execution order as motivating issues.  
  https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- Cargo 1.94 still lists finishing libtest JSON as a live focus area needing owners.  
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- nextest already provides machine-readable test and binary lists, JUnit support, experimental libtest-like JSON output, and stable run/binary ids.  
  https://nexte.st/docs/machine-readable/  
  https://nexte.st/docs/glossary/
- nextest’s Miri docs show that execution model changes what a run proves, which is exactly why runner semantics need to stay explicit.  
  https://nexte.st/docs/integrations/miri/
- `cargo-llvm-cov` and `cargo-mutants` already emit machine-usable outputs and attachment-worthy artifacts.  
  https://docs.rs/crate/cargo-llvm-cov/latest/source/README.md  
  https://mutants.rs/mutants-out.html

## Non-goals
- Replacing libtest, nextest, or every custom harness
- Defining one universal raw log format for all testing tools
- Hiding flaky retries or infra failures behind a fake green badge
- Owning coverage, replay, fuzzing, or hardware semantics directly
- Building a hosted dashboard before portable packs exist

## Strategic value
This kit has high leverage because it connects:
- default `cargo test` and emerging machine-readable harness work,
- the de facto ecosystem runner (`cargo nextest`),
- CI/release evidence,
- coverage/replay/fuzz/mutation/device consumers,
- and future policy/debugging/downstream workflows that need stable run identity.

## Milestones
1. **Pilot 1 / v0**
   - libtest/nextest subject and run reports
   - stable reason codes for pass/fail/infra/timeout/cancel
   - JUnit attachment without JUnit becoming the canonical source
2. **Pilot 2 / v0.2**
   - config-id import from `config-pack/v0`
   - CI matrix-aware run packs
   - flake observation and retry reporting
3. **Pilot 3 / v0.3**
   - coverage and Miri attachments
   - clearer semantics around what special lanes do and do not prove
4. **Pilot 4 / v0.4**
   - replay / fuzz / mutation attachment adapters
   - raw attachment indexing with digests
5. **v1**
   - downstream/device-lab consumers
   - stronger release/policy attachment guidance
   - broader custom-harness support

## What success looks like
- A maintainer can attach one pack that answers “what tests ran, under which semantics, and what specialized evidence attaches to that run?”
- A CI system can compare runs by stable ids and config ids rather than job-name folklore.
- Coverage, replay, fuzzing, mutation, and device-lab tools can reuse shared run identity without giving up their own semantics.
- Rust testing gets more composable without requiring consensus on one runner.

## Execution order
For the ranked rollout order, see `design/test-execution-pilot-program.md`.
The archive should treat this epic as schema + integration design, and the pilot-program doc as the staging plan for which lanes to win first.
