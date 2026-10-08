---
id: P-0106
title: Test Run Artifact Standard Kit — run receipts, selection basis, attempt topology, and share-safe portable bundles
status: idea
domains: [testing, tooling, ci, artifacts, observability, support]
last_reviewed: 2026-03-21
evidence:
  - https://doc.rust-lang.org/cargo/commands/cargo-test.html
  - https://doc.rust-lang.org/cargo/reference/external-tools.html
  - https://rust-lang.github.io/rust-project-goals/2025h1/libtest-json.html
  - https://docs.rs/libtest-mimic/latest/libtest_mimic/
  - https://nexte.st/docs/design/architecture/recording-runs/
  - https://nexte.st/docs/features/record-replay-rerun/
  - https://nexte.st/docs/features/record-replay-rerun/portable-recordings/
  - https://nexte.st/docs/machine-readable/libtest-json/
  - https://nexte.st/docs/features/retries/
  - https://nexte.st/docs/features/stress-tests/
---

# Problem

Rust has meaningful test-running substrate, but it still lacks one boring crate that lets teams publish a **portable, reviewable test-run artifact contract**.

Today’s substrate is real and useful:

- `cargo test` still builds libtest-based executables and can forward test-selection arguments to them;
- Cargo’s own `--message-format=json` only covers Cargo and rustc messages, not arbitrary test-runner output;
- the Rust project has an explicit goal to finish/stabilize libtest JSON because people already depend on machine-readable test output;
- `libtest-mimic` lets custom harnesses look and behave like libtest without making them literally the same protocol;
- `cargo-nextest` now records full event streams, captured outputs, workspace metadata, attempt IDs, retries, stress iterations, and portable recordings.

But those pieces still do **not** by themselves answer the artifact questions teams actually hit in CI, flaky-test triage, support bundles, and reproducible failure review:

- what exactly identified one run,
- what test-selection basis produced it,
- whether retries/stress/fail-fast changed the meaning of the result,
- which parts of the bundle are safe to share,
- and which imports are exact versus lossy.

The missing crate is therefore **not** another test runner, another XML exporter, or another snapshot framework.
It is a **Test Run Artifact Standard Kit**: one receiver-facing layer that can publish stable receipts for run identity, selection basis, attempt topology, and bundle sensitivity above built-in test harnesses, nextest recordings, and custom harnesses.

# Main judgment

This is worthy because testing is one of the few Rust surfaces that every serious project touches, yet the artifact story is still fragmented:

- CI systems want machine-readable results and rerun handles,
- maintainers want shareable failure bundles instead of screenshots and truncated logs,
- flaky-test triage needs retries/attempt IDs/stress semantics that survive export,
- platform teams need to know whether a recording is safe to attach to tickets,
- and custom-harness authors need a path into the same ecosystem without pretending they are identical to built-in libtest.

The missing value is not “more test output.”
The missing value is **portable test-run support posture with receipts**.

# What it provides

- `run-identity.receipt.json` — stable run ID, runner family, harness class, import route, and exactness class.
- `selection-basis.receipt.json` — workspace/package/target/filter/profile/platform basis and replay exactness.
- `attempt-topology.report.json` — concurrency class, retry policy, fail-fast posture, stress/repeat behavior, and per-attempt identity posture.
- `bundle-sensitivity.receipt.json` — whether stdout/stderr, env values, paths, fixture excerpts, or host details may appear and what export posture applies.
- `testrun-bundle.manifest.json` — a portable bundle manifest for event streams, metadata snapshots, outputs, and optional derived exports.
- `testrun.summary.md` — a compact human summary for CI artifacts, issue attachments, and release review.
- `testrun.diff.json` — compares two captured runs and classifies `selection_changed`, `topology_changed`, `identity_route_changed`, and `sensitivity_changed`.
- `cargo testrun capture` — capture a run artifact with receipts.
- `cargo testrun import-nextest` — import a nextest recording into the stable bundle shape.
- `cargo testrun gate` — fail review when exactness/sensitivity/topology posture is too weak for the claimed use.
- `cargo testrun bundle` — produce one small exportable archive for CI/support/repro handoff.

