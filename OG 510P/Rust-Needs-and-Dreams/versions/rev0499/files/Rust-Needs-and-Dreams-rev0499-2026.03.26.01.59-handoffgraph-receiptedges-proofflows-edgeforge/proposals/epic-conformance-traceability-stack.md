# Epic Proposal: Conformance Traceability Stack (`cargo traceability` + `traceability-pack/v0`)

## One-sentence pitch
Give Rust one portable way to connect **spec text, executable vectors, compiler-lane acceptance reality, and assurance/release consumers** without flattening them into a fake universal conformance or certification badge.

## Why this is worthy
Rust now has credible ingredients on all sides of this seam, but still lacks the attachable execution layer above them:
- RFC 3355 says the specification should serve unsafe-code authors, safety-critical users, language designers, and tooling maintainers, and should eventually be incorporated into language evolution.
  https://rust-lang.github.io/rfcs/3355-rust-spec.html
- The Rust Project accepted a goal to bring the FLS into rust-lang infrastructure and then followed it with a goal to develop the capabilities to keep the FLS updated sustainably.
  https://rust-lang.github.io/rust-project-goals/2025h1/spec-fls-publish.html
  https://rust-lang.github.io/rust-project-goals/2025h2/FLS-up-to-date-capabilities.html
- The 2026 flagship roadmap makes Safety-Critical Rust concrete through MC/DC support, normative `unsafe` documentation, safety-critical Clippy work, and FLS release cadence.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  https://rust-lang.github.io/rust-project-goals/2026/mcdc-coverage-support.html
  https://rust-lang.github.io/rust-project-goals/2026/safe-unsafe-for-safety-critical.html
  https://rust-lang.github.io/rust-project-goals/2026/safety-critical-lints-in-clippy.html
  https://rust-lang.github.io/rust-project-goals/2026/stabilize-fls-releases.html
- The experimental language-specification goal explicitly proposes an experimental/nightly spec with instability markers, team review, and process integration, which means text authority and artifact traceability can no longer be treated as the same thing.
  https://rust-lang.github.io/rust-project-goals/2026/experimental-language-specification.html
- a-mir-formality explicitly aims to integrate with the Rust specification and complementary models like MiniRust, creating a foundation for validating Rust’s type-safety guarantees.
  https://rust-lang.github.io/rust-project-goals/2025h2/a-mir-formality.html
- Cargo and rustc already expose real execution primitives (`cargo test`, doctests, source-based coverage), but those primitives do not by themselves provide a durable spec-to-result traceability contract.
  https://doc.rust-lang.org/cargo/commands/cargo-test.html
  https://doc.rust-lang.org/beta/rustc/instrument-coverage.html

The missing contribution is no longer “more prose” or “another runner”.
It is the reviewable boundary above those ingredients.

## Deliverables
- Read together with [`design/conformance-traceability-stack.md`](../design/conformance-traceability-stack.md), [`design/conformance-traceability-pilot-program.md`](../design/conformance-traceability-pilot-program.md), and [`design/spec-conformance-pilot-program.md`](../design/spec-conformance-pilot-program.md) so the stack lands as a composition layer rather than a leaf-harness rewrite.
- `cargo traceability` reference tool
- Schemas:
  - `traceability-brief/v0`
  - `traceability-diff/v0`
  - `traceability-pack/v0`
  - `traceability-handoff/v0`
- Imported artifacts:
  - `spec-pack/v0`
  - `conformance-vectors/v0`
  - `implementation-capabilities/v0`
  - `conformance-report/v0`
  - acceptance-lane reports
  - selected safety-evidence / coverage / proof attachments
- Docs:
  - stable-text profile recipe
  - experimental-text authority guide
  - acceptance-vs-conformance guide
  - release / qualification handoff guide

## Strategic value
This deserves promotion because it gives the archive one **language-semantics traceability boundary** that many other seams can import.

With it:
- spec work stops being trapped in prose-only progress,
- compiler and language teams get narrow diffable traces instead of issue-thread archaeology,
- safety-critical and assurance consumers can import conformance subjects rather than restating semantics,
- release/support/audit consumers can attach bounded evidence without inheriting raw test logs,
- and future Rust evolution work can publish what text, vectors, and implementation reality actually lined up.

The prize is not a giant conformance platform.
The prize is a boring, portable bridge from text to evidence.

## Proposed shape
Ship a narrowly scoped stack-level layer:
1. import `spec-pack/v0`, `conformance-vectors/v0`, `implementation-capabilities/v0`, and `conformance-report/v0` as the core language-facing traceability boundary;
2. attach acceptance-lane artifacts rather than pretending implementation reality is identical to conformance;
3. attach safety-evidence / coverage / proof artifacts without letting them redefine language semantics;
4. emit `traceability-handoff/v0` for release, qualification, support, and audit consumers;
5. provide diffing that preserves authority class, profile scope, and incompleteness instead of flattening everything into one status bit.

## Critical design bet
The critical bet is that **traceability should stop at preserving the chain from text to vectors to results to bounded downstream handoffs**.
That means:
- normative and experimental text are both in scope,
- executable vectors and capabilities are in scope,
- acceptance-lane reality is attached,
- assurance and release consumers may import the packs,
- but the stack does **not** become the sole owner of certification templates, compiler policy, or one universal “Rust conformant” verdict.

Without that boundary, the proposal either stays too weak to matter or expands into a fake certification framework.

## Milestones
1. **v0 schemas + stable-text lane**
   - publish `traceability-brief` / `traceability-pack`
   - import the existing conformance-kit artifacts
2. **v0.2 experimental-text lane**
   - authority classes for stable vs experimental text
   - instability-marker aware diffing
3. **v0.3 acceptance-diff lane**
   - attach stable/beta/nightly or solver/borrow-check acceptance reports
   - keep workaround truth explicit
4. **v0.4 safety-evidence import lane**
   - attach coverage / unsafe-doc / proof-oriented evidence
   - preserve authority and criterion boundaries
5. **v1 release / qualification handoff lane**
   - emit bounded handoffs for audit, archaeology, support, and qualification consumers

## Execution order
Use [`design/conformance-traceability-pilot-program.md`](../design/conformance-traceability-pilot-program.md) as the stack-level rollout:
1. stable-text core-profile lane,
2. experimental-text / instability-marker lane,
3. acceptance-diff lane,
4. safety-evidence import lane,
5. release / qualification / archaeology lane.

Use [`design/spec-conformance-pilot-program.md`](../design/spec-conformance-pilot-program.md) as the leaf-level conformance rollout beneath it.
Use [`design/safety-critical-pilot-program.md`](../design/safety-critical-pilot-program.md) as the assurance rollout beneath it.

## Non-goals
- replacing the Rust specification, the FLS, or the Rust Reference;
- replacing compiletest, `ui_test`, libtest, or coverage tools with one giant runner;
- creating an official certification badge or universal qualification binder;
- flattening experimental text, stable text, acceptance quirks, and assurance conclusions into one verdict;
- turning every Rust release into a full conformance-suite event.

## Success bar
This becomes worthy when a maintainer or downstream consumer can answer:
- what text authority was in scope;
- what vectors and capability profile defined the run;
- what was a conformance result versus an acceptance-lane reality note;
- what assurance or release consumer imported the result;
- what remained partial, provisional, or out of scope;
- and what claim is still safe to repeat months later,

without reverse-engineering prose docs, compiletest trees, CI logs, and certification notes by hand.
