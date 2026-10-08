# Decisions — rev0147

## D-0147-01: Add explicit cross-claim relations

**Decision:** Store `excludes`, `negates`, `entails`, and `equivalent` as first-class, event-sourced records between distinct claims.

**Reason:** Same-claim contradiction cannot represent mutually exclusive culprits, inverse propositions, implication constraints, or identity equivalence.

**Consequence:** Relations carry source, rationale, creation custody, and optional retirement custody.

## D-0147-02: Relations constrain; they do not infer

**Decision:** Relation evaluation only rejects incompatible explicit truth assignments. It never materializes another endpoint.

**Reason:** Silent closure would blur authored assertions, planner deductions, agent knowledge, and world truth.

**Consequence:** `unknown` creates no violation, and a future inference layer must remain an inspectable projection.

## D-0147-03: Use one pairwise consistency engine

**Decision:** Centralize same-claim and relation-based compatibility checks across anchors, world assignments, reactivation, relation declaration, conflict reporting, and verification.

**Reason:** Divergent validators turn invariants into path-dependent accidents.

**Consequence:** The refactor also repairs partially overlapping opposite assignments inside one world.

## D-0147-04: Refuse retroactively corrupting relation declarations

**Decision:** A new relation is rejected if current anchors or any live/selected world already violate it.

**Reason:** Adding a constraint must not quietly make accepted state internally impossible.

**Consequence:** Authors must first retire/change conflicting commitments or prune/repair worlds, preserving an auditable sequence.

## D-0147-05: Keep relations planner-only

**Decision:** Include relations in privileged planner context and explicitly omit them from perspective context.

**Reason:** A relation can reveal hidden ontology or mystery structure even without exposing assignments.

**Consequence:** Audience-profile turn grants cannot declare or retire relations.

## D-0147-06: Add custody explanation before proof search

**Decision:** Implement a one-hop `explain` query over origin, termination, dependencies, dependents, and visibility.

**Reason:** Commitment governance and revision cost need trustworthy lineage, but a premature theorem-prover interface would overclaim.

**Consequence:** Every response states that provenance is not truth, fairness, or sufficient justification.

## D-0147-07: Explanation access follows the perspective firewall

**Decision:** Perspective explanations refuse planner-only record kinds and apply assertion/question/source/claim visibility rules.

**Reason:** A diagnostic endpoint must not become a hidden-state oracle for guessed IDs.

## D-0147-08: Separate database schema from event schema

**Decision:** Advance the physical database to schema 2 while retaining immutable event schema 1.

**Reason:** Adding projections does not require rewriting historical event envelopes.

**Consequence:** Runtime status and verification report both concepts independently.

## D-0147-09: Require explicit forward migration

**Decision:** Refuse schema-1 cubes until `lacuna migrate` performs the supported 1→2 transformation.

**Reason:** Silent schema reinterpretation weakens custody and makes failures nondeterministic.

**Consequence:** Migration checks integrity and foreign keys, records its statement digest, and proves that the event-ledger head did not change.

## D-0147-10: Preserve the source-bound v2 turn surface

**Decision:** Document and schema only `lacuna.turn-request.v2` and `lacuna.turn-proposal.v2`; remove stale v1 turn schemas/examples.

**Reason:** A proposal must be bound to the request source, input digest, immutable grant, and post-issuance head.
