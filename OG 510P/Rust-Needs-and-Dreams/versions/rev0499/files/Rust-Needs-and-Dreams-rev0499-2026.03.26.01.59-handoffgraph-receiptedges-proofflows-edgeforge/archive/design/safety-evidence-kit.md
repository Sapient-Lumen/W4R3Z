# Design: Safety Evidence Kit (`cargo safety`, `safety-pack/v0`)

## Goal
Standardize how Rust projects assemble **reviewable safety cases** by defining:
- portable artifacts for unsafe surface, cited safety contracts, lint posture, coverage criteria, verification claims, and waivers;
- a reference CLI (`cargo safety`) that can collect, diff, validate, and explain those artifacts;
- and clear boundaries between raw evidence, derived case status, and optional certification-specific packaging.

This is intentionally **not** a universal “safe crate” badge.
It is a substrate for attaching evidence and identifying unresolved gaps.

## References (signals)
- Rust 2026 flagship roadmap: Safety-Critical Rust milestones
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Normative Documentation for Sound `unsafe` Rust
  https://rust-lang.github.io/rust-project-goals/2026/safe-unsafe-for-safety-critical.html
- Implement and Maintain MC/DC Coverage Support
  https://rust-lang.github.io/rust-project-goals/2026/mcdc-coverage-support.html
- Instrument the Rust standard library with safety contracts
  https://rust-lang.github.io/rust-project-goals/2025h1/std-contracts.html
- `core::contracts` experimental module
  https://doc.rust-lang.org/core/contracts/index.html
- Unsafe Fields
  https://rust-lang.github.io/rust-project-goals/2025h1/unsafe-fields.html
- FLS publication + upkeep work
  https://rust-lang.github.io/rust-project-goals/2025h1/spec-fls-publish.html
  https://rust-lang.github.io/rust-project-goals/2025h2/FLS-up-to-date-capabilities.html
- FLS conformance text
  https://rust-lang.github.io/fls/general.html
- rustc instrumentation-based coverage
  https://doc.rust-lang.org/beta/rustc/instrument-coverage.html
- Clippy configuration and lint groups
  https://doc.rust-lang.org/clippy/configuration.html
  https://github.com/rust-lang/rust-clippy
- cargo-geiger
  https://github.com/geiger-rs/cargo-geiger
- Kani
  https://model-checking.github.io/kani/
- Prusti
  https://www.pm.inf.ethz.ch/research/prusti.html
- Creusot
  https://creusot-rs.github.io/creusot/
- Verus
  https://verus-lang.github.io/verus/

## Design principles
1. **Unsafe inventory is not a safety case**
   - counts and locations are useful, but must remain separate from the contracts and evidence that justify them.
2. **Authoritative citations matter**
   - the kit should distinguish normative references, experimental upstream contracts/docs, and local rationale.
3. **Coverage criteria must be named explicitly**
   - line, branch, decision, and MC/DC are not interchangeable.
4. **Verification engines are heterogeneous**
   - sanitizer findings, Miri runs, bounded model checking, deductive verification, and proof-oriented Rust subsets should remain distinct evidence families.
5. **Waivers and incompleteness are first-class**
   - “not yet justified”, “not yet covered”, and “waived until date X” are meaningful review states.
6. **Certification wrappers come after shared evidence**
   - do not hard-code one aviation/automotive/medical template into v0; make the underlying evidence portable first.

## Core components

### 1) `safety-subject/v0`
A scoped identity for what the case is about.

Required fields:
- workspace / crate / binary identity
- target triple / profile / features / configuration id
- release candidate or commit identity
- optional deployment or assurance profile tags:
  - `general-purpose`
  - `unsafe-heavy`
  - `safety-critical`
  - `ffi-heavy`
  - `no_std`

Design rule: safety claims are never context-free.

### 2) `unsafe-surface-report/v0`
Inventory of places where unsafe obligations or invariant-carrying surfaces exist.

