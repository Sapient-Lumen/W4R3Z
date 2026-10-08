## Current proposal note (rev0442)
Read this proposal now as the proposal-layer framing of a **Safety-Critical Readiness Commons**.

The worthy contribution is not merely “better evidence artifacts” and not “a qualified toolchain” in the abstract.
It is the thin `cargo readiness-critical` / `safety-readiness-pack/v0` layer that composes:
- critical-slice identity,
- authority and requirement profiles,
- qualified toolchain / target / runtime scope,
- dependency lifecycle posture,
- mixed-language / interface boundary posture,
- imported assurance and waiver truth,
- and bounded engineering / audit / qualification-prep handoffs,
without collapsing them into one fake certification score.

# Epic Proposal: Safety-Critical Readiness Commons (`cargo readiness-critical` + `safety-readiness-pack/v0`)

## One-sentence pitch
Give Rust one portable way to assemble **target readiness, qualified-scope truth, dependency lifecycle posture, interface-boundary posture, and imported assurance evidence** into a reviewable safety-readiness package without pretending to automate certification.

## Why this is worthy
Rust now has unusually strong official motion at every layer of this seam, but still lacks the attachable program layer above them:
- Rust's January 2026 safety-critical writeup says the key pressures are process, verification, and evidence; recommends target-focused readiness checklists, dependency lifecycle patterns, async-runtime requirements, and C/C++ interop as part of the safety story; and explicitly says the highest-criticality logic is often isolated into the smallest possible slice.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- Rust's 2026 flagships page defines Safety-Critical Rust in terms of MC/DC, normative `unsafe` docs, safety-critical lints, and FLS cadence — a roadmap of readiness surfaces rather than one language-only feature.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The MC/DC, normative-unsafe-docs, Clippy, and FLS goals each strengthen one substrate lane, but none by itself composes target scope, dependency posture, interface boundaries, and evidence imports into one review boundary.
  https://rust-lang.github.io/rust-project-goals/2026/mcdc-coverage-support.html
  https://rust-lang.github.io/rust-project-goals/2026/safe-unsafe-for-safety-critical.html
  https://rust-lang.github.io/rust-project-goals/2026/safety-critical-lints-in-clippy.html
  https://rust-lang.github.io/rust-project-goals/2026/stabilize-fls-releases.html
- Ferrocene's public docs show what real qualification scope looks like: many flags are out of scope, some settings are qualified only narrowly, and experimental targets/features are explicitly not qualified for safety-critical use.
  https://public-docs.ferrocene.dev/main/user-manual/rustc/cli.html
  https://public-docs.ferrocene.dev/main/release-notes/25.11.0.html

The missing contribution is therefore not another lint crate, not another verification wrapper, and not another qualification marketing site.
It is the thin readiness boundary above the ingredients.

## Deliverables
- Read together with [`design/safety-critical-readiness-commons-execution-blueprint-2026Q1.md`](../design/safety-critical-readiness-commons-execution-blueprint-2026Q1.md), [`design/safety-critical-assurance-contract-2026Q1.md`](../design/safety-critical-assurance-contract-2026Q1.md), [`design/safety-critical-evidence-stack.md`](../design/safety-critical-evidence-stack.md), [`design/native-edge-execution-blueprint-2026Q1.md`](../design/native-edge-execution-blueprint-2026Q1.md), and [`design/async-capability-commons-execution-blueprint-2026Q1.md`](../design/async-capability-commons-execution-blueprint-2026Q1.md) so the commons lands as a composition layer rather than a new leaf tool.
- `cargo readiness-critical` reference tool
- Schemas:
  - `critical-slice-profile/v0`
  - `safety-authority-profile/v0`
  - `qualified-scope-profile/v0`
  - `target-readiness-profile/v0`
  - `dependency-lifecycle-profile/v0`
  - `interface-boundary-profile/v0`
  - `safety-readiness-brief/v0`
  - `safety-readiness-pack/v0`
  - `safety-readiness-handoff/v0`
- Imported artifacts:
  - `assurance-pack/v0` / `safety-pack/v0`
  - `coverage-pack/v0`
  - `sanitize-pack/v0`
  - `verify-pack/v0`
  - package-intake / maintenance / async / native-edge attachments where relevant
- Docs:
  - target-readiness lane guide
  - dependency-lifecycle lane guide
  - interface-boundary lane guide
  - qualified-scope / toolchain-profile guide
  - audit and qualification-prep handoff guide

## Proposed shape
Ship a narrowly scoped program layer:
1. declare the critical slice and the requirement/authority profile;
2. attach explicit in-scope / out-of-scope toolchain, flag, target, and runtime posture;
3. attach dependency lifecycle posture for higher-criticality slices;
4. attach interface/interop boundary posture for mixed-language systems;
5. import assurance/evidence packs and keep waivers/residue explicit;
6. emit bounded engineering, release, audit, and qualification-prep handoffs.

## Critical design bet
The critical bet is that **safety-critical Rust needs a shared readiness commons more than it needs one more tool-specific success story**.
That means:
- evidence lanes are in scope,
- target and async/runtime caveats are in scope,
- dependency lifecycle and package-intake posture are in scope,
- interop boundaries are in scope,
- downstream certification work may import the result,
- but the commons does **not** become the whole certification process.

## Non-goals
- replacing Ferrocene, assessors, or local standards work;
- flattening targets, flags, runtimes, dependencies, and evidence into one score;
- pretending every public Rust target has the same safety-readiness posture;
- generating domain-specific compliance dossiers automatically.

## Success bar
This becomes worthy when a maintainer, systems engineer, or assessor-facing team can answer:
- what slice is under review,
- which authorities and requirement profiles apply,
- which toolchain/flag/target/runtime surfaces are actually in scope,
- what the dependency lifecycle plan is,
- what mixed-language boundaries matter,
- what evidence and waivers are attached,
- and what downstream consumers may safely repeat later,

without reverse-engineering vendor docs, CI recipes, issue trackers, and private spreadsheets by hand.
