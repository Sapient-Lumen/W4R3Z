# Native build crate contracts — implementation brief (2026-03-08)

This note takes the archive's current native-build stack and turns it into a more implementation-shaped brief.

The stack remains:

1. **P-0046 buildscript-ux-kit**
2. **P-0059 buildscript-testkit**
3. **P-0058 native-deps-kit**

## Main judgment

The strongest next move in this frontier is still **P-0046 first**.

That is not because P-0046 is the most ambitious crate. It is because it has the best ratio of:

- breadth of immediate usefulness,
- honesty about what Cargo exposes today,
- compatibility with upstream Cargo changes,
- and usefulness as a vocabulary layer for the next two crates.

P-0059 and P-0058 should be treated as follow-ons that **reuse** the same bundle/report language rather than inventing adjacent but incompatible artifact names.

## Shared bundle vocabulary

Across the whole stack, prefer these stable terms:

- `observed_directive`
- `backend_attempt`
- `suggested_fix`
- `manual_review_required`
- `redaction_policy`
- `normalized_path_placeholder`
- `env_allowlist`
- `comparison_baseline`
- `bundle_schema_version`
- `workspace_policy_scope`

That vocabulary is intentionally narrower than “full Cargo causality”.

## P-0046 — buildscript-ux-kit

### What it should provide other people

P-0046 should give another human one compact answer to:

> “This build failed in `build.rs`. What mattered, what was ignored, and what should I try next?”

The crate should provide:

- `buildscript-report.json`
- `buildscript-summary.txt`
- `policy-gate.report.json`
- optional `notes.md`

### Recommended crate split

Keep 0.1 boring and explicit:

- `buildscript-report-core`
  - typed parser / normalizer for directives, messages, excerpts, redaction marks
- `cargo-buildscript-report`
  - cargo-subcommand or wrapper-oriented CLI
- optional later `buildscript-report-macros`
  - helper macros for maintainers who want better diagnostic emission

### 0.1 command surface

- `cargo buildscript report -- <cargo args...>`
- `cargo buildscript gate --deny-warnings`
- `cargo buildscript summarize path/to/raw.log`

### 0.1 Rust API surface

- `BuildscriptReport::from_streams(...)`
- `BuildscriptSummary::render_human(...)`
- `PolicyGate::evaluate(report, policy)`

### Honest boundaries

A good 0.1 does **not** pretend Cargo exposes a complete explanation graph.

It should be comfortable saying:

- “these directives were observed,”
- “this warning would normally be hidden,”
- “this message looks actionable,”
- “this workspace policy failed,”
- and “manual review required.”

### Ideal first adopters

- `-sys` crates with recurring install/support issues
- workspace CI maintainers who want reviewable gating
- IDE / editor wrappers that want structured build-script diagnostics

## P-0059 — buildscript-testkit

### What it should provide other people

P-0059 should let another human answer:

> “Did the build script still emit the contract we thought it emitted?”

The crate should provide:

- `fixture-manifest.toml`
- `buildscript-run.report.json`
- `directives.normalized.json`
- optional `notes.md`

### Recommended crate split

- `buildscript-test-core`
  - fixture execution, output capture, directive normalization
- `buildscript-fixture-tools`
  - fake `pkg-config`, fake `vcpkg`, temp env / path helpers
- `cargo-buildscript-test`
  - workspace-facing test runner

### 0.1 command surface

- `cargo buildscript-test`
- `cargo buildscript-test --update-goldens`
- `cargo buildscript-test --scenario fake_pkg_config_missing`

### 0.1 Rust API surface

- `TestContext`
- `BuildscriptRunner`
- `NormalizedDirectives`
- `GoldenComparison`

### Honest boundaries

A good 0.1 should emulate **fixture inputs**, not the whole Cargo scheduler.

It should prefer:

- fake-tool backends,
- env allowlists,
- normalized outputs,
- and deterministic placeholders for paths / temps.

### Ideal first adopters

- maintainers of `*-sys` crates
- crates with fallback probe logic (`pkg-config` then vendored, etc.)
- tooling authors who need real build-script fixture corpora

## P-0058 — native-deps-kit

### What it should provide other people

P-0058 should let another human answer:

> “What native library support was promised, what probe path was attempted, and how should I satisfy it on this platform?”

The crate should provide:

- `native-contract.toml`
- `native-resolution.report.json`
- `backend-attempts.receipt.json`
- `consumer-doctor.txt`
- optional later `consumer-doctor.report.json`

### Recommended crate split

- `native-contract-core`
  - schema/parser/normalizer for declared native requirements
- backend crates:
  - `native-contract-pkg-config`
  - `native-contract-vcpkg`
  - later vendored/source-build helper crate
- `cargo-native-deps`
  - doctor / explain / CI-facing UX

### 0.1 command surface

- `cargo native-deps doctor`
- `cargo native-deps explain <crate-or-lib>`
- `cargo native-deps check --offline`

### 0.1 Rust API surface

- `NativeContract`
- `ProbeBackend`
- `ResolutionReport`
- `BackendAttemptReceipt`

### Honest boundaries

P-0058 should **not** try to become a package manager.

Its job is:

- declare support intent,
- probe through available backends,
- produce a compact receipt,
- and suggest the next action.

It should be willing to say “manual review required” instead of inventing a false cross-platform abstraction.

### Ideal first adopters

- sys crates that currently hand-roll `pkg-config` / `vcpkg` / vendored fallbacks
- enterprise or air-gapped teams who need a repeatable support artifact
- Windows/MSVC crates where “what exactly did we find and link?” is otherwise buried

## Sequence constraint

The stack gets worse if implemented in reverse.

Why:

- P-0058 without the P-0046/P-0059 vocabulary tends to turn into another probe helper.
- P-0059 without P-0046 tends to compare raw logs instead of stable normalized outputs.
- P-0046 can stand on its own and helps every later step.

## Minimum scenario corpus

A good first implementation pass should only insist on a few scenarios:

1. missing `pkg-config` library with actionable package-install hint,
2. warning hidden for non-path dependency unless verbose/failure,
3. fake `pkg-config` success with stable normalized directives,
4. fallback from system probe to vendored path,
5. links override / metadata handoff without running the live build script.

## Repo implication

Future revisions in this frontier should prefer:

- a few example bundles,
- schema evolution notes,
- explicit 0.1 CLI/API surfaces,
- and evidence about where Cargo does and does not already provide the needed contract.

They should not default back to “add another native-build-adjacent proposal.”
