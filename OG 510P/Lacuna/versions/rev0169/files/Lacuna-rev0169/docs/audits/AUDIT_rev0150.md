# Audit — rev0150

## Scope

This audit examined consequence-debt lifecycle, reviewed mutations inside atomic turns, projection/event agreement, context separation, migration, CLI/direct-library parity, and active endpoint validity.

## A-0150-01 — repair debt had no first-class discharge transaction

**Severity:** high semantic integrity

**Before:** rev0149 surfaced an active consequence whose premise or dependent had ended, but the only available actions were to retire the old link or create an unrelated new link.

**Risk:** callers could perform a non-atomic two-step repair, lose the relationship between old and new custody, or implement private transfer conventions that replay and explanation could not verify.

**Repair:** add `consequence_repair_review` and `replace_consequence`. One `consequence.replaced` event atomically ends the predecessor, creates a successor, and writes an identified repair relation.

**Evidence:** orphan repair, semantic replacement, replay, snapshot, explanation, turn, and CLI tests.

## A-0150-02 — retire-plus-link had an observable semantic gap

**Severity:** high transactional integrity

**Before:** a host attempting repair through two operations could expose a state in which the predecessor was ended but no successor existed, or could commit one action without the other across separate change-sets.

**Risk:** repair lineage became ambiguous and concurrent writers could race into the gap.

**Repair:** one event and one transaction sequence owns all three projection changes. Refusal leaves all rows untouched.

**Evidence:** stale-review atomicity test and event-sequence assertions.

## A-0150-03 — new links could target already-ended records

**Severity:** high lifecycle integrity

**Before:** target validation checked existence, not active lifecycle, for consequence creation.

**Risk:** a new consequence could be born already orphaned, bypassing the intended distinction between historical debt and valid new custody.

**Repair:** centralize active target validation. New and replacement links require active assignments/assertions and open questions.

**Evidence:** ended assertion and closed-question refusal tests; existing historical orphan behavior remains accepted.

## A-0150-04 — cycle checks must model the post-repair graph

**Severity:** medium correctness

**Before:** naïvely testing a proposed successor against the active graph would include the predecessor edge that the same transaction ends.

**Risk:** valid edge reversal or endpoint change could be falsely refused.

**Repair:** allow graph-edge enumeration to exclude the predecessor consequence during replacement validation, then test the candidate edge against that post-removal graph.

**Evidence:** valid reversal test and true-cycle refusal test.

## A-0150-05 — current-head review semantics conflicted with source-bound turns

**Severity:** high protocol correctness

**Before:** adding the immutable narration source before a reviewed operation advanced the live head, making a review embedded in the turn packet stale inside the same atomic commit.

**Risk:** director turns could not safely combine source custody and reviewed mutation, encouraging source omission or multi-transaction workarounds.

**Repair:** `apply_changeset` captures its base head and supplies it to reviewed operation validation. The review is recomputed from current in-transaction projections with that base head in the digest core.

**Evidence:** direct atomic batch and director-turn tests. A separately committed intervening source still stales the receipt.

## A-0150-06 — repair projection integrity needed origin-event binding

**Severity:** high replay integrity

**Before:** table constraints could prove one-to-one local shape but not that repair fields matched the immutable event that created them.

**Risk:** coordinated projection edits could preserve foreign keys and uniqueness while changing reason, digest, endpoints, or semantics.

**Repair:** verifier maps event sequence to payload, checks each repair row originates from `consequence.replaced`, compares projected fields to payload, and detects replacement events missing repair projection.

**Evidence:** coordinated projection tamper is detected; rebuild restores event-derived state.

## A-0150-07 — turn packet receipt rebinding needed explicit handling

**Severity:** medium protocol integrity

**Before:** planner context could include a repair review calculated before opening the turn. Recording the turn request source necessarily changed the expected head.

**Risk:** the packet could carry internally stale receipts despite being freshly generated.

**Repair:** when the turn adapter rebinds planner context to the post-request-source head, it also recomputes embedded repair-frontier receipts. Only the adapter’s own source event occurs between context construction and rebinding; no epistemic projection changes.

**Evidence:** director packet frontier and commit tests.

## A-0150-08 — one model operation creates two independent identities

**Severity:** medium integration correctness

**Before:** alias normalization assumed one creator ID per operation.

**Risk:** `replace_consequence` needs both a successor consequence ID and a repair ID; conflating them would break namespace clarity or force models to coordinate IDs manually.

**Repair:** retain the primary alias binding for `consequence_id` and add a secondary generated-ID registry for `repair_id`.

**Evidence:** turn proposal normalization and returned binding tests.

## A-0150-09 — repair lineage could leak through audience projections

