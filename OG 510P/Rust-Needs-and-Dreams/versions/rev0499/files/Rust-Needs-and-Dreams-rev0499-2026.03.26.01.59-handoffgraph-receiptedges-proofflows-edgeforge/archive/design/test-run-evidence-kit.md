# Design: Test Run Evidence Kit (`cargo testrun`, `test-pack/v0`)

## Goal
Define a portable contract for enumerating, executing, diffing, and reviewing Rust test runs so the ecosystem can share **test subject identity, runner semantics, result truth, recording imports, flake posture, and attachments** without pretending every runner or harness behaves the same.

This should **not** replace `cargo test`, libtest, `cargo nextest`, `libtest-mimic`, `trybuild`, `ui_test`, Miri, coverage tools, or mutation testing tools.
It should also **not** own harness capability/discovery contracts for tests, benches, doctests, or custom frameworks; that boundary now belongs to [`design/harness-protocol-kit.md`](./harness-protocol-kit.md).
It should make them compose better.

## References (signals)
- Rust’s 2026 flagships explicitly call out **better test tooling** under **Building blocks**, which means test infrastructure is now roadmap-visible core work rather than mere runner polish:  
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The libtest-JSON goal says libtest is Cargo’s default harness, says users rely on programmatic output, and points toward reporting shifting into Cargo so custom runners and custom harnesses can grow more cleanly:  
  https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- Cargo 1.94 still lists finishing libtest JSON as a live focus area needing owners:  
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- `cargo test` still mixes libtest, rustdoc doctests, and `harness = false` custom flows, and explicitly warns that doctest execution details are not guaranteed and may change:  
  https://doc.rust-lang.org/cargo/commands/cargo-test.html
- The rustc tests book still says libtest `--format json` is unstable, and benchmarks plus custom test frameworks remain unstable/experimental:  
  https://doc.rust-lang.org/rustc/tests/index.html
- nextest already provides machine-readable test lists, binary lists, JUnit output, experimental libtest-like JSON output, and persistent run recordings with event streams, captured outputs, and workspace metadata; its own docs still call first-class JSON test-run output and detected configuration future work:  
  https://nexte.st/docs/machine-readable/  
  https://nexte.st/docs/machine-readable/junit/  
  https://nexte.st/docs/design/architecture/recording-runs/  
  https://nexte.st/docs/running/
- Cargo’s external-tools docs say `--message-format=json` only controls Cargo and rustc output, not arbitrary tool output, which is exactly why a portable run pack cannot just be “whatever was printed as JSON”:  
  https://doc.rust-lang.org/cargo/reference/external-tools.html

## Design principles
1. **Separate harness identity from runner identity.** libtest, nextest, and custom harnesses are related but not interchangeable.
2. **Execution semantics are first-class.** Process-per-test, setup scripts, retries, cancellation, and Miri/dynamic-analysis lanes must stay visible.
3. **Subject ids must be stable enough for attachments.** Coverage, replay, mutation, and downstream consumers need shared ids.
4. **Portable reports and runner-native recordings are both real, but not the same artifact.** A summary pack should not erase richer native recordings, and a native recording should not silently become the whole canonical truth.
5. **Attachments stay distinct.** Coverage, sanitizer, replay, and device-lab artifacts should attach to runs, not be flattened into one mega-report.
6. **Flakes are part of the evidence.** Retries and instability should be reviewable, not hidden in CI wrappers.
7. **Adapters before replacement.** The first win is a shared result boundary, not a new universal test runner.
8. **Import harness truth instead of recreating it.** Suite hierarchy, locations, markers, benchmark subject posture, and doctest support should come from Harness Protocol imports where possible rather than being re-invented in run reports.
9. **Matrix truth is imported, not guessed.** Feature/cfg/target/profile choices should come from `config-pack/v0` or equivalent inputs where available.

## Artifact family

### 1) `test-subject/v0`
Top-level identity for what is under test.

Fields should include:
- workspace / package / commit / lockfile identity
- selected package scope
- command lane (`test`, `bench-like`, `miri`, `custom`, `other`)
- config id / config-pack reference when present
- optional docs / support / release references

### 2) `test-binary-catalog/v0`
Inventory of discovered test binaries and their identities.

Fields should include:
- binary id
- binary kind (`unit`, `integration`, `example`, `bench`, `custom-harness`, `other`)
- package/crate identity
- target triple / host-target posture
- harness identity (`libtest`, `libtest-mimic`, `custom`, `nextest-import`, `other`)
- runner eligibility notes

### 3) `test-list-report/v0`
Machine-readable test discovery output.

Fields should include:
- discovered test ids
- binary ids
- ignored/skipped-at-discovery posture
- parameterized / generated-test notes where relevant
- discovery engine identity
- lossiness notes if imported from a runner with partial fidelity

### 4) `test-run-profile/v0`
Describes how the tests were executed.

Fields should include:
- runner identity (`cargo-test`, `nextest`, `custom`, `other`)
- execution model (`same-process`, `process-per-test`, `process-per-binary`, `hybrid`)
- retry / rerun policy
- setup-script / wrapper-script posture
- timeout policy
- concurrency / rate-limit posture
- special lane tags (`miri`, `sanitizer`, `coverage`, `device-lab`, `mutation`, `other`)
- environment / capability notes