Should record:
- `unsafe` blocks / functions / impls / traits / extern blocks
- invariant-carrying field or layout surfaces
- modules/files with concentrated unsafe density
- public-facing unsafe exposure estimate
- classification tags such as:
  - `layout`
  - `aliasing`
  - `ffi`
  - `initialization`
  - `concurrency`
  - `shared-memory`
  - `simd`
  - `proc-macro/build`

Sources may include compiler-assisted analysis, `cargo-geiger`, or future rustc support.

Design rule: this report names **where obligations live**, not whether they are justified.

### 3) `safety-contract-report/v0`
Traceability between unsafe sites and their safety contracts.

Each entry should support:
- referenced unsafe site / module / API id
- contract source type:
  - `NORMATIVE_DOC`
  - `UPSTREAM_EXPERIMENTAL_CONTRACT`
  - `LOCAL_RATIONALE`
  - `OPEN_GAP`
- citation targets:
  - Reference / FLS paragraph ids
  - std/core docs
  - accepted goal / tracking issue / MCP
  - local design note or code comment digest
- contract shape:
  - preconditions
  - postconditions
  - invariants
  - environmental assumptions
- review status:
  - `JUSTIFIED`
  - `PARTIAL`
  - `UNREVIEWED`
  - `CONTESTED`

Design rule: v0 should reward projects for citing the best available authority **without pretending local rationale is normative**.

### 4) `safety-lint-report/v0`
The lint-policy and waiver portion of the safety case.

Should capture:
- lint engines involved (`rustc`, `clippy`, future safety-specific crates)
- lint groups / explicit lints enabled
- severity mapping (`allow`, `warn`, `deny`, `forbid`, `expect`)
- configuration values / MSRV assumptions when relevant
- scoped suppressions / waivers with owner, expiry, justification
- result summary and changed findings

Design rule: a safety case should show **which static checks mattered**, not just that “Clippy passed”.

### 5) `coverage-criterion-report/v0`
Coverage evidence with explicit criterion identity.

Should record:
- engine identity and version
- criterion:
  - `line`
  - `region`
  - `branch`
  - `decision`
  - `mcdc`
- scope and exclusions
- target/profile/toolchain assumptions
- caveats and unsupported language/engine areas
- raw evidence references when retained externally

Design rule: never collapse MC/DC, decision, and ordinary source coverage into one undifferentiated number.

### 6) `verification-claim-report/v0`
Machine-readable claims backed by verification or dynamic-analysis engines.

Each claim should support:
- claim id and natural-language summary
- scope (crate/module/function/property)
- engine family:
  - `sanitizer`
  - `miri`
  - `model-checking`
  - `deductive-verification`
  - `proof-oriented-subset`
  - `manual-review-attestation`
- result:
  - `PASS`
  - `FAIL`
  - `INCONCLUSIVE`
  - `NOT_RUN`
- assumptions / bounds / unsupported constructs
- link to raw report / counterexample / proof artifact

Design rule: a verification claim is about **one property with one engine family**, not a blended assurance score.

### 7) `safety-case-report/v0`
Derived review summary over the above evidence.

Should include:
- subject identity
- key unresolved gaps
- waiver list
- derived status:
  - `PASS`
  - `WARN`
  - `FAIL`
  - `INCOMPLETE`
- explanation chains linking:
  - unsafe surface
  - contract citation or gap
  - lint / coverage / verification evidence
  - waiver or failure reason

Design rule: this is the opinionated review layer, but every conclusion must point back to source evidence.

### 8) `safety-pack/v0`
Bundle format containing:
- `safety-subject/v0`
- `unsafe-surface-report/v0`
- `safety-contract-report/v0`
- `safety-lint-report/v0`
- optional `coverage-criterion-report/v0`
- optional `verification-claim-report/v0`
- `safety-case-report/v0`
- optional raw attachments / signatures / external references

This is the artifact that should move through CI, release review, and external assurance workflows.

### 9) `cargo safety`
Reference UX:
- `cargo safety inventory`
- `cargo safety contracts`
- `cargo safety lint-report`
- `cargo safety coverage-report`
- `cargo safety verify-report`
- `cargo safety case`
- `cargo safety diff`
- `cargo safety pack`

