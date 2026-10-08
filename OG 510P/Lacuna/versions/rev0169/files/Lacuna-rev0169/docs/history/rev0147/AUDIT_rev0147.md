# Audit — rev0147

## Scope

This pass audited the rev0146 kernel for failure modes that would become severe once a planner starts keeping many candidate worlds and revising them over time.

## Finding A-0147-01 — distinct claims had no integrity relationship

**Severity:** architecture-blocking

**Before:** Lacuna could detect opposite stances on one claim but could not express that two different claims exclude, negate, entail, or equal one another.

**Failure examples:** two simultaneous culprits in a supposedly single-culprit world; incompatible identities; an antecedent true while its required consequence is explicitly false.

**Repair:** first-class, event-sourced claim relations plus relation-aware consistency checks.

**Tests:** world-local exclusion, cross-anchor exclusion, entailment compatibility, no closure, retroactive-declaration refusal, retirement/rebuild.

## Finding A-0147-02 — world assignment overlap check was too literal

**Severity:** high

**Before:** replacement logic could prevent an exact duplicate interval from coexisting, but opposite assignments over partially overlapping intervals could survive because interval identity and interval overlap were conflated.

**Repair:** normalize all candidate records through one overlap-aware pair consistency engine. Exact-interval replacement still works; partial overlap with opposite truth is refused.

**Test:** `test_overlapping_same_claim_contradiction_is_rejected_but_exact_replacement_is_valid`.

## Finding A-0147-03 — adding a rule could corrupt already-live state

**Severity:** high

**Before:** no relation mechanism existed; a naïve implementation could have inserted a rule first and discovered afterward that every active world violated it.

**Repair:** relation declaration is preflighted against active anchors and every live/selected world before its event is appended.

**Test:** relation declaration leaves head and relation projection unchanged on refusal.

## Finding A-0147-04 — constraint and inference were at risk of collapse

**Severity:** epistemic-critical

**Risk:** treating `A entails B` as permission to write `B=true` would erase whether B was observed, authored, inferred, believed, or merely required for one world’s consistency.

**Repair:** logic functions return compatibility violations only. `unknown` never manufactures a value. Tests assert absence of materialized closure.

## Finding A-0147-05 — planner ontology could leak through audience context

**Severity:** high

**Risk:** even without world assignments, a relation such as “Ada culprit excludes Basil culprit” exposes hidden mystery design.

**Repair:** planner context includes active relations; perspective context returns an empty relation list and a labelled omission reason.

**Test:** context separation for relations.

## Finding A-0147-06 — there was no trustworthy “why?” surface

**Severity:** product-blocking for commitment governance

**Before:** an operator could inspect tables/events manually but could not ask for one record’s creation, termination, direct inputs, direct users, and access class.

**Repair:** add `explain` across record namespaces with normalized data, origin/end events, dependencies, dependents, and an explicit nonproof statement.

**Security repair:** perspective mode refuses planner-only kinds and invisible records.

## Finding A-0147-07 — schema evolution had no executable policy

**Severity:** release-blocking

**Before:** rev0146 deliberately stayed on database schema 1. The first kernel table addition required a real migration boundary.

**Repair:** separate `DATABASE_SCHEMA_VERSION` from `EVENT_SCHEMA_VERSION`, refuse old cubes, add an integrity-checked 1→2 migration, record migration custody and digest, and assert unchanged ledger head.

## Finding A-0147-08 — turn documentation and examples lagged runtime v2

**Severity:** high integration risk

**Before this documentation pass:** stale v1 templates omitted `request_source_id` and `player_input_sha256`, weakening the apparent contract even though runtime v2 enforced them.

**Repair:** remove stale turn schemas, publish strict v2 schemas and examples, and document input-source issuance plus immutable write grants.

## Refactor summary

- Extracted relation truth tables and pair conflict description into `logic.py`.
- Reused one semantic consistency engine across mutation and audit paths.
- Added relation projection replay and snapshot custody.
- Split physical database schema version from immutable event schema version.
- Added a record-namespace resolver and direct dependency vocabulary for explanations.
- Preserved least-authority audience/director turn profiles and context separation.

## Verification performed

- 44 behavioral and executable end-to-end tests.
- Relation declaration, retirement, refusal atomicity, and projection replay.
- Real schema-1-to-2 migration with unchanged ledger head.
- SQLite integrity, foreign keys, event chain, change receipts, migration custody, and invariant verification.
- Python compilation.
- JSON parse and Draft 2020-12 meta-schema checks for all six schemas.
- Actual emitted v2 request packet and proposal template validated against their schemas.

## Remaining audit concerns

- Pairwise `excludes` cannot express exactly-one or at-least-one.
- Relations are authored policy and can be wrong even when perfectly custodied.
- Explanation output is one hop and not a causal proof.
- No automatic logical closure means callers must not assume all consequences are present.
- Candidate worlds are still eagerly copied on fork and lack diversity-preserving resampling.
- Causal agency, counterfactual depth, mystery fairness, and character identity stability remain unimplemented evaluation surfaces.