# What the crate should provide other people

1. **Stable run identity** so a later replay or support review can talk about one run without inheriting a specific runner forever.
2. **Selection-basis truth** so test-name filters, package filters, profiles, platforms, and imported test lists do not get compressed into one fake “same run” claim.
3. **Attempt-topology honesty** so retries, fail-fast, stress loops, and setup-script behavior survive export.
4. **Share-safety receipts** so a portable bundle does not quietly become a public-safe bundle.
5. **Loss-aware imports** so JUnit, libtest JSON, console logs, and nextest recordings can all be classified without pretending they have equal fidelity.
6. **One boring artifact vocabulary** that CI, support, flake triage, and issue handoff can all understand.

# Personas / who it’s for

- maintainers triaging failing CI runs
- infra teams building test dashboards or artifact retention systems
- flaky-test investigators
- crate authors exposing custom test harnesses
- release engineers who want replayable and reviewable test evidence

# Users & user stories

- **Maintainer:** “Attach one portable artifact to the issue so somebody else can understand what ran and whether the retry changed the verdict.”
- **CI engineer:** “Store one bundle shape across `cargo test`, nextest, and imported custom harnesses.”
- **Flake investigator:** “I need attempt IDs, retry counts, and stress-iteration truth, not just a final pass/fail line.”
- **Security reviewer:** “Tell me whether the captured outputs or metadata are safe to share outside the org.”
- **Harness author:** “I want my custom runner to participate in the same bundle format without pretending it is built-in libtest.”

# Prior art (and why it’s insufficient)

- `cargo test` and libtest provide the default substrate, but not a stable portable artifact contract for downstream tools.
- Cargo JSON output helps with build diagnostics, but Cargo explicitly says it does **not** control arbitrary tool output.
- The libtest JSON goal proves real demand, but that still leaves bundle shape, sensitivity posture, and loss-aware imports unresolved.
- `cargo-nextest` has the strongest current recording/replay story, but its recording format is runner-specific and portable recordings can contain sensitive data that nextest does not redact for you.
- JUnit is widely understood, but it is a lossy interchange surface, especially once retries, setup scripts, stress loops, or richer timing/event data matter.
- `libtest-mimic` is valuable, but “looks like libtest” is not the same as one stable artifact contract.

What remains missing is the **run identity + selection basis + attempt topology + bundle sensitivity** layer above today’s runners and exports.

# Design goals

1. **Artifact-first, not runner-first.** Start from what another team can review or replay.
2. **Runner-agnostic core.** The first bundle vocabulary must work above `cargo test`, nextest, and custom harnesses.
3. **Loss-aware imports.** Conversions must say when information was inferred, missing, or downgraded.
4. **Selection exactness.** Replay claims must stay separate from “we know roughly what tests were included.”
5. **Attempt granularity.** Retries, flakes, fail-fast, stress loops, and setup-script runs must remain visible.
6. **Share-safety honesty.** Portable does not mean public-safe.
7. **Small and exportable.** `0.1` should be boring enough for CI artifacts, support tickets, and cache retention.
8. **Import, don’t replace.** The crate should import from existing runners rather than force one new runner protocol everywhere.
9. **Manual-review over fake certainty.** When the source is lossy or mixed, emit `manual_review_required`.

# MVP surface

- Minimal types:
  - `RunIdentityReceipt`
  - `SelectionBasisReceipt`
  - `AttemptTopologyReport`
  - `BundleSensitivityReceipt`
  - `TestRunBundleManifest`
  - `TestRunDiff`
- Minimal functions:
  - `capture_testrun_bundle()`
  - `import_nextest_recording()`
  - `diff_testrun_bundle()`
  - `bundle_testrun()`
- Feature flags:
  - `serde`
  - `nextest-import`
  - `junit-export`
  - `libtest-json-import`
  - `cli`

# First-class review objects

## `run-identity.receipt`

