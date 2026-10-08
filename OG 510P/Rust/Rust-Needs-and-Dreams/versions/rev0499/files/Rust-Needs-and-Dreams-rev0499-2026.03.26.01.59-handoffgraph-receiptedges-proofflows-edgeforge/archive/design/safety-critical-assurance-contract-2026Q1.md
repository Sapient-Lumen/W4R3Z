# Design: Safety-Critical Assurance Contract 2026Q1

## Goal
Promote the archive's existing **Safety-Critical Evidence Stack** into an explicit **Safety-Critical Assurance Contract**:
a review boundary for **critical slice identity, authority sources, requirement profile, criterion-aware evidence imports, waivers, and bounded consumer handoff**.

The missing contribution is **not** another verifier, another lint bundle, another coverage wrapper, or another certification dashboard.
It is the thin composition layer that lets Rust teams answer, for one critical slice:
- what is under review,
- which requirements or coding rules are in force,
- which safety contracts are authoritative versus local,
- which evidence lanes actually ran,
- what those lanes are allowed to claim,
- what remains waived / partial / unsupported,
- and what a release, audit, or qualification-prep consumer may safely reuse.

## Why this is the right move now
Current official Rust signals are unusually aligned around one theme: **evidence and specification now matter as first-class product surfaces for Rust adoption in safety-critical work**.

- Rust's 2026 flagship roadmap explicitly defines **Safety-Critical Rust** in terms of **MC/DC coverage support**, **normative unsafe documentation**, **safety-critical lints in Clippy**, and a **stable FLS release cadence**.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Rust's January 2026 safety-critical writeup says the pressure in these domains is not only language semantics but the escalating burden of **process, verification, and evidence**, and it says teams are strongly incentivized to isolate the highest-criticality logic into the smallest surface area possible.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- The 2026 MC/DC goal says the earlier implementation was removed for maintenance reasons, says external implementation is infeasible for real Rust because macro expansion makes post-expansion source reconstruction unrealistic, and now proposes a more sustainable architecture plus a maintenance commitment.
  https://rust-lang.github.io/rust-project-goals/2026/mcdc-coverage-support.html
- The 2026 normative-unsafe-docs goal says the Rustonomicon is incomplete, the Unsafe Code Guidelines Reference is largely abandoned, and safety-critical users need authoritative documentation for common `unsafe` patterns. It proposes a concrete pattern-catalog workflow over real codebases.
  https://rust-lang.github.io/rust-project-goals/2026/safe-unsafe-for-safety-critical.html
- The 2026 Clippy goal says safety-critical coding-guideline enforcement may require **50 to 200 lints** over one to two years and prefers a sustainable home in Clippy rather than a fork or separate tool.
  https://rust-lang.github.io/rust-project-goals/2026/safety-critical-lints-in-clippy.html
- The 2026 FLS cadence goal says each FLS version should ship within six weeks of the corresponding stable Rust release so assessors and qualification consumers have a current spec surface.
  https://rust-lang.github.io/rust-project-goals/2026/stabilize-fls-releases.html
- The accepted standard-library contracts goal plus the experimental `core::contracts` module show that executable contracts are no longer only theory work.
  https://rust-lang.github.io/rust-project-goals/2025h1/std-contracts.html
  https://doc.rust-lang.org/core/contracts/index.html
- rustc's coverage docs already make criterion-sensitive source-based coverage practical, but they also keep caveats explicit: doc tests need special handling, some flags can break coverage-map expectations, and engine/tooling provenance matters.
  https://doc.rust-lang.org/rustc/instrument-coverage.html

Taken together, the ecosystem now has enough upstream motion that the real missing piece is **honest composition and handoff**, not one more isolated evidence leaf.

## What this contract should own
The contract should sit above the existing leaves and stacks, not replace them.

It should own six distinct truths:
1. **critical-slice subject truth**
   - which crate / module / binary / target / release slice is under review;
   - what scope boundaries and exclusions apply.
2. **authority truth**
   - which obligations cite the Rust Reference, std docs, FLS, normative unsafe docs, local rationale, or project policy;
   - which citations are normative, aspirational, imported, or unresolved.
