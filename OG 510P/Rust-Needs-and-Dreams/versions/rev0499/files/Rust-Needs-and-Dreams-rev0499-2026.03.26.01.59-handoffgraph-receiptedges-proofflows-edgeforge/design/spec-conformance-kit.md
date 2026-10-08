# Design: Spec Conformance Kit (`cargo conform`, `conformance-pack/v0`)

## Goal
Define a portable specification/conformance contract for Rust so spec work, executable vectors, and toolchain results can be exchanged as versioned artifacts instead of being trapped inside one runner, one qualification pipeline, or one compiler repository.

This should **not** replace the Rust specification effort, FLS, compiletest, or project-specific qualification workflows. It should make them easier to compose, scope, diff, and archive.

## References (signals)
- The 2026 roadmap now treats Safety-Critical Rust as a flagship and makes MC/DC, normative `unsafe` documentation, safety-critical Clippy work, and FLS release cadence explicit milestones, which raises the value of attachable conformance evidence.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The experimental language-specification goal is about a nightly/reference branch with stability markers and team-integrated review. That makes it more important to keep official text, experimental text, and executable evidence distinct but connected.
  https://rust-lang.github.io/rust-project-goals/2026/experimental-language-specification.html
- The Rust Reference expansion goal and a-mir-formality goal both reinforce that specification work is becoming more operational and more connected to executable semantics.
  https://rust-lang.github.io/rust-project-goals/2025h2/reference-expansion.html
  https://rust-lang.github.io/rust-project-goals/2025h2/a-mir-formality.html
- RFC 3355 defines the motivation for a Rust specification and explicitly names unsafe-code authors, safety-critical users, and tooling maintainers as beneficiaries.
  https://rust-lang.github.io/rfcs/3355-rust-spec.html
- The accepted 2025H1 goal transferred the FLS into rust-lang infrastructure and aimed to publish it like other rust-lang-maintained books.
  https://rust-lang.github.io/rust-project-goals/2025h1/spec-fls-publish.html
- The 2025H2 follow-on goal is about developing the capability and capacity to keep the FLS up to date sustainably.
  https://rust-lang.github.io/rust-project-goals/2025h2/FLS-up-to-date-capabilities.html
- Rust’s 2026 flagships treat stabilizing the FLS release cadence as a Safety-Critical Rust milestone.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The FLS now lives under rust-lang infrastructure, contains normative sections and paragraph ids, and defines what a “conforming tool” must do; but it also says it is not intended as a document enabling conformance between compilers.
  https://rust-lang.github.io/fls/general.html
- `compiletest` is the main harness of the Rust compiler test suite and proves that large structured test inventories are tractable, but it is an internal harness rather than a portable ecosystem artifact boundary.
  https://rustc-dev-guide.rust-lang.org/tests/compiletest.html
- `ui_test` proves there is demand for reusable compile-and-compare harnesses outside rust-lang proper.
  https://docs.rs/ui_test
- `toml-test-rs` is a useful adjacent pattern: language-agnostic test data plus Rust-native harness pieces.
  https://github.com/toml-rs/toml-test-rs


Execution anchor: use [`design/spec-conformance-pilot-program.md`](./spec-conformance-pilot-program.md) as the ranked rollout plan, and read this kit as the execution core of [`design/conformance-traceability-stack.md`](./conformance-traceability-stack.md) rather than as an isolated language-tooling curiosity.

## Core components

### 1) `spec-pack/v0`
A pack of *references* to the normative material in scope, not a giant duplicated book snapshot by default.

Required ideas:
- source documents (`fls`, Reference, Nomicon, RFC fragments, UCG notes when explicitly in-scope)
- version/digest identifiers
- paragraph / anchor references
- applicability metadata:
  - edition(s)
  - target scope
  - library scope (`core`, `alloc`, `std`)
  - feature-gate assumptions
- profile tags such as:
  - `core_language`
  - `unsafe_basics`
  - `ffi_surface`
  - `no_std`
  - `safety_critical_subset`

Design rule: v0 should prefer **pointers + digests + paragraph ids** over embedding huge documents.

### 2) `conformance-vectors/v0`
Executable tests and fixtures mapped to the spec references they exercise.

Each vector should support:
- stable vector id
- vector kind (`compile-pass`, `compile-fail`, `run-pass`, `run-output`, `ffi`, `layout`, `target-specific`)
- referenced spec ids / paragraph ids
- required capabilities / target assumptions
- optional expected-inconclusive reasons
- optional fixture attachments / golden outputs

Design rule: a vector is about **observable behavior**, not about reusing one exact test harness implementation.

### 3) `implementation-capabilities/v0`
What a toolchain + runner combination claims to support.