`cargo safety` should start as an orchestrator / validator / explainer.
It should not try to replace Clippy, rustc coverage, sanitizers, or proof engines.

## Suggested integrations
- **Coverage Evidence Kit:** contributes criterion-specific coverage artifacts.
- **Formal Verification Kit:** contributes backend-specific proof and counterexample reports.
- **Sanitizer Battery Kit:** contributes runtime-checking claims.
- **Spec Conformance Kit:** contributes language/toolchain conformance evidence where relevant.
- **Validity Surface Kit / Pointer Surface Kit / Initialization Surface Kit / Atomic Surface Kit:** provide surface-specific context for interpreting unsafe obligations.
- **Trust Signals Kit:** can optionally contribute third-party dependency review inputs, but supply-chain trust should remain a distinct evidence family.

## What the kit should provide to others
- **unsafe-library maintainers:** a way to justify unsafe code with citations and scoped evidence.
- **safety-critical users:** attachable safety-case artifacts instead of bespoke spreadsheets.
- **CI/release tooling:** explainable PASS/WARN/FAIL/INCOMPLETE outcomes over explicit evidence families.
- **docs/spec teams:** a path for normative documentation work to land in downstream review workflows.
- **tool authors:** a shared report boundary for lints, coverage, contracts, and proofs.

## Overlap boundaries
- **Not Formal Verification Kit:** that kit standardizes backend-specific proof workflows; Safety Evidence assembles system-level case status.
- **Not Coverage Evidence Kit:** that kit defines coverage collection/merge semantics; Safety Evidence consumes criterion-aware coverage claims.
- **Not Sanitizer Battery Kit:** that kit runs and normalizes engines; Safety Evidence decides how those results contribute to the case.
- **Not Spec Conformance Kit:** that kit connects spec text to vectors/results; Safety Evidence consumes selected conformance outputs where relevant.
- **Not Trust Signals Kit:** dependency provenance and audits are trust inputs; Safety Evidence should only import them when explicitly relevant to a system-level case.

## Hard problems (explicitly scoped)
1. **Normative gaps will remain**
   - many unsafe patterns still will not have complete authoritative documentation.
2. **Evidence heterogeneity**
   - proofs, lints, sanitizers, and coverage do not yield a single comparable confidence metric.
3. **Certification language pressure**
   - teams will want certification-ready conclusions; v0 should provide evidence and case status, not fake compliance certificates.
4. **Scope explosion**
   - projects must be able to scope cases to selected modules / targets / binaries.
5. **Raw artifact retention**
   - some raw logs or traces may be large or private; v0 should support content-addressed references.

## Evaluation plan
Pilot on:
1. an unsafe-heavy library with good internal rationale but weak external traceability,
2. a safety-critical or robotics/embedded project that needs explicit criterion-aware coverage claims,
3. a crate using contracts or proof tools for a narrow hot spot,
4. a mixed project where some evidence families are intentionally missing and must show up as `INCOMPLETE` rather than being hand-waved.

Success bar:
- reviewers can see where unsafe obligations live,
- every important unsafe cluster has either authoritative citations or an explicit gap,
- coverage claims name the actual criterion,
- verification results preserve engine identity and assumptions,
- and waivers/incompleteness are durable artifacts rather than oral tradition.

## Stack note
Treat this kit as the assembly layer inside the shared **Safety-Critical Evidence Stack** described in [`design/safety-critical-evidence-stack.md`](./safety-critical-evidence-stack.md).
That stack should keep safety-case assembly, coverage criteria, dynamic-analysis lanes, and proof workflows distinct while letting them compose.

## Recommended execution posture
Use [`design/safety-critical-pilot-program.md`](./safety-critical-pilot-program.md) as the ranked rollout plan:
1. unsafe-heavy library review lane;
2. dynamic-analysis battery lane;
3. criterion-aware release lane;
4. proof-augmented module lane;
5. certification-facing release-candidate lane.

The point is not to make `cargo safety` swallow the rest of the stack.
The point is to make `cargo safety` the place where those other evidence families can be cited, correlated, and summarized honestly.
