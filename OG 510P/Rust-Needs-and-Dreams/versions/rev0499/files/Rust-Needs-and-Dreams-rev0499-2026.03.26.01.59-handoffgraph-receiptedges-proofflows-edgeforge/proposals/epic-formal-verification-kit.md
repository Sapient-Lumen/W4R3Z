# Epic Proposal: Formal Verification Kit (`cargo verify`, `verify-pack/v0`)

## One-sentence pitch
Give Rust a standard way to declare verification intent, record backend capabilities, publish proof results, and replay counterexamples so formal methods can plug into normal Cargo/CI/release workflows without forcing one verifier to win.

## Deliverables
- `cargo verify` reference tool
- Schemas:
  - `verify-intent/v0`
  - `verify-capabilities/v0`
  - `verification-report/v0`
  - `counterexample-pack/v0`
  - `verify-diff-report/v0`
  - `verify-pack/v0`
- Adapters / publishers for:
  - Kani-style model checking
  - Creusot-style deductive verification
  - Prusti-style contract verification
  - Verus-style proof workflows
  - ESBMC-aligned backends where feasible
  - future Flux / VeriFast imports where feasible
- Ranked rollout in `design/formal-verification-pilot-program.md`
- Docs:
  - proof-scope authoring guide
  - assumptions / trusted-code disclosure guide
  - CI and release attachment guide

## Why now (signals)
- The Rust project’s standard-library verification survey/challenge makes formal verification an official upstream concern rather than an external curiosity.
  https://rust-lang.github.io/rust-project-goals/2024h2/std-verification.html
- The `std` contracts goal explicitly aims to enable verification of the standard library and treats contracts as code.
  https://rust-lang.github.io/rust-project-goals/2025h1/std-contracts.html
- `a-mir-formality` is explicitly about aligning a formal model with compiler behavior and helping validate Rust’s type-safety story.
  https://rust-lang.github.io/rust-project-goals/2025h2/a-mir-formality.html
- Safety-Critical Rust is now a roadmap/application area that needs reviewable evidence and qualification-friendly workflows.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
  https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- The Rust Foundation says ESBMC work is intended to expand Rust verification support, is live in the std-verification workflow, and is aiming to align as an alternative backend for Kani, which is a strong signal that interop will matter more, not less.
  https://rustfoundation.org/media/expanding-the-rust-formal-verification-ecosystem-welcoming-esbmc/
- The Verify Rust Std project now lists multiple approved tools in CI — ESBMC, Flux, Kani, and VeriFast — which is direct evidence that the public verification substrate is plural.
  https://model-checking.github.io/verify-rust-std/tools.html
- The Rust Formal Methods Interest Group explicitly wants better inter-compatibility, especially for specifications.
  https://rust-formal-methods.github.io/
- The ecosystem already has multiple live toolchains with distinct workflows (`cargo kani`, `cargo creusot prove`, `cargo prusti`, Verus), but no shared proof-artifact/report boundary.
  https://model-checking.github.io/kani/usage.html
  https://creusot-rs.github.io/creusot/guide/
  https://viperproject.github.io/prusti-dev/user-guide/basic.html
  https://verus-lang.github.io/verus/guide/

## Non-goals
- Building a universal verifier that replaces Kani, Creusot, Prusti, Verus, or ESBMC
- Claiming that one `pass` means the same thing across all backends
- Collapsing proof results into a single badge without assumptions or scope
- Replacing Safety Evidence Kit, Spec Conformance Kit, or Sanitizer Battery Kit
- Forcing every proof workflow into Cargo orchestration before pack/interop value exists

## Strategic value
This is a worthy contribution because it upgrades verification from **tool-specific heroics** into **reviewable ecosystem infrastructure**.

That unlocks:
- attachable proof evidence for release and safety-critical workflows,
- cleaner backend experimentation without losing comparability,
- replayable counterexamples for debugging and incident response,
- proof regression review across crate versions and toolchain updates,
- and a thinner integration target for IDEs, CI systems, auditors, and policy tooling.

The archive already has Safety Evidence Kit as a broad assurance layer.
Formal Verification Kit fills the more precise missing seam underneath it: one portable proof/counterexample/report boundary.

## Milestones
1. **v0 schemas + validators**
   - publish schemas and canonical reason codes
   - validate assumptions, capability claims, and pack structure
2. **v0.2 ranked pilot path**
   - run the Cargo-native pair from `design/formal-verification-pilot-program.md`
   - ingest one model-checking lane and one deductive-verification lane
   - produce `verification-report/v0` and optional `counterexample-pack/v0`
3. **v0.3 replay + std-contract slice**
   - prove replay/counterexample or failed-obligation portability
   - run one std-contract/library-slice comparison lane
4. **v0.4 diff + CI workflow**
   - compare proof results across versions and backends
   - expose “new unknown”, “scope shrank”, and “bound changed” deltas
5. **v1 ecosystem adapters + evidence hooks**
   - integrate with Safety Evidence Kit, Incident Kit, and Release Pipeline Kit
   - publish example release/CI templates

## Success metrics
- Two distinct backend families publish the same `verify-pack/v0` successfully.
- Counterexample packs are reproducible in CI and local workflows.
- Release/assurance pipelines can attach proof artifacts without log scraping.
- Policy tooling can distinguish proved, falsified, unsupported, and unknown outcomes without backend-specific parsers.
