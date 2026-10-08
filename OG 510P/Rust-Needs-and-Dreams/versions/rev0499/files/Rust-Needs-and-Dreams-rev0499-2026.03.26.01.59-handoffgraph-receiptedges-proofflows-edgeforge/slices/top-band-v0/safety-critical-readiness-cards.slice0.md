# Kernel slice 0: Safety-Critical Readiness Cards

## Identity
- candidate: **Safety-Critical + Institutional Readiness Commons**
- governing kernel: `kernels/top-band-v0/safety-critical-readiness-cards.v0.md`
- current verdict context: `deepen`
- slice codename: `safety-critical-readiness-cards/slice0`

## Why this slice first
This slice should prove that the repo can maintain **validated, freshness-bearing readiness cards** for real institutional decisions.
That is a better first milestone than certification tooling because current public guidance still points to checklists, playbooks, requirements sketches, and shared ownership rather than one certifiable product.

## Exact deliverables
Ship only:
1. `schemas/readiness-card-v0.schema.json`
2. `tools/lint_readiness_cards.py`
3. `cards/targets/` with at least one narrow target family card
4. `cards/dependency-lifecycle/` with one tightening-path playbook
5. `cards/ffi-and-interop/` with one evidence recipe
6. `examples/` with one packed exemplar set
7. `docs/shared-ownership.md`

## Acceptance checks
The slice counts as done when it can:
- lint cards for owner, freshness date, known blockers, evidence links, and “does not prove” clauses;
- produce one small readiness pack for a concrete target/program decision;
- diff two revisions of a readiness card and surface changed risk posture;
- and keep example adopters clearly marked as illustrative receipts rather than universal proof.

## Proving grounds
Start with:
- one narrow target family,
- one dependency-lifecycle path,
- one FFI/interop evidence recipe,
- one async-runtime requirements sketch marked as requirements work, not validation proof.

## Imports and dependencies
Allowed imports:
- official Rust target, project-goals, and release references
- steward notes and playbook evidence
- example adopter references as illustrative evidence only

## Postponed work
Do **not** include yet:
- badges or certification claims
- broad readiness claims for all criticality levels
- tool-first qualification workflows
- large portal/search experiences

## Failure receipts
Ship unsupported-state receipts for:
- missing evidence links
- stale freshness dates
- ownerless cards
- cards whose scope drifts beyond what the evidence can support

## Next-slice trigger
Take slice 1 only after a small steward group can renew the cards on schedule and a real program decision uses a pack without treating it as proof of certification.
