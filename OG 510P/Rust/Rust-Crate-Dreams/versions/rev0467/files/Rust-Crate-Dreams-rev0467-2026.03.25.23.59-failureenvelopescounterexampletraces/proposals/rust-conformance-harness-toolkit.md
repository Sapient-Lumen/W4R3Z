---
id: P-0264
title: Rust Conformance Harness Toolkit — reusable suites, custom runners, and evidence bundles
status: idea
domains: [tooling, testing, conformance, ci, interoperability]
last_reviewed: 2026-03-09
evidence:
  - https://doc.rust-lang.org/cargo/commands/cargo-test.html
  - https://doc.rust-lang.org/cargo/reference/cargo-targets.html
  - https://nexte.st/docs/design/custom-test-harnesses/
  - https://nexte.st/docs/machine-readable/junit/
  - https://docs.rs/libtest-mimic/latest/libtest_mimic/
  - https://docs.rs/datatest-stable
needs:
  - Rust has enough custom-harness substrate that teams can build conformance runners, but no shared crate has become the boring default for suite packaging, execution, and shareable evidence.
  - The missing value is not another one-off test DSL; it is a reusable suite/runner/bundle contract that many protocol, format, security, and device ecosystems can adopt.
risks:
  - It can sprawl into “reinvent libtest/nextest”.
  - The toolkit must stay suite-first and artifact-first, not become a generic test framework replacement.
  - It must separate “case unsupported”, “environment missing”, and “implementation failed” cleanly or it will produce misleading interop results.
---

# P-0264 — Rust Conformance Harness Toolkit

**Codename:** `conformkit`

**Bundle:** `*.conformbundle.zip`

**Primary surface:** reusable conformance suites as dependencies, custom runners, and evidence bundles.

## Problem

Rust already has real substrate for custom test execution.

- Cargo supports disabling the built-in harness with `harness = false`.
- Cargo target settings make it possible to own `main()` and build custom test/bench executables.
- Nextest documents custom-harness patterns and practical integration constraints.
- `libtest-mimic` exists precisely because people want libtest-like UX while still owning discovery and execution.
- `datatest-stable` shows that file-driven suites are a recurring need, not an edge case.
- Nextest also already emits JUnit, which means Rust has runner/output substrate but still lacks a reusable suite contract above it.

That means the ecosystem is not blocked on raw capability.
It is blocked on the absence of a **shared conformance contract**.

Today, when a Rust implementation wants to ship an RFC/standard/profile/fixture suite, it often improvises:
- test discovery,
- case metadata,
- capability gating,
- reporting formats,
- artifact capture,
- sharding semantics,
- and minimal repro packaging.

The result is fragmentation: every standards effort builds its own half-runner.

## Main judgment

A worthy crate here would not try to replace `cargo test`.
It would give other people a portable way to say:

- here is the suite,
- here are the cases,
- here is how to execute them,
- here is the result shape,
- and here is the failing evidence bundle you can attach to a bug or interoperability report.

That is why this proposal is one of the archive’s stronger **ecosystem multiplier** bets.

## What the crate should provide other people

### 1. Publishable suites as dependencies
A conformance suite should be shippable as a crate that other implementations can depend on.

That means:
- stable case IDs,
- stable case metadata,
- capability tags,
- suite versioning,
- redistributable fixtures where licensing allows,
- and a manifest strict enough that another implementation can tell which cases are “the same” across releases.

### 2. One runner contract
The crate should define a standard way to:
- discover cases,
- filter/select them,
- run them against one or more implementations,
- capture structured outputs,
- and classify unsupported / skipped / environment-gated / failed outcomes honestly.

A real missing feature here is not raw execution, but **verdict vocabulary** that does not collapse everything into pass/fail.

### 3. Environment receipts
Conformance runs are often only meaningful relative to an environment: feature flags, target platform, external binaries, device lane, server profile, or simulator state.

The crate should emit a compact `environment.receipt.json` that records:
- runner version,
- suite version,
- implementation id/version,
- capability set,
- target triple / OS / architecture,
- optional external service or device lane,
- and any environment preconditions that were missing.