3. **requirement-profile truth**
   - which coding-standard, lint, target-readiness, or assurance profile is being evaluated;
   - which rules are in scope versus intentionally deferred.
4. **evidence-lane truth**
   - imported `safety-pack`, `coverage-pack`, `sanitize-pack`, `verify-pack`, and optional conformance/spec packs;
   - criterion identity, engine family, target/runtime lane, proof scope, and comparability class remain explicit.
5. **waiver / residue truth**
   - explicit waivers, unsupported areas, partial results, and review holds;
   - no flattening into a fake green badge.
6. **consumer-handoff truth**
   - bounded summaries for release review, audit prep, qualification prep, support, and downstream integrators;
   - what is safe to repeat later versus what is merely informative.

## What a worthy contribution should look like in practice
A serious contribution here now looks like a thin `cargo assurance` / `assurance-pack/v0` layer above the archive's existing safety, coverage, sanitizer, verification, and traceability kits.

### Suggested artifact family
- `assurance-subject/v0`
  - critical slice identity, scope, target, toolchain, support envelope pointers.
- `assurance-authority-lane/v0`
  - authoritative citations, local rationale, unresolved authority gaps.
- `assurance-requirement-profile/v0`
  - selected coding standard / lint profile / conformance profile / target-readiness profile.
- `assurance-import-index/v0`
  - imported evidence families with freshness, provenance, and comparability markers.
- `assurance-waiver-ledger/v0`
  - waivers, residue, review holds, expiry / renewal posture.
- `assurance-handoff/v0`
  - bounded consumer view for release, audit, qualification-prep, or support.
- `assurance-pack/v0`
  - one attachable unit linking all of the above.

### Expected imports
- `safety-pack/v0`
- `coverage-pack/v0`
- `sanitize-pack/v0`
- `verify-pack/v0`
- optional `conformance-pack/v0`, `spec-pack/v0`, or compatibility/support claims

### MVP usage sequence
1. identify a critical slice;
2. attach authority sources and requirement profile;
3. import evidence lanes without flattening them;
4. record residue and waivers explicitly;
5. emit a bounded handoff for a named consumer.

## How this differs from nearby seams
- It is **not** the same seam as **Harness Protocol Contract**.
  Harness protocol is about what test/harness subjects declare before execution; assurance contract is about what high-assurance consumers may conclude after importing multiple evidence families.
- It is **not** the same seam as **Coverage Evidence Kit**.
  Coverage remains one evidence family; assurance must preserve whether that family is line, branch, decision, or MC/DC, and whether it is comparable.
- It is **not** the same seam as **Safety Evidence Kit**.
  Safety evidence is a leaf / import family; assurance is the composition and handoff layer above it.
- It is **not** the same seam as **Conformance Traceability**.
  Conformance traceability may be imported, but assurance must also integrate runtime-checking, proofs, waivers, and consumer posture.

## Ranking decision
This promotion **does not** rewrite the broad ecosystem ladder.
It does **not** outrank Build-State Evidence, Adoption Navigation, Debuggability, or the build/debug/tooling contracts.

What changes is the frontier map:
- the archive now has a clearly named **high-assurance / evidence-shaping** move;
- that move is stronger than leaving safety-critical work as a loose pile of coverage, lint, doc, spec, and proof notes;
- but it should still remain below the broad cross-cutting toolchain/control-plane bets in the overall ranking.

## Recommended immediate execution posture
Read this note together with:
- `design/safety-critical-evidence-stack.md`
- `design/safety-evidence-kit.md`
- `design/coverage-evidence-kit.md`
- `design/sanitizer-battery-kit.md`
- `design/formal-verification-kit.md`
- `design/conformance-traceability-stack.md`
- `proposals/epic-safety-critical-evidence-stack.md`
- `gaps/unsafe-and-verification-evidence.md`

The archive should now treat those files as the substrate for one explicit frontier instead of several adjacent but weaker themes.

## Anti-goals
Do not turn this into:
- a universal certification dossier generator;
- a one-number safety score;
- a replacement for Clippy, Kani, Verus, Miri, sanitizers, coverage tools, or future contracts tooling;
- or a policy engine that hides missing authority or unsupported evidence lanes.

The winning contribution is a **reviewable handoff layer**, not a compliance theater machine.
