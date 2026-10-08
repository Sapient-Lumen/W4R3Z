## Current proposal note (rev0404)
Read this proposal now as the proposal-layer framing of a **Safety-Critical Assurance Contract**.

The worthy contribution is not merely “better safety evidence artifacts.”
It is the thin `cargo assurance` / `assurance-pack/v0` layer that composes:
- critical-slice identity,
- authoritative and local safety-contract sources,
- selected requirement profiles,
- criterion-aware evidence imports,
- waiver / unsupported residue,
- and bounded release / audit / qualification-prep handoffs,
without collapsing them into one fake certification score.

# Epic Proposal: Safety-Critical Evidence Stack (`cargo safety-critical` + `safety-critical-pack/v0`)

## One-sentence pitch
Give Rust one portable way to assemble **unsafe-contract authority, criterion-aware coverage, dynamic-analysis lane truth, and proof/assumption evidence** into a reviewable high-assurance package without collapsing them into a fake certification badge.

## Why this is worthy
Rust now has unusually strong official motion at every layer of this seam, but still lacks the attachable composition boundary above them:
- Rust’s 2026 flagship roadmap explicitly defines **Safety-Critical Rust** in terms of MC/DC coverage support, normative `unsafe` documentation, safety-critical lints in Clippy, and a stable FLS release cadence. That is already an evidence roadmap, not only a language-marketing story.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The official safety-critical adoption writeup says the hardest pressure in these domains is not only language semantics but the growth of process, verification, and evidence demands with criticality, and it says teams are strongly incentivized to isolate the highest-criticality logic into the smallest surface area possible.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- The MC/DC goal says MC/DC is required by standards such as DO-178C, ISO 26262, and IEC 61508, and that implementing it outside the compiler is infeasible because macro expansion makes a post-expansion source model unrealistic.
  https://rust-lang.github.io/rust-project-goals/2026/mcdc-coverage-support.html
- The normative-unsafe-docs goal says the current unsafe-documentation story is not yet authoritative enough for rigorous safety cases and proposes a real-world pattern-catalog process over production codebases.
  https://rust-lang.github.io/rust-project-goals/2026/safe-unsafe-for-safety-critical.html
- The Clippy goal says safety-critical development will likely need on the order of 50 to 200 lints over one to two years, which is a strong signal that lint posture itself needs durable review artifacts rather than ad hoc CI toggles.
  https://rust-lang.github.io/rust-project-goals/2026/safety-critical-lints-in-clippy.html
- The FLS goals make specification upkeep operational: Rust already published the first rust-lang-owned FLS release and now wants predictable release cadence because safety and qualification consumers need that text to move with the language rather than as a disconnected side project.
  https://rust-lang.github.io/rust-project-goals/2025h1/spec-fls-publish.html
  https://rust-lang.github.io/rust-project-goals/2026/stabilize-fls-releases.html
- The standard-library contracts effort and the `core::contracts` experimental module show that executable contracts are no longer a distant theory topic.
  https://rust-lang.github.io/rust-project-goals/2025h1/std-contracts.html
  https://doc.rust-lang.org/core/contracts/index.html
- rustc already documents source-based coverage as an official instrumentation flow, and the unstable sanitizer book already documents concrete engine and target support with explicit caveats. That means the review problem is now more about honest composition than about finding any raw evidence source at all.
  https://doc.rust-lang.org/rustc/instrument-coverage.html
  https://doc.rust-lang.org/beta/unstable-book/compiler-flags/sanitizer.html

The missing contribution is therefore not another checklist, verifier fork, or dashboard.
It is the thin review boundary above the existing ingredients.

## Deliverables
- Read together with [`design/safety-critical-evidence-stack.md`](../design/safety-critical-evidence-stack.md), [`design/safety-critical-pilot-program.md`](../design/safety-critical-pilot-program.md), [`design/safety-evidence-kit.md`](../design/safety-evidence-kit.md), [`design/coverage-evidence-kit.md`](../design/coverage-evidence-kit.md), [`design/sanitizer-battery-kit.md`](../design/sanitizer-battery-kit.md), and [`design/formal-verification-kit.md`](../design/formal-verification-kit.md) so the stack lands as a composition layer rather than one more leaf tool.
- `cargo safety-critical` reference tool
- Schemas:
  - `safety-critical-brief/v0`
  - `critical-slice-profile/v0`
  - `safety-import-profile/v0`
  - `assurance-waiver-budget/v0`
  - `safety-critical-handoff/v0`
  - `safety-critical-pack/v0`
- Imported artifacts:
  - `safety-pack/v0`
  - `coverage-pack/v0`
  - `sanitize-pack/v0`
  - `verify-pack/v0`
  - selected `spec-pack/v0` / FLS / unsafe-doc references
  - optional release/support/conformance attachments for downstream consumers
