## Gap refresh (rev0404)
Read this gap now as a gap for a **Safety-Critical Assurance Contract**, not only for isolated safety-case artifacts.

The updated missing piece is the bounded review layer that keeps **authority**, **criteria**, **engines**, **waivers**, and **consumer handoffs** explicit while composing safety evidence, coverage, lints, specs, and proofs into one attachable unit.

# Gap: reviewable safety cases for unsafe Rust and safety-critical systems

## Summary
Rust is rapidly gaining the ingredients needed for serious safety cases:
- normative unsafe documentation is now an explicit roadmap item;
- MC/DC coverage support is an explicit roadmap item;
- safety-critical linting in Clippy is an explicit roadmap item;
- the FLS is becoming a maintained rust-lang specification artifact;
- contracts are now an experimental part of `core` on nightly;
- and Rust continues to invest in unsafe-surface primitives like `unsafe` fields.

What the ecosystem still lacks is a **portable safety-case boundary** that can connect those ingredients into one reviewable story.
Today, teams can often produce individual artifacts — a list of `unsafe` blocks, a lint run, a coverage report, a Kani job, a note explaining an invariant, a waiver in CI — but they still struggle to answer, in one attachable unit:
- what unsafe surface exists,
- which safety contracts are backed by authoritative documentation versus local rationale,
- which lint profiles and waivers apply,
- which coverage criterion was actually achieved,
- which verification claims are evidence-backed and which remain aspirational,
- and what gaps remain before a release can be treated as safety-critical-ready.

That missing layer is not another verifier, linter, or dashboard.
It is a **safety-case evidence substrate** for Rust.

## Why now
Recent upstream Rust work makes this seam much more concrete than it used to be:
- Rust’s 2026 flagship roadmap explicitly names **Safety-Critical Rust** and lists four key milestones: MC/DC coverage support, normative unsafe documentation, safety-critical lints in Clippy, and a stable FLS release cadence. That is direct evidence that safety cases are becoming first-class ecosystem work, not just out-of-tree process glue.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The proposed 2026 goal **Normative Documentation for Sound `unsafe` Rust** says today’s unsafe documentation has gaps, that the Nomicon is incomplete, the UCG reference is largely abandoned, and that safety-critical users need authoritative documentation to build rigorous safety cases. It also proposes a concrete pattern-catalog workflow over real codebases such as `iceoryx2`.
  https://rust-lang.github.io/rust-project-goals/2026/safe-unsafe-for-safety-critical.html
- The proposed 2026 goal **Implement and Maintain MC/DC Coverage Support** says MC/DC is required by standards such as DO-178C, ISO 26262, and IEC 61508, and that implementing it outside the compiler is infeasible for real Rust because macro expansion makes source reconstruction unrealistic. That is direct evidence that coverage criterion identity has to be first-class in the safety story, not hidden behind a generic “coverage percentage”.
  https://rust-lang.github.io/rust-project-goals/2026/mcdc-coverage-support.html
- The accepted 2025H1 goal **Instrument the Rust standard library with safety contracts** aimed to finish compiler contract attributes and port contracts into the standard library. The `core::contracts` module now exists on nightly with experimental `#[requires]` and `#[ensures]` attribute macros. That is unusually strong support for treating contracts as machine-readable evidence inputs rather than prose comments alone.
  https://rust-lang.github.io/rust-project-goals/2025h1/std-contracts.html
  https://doc.rust-lang.org/core/contracts/index.html
- The accepted 2025H1 **Unsafe Fields** goal exists because safety invariants carried by fields are otherwise hard to denote and hard to evaluate. That is strong evidence that “where the unsafe obligations live” must remain explicit instead of being flattened into a global unsafe count.
  https://rust-lang.github.io/rust-project-goals/2025h1/unsafe-fields.html
- The FLS now lives under rust-lang infrastructure, defines conformance requirements for tools, and has an explicit follow-on goal about keeping it updated at the cadence needed by users and stakeholders. That is exactly the kind of spec substrate a safety-case layer should point at instead of copying into bespoke binders.
  https://rust-lang.github.io/fls/general.html
  https://rust-lang.github.io/rust-project-goals/2025h2/FLS-up-to-date-capabilities.html
- Clippy already has categories, configurable lint levels, Cargo.toml integration, and MSRV-sensitive behavior. That means Rust already has meaningful lint-policy building blocks; what is missing is the safety-case layer that records which lint profile mattered, why it mattered, and what was waived.
  https://doc.rust-lang.org/clippy/configuration.html
  https://github.com/rust-lang/rust-clippy

## The current seam is awkward
Today, safety-oriented review is stitched together from incompatible fragments:
- unsafe counts or grep results,
- comments in code explaining invariants,
- ad hoc citations into the Reference / Nomicon / issue trackers,
- Clippy and rustc lints with local `allow`/`expect` decisions,
- line or branch coverage percentages that may not match the required criterion,
- sanitizer / Miri / model-checking outputs,
- and external spreadsheets or certification binders.

Those pieces rarely become one diffable artifact.
This causes recurring failure modes:
- unsafe inventory is present, but not linked to the safety contracts that justify it;
- teams claim “coverage” without naming whether they mean line, branch, decision, or MC/DC;
- lint waivers live in code or CI without durable rationale;
- proof or sanitizer runs are hard to scope and compare across releases;
- system-level safety cases cannot cleanly distinguish authoritative upstream semantics from local assumptions or unresolved gaps.

## Why this matters
A real safety-case substrate would help:
1. **unsafe-library maintainers** justify invariants with durable citations and scoped evidence;
2. **safety-critical adopters** assemble reviewable evidence without bespoke document engineering;
3. **tool authors** publish contracts, lint findings, coverage-criterion results, and verification claims into one shared shape;
4. **CI/release systems** gate on explicit safety criteria instead of vague “passed checks” language;
5. **specification and documentation efforts** land in downstream review workflows rather than stopping at prose.

## What “good” looks like
A worthy contribution here is a **portable Rust safety-case kit** with at least:
- `unsafe-surface-report/v0` — where unsafe obligations and invariant-carrying surfaces exist;
- `safety-contract-report/v0` — which sites are justified by normative docs, experimental contracts, or local rationale, and where gaps remain;
- `safety-lint-report/v0` — which lint profiles, severities, and waivers were in force;
- `coverage-criterion-report/v0` — which criterion and engine actually produced the claimed results;
- `verification-claim-report/v0` — which claims are backed by sanitizers, model checking, deductive proofs, or other engines;
- `safety-case-report/v0` — a scoped PASS/WARN/FAIL/INCOMPLETE view over the above;
- and `safety-pack/v0` — one attachable unit for CI, release review, or external assurance workflows.

The winning version is **traceable, criterion-aware, citation-aware, and explicit about gaps**.
It should feel more like structured evidence than like a badge, dashboard, or marketing claim.
