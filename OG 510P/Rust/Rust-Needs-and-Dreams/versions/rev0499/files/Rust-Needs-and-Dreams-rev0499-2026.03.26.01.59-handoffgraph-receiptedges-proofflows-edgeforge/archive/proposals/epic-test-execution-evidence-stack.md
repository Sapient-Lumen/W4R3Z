# Epic Proposal: Test Execution Evidence Stack (`cargo test-execution` + `test-exec-pack/v0`)

## One-sentence pitch
Give Rust one portable way to assemble **harness contracts, run profiles/results, config identities, runner-recording imports, and specialized testing attachments** into a reviewable execution package without forcing libtest, nextest, benches, doctests, Miri, coverage, fuzzing, replay, and hardware labs into one fake runner.

## Why this is worthy
Rust now has enough real testing machinery that the missing contribution is no longer “another runner” or “another XML bridge”. It is the attachable execution boundary above them:
- Rust’s 2026 flagships put **better test tooling** under **Building blocks**, which means testing infrastructure is now explicitly strategic project terrain.  
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The libtest-JSON goal says the goal is to finish programmatic output for **libtest**, the default harness for Cargo projects. It explicitly says Cargo could use this to improve summaries, reduce noisy output, support parallel test-binary execution, and lower the barrier for both custom runners like `cargo nextest` and custom harnesses like `libtest-mimic`.  
  https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- Cargo 1.94 still lists **Finish the libtest json output experiment** among focus areas needing owners. This seam is active, not archival.  
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Cargo’s own docs say doctest execution details **are not guaranteed and may change in the future**, while the rustc tests book still says libtest JSON is unstable and benchmarks plus custom test frameworks remain unstable or experimental. That is strong evidence that portable test evidence must preserve capability and stability posture rather than hiding it.  
  https://doc.rust-lang.org/cargo/commands/cargo-test.html  
  https://doc.rust-lang.org/rustc/tests/index.html
- Cargo’s external-tools docs say `--message-format=json` only controls Cargo and rustc output, not arbitrary tool output. So the ecosystem still lacks one honest boundary for turning mixed testing activity into reviewable execution evidence.  
  https://doc.rust-lang.org/cargo/reference/external-tools.html
- nextest’s current docs show why this should be a stack rather than a one-runner format. It already provides machine-readable test/binary lists, JUnit output, experimental libtest-like JSON, and persistent recordings with full event streams, captured outputs, and workspace metadata. Its own machine-readable docs still list first-class newline-delimited JSON test-run output and detected configuration as future work.  
  https://nexte.st/docs/machine-readable/  
  https://nexte.st/docs/machine-readable/junit/  
  https://nexte.st/docs/design/architecture/recording-runs/

## Deliverables
- Read together with [`design/test-execution-evidence-stack.md`](../design/test-execution-evidence-stack.md), [`design/test-execution-pilot-program.md`](../design/test-execution-pilot-program.md), [`design/harness-protocol-kit.md`](../design/harness-protocol-kit.md), [`design/test-run-evidence-kit.md`](../design/test-run-evidence-kit.md), [`design/config-set-kit.md`](../design/config-set-kit.md), [`design/coverage-evidence-kit.md`](../design/coverage-evidence-kit.md), [`design/fuzzpack-kit.md`](../design/fuzzpack-kit.md), [`design/replay-kit.md`](../design/replay-kit.md), [`design/downstream-testing-kit.md`](../design/downstream-testing-kit.md), and [`design/device-lab-kit.md`](../design/device-lab-kit.md) so the stack lands as a composition layer rather than another leaf tool.
- `cargo test-execution` reference tool
- Schemas:
  - `test-execution-brief/v0`
  - `test-execution-pack/v0`
  - `test-execution-diff/v0`
  - `test-execution-handoff/v0`
  - `runner-semantic-import/v0`
  - `runner-recording-import/v0`
  - `test-attachment-summary/v0`
- Imported artifacts:
  - `harness-pack/v0`
  - `test-pack/v0`
  - `config-pack/v0`
  - optional `coverage-pack/v0`, `replay-pack/v0`, `fuzz-pack/v0`, `downstream-report/v0`, `lab-pack/v0`, and runner-native recording artifacts
- Docs:
  - harness-vs-runner boundary guide
  - libtest / nextest import posture guide
  - config-bound CI evidence guide
  - recording-import / replay / rerun guide
  - coverage / Miri / fuzz / replay attachment guide
  - release / support / qualification-facing handoff guide

