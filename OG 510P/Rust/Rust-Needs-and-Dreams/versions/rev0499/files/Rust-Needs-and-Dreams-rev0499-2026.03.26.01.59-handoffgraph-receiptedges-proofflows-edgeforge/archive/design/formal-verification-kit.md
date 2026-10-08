# Design: Formal Verification Kit (`cargo verify`, `verify-pack/v0`)

## Goal
Define a portable workflow and artifact contract for Rust formal verification so proofs, failures, assumptions, and tool capabilities can be exchanged as versioned evidence instead of being trapped inside one verifier’s logs.

This should **not** replace Kani, Creusot, Prusti, Verus, ESBMC, or future proof tools.
It should make them easier to compare, compose, archive, and review.

## References (signals)
- The standard-library verification survey/challenge exists under the Rust project and includes representative challenge problems for contributors.
  https://rust-lang.github.io/rust-project-goals/2024h2/std-verification.html
- The `std` contracts goal explicitly treats contracts as code and aims to enable verification of the standard library implementation.
  https://rust-lang.github.io/rust-project-goals/2025h1/std-contracts.html
- `a-mir-formality` is explicitly about capturing the compiler’s static semantics in a lighterweight model and helping validate Rust’s type safety.
  https://rust-lang.github.io/rust-project-goals/2025h2/a-mir-formality.html
- Safety-Critical Rust is now a roadmap/application area oriented around evidence-heavy adoption and attestation workflows.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
  https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- The Rust Foundation says ESBMC work is aimed at expanding Rust verification support, that ESBMC is live in the standard-library verification workflow, and that the team is aiming to integrate it as an alternative backend for Kani.
  https://rustfoundation.org/media/expanding-the-rust-formal-verification-ecosystem-welcoming-esbmc/
- The Verify Rust Std project now explicitly lists multiple approved tools in CI — ESBMC (via GOTO-Transcoder), Flux, Kani, and VeriFast — which is strong evidence that Rust verification is already plural at the public ecosystem boundary.
  https://model-checking.github.io/verify-rust-std/tools.html
- Kani already has a Cargo-native workflow via `cargo kani`, supports concrete-counterexample playback, and exposes verification-specific build/config posture.
  https://model-checking.github.io/kani/usage.html
- Creusot already has a Cargo-native workflow via `cargo creusot` / `cargo creusot prove`, exposes intermediate Coma artifacts, and supports replay / IDE-oriented proof workflows.
  https://creusot-rs.github.io/creusot/guide/
- Prusti already has IDE-assisted and Cargo-native (`cargo-prusti` / `cargo prusti`) workflows.
  https://viperproject.github.io/prusti-dev/user-guide/basic.html
- Verus already provides a distinct proof-oriented model for Rust code and low-level systems code, and explicitly frames itself as static verification rather than runtime checking.
  https://verus-lang.github.io/verus/guide/
- The Rust Formal Methods Interest Group is now a visible landscape hub rather than a one-tool ecosystem and explicitly says it wants better tool inter-compatibility, especially for specifications.
  https://rust-formal-methods.github.io/

## Core components

### 1) `verify-intent/v0`
Declares what the run was *trying* to prove.

Required ideas:
- workspace / package / module scope
- target / feature / edition assumptions
- property classes, for example:
  - `memory_safety`
  - `panic_freedom`
  - `overflow_freedom`
  - `functional_contracts`
  - `unsafe_abstraction_soundness`
- selected backends
- time / unwind / solver / loop bounds where relevant
- proof budget and policy metadata
- raw-tool attachments allowed but not required

Design rule: intent is first-class because “verified” without property scope is not useful.

### 2) `verify-capabilities/v0`
Declares what a backend currently supports and how to interpret its results.

Examples:
- backend identity + version
- analysis class (`bounded_model_checking`, `deductive_verification`, `symbolic`, `hybrid`)
- target / platform support
- concurrency support
- `unsafe` support caveats
- `no_std` / FFI / proc-macro / inline-asm caveats
- counterexample support
- output granularity (`property`, `function`, `module`, `crate`)

This prevents teams from pretending all tools mean the same thing when they say “pass”.

### 3) `verification-report/v0`
Machine-readable result artifact.

Required fields:
- run identity and timestamps
- digests of `verify-intent/v0` and input source snapshot
- backend + version + configuration
- per-property outcomes:
  - `proved`
  - `falsified`
  - `unknown`
  - `skipped`
  - `unsupported`
- reason codes
- scope and attachment pointers
- assumptions and trusted axioms
- optional obligation / solver statistics

Design rule: **unknown and unsupported are normal outcomes**.
The contract must reward honest scope boundaries instead of encouraging fake certainty.

### 4) `counterexample-pack/v0`
Portable replay bundle for failing properties.

Should support:
- property id
- failing backend and version
- minimized input / seed / nondeterministic choices where available
- trace and witness attachments
- harness / module / function pointers
- exact rerun instructions
- redaction metadata if traces contain sensitive values