Captures:
- stable run identifier and its basis,
- runner family (`cargo_test`, `cargo_nextest`, `custom_harness`, `manual_import`),
- harness class (`libtest_builtin`, `libtest_mimic`, `custom_protocol`, `manual_review_required`),
- import route (`native_capture`, `native_recording_import`, `lossy_import`, `manual_reconstruction`),
- and exactness class.

## `selection-basis.receipt`

Captures:
- workspace root / manifest basis,
- package and target selection,
- test/binary list source,
- profile/platform/toolchain hints,
- filter expression or explicit test list,
- replay exactness (`exact`, `approximate`, `manual_review_required`).

## `attempt-topology.report`

Captures:
- execution class (`shared_process`, `process_per_test`, `mixed`, `manual_review_required`),
- fail-fast posture,
- retry policy and flake classification basis,
- stress/repeat posture,
- attempt ID posture,
- setup-script or harness-side extra-attempt semantics.

## `bundle-sensitivity.receipt`

Captures:
- whether stdout/stderr is included,
- whether env values, paths, fixture snippets, usernames/hosts, or secret-like data may appear,
- whether outputs were redacted, unredacted, or imported without redaction proof,
- export posture (`internal_only`, `redaction_required`, `share_safe`, `manual_review_required`).

# Suggested commands

- `cargo testrun capture`
- `cargo testrun import-nextest`
- `cargo testrun gate`
- `cargo testrun diff old.json new.json`
- `cargo testrun bundle`

# Compatibility story

- Stable Rust first for receipt schemas and core bundle logic.
- Must import nextest recordings without discarding attempt/topology/sensitivity truth.
- Must tolerate plain `cargo test` inputs even when machine-readable detail is partial.
- Should classify libtest JSON as stable, unstable, or experimental based on the real source.
- Should treat JUnit as a derivative export/import surface, not the source of truth.
- Should give custom harnesses a registration hook rather than assuming libtest equivalence.

# Conformance & fixtures

- one fixture where a nextest portable recording is exportable but still `redaction_required`
- one fixture where libtest-style JSON exists but the source remains unstable or partial
- one fixture where a custom harness mimics libtest output but still needs explicit harness-class truth
- one fixture where retries/stress/fail-fast materially change the meaning of the run bundle

# Path to boring stability

- Freeze receipt vocabulary before inventing a universal event protocol.
- Start with capture/import/diff/gate workflows rather than replaying every runner perfectly.
- Keep derived exports (`junit.xml`, loose console logs) clearly secondary.
- Require explicit loss/sensitivity receipts before blessing public-safe or exact-replay claims.
- Prefer tiny artifacts that can be attached to issues or CI runs.

# Non-goals

- Not a replacement for `cargo test`, libtest, or `cargo-nextest`.
- Not a universal benchmark/result database.
- Not a flake-detection service by itself.
- Not a generic log-redaction engine.
- Not a promise that every historical test output format can be imported losslessly.

# Architecture & API sketch

```rust
pub struct RunIdentityReceipt {
    pub run_id: String,
    pub runner_family: RunnerFamily,
    pub harness_class: HarnessClass,
    pub import_route: ImportRoute,
    pub exactness: ExactnessClass,
}

pub struct SelectionBasisReceipt {
    pub workspace_root: String,
    pub package_scope: Vec<String>,
    pub target_scope: Vec<String>,
    pub filter_basis: Option<String>,
    pub replay_exactness: ReplayExactness,
}

pub fn capture_testrun_bundle(subject: &Path) -> Result<TestRunBundle>;
pub fn import_nextest_recording(path: &Path) -> Result<TestRunBundle>;
pub fn diff_testrun_bundle(old: &TestRunBundle, new: &TestRunBundle) -> TestRunDiff;
```

# Maintenance & governance plan

- Keep the receipt vocabulary compact and versioned.
- Publish tiny fixture families for built-in libtest, nextest, and custom harness imports.
- Treat any future event-stream standardization as a later layer above the core receipts.
- Require every “share-safe” claim to carry one typed sensitivity receipt.
- Prefer typed `manual_review_required` states whenever a source is lossy or mixed.