## Strategic value
This deserves promotion because it gives the archive one **portable testing evidence boundary** that many other seams can import honestly.

With it:
- harness capability/discovery truth can stay separate from execution/result truth;
- default-harness, nextest, benchmark, doctest, and custom-framework lanes can share bounded artifacts without pretending they behave the same;
- runner-native recordings can be imported without being mistaken for the canonical cross-runner schema;
- coverage, Miri, fuzz, replay, mutation, downstream, and hardware-lab lanes get a stable place to attach specialized evidence;
- CI, release, support, and conformance/safety consumers can inspect one linked package instead of scraping logs, JUnit, and runner-specific storage;
- Cargo-side future work can evolve without every downstream tool reverse-engineering unstable output again.

The prize is not a new universal runner.
The prize is a boring, portable bridge from test execution to review.

## Proposed shape
Ship a narrowly scoped stack-level layer:
1. import `harness-pack/v0` as the capability / discovery / adapter boundary;
2. import `test-pack/v0` as the concrete run / result / flake / attachment-index boundary;
3. import `config-pack/v0` where matrix or target/profile selection matters;
4. attach runner-native recording artifacts and raw outputs without making them the sole source of truth;
5. emit `test-execution-handoff/v0` for CI, release, support, conformance, and safety/quality consumers;
6. preserve `PARTIAL`, `INCONCLUSIVE`, `UNSUPPORTED`, retried, infra-failed, and adapter-lossy states explicitly instead of forcing one pass/fail verdict.

## Critical design bet
The critical bet is that **test execution evidence should stop at portable execution review, not at becoming the universal owner of all testing policy**.
That means:
- harness capability / discovery facts are in scope,
- runner semantics and result truth are in scope,
- runner-recording imports are in scope,
- config ids and specialized attachments are in scope,
- downstream consumers may import the result,
- but release gates, quality scores, flake budgets, and assurance verdicts stay with their own policy/evidence consumers.

Without that boundary, the proposal either stays too weak to matter or expands into a fake mega-runner / mega-dashboard.

## Milestones
1. **v0 harness + default-run lane**
   - publish `test-execution-brief` / `test-execution-pack`
   - import `harness-pack/v0` + `test-pack/v0` for ordinary `cargo test`
2. **v0.2 nextest import lane**
   - attach runner-semantic imports and recording artifacts
   - preserve termination/retry/process-model posture explicitly
3. **v0.3 config-bound CI lane**
   - attach `config-pack/v0`
   - preserve skipped/unprovisioned configs and package-selection truth
4. **v0.4 specialized attachment lane**
   - attach coverage, Miri, replay, fuzz, mutation, or downstream/device-lab evidence without redefining subject identity
5. **v1 thin consumer handoffs**
   - emit bounded handoffs for release review, support triage, safety/conformance import, and archaeology

## Execution order
Use [`design/test-execution-pilot-program.md`](../design/test-execution-pilot-program.md) as the stack-level rollout:
1. harness protocol lane,
2. default-harness / nextest run-truth lane,
3. config-bound CI lane,
4. coverage + Miri attachment lane,
5. replay / fuzz / mutation consumer lane,
6. downstream / device-lab lane.

Use [`proposals/epic-harness-protocol-kit.md`](./epic-harness-protocol-kit.md) and [`proposals/epic-test-run-evidence-kit.md`](./epic-test-run-evidence-kit.md) as the leaf-level execution guides beneath it.

## Non-goals
- replacing libtest, nextest, Miri, `cargo-llvm-cov`, Criterion, `cargo-mutants`, or device-lab runners with one tool;
- flattening harness capability, run outcomes, benchmark metrics, doctest posture, runner-native recordings, and specialized attachments into one schema or score;
- pretending nightly-only Cargo or libtest interfaces are already stable enough to be the canonical long-term contract;
- requiring every testing tool to emit the same raw output format;
- turning one stack pack into the sole release or quality gate for a project.

## Success bar
This becomes worthy when a maintainer, reviewer, or downstream consumer can answer:
- what subjects and harness capabilities existed,
- what runner semantics actually applied,
- which configs and packages were exercised,
- what results and flakes occurred,
- which specialized evidence attached,
- what raw runner-native material was imported with what stability posture,
- and what CI/release/support/conformance consumers may legitimately conclude from that package.