Examples:
- compiler identity / version / commit
- runner identity / version
- supported editions / target triples
- hosted vs freestanding / `no_std` support
- FFI execution support
- unsupported or intentionally out-of-scope areas
- known deviations / accepted caveats

This prevents consumers from mistaking a partial conformance run for a universal one.

### 4) `conformance-report/v0`
The machine-readable results artifact.

Required fields:
- toolchain + runner identity
- input pack digests
- vector results (`pass`, `fail`, `skip`, `xfail`, `inconclusive`)
- reason codes
- target / flags / environment summary
- traceability rows linking:
  - `spec_ref`
  - `vector_id`
  - `result`
- optional human summary + deviation notes

Design rule: **partial coverage must be first-class**.
A useful report that covers 180 precise vectors honestly is better than a fake “Rust conformant” badge.

### 5) `conformance-diff-report/v0`
Structured diff between two conformance runs.

Use cases:
- nightly/stable regressions
- target bring-up progress
- qualification delta review
- “what changed when we upgraded the runner or spec-pack?”

Must explicitly distinguish:
- result delta caused by toolchain
- result delta caused by vector changes
- result delta caused by spec-pack scope changes

### 6) `conformance-pack/v0`
Bundle format containing:
- `spec-pack/v0`
- `conformance-vectors/v0`
- `implementation-capabilities/v0`
- `conformance-report/v0`
- optional `conformance-diff-report/v0`
- optional raw logs / stdout / stderr / binaries / fixtures

This is the attachable unit for CI, qualification evidence, issue reports, or release metadata.

### 7) `cargo conform`
Reference UX:
- `cargo conform run`
- `cargo conform diff`
- `cargo conform doctor`
- `cargo conform pack`
- `cargo conform list-vectors`

`cargo conform` should begin as an orchestrator / packer / validator.
It should not force all conformance work into one mega-runner.

## Default policy
- **Spec text is source truth; artifacts point at it.**
- **Executability and traceability are separate concerns from specification authorship.**
- **Profiles beat universal claims.**
- **Honest incompleteness beats fake certification language.**
- **Runner independence matters:** vectors should be portable across compiletest-style, ui_test-style, or custom runners where feasible.

## What the kit should provide to others
- **Spec team / language team:** a path from normative text to executable traceability.
- **Compiler teams:** replayable semantic regression packs, diffable across versions and targets.
- **Safety-critical users:** attachable evidence that links scope, vectors, and results.
- **Alternative toolchains / analyzers:** profile-based partial conformance claims with explicit capability declarations.
- **Library/platform maintainers:** reusable subsets rather than all-or-nothing language qualification.

## Overlap boundaries
- **Not MIR Analysis Kit:** MIR export is a compiler-analysis substrate; this kit is about spec references, vectors, and externally observable conformance.
- **Not Safety Evidence Kit:** safety policy and assurance conclusions stay there; this kit supplies one evidence input.
- **Not Cargo Report Kit:** build/session/timing artifacts remain separate.
- **Not Debugger Experience Kit / DST Kit:** runtime debugging and deterministic failure reproduction are distinct from language/toolchain conformance.
- **Not Schema Contract Kit:** this is about Rust language/toolchain behavior, not service or data contracts.

## Hard problems (explicitly scoped)
1. **Spec churn and overlap**
   - Some areas will still straddle FLS, Reference, UCG, RFCs, and implementation reality.
   - v0 must allow multiple cited sources and “provisional” mappings.

2. **Undefined behavior and non-normative areas**
   - Not every sharp edge should yield a binary pass/fail conformance claim.
   - `inconclusive` / `not-in-scope` must be normal outcomes.

3. **Target-dependent behavior**
   - Many vectors are target/ABI/environment specific.
   - Target assumptions belong in both vector metadata and reports.

4. **Diagnostics vs semantics**
   - Diagnostics are useful test targets, but wording and formatting are often not normative.
   - v0 should distinguish semantic result vectors from diagnostic-expectation vectors.

5. **Qualification-language abuse**
   - The tool must avoid sounding like a certification oracle.
   - Reports should state coverage and exclusions prominently.

## Minimal adoption path
1. Publish schemas + validators.
2. Ship a tiny reference `cargo conform` that can validate packs and run a small vector profile.
3. Pilot on a narrow `core_language` profile.
4. Add adapters for compiletest-style and ui_test-style execution.
5. Make it easy to attach `conformance-pack/v0` to CI and broader evidence bundles.

## Why this is worth doing
Rust now has real specification momentum. The missing opportunity is to keep that momentum from ending at prose.
A good Spec Conformance Kit would turn the spec effort into something toolchains, vendors, CI systems, and assurance-heavy teams can actually run, diff, and archive.