### 4. A shareable failure artifact
The runner should emit `*.conformbundle.zip` so a failing case becomes reviewable by another maintainer.

That bundle should capture:
- suite version,
- case inputs,
- expected outcome or property,
- actual outputs,
- environment and runner info,
- logs/traces,
- and a minimal reproduction summary.

### 5. Result interoperability
The toolkit should speak both human and machine:
- terminal summaries,
- JSON,
- JUnit,
- and optional HTML.

But the **canonical** result model should be the toolkit’s own stable JSON/CBOR-ish schema, with JUnit as an export lane rather than the source of truth.

### 6. Comparison mode without fake certainty
The crate should help two implementations be compared on the same suite, but it must stay honest about ambiguity.

A good comparison report should be able to say:
- both passed,
- one failed,
- one lacked a declared capability,
- environments were not actually comparable,
- or the outputs differed but the verdict remained inconclusive.

### 7. Suite-author ergonomics
The best version of this crate helps authors publish a good suite with very little bespoke glue:
- macros or builders for case declaration,
- fixture discovery helpers,
- capability tags,
- skip/xfail vocabulary,
- stable sharding semantics,
- and predictable filters that map onto nextest/libtest-style workflows.

## Persona / who it’s for

- standards/profile maintainers
- protocol and format crate authors
- CI engineers running cross-implementation compatibility checks
- tool authors who need data-driven or environment-specific harnesses
- interoperability event organizers and implementers
- safety/security teams that later want conformance evidence imported into higher-layer review packs

## Users & user stories

- **Protocol maintainer:** “Ship the official case corpus as a crate so every implementation can run the same suite.”
- **Implementation author:** “Run the suite against my library, emit JSON and one failure bundle, and attach it upstream.”
- **CI owner:** “Shard the suite in CI while preserving stable case IDs and reproducible reports.”
- **Interop lead:** “Compare two implementations on the same suite without inventing a bespoke runner.”
- **Safety engineer:** “Import conformance evidence into an assurance review without reinterpreting ad hoc logs.”

## Prior art (and why it’s insufficient)

- **Cargo/libtest** are excellent defaults for normal Rust tests, but not a suite-publishing and conformance-artifact story.
- **Nextest** is a strong runner with machine-readable outputs, but not itself a suite definition and evidence-bundle standard.
- **libtest-mimic** is useful infrastructure, but not a complete suite/runner/bundle contract.
- **datatest-stable** proves file-driven suites are real, but it remains one harness style, not a cross-ecosystem schema and bundle contract.

The missing value is the **shared suite packaging and result artifact layer** above them.

## Design goals

1. **Suite-first** — optimize for reusable conformance suites, not ordinary unit tests.
2. **Artifact-first** — a failing case should become a shareable bundle, not a pile of logs.
3. **Implementation-neutral** — support single implementation runs and cross-implementation matrices.
4. **Small core, layered extras** — keep the model stable; let execution/reporting adapters vary.
5. **Honest unsupported states** — don’t collapse “not implemented”, “environment missing”, and “failed” into one bucket.
6. **Assurance-friendly** — conformance artifacts should be importable by higher-layer review tools without pretending a suite run is the whole safety argument.

## Proposed architecture

```text
conformkit-core/       # case model, suite manifests, discovery, filter semantics
conformkit-macros/     # optional declaration macros
conformkit-runner/     # execution engine and adapter traits
conformkit-report/     # JSON, JUnit, terminal, optional HTML
conformkit-bundle/     # conformbundle.zip read/write and diff helpers
cargo-conform/         # cargo-facing UX and CI helpers
```

## Core data model

- `SuiteId`
- `SuiteVersion`
- `CaseId`
- `CaseMetadata`
- `CapabilityTag`
- `EnvironmentConstraint`
- `EnvironmentReceipt`
- `ObservedResult`
- `ConformanceVerdict`
- `ComparisonFinding`
- `ConformanceBundle`