This is the key workflow upgrade for debugging and CI triage.

### 5) `verify-diff-report/v0`
Structured diff between verification runs.

Use cases:
- release-to-release proof regression review
- “new unknowns” after toolchain upgrade
- proof-scope shrinkage detection
- comparison across backends or targets

Must distinguish:
- source change
- backend change
- configuration/bound change
- intent/scope change

### 6) `verify-pack/v0`
Bundle containing:
- `verify-intent/v0`
- `verify-capabilities/v0`
- `verification-report/v0`
- optional `counterexample-pack/v0`
- optional `verify-diff-report/v0`
- optional raw backend outputs

This is the attachable unit for CI artifacts, release evidence, qualification dossiers, or issue reports.

### 7) `cargo verify`
Reference UX:
- `cargo verify run`
- `cargo verify diff`
- `cargo verify doctor`
- `cargo verify pack`
- `cargo verify list-backends`

`cargo verify` should begin as an orchestrator / validator / packer.
It should not try to force every verifier into one execution engine.

## What the kit should provide to others
- **Safety Evidence Kit:** consumes verification artifacts rather than re-inventing proof output schemas.
- **Spec Conformance Kit:** stays focused on language/toolchain behavior, while Formal Verification Kit focuses on program/crate properties.
- **Release Pipeline Kit / Repro Build Kit:** can attach proof packs as release evidence.
- **Incident Kit:** can carry replayable counterexample packs during triage.
- **MIR Analysis Kit:** can become an input source for future proof backends without being the report format itself.

## Overlap boundaries
- **Not Safety Evidence Kit:** that kit aggregates broader assurance signals (unsafe census, audits, proofs). This one standardizes proof-specific workflows and artifacts.
- **Not Spec Conformance Kit:** conformance is about Rust language/toolchain behavior against normative sources; this kit is about properties of crates and programs.
- **Not Sanitizer Battery Kit:** dynamic/runtime checking remains separate from proof artifacts.
- **Not MIR Analysis Kit:** MIR export is an analysis substrate, not a proof-report boundary.
- **Not Coverage Evidence Kit:** proof results and test coverage are related but distinct evidence channels.

## Hard problems (explicitly scoped)
1. **Backend diversity is real**
   - Bounded model checking, deductive verification, and proof-oriented Rust subsets will not collapse into one semantic model in v0.
   - The contract should normalize metadata and outcomes, not invent fake equivalence.

2. **Assumptions and trusted code are unavoidable**
   - Proofs often rely on axioms, stubs, contracts, bounds, or trusted libraries.
   - Those assumptions must be first-class and diffable.

3. **Counterexamples differ by backend**
   - Some tools produce concrete traces; others primarily produce failed obligations.
   - `counterexample-pack/v0` must allow partial availability.

4. **Performance budgets matter**
   - Formal verification can be expensive.
   - `verify-intent/v0` needs explicit proof-budget semantics so CI policy stays honest.

5. **Marketing pressure toward binary claims**
   - The pack must make scope, exclusions, and unsupported areas prominent to prevent “verified” from becoming a hand-wavy badge.

## Minimal adoption path
1. Publish schemas + validators.
2. Ship `cargo verify pack` for existing backend outputs before trying to orchestrate everything.
3. Run the ranked execution path in [`design/formal-verification-pilot-program.md`](./formal-verification-pilot-program.md): Cargo-native pair first, replay/counterexample lane second, std-contract slice third, diff/regression lane fourth, safety-critical import lane fifth.
4. Add counterexample packing and diff support where the pilot reveals real backend differences.
5. Integrate with Safety Evidence and Release Pipeline kits as attachable evidence only after the proof lane itself stays honest under the pilot.

## Why this is worth doing
Rust now has enough serious formal-methods activity that workflow fragmentation is becoming a larger problem than tool nonexistence. The widening public std-verification tool list, the RFMIG interop agenda, and the safety-critical roadmap all raise the value of a reusable proof/report boundary.
A good Formal Verification Kit would turn scattered proof results into something teams can actually review, compare, archive, and ship. Its next honest step is a ranked pilot, not a bigger promise.

## Safety-critical stack note
Treat this kit as the **proof and assumption layer** inside the shared **Safety-Critical Evidence Stack** in [`design/safety-critical-evidence-stack.md`](./safety-critical-evidence-stack.md).
Its job is to standardize proof intent, backend capabilities, assumptions, and counterexamples without pretending proof artifacts erase the need for contracts, runtime-checking lanes, or criterion-aware test evidence.
Use [`design/safety-critical-pilot-program.md`](./safety-critical-pilot-program.md) to keep proof-augmented module pilots scoped before widening toward release-candidate or qualification-oriented consumers.

## Reference execution path
Use [`design/formal-verification-pilot-program.md`](./formal-verification-pilot-program.md) as the ranked rollout for this kit. It starts with a Cargo-native pair across unlike proof families and only later widens toward std-contract imports, backend diffs, and safety-critical consumers.