### 5) `test-run-report/v0`
Portable result artifact.

Fields should include:
- run id
- referenced subject / config / profile ids
- per binary summary
- per test summary with stable ids
- statuses (`passed`, `failed`, `ignored`, `skipped`, `timed-out`, `cancelled`, `not-run`, `infra-failed`)
- duration data
- failure class (`assertion`, `panic`, `timeout`, `signal`, `infra`, `setup-script`, `wrapper`, `other`)
- stdout/stderr/log refs or content-addressed pointers
- summary counts

### 6) `runner-recording-import/v0` (optional)
Records richer runner-native material without pretending it is the universal portable format.

Fields should include:
- runner identity and version
- raw recording refs (event streams, output stores, run-native summaries)
- replay/rerun compatibility notes
- projected-into-pack fields and lossiness notes
- retention / storage-location posture
- stability posture (`stable`, `experimental`, `tool-local`, `nightly-coupled`, `other`)

### 7) `flake-observation-report/v0` (optional)
Records instability without silently normalizing it away.

Fields should include:
- run ids compared
- retries attempted
- tests with outcome drift
- suspected flake classes (`timing`, `order`, `shared-resource`, `infra`, `unknown`)
- stabilized/not-stabilized verdict
- notes on whether the runner masked the flake from the final pass/fail verdict

### 8) `test-attachment-index/v0` (optional)
Index of specialized artifacts attached to the run.

Fields should include:
- coverage refs (`coverage-pack/v0`, LCOV/JSON/Cobertura refs)
- sanitizer refs (`sanitize-pack/v0`)
- replay refs (`replay-pack/v0`)
- fuzz refs (`fuzz-pack/v0`)
- downstream refs (`downstream-report/v0`)
- mutation refs (`mutants.json`, `outcomes.json`, future `mutation-pack/v0`)
- device-lab refs (`lab-pack/v0`)
- raw attachment pointers and digests

### 9) `test-pack/v0`
Bundle for CI, release review, debugging, and long-term archaeology.

Should contain:
- `test-subject.json`
- `test-binary-catalog.json`
- optional `test-list-report.json`
- `test-run-profile.json`
- `test-run-report.json`
- optional `runner-recording-import.json`
- optional `flake-observation-report.json`
- optional `test-attachment-index.json`
- checksums / provenance / schema versions

## Boundary with Harness Protocol Kit
- Harness Protocol Kit owns what a harness can declare before execution: capabilities, discovery, suite/case shape, locations, benchmark subject posture, doctest posture, and adapter lossiness.
- Test Run Evidence Kit begins once there is a concrete run subject and records what execution happened, under which runner semantics, with which results, recording imports, and attachments.
- This kit should import harness-side truth rather than pretending run reports are the right place to define custom-framework or bench/doctest semantics from scratch.

## Reference UX: `cargo testrun`
- `cargo testrun list`
  - emit `test-binary-catalog/v0` and `test-list-report/v0`
- `cargo testrun run`
  - execute through an adapter and emit `test-run-profile/v0` + `test-run-report/v0`
- `cargo testrun import-recording`
  - attach runner-native recordings and emit `runner-recording-import/v0`
- `cargo testrun diff <A> <B>`
  - compare two runs and emit stable deltas
- `cargo testrun flakes`
  - summarize reruns and instability observations
- `cargo testrun pack`
  - bundle a `test-pack/v0`
- `cargo testrun verify-pack <path>`
  - verify schemas, digests, and attachment references

This command should begin as an adapter / importer / packer / explainer, not a replacement runner.

## What the kit should provide to others
- **Config Set Kit:** reusable config ids for test runs instead of CI-only matrix folklore.
- **Coverage Evidence Kit:** a shared run subject and attachment boundary.
- **FuzzPack / Replay / Sanitizer Battery:** a place to hang specialized results without redefining test identity.
- **Downstream Testing Kit:** one run/result vocabulary for reverse-dependency test lanes.
- **Device Lab Kit:** hardware runs can remain distinct while still attaching to the same review culture.
- **Release Pipeline Kit / Policy Kit / Support Envelope:** attach one reviewable run pack instead of scraped logs and ad hoc XML.

## Overlap boundaries
- **Not Config Set Kit:** config selection explains which matrix entries exist; Test Run Evidence records what actually ran.
- **Not Coverage Evidence Kit:** coverage remains its own evidence family; this kit owns execution identity and result truth.
- **Not Replay Kit / FuzzPack / Sanitizer Battery:** those kits own specialized semantics and artifacts; this kit only indexes them.
- **Not Downstream Testing Kit:** downstream selection is about which dependents to test; this kit is about how the resulting runs are represented.
- **Not one hosted dashboard:** the design should work in local CI and artifact stores before any central service exists.

## Why this could matter
A good Test Run Evidence Kit would:
- lower the cost of building better runners and harnesses,
- preserve portable review artifacts without erasing richer runner-native recordings,
- make CI/release/debugging artifacts comparable,
- give specialized testing tools a stable place to attach results,
- and let Rust testing move from logs/XML folklore toward reviewable evidence without requiring one canonical runner to win first.
