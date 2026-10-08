# Audit — rev0149

## Scope

This pass audited rev0148 as a custody kernel for a long-running adaptive campaign. The primary question was whether latent-world facts could change without preserving the reason, review surface, and downstream obligations. A second review targeted perspective-scoped explanations as a confidentiality boundary.

## A-0149-01 — exact-slot assignment silently acted as revision

**Severity:** architecture-blocking

**Before:** submitting a new truth value for the same world, claim, timeline, and exact interval could end the old projection and install the new one through the ordinary assignment path.

**Risk:** a planner could rewrite a premise without an impact review, lineage reason, or stable distinction between initial adoption and later correction. Downstream records had no authoritative revision event to cite.

**Repair:** `assign_world` now refuses `assignment-slot-occupied`. Truth-changing mutation requires `revision-impact` followed by `revise_world` with the exact digest. The successor stores predecessor, reason, and review hash.

**Evidence:** no-clobber atomicity, stale-review, lineage, rebuild, and CLI end-to-end tests.

## A-0149-02 — commitment was descriptive, not governed

**Severity:** high integrity boundary

**Before:** commitment labels existed on assignments, but the runtime did not preserve how a level was reached or prevent a later operation from weakening its meaning.

**Risk:** “hard” could become cosmetic. A planner could revise a supposedly fixed premise or jump directly between levels without review custody.

**Repair:** adjacent monotone `raise_commitment` transitions, durable bases for hard assignments, source requirements for evidence/disclosure, and a hard revision blocker. Lowering has no in-place command.

**Evidence:** transition-chain, invalid-basis, skipped-boundary, downgrade-refusal, hard-blocker, verification, and replay tests.

## A-0149-03 — narrative proximity could be mistaken for causality

**Severity:** high semantic risk

**Before:** there was no explicit directed representation of what depended on a latent assignment. Any revision-cost calculation would have had to infer dependence from shared claims, chronology, or prose.

**Risk:** the system could either miss real promises or overfit every nearby detail into a retroactive clue.

**Repair:** the impact report separates ambient exposure from authored `consequence_links`. Links have typed dependents, named relations, severities, source/rationale custody, retirement, cycle checks, and lifecycle diagnostics.

**Evidence:** binding/nonbinding behavior, transitive traversal, cycle refusal, orphaned repair debt, context, snapshot, status, replay, and CLI tests.

## A-0149-04 — nonbinding consequences could disappear during revision

**Severity:** high auditability risk

**Before:** no protocol specified what should happen to downstream records when their premise ended.

**Risk:** deleting or auto-transferring links would both falsify custody: deletion erases debt; transfer asserts a new dependency without authorship.

**Repair:** notice/material links remain active when an endpoint ends. Queries mark `repair_required`; conflicts emit `orphaned-consequence`; explicit retirement or replacement is required.

**Evidence:** material-revision test verifies visibility, status count, conflict record, replay stability, and clean database verification.

## A-0149-05 — perspective `explain` leaked hidden structure through links

**Severity:** high confidentiality boundary

**Before:** target access was checked, but a visible assertion or source could still return dependent IDs naming hidden world assignments, consequence links, constraints, or other privileged records. Raw custody events also carried payload/change information inappropriate for perspective access.

**Risk:** a player could infer hidden worlds, latent causal structure, revision ancestry, or undisclosed operations without directly querying a forbidden target.

**Repair:** every explanation dependency/dependent now passes the same target visibility check. Perspective event custody is a safe envelope; raw payloads and change IDs are omitted. Source locator/metadata, agent metadata, invisible supersession IDs, and invisible question-resolution IDs are removed.

**Evidence:** perspective noninterference and historical-visibility regression tests serialize the complete response and assert absence of hidden IDs.

## A-0149-06 — schema evolution needed a third migration edge

**Severity:** medium operational integrity

**Before:** the ordered migration chain ended at schema 3.

**Risk:** campaigns skipping this runtime could have governance projections partially provisioned or remain stranded on an older physical layout.

**Repair:** schema 3→4 DDL and digest custody are added. Migration accepts coherent schema 1, 2, or 3 and preserves the event-ledger head. Forward-provisioned objects are tolerated only during DDL execution; post-migration shape and verifier invariants remain authoritative.

**Evidence:** schema-1, schema-2, and schema-3 migration tests all preserve the head and pass full verification.

## Refactor findings

- Pure commitment ordering, burden calculation, and deterministic cycle-witness logic were extracted to `commitment.py` instead of extending the storage class with policy arithmetic.
- Consequence endpoint lifecycle diagnostics are centralized in one query path and reused by conflicts, snapshots, context, and status.
- Explanation access is now link-aware rather than a target-only special case.
- Turn aliases and JSON Schemas treat governance operations as normal typed mutations, preserving one atomic path.

## Residual risks

- Burden weights are transparent policy constants, not empirically calibrated estimates.
- A malicious planner can author false consequence links or misuse severity.
- An authorized planner model can leak hidden state in prose; projection separation cannot police semantics after disclosure.
- Nonbinding repair debt is surfaced but not automatically resolved.
- Consequence traversal is bounded; truncation safely blocks revision but may require application-level graph cleanup.
- `precommitment` records intent but does not itself produce an external cryptographic commitment.
- Transcript bodies remain outside the cube, so impact review cannot inspect unstored wording.