## Bundle draft

`*.conformbundle.zip`

- `suite.json`
- `case.json`
- `inputs/`
- `expected.json`
- `observed.json`
- `environment.receipt.json`
- `verdict.json`
- `runner-contract.report.json`
- `logs/`
- `notes.md`

## MVP surface

### 0.1
- stable case/suite model
- runner traits
- terminal + JSON output
- `environment.receipt.json`
- failing-case bundle export

### 0.2
- JUnit export
- sharding/filter expressions
- fixture discovery helpers
- `skip`, `xfail`, and capability-gated execution
- simple single-implementation `cargo conform doctor`

### 0.3
- multi-implementation comparison mode
- optional HTML reports
- bundle diffing and minimal repro helpers
- import bridge for higher-layer evidence consumers

## Compatibility story

- The toolkit should layer over Cargo, nextest, libtest-mimic, or bespoke runners rather than replace them.
- Case IDs, manifest schemas, and bundle shapes should stabilize earlier than macro syntax.
- JUnit and terminal output are export lanes, not the canonical semantic model.
- Cross-implementation comparison should remain conservative when environments are mismatched.

## Conformance & fixtures

The first fixture family should include:

1. `capability_missing_not_failure` — a case is not supported because the implementation never claimed the required capability.
2. `environment_missing_external_service` — execution could not start because a declared external precondition was absent.
3. `same_case_two_impls_diverge` — two implementations produced meaningfully different outcomes for the same case.
4. `upstream_bug_bundle_minimal_repro` — one failing case exports a compact bundle suitable for issue filing.

Goldens should verify:

- stable case IDs across sharding and filter operations,
- explicit unsupported vs failed vs environment-missing verdicts,
- stable `environment.receipt.json` semantics,
- JUnit export without losing internal verdict detail,
- and conservative comparison findings when runs are not really comparable.

## Path to boring stability

- Freeze the case/suite/bundle schema early.
- Avoid becoming a general-purpose replacement for libtest.
- Keep execution adapters thin so nextest/libtest-mimic/custom runners remain interoperable substrate.
- Prefer stable case IDs and bundle formats over elaborate DSL design.
- Keep assurance import secondary and adapter-driven.

## Adoption plan

1. Start with one suite crate plus one implementation.
2. Add JSON/JUnit outputs for CI and maintainers.
3. Add failure bundles for upstream issue filing.
4. Only then add cross-implementation comparison or distributed execution.
5. Add assurance-case imports only after the conformance artifact itself feels boring and stable.

## Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 27/30**

## Minimum lovable MVP

A crate workspace that lets authors publish a conformance suite as a dependency, run it with a custom harness, emit machine-readable results, classify unsupported versus failed cases honestly, and package a failing case as one portable bundle.

## De-risk plan

1. Build around stable case IDs and manifests first.
2. Use existing harness substrate rather than replacing it.
3. Pilot on one data-driven corpus and one protocol-style conformance suite.
4. Add comparison mode only after single-implementation bundle workflows feel solid.
5. Treat assurance imports as a consumer-side adapter, not as proof that conformkit must become a certification tool.

## Non-goals

- Not a replacement for `cargo test` in ordinary Rust projects.
- Not a generic property-testing framework.
- Not a standards body or certification program.
- Not a giant custom CI orchestrator.
- Not an assurance-case editor.

## Open questions

- Which suite-manifest shape is small enough to stabilize early?
- How much of nextest integration should be native versus adapter-driven?
- Which bundle fields must be mandatory for useful upstream bug reports?
- Which comparison findings deserve first-class vocabulary in 0.3?

## Sources

- https://doc.rust-lang.org/cargo/commands/cargo-test.html
- https://doc.rust-lang.org/cargo/reference/cargo-targets.html
- https://nexte.st/docs/design/custom-test-harnesses/
- https://nexte.st/docs/machine-readable/junit/
- https://docs.rs/libtest-mimic/latest/libtest_mimic/
- https://docs.rs/datatest-stable
