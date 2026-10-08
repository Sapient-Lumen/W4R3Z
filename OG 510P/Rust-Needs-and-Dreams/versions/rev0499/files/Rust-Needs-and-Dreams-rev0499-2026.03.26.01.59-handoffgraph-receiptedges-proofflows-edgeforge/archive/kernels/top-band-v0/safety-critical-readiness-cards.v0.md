# V0 kernel brief: Safety-Critical Readiness Cards

## Identity
- candidate: **Safety-Critical + Institutional Readiness Commons**
- macro-program: **Safety-Critical + Institutional Readiness Commons**
- current verdict context: `deepen`
- kernel codename: `readiness-cards/v0`

## Why this kernel and not a bigger build
The first honest build is not a certification crate and not a badge scheme.
It is a **validated commons of readiness cards and playbooks** for concrete institutional decisions.
That is justified because the current public recommendations are already specific: target-focused readiness checklists, dependency-lifecycle patterns, safety-case-friendly async requirements, and shared ownership / maintenance expectations. The missing work is packaging those into reusable, reviewable artifacts.
Relevant sources:
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://rust-lang.github.io/rust-project-goals/2026/
- https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- https://rustfoundation.org/strategic-plan/

## Repo shape
Suggested first repo tree:
- `cards/targets/` — target-readiness cards
- `cards/dependency-lifecycle/` — early-use / shrink / replace playbooks
- `cards/ffi-and-interop/` — FFI burden and evidence recipes
- `cards/async-requirements/` — safety-case-friendly async runtime requirement sketches
- `schemas/readiness-card-v0.schema.json` — required front matter and evidence fields
- `examples/` — filled-out sample cards for a small target set
- `tools/lint_readiness_cards.py` — validation for required fields and freshness markers
- `docs/shared-ownership.md` — stewardship, maintenance, and host-shape guidance

## User surfaces
The first user surfaces should be:
1. `lint` — validate that cards contain required fields, owners, freshness dates, and caveats
2. `pack` — gather a bounded set of cards and playbooks for one target/program decision
3. `diff` — compare two revisions of a readiness pack and surface changed risk posture

Each card should answer:
- what target or concern it covers
- current support/known-blocker posture
- required external evidence links
- dependency-lifecycle expectations
- owner / steward expectation
- freshness / renewal date
- what this card explicitly does **not** prove

## Import seams
The kernel should import:
- official Rust target / project-goals / release or issue references when available
- steward-group notes and playbook evidence
- example adopters only as illustrative receipts, never as universal proof

This kernel is document-first, but it still needs machine-checkable structure.

## Proof assets
The kernel should emit:
- one readiness card pack for a concrete target or program area
- explicit missing-evidence receipts
- diffable freshness metadata
- one stewardship note naming owner shape and renewal burden

## Proving grounds
Start with:
1. one target-readiness card set for a narrow target family
2. one dependency-lifecycle playbook grounded in a realistic higher-criticality tightening path
3. one FFI / interop evidence recipe
4. one async-runtime requirements sketch that is clearly marked as requirements work, not implementation proof

## Owner shape / upkeep
Best first owner:
- consortium or foundation-backed steward group plus adopters who can renew cards with real evidence

Immediate upkeep tax:
- standards/process drift
- freshness and evidence-link maintenance
- target-specific blocker updates
- host-shape coordination across companies and maintainers

## Refused expansions
Do not let v0 become:
- a Rust-is-certified badge system
- generic claims that Rust is ready for all safety-critical use
- a single tool claiming to solve qualification
- or a doc pile with no validation and no freshness discipline

## Exit criteria
This kernel has earned a stronger next stage when it can show:
- a small but maintained card corpus with renewal receipts
- at least one credible steward coalition
- concrete use in real institutional decision-making
- and clear evidence boundaries that survive contact with higher-assurance review