**Severity:** high confidentiality

**Before:** a newly introduced projection and frontier could accidentally be included by generic context/render code.

**Risk:** hidden predecessor/successor IDs and planner deliberation could expose ontology or future intent to a player.

**Repair:** perspective context returns structurally empty repair fields plus explicit omission reasons; planner context alone receives lineage and reviews. Perspective `explain` refuses repair targets.

**Evidence:** serialized noninterference test checks absence of repair, predecessor, and successor IDs.

## A-0150-10 — exchange schemas could drift from the runtime registry

**Severity:** medium integration integrity

**Before:** adding a runtime operation and independently editing two JSON Schemas relied on review discipline alone.

**Risk:** direct change-sets, turn proposals, and runtime normalization could accept different operation sets or field names.

**Repair:** add schema parity tests that compare every change-set operation variant and the turn-operation enum to `OPERATION_FIELDS`, plus a concrete replacement instance/digest test. `jsonschema` remains an optional test dependency rather than a runtime dependency.

**Evidence:** four exchange-schema tests pass; the standard-library parity tests still run when the optional validator is absent.

## A-0150-11 — digest construction existed at two protocol layers

**Severity:** medium authorization integrity

**Before:** storage validation and turn-packet receipt rebinding could independently reconstruct the same digest contract.

**Risk:** a future field addition could make a receipt accepted by one layer and refused by the other, or leave an authorization field unhashed in one path.

**Repair:** move the canonical digest constructor beside the storage policy constant and call it from both review issuance and the turn adapter.

**Evidence:** schema/runtime parity tests plus director-turn commit using a rebound embedded review.

## A-0150-12 — repair review-head custody was implicit

**Severity:** medium auditability

**Before:** the repair projection retained the review digest but did not directly expose which immutable change-set head the event claimed to review.

**Risk:** an auditor could verify local lineage yet still need to reconstruct authorization context manually.

**Repair:** record `repair_review_head` in the immutable event, verify it equals the origin change receipt's `before_head`, and expose that receipt-derived head with origin event and change IDs in planner repair queries.

**Evidence:** repair-custody query assertions and verifier mismatch coverage.

## A-0150-13 — cleanup could mask a useful failure

**Severity:** low operational correctness

**Before:** teardown paths could converge on an already-closed SQLite connection after a failed migration or context-manager exit.

**Risk:** a secondary `sqlite3.ProgrammingError` could obscure the original Lacuna refusal.

**Repair:** make `Cube.close()` idempotent while preserving non-closure database errors.

**Evidence:** explicit double-close and clean-reopen test.

## A-0150-14 — acceptance had no conventional discovery entrance

**Severity:** low operational reliability

**Before:** `python -m unittest discover` from the archive root reported zero tests because `tests/` was not importable, while the full schema checks also assumed an undeclared validator package.

**Risk:** a maintainer could mistake an empty run for acceptance, or fail the suite for an optional tool that is not a runtime dependency.

**Repair:** make `tests/` importable, declare `jsonschema` as an optional `test` extra, and skip only validator-specific checks when it is absent. Runtime/schema registry parity remains standard-library-only.

**Evidence:** default discovery finds 95 tests; the full environment passes all 95, and an import-blocked validator run still executes the parity checks while skipping only two external-validator checks.

## Refactor findings

- Reviewed operations now share one `review_head` path through `apply_changeset` and `_prepare_operation`.
- Repair review hashing has one canonical constructor shared by store and turn adapter.
- Repair queries expose receipt-derived review-head custody plus origin event/change identities.
- Cube shutdown is idempotent, so cleanup does not replace the primary failure.
- Consequence target lifecycle validation is centralized and parameterized for historical versus active lookup.
- Assignment-edge enumeration accepts an explicit exclusion for post-change graph analysis.
- Repair lineage is a first-class namespace in query, explanation, snapshot, status, verification, and rebuild.
- Turn ID generation distinguishes primary alias targets from secondary custodial identities.
- Conventional `unittest` discovery and an optional schema-validation extra make the acceptance entrance honest.

## Residual risks

- The review digest is predecessor/state-bound, not candidate-bound. Candidate validity is checked structurally during commit, but semantic appropriateness remains a planner decision.
- A malicious authorized planner may replace a dependency with a false or manipulative one.
- One-to-one lineage cannot express split, merge, partial transfer, or weighted replacement.
- External narration and game-engine effects are not compensated automatically.
- Planner context can still be leaked by an authorized model through prose.
- Base-head receipts are safe under Lacuna’s single atomic transaction path; distributed adapters must preserve the same expected-head discipline.
- Known successor discovery follows explicit revision/supersession lineage only and does not find semantically equivalent records.