- Docs:
  - unsafe-review lane guide
  - criterion-aware coverage guide
  - sanitizer capability / blind-spot guide
  - proof-assumption import guide
  - certification-facing handoff guide

## Strategic value
This deserves promotion because it gives the archive one **high-assurance evidence boundary** that other seams can import honestly.

With it:
- unsafe-heavy libraries can attach reviewable safety-case material without pretending they already have full certification posture;
- coverage reports can stay criterion-aware as MC/DC work matures instead of being flattened into generic percentages;
- sanitizer and exploit-mitigation lanes can remain explicit about engines, targets, std/runtime provenance, and blind spots;
- proof-oriented workflows can attach assumptions and trusted-code boundaries without becoming the whole assurance story;
- conformance, release, support, audit, and qualification-prep consumers can import a bounded package instead of reverse-engineering CI jobs and binders.

The prize is not a giant assurance platform.
The prize is a boring, portable bridge from evidence to review.

## Proposed shape
Ship a narrowly scoped stack-level layer:
1. import `safety-pack/v0`, `coverage-pack/v0`, `sanitize-pack/v0`, and `verify-pack/v0` as distinct evidence families under one subject identity;
2. attach normative references (FLS, Reference, unsafe-doc pattern catalogs, contracts) without pretending every local rationale is normative;
3. make criterion truth, dynamic-analysis capability truth, and proof-assumption truth first-class instead of burying them in notes;
4. emit `safety-critical-handoff/v0` for release-review, safety-review, support, audit-prep, and qualification-prep consumers;
5. preserve `PARTIAL`, `INCONCLUSIVE`, `UNSUPPORTED`, and waiver states explicitly instead of forcing green badges.

## Critical design bet
The critical bet is that **safety-critical evidence should stop at composing authoritative sources and executable evidence into a review boundary, not at automating certification**.
That means:
- authoritative unsafe and spec references are in scope,
- criterion-aware coverage is in scope,
- sanitizer and exploit-mitigation lanes are in scope,
- proof and trusted-code boundaries are in scope,
- downstream audit / qualification preparation may import the result,
- but the stack does **not** become the sole owner of a universal compliance dossier, domain standard mapping, or one universal assurance score.

Without that boundary, the proposal either stays too weak to matter or expands into certification theater.

## Milestones
1. **v0 unsafe-review lane**
   - publish `safety-critical-brief` / `critical-slice-profile` / `safety-critical-pack`
   - import existing `safety-pack` outputs for unsafe-heavy library slices
2. **v0.2 dynamic-analysis lane**
   - attach `sanitize-pack` with explicit target/std/runtime provenance
   - preserve engine capability and blind-spot truth
3. **v0.3 criterion-aware coverage lane**
   - attach `coverage-pack` with explicit criterion and comparability rules
   - preserve ordinary coverage vs decision vs MC/DC posture
4. **v0.4 proof-augmented module lane**
   - attach `verify-pack` with assumption and trusted-code boundaries
   - support mixed evidence for one critical slice
5. **v1 certification-facing handoff lane**
   - emit bounded review handoffs for safety-review, audit-prep, and qualification-prep consumers
   - keep domain-standard mapping pointer-based and explicitly local where necessary

## Execution order
Use [`design/safety-critical-pilot-program.md`](../design/safety-critical-pilot-program.md) as the stack-level rollout:
1. unsafe-heavy library review lane,
2. dynamic-analysis battery lane,
3. criterion-aware release lane,
4. proof-augmented module lane,
5. certification-facing release-candidate lane.

Use [`design/conformance-traceability-pilot-program.md`](../design/conformance-traceability-pilot-program.md) where language/spec traceability must be imported.
Use [`design/release-truth-pilot-program.md`](../design/release-truth-pilot-program.md) and [`design/distribution-contract-pilot-program.md`](../design/distribution-contract-pilot-program.md) where downstream release or install consumers need bounded handoffs.

## Non-goals
- replacing domain certification processes or creating an official Rust certification badge;
- replacing Kani, Creusot, Prusti, Verus, Miri, sanitizers, or future engines with one mega-runner;
- flattening unsafe-doc authority, coverage percentages, sanitizer findings, and proof outcomes into one score;
- requiring MC/DC or proof machinery for every project that merely wants better unsafe-review evidence;
- pretending that one pack can erase target-, domain-, or standard-specific assurance work.

## Success bar
This becomes worthy when a maintainer, reviewer, or downstream integrator can answer:
- what critical slice was under review;
- what authority justified the safety obligations;
- what coverage criterion actually ran and how comparable the result is;
- what dynamic-analysis engines and capabilities were exercised on which target/runtime lane;
- what properties were proved, under which assumptions and trusted-code boundaries;
- what remained waived, partial, or unsupported;
- and what a release, support, audit, or qualification-prep consumer may safely repeat later,

without reverse-engineering prose binders, CI matrices, sanitizer flags, and proof logs by hand.
