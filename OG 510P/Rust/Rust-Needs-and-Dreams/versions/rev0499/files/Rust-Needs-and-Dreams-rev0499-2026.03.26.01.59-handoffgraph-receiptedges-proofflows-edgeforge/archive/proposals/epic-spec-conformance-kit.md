# Epic Proposal: Spec Conformance Kit (`cargo conform`, `conformance-pack/v0`)

## One-sentence pitch
Give Rust a standard way to connect specification text, executable vectors, capability claims, and conformance results so language/toolchain assurance becomes portable evidence instead of bespoke process glue.

## Deliverables
- Read together with [`design/conformance-traceability-stack.md`](../design/conformance-traceability-stack.md) and [`design/spec-conformance-pilot-program.md`](../design/spec-conformance-pilot-program.md) so the kit is executed as part of a broader traceability stack rather than as a standalone test harness bid.
- `cargo conform` reference tool
- Schemas:
  - `spec-pack/v0`
  - `conformance-vectors/v0`
  - `implementation-capabilities/v0`
  - `conformance-report/v0`
  - `conformance-diff-report/v0`
  - `conformance-pack/v0`
- Adapters / publishers for:
  - compiletest-style suites
  - `ui_test`-style suites
  - profile-specific vector bundles (`core_language`, `unsafe_basics`, `ffi_surface`, `no_std`)
- Docs:
  - traceability mapping guide
  - profile authoring guide
  - qualification / assurance caveat guide

## Why now (signals)
- Rust now has a live, official specification trajectory. RFC 3355 laid out the need for a Rust specification and named safety-critical users, unsafe-code authors, and tooling maintainers as core beneficiaries.
  https://rust-lang.github.io/rfcs/3355-rust-spec.html
- The 2026 roadmap makes Safety-Critical Rust a flagship and explicitly ties it to MC/DC, normative `unsafe` documentation, Clippy lint work, and FLS release cadence. That makes attachable conformance evidence more urgent, not less.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The experimental language-specification goal says Rust wants a nightly/reference branch with stability markers and process integration across domain teams. That means the ecosystem now needs artifacts that can preserve official text, experimental text, and tested behavior as different but related truths.
  https://rust-lang.github.io/rust-project-goals/2026/experimental-language-specification.html
- In 2025H1, the Rust Project accepted a goal to transfer the Ferrocene Language Specification into rust-lang infrastructure and publish a rust-lang-owned version.
  https://rust-lang.github.io/rust-project-goals/2025h1/spec-fls-publish.html
- In 2025H2, the follow-on goal became sustaining the capability to keep the FLS updated, which is a strong signal that spec work is moving from one-time transfer to operational maintenance.
  https://rust-lang.github.io/rust-project-goals/2025h2/FLS-up-to-date-capabilities.html
- Rust’s 2026 flagship themes now list **stabilizing FLS release cadence** as part of Safety-Critical Rust.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The current FLS is already a serious normative artifact with paragraph ids and conforming-tool language, but it explicitly says it is not intended as a document enabling conformance between compilers. That means the ecosystem still needs a separate executable/traceable layer.
  https://rust-lang.github.io/fls/general.html
- Existing Rust test tools prove the primitives exist (`compiletest`, `ui_test`), and adjacent ecosystems already use split data/harness patterns (`toml-test-rs`), but Rust still lacks one versioned conformance pack/report boundary.
  https://rustc-dev-guide.rust-lang.org/tests/compiletest.html
  https://docs.rs/ui_test
  https://github.com/toml-rs/toml-test-rs

## Non-goals
- Replacing the Rust specification effort or FLS
- Declaring a new “official spec” by tool fiat
- Replacing compiletest with one universal runner
- Claiming that a conformance pack is itself certification
- Flattening every normative ambiguity into a fake binary answer

## Strategic value
This is a worthy contribution because it upgrades specification progress from **documents people read** into **artifacts systems can run and review**.

That unlocks several high-leverage workflows:
- release-to-release semantic regression review for toolchains,
- traceable qualification evidence for safety-heavy environments,
- partial profile claims for alternative implementations and analyzers,
- reusable target/edition-specific language subsets for platform teams,
- and better feedback loops between spec text and executable examples.

The archive already covers safety evidence, MIR export, coverage, policy, and release evidence. Spec Conformance Kit fills a deeper missing seam underneath them: a portable way to say what language behavior is in scope, how it was exercised, and what happened.

## Milestones
1. **v0 schemas + validator**
   - publish artifact schemas
   - validate traceability and capability declarations
2. **v0.2 reference runner + tiny core profile**
   - run a narrow `core_language` pack
   - emit `conformance-report/v0`
3. **v0.3 diff + partial-coverage workflow**
   - compare runs across toolchains / targets / spec revisions
   - make exclusions and incompleteness explicit
4. **v1 ecosystem adapters**
   - compiletest-style and `ui_test`-style adapters
   - integration points for safety evidence and release attachments
