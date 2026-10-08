# Publication mutation ledger and member observation-gap interface spec

## Purpose

The archive now has:

- reviewed sender-side issuance
- explicit per-subject publication
- living subject × member publication matrix truth
- affected-cell delta preview before apply
- member policy cards for future-arrival defaults

What still remained too easy to blur was the question that appears **after** a reviewed publication change has been applied:

> what exactly changed, which reviewed delta set did it come from, which target members have actually observed the new state, which ones still have only a sender-side mutation record, and what facts must not be inferred from silence?

Without one explicit ledger, the product can still recreate the Resilio seam in a more polished costume.
Permission change becomes `we already changed it`, withdrawal becomes `they no longer have it`, and a pending or silent member gets flattened into a false sense of closure.

This document defines the interface contract for durable publication-mutation history and per-member observation gaps.

## Core rule

Every meaningful publication mutation must be rendered as one first-class **publication mutation ledger entry** with explicit lineage to:

1. the reviewed change that proposed it
2. the exact cell set it intended to affect
3. what was applied locally
4. what each affected member has or has not yet observed
5. which stronger claims still require later evidence

A mutation ledger is not a cosmetic activity feed.
It is the public truth of what changed and how much of that change is merely recorded locally versus actually observed in the field.

## Why this needs its own spec

Current Resilio docs are useful here in a negative way.
`User Management` documents on-the-fly permission changes and disconnecting peers while also stating that already synchronized files remain in the peer's folder.
`Comprehensive guide to syncing` and `Sync Share Dialog` describe approval requests, peer identity review, and later access changes.
That is real functionality.
But it still leaves an operator reconstructing too much from scattered peer lists, approval history, and remembered support lore.

AnonSync should refuse that reconstruction burden.
A publication change should not disappear into `permission updated` or `revoked` once the button is pressed.
The operator should be able to inspect one ledger entry and answer:

- what change was reviewed
- what change was actually applied
- who has observed it
- who has not yet observed it
- which non-effects still stand
- which stronger claims would require recall, cleanup, or later receipts elsewhere

## Public objects

### Publication mutation ledger entry

A durable record of one reviewed publication mutation after apply.

Suggested fields:

- `publication_mutation_entry_id`
- `mutation_kind` (`publish`, `narrow-role`, `widen-role`, `withdraw`, `member-default-apply`, `template-apply`, `override-revert`)
- `initiating_subject_refs[]`
- `initiating_member_refs[]`
- `source_review_ref`
- `source_delta_preview_ref` nullable
- `applied_cell_refs[]`
- `non_effect_guarantees[]`
- `created_at`
- `supersedes_entry_ref` nullable
- `receipt_ref`

### Member observation row

A compact row describing what one affected member has or has not yet observed from one mutation.

Suggested fields:

- `member_observation_row_id`
- `publication_mutation_entry_ref`
- `member_ref`
- `affected_cell_refs[]`
- `observation_state` (`not-announced-yet`, `announced-pending-observation`, `observed-no-local-claim`, `observed-with-pending-local-work`, `observed-and-settled`, `offline-unknown`, `superseded`)
- `latest_member_receipt_ref` nullable
- `local_work_summary`
- `stronger_claims_blocked[]`
- `last_observed_at` nullable

### Publication mutation receipt

A durable proof that the reviewed mutation was applied and what observation state was honestly known at apply time.

Suggested fields:

- `publication_mutation_receipt_id`
- `publication_mutation_entry_ref`
- `actor_ref`
- `applied_cell_count`
- `member_observation_summary[]`
- `non_effect_summary[]`
- `created_at`
- `proof_refs[]`

## Fixed inspection order

Every publication-mutation-ledger surface should preserve the same order:

1. **Mutation requested and why**
2. **Reviewed delta lineage**
3. **What was actually applied**
4. **Per-member observation rows**
5. **What this mutation definitely does not prove**
6. **Next honest actions and follow-up receipts**

### 1) Mutation requested and why

This section should state plainly:

- whether the mutation published, widened, narrowed, withdrew, or changed future defaults
- who or what initiated it
- whether the change was subject-specific, member-specific, or template/default-driven
- what problem or intent it addressed

### 2) Reviewed delta lineage

This section should keep lineage explicit:

- source review pane
- source delta preview, when one existed
- counts of reviewed affected cells
- whether any blocked cells were omitted or deferred

A mutation ledger entry without review lineage is too easy to misread as raw activity noise.

### 3) What was actually applied

This section should state:

- which cells changed locally
- which cells remained intentionally unchanged
- whether the mutation superseded an earlier still-pending mutation
- what receipt proves the local apply

### 4) Per-member observation rows

Each affected member row should keep these truths adjacent:

- member
- affected cell count
- observation state
- latest observed receipt or lack of receipt
- local work still pending on that member
- next honest action

Examples:

- `travel-laptop   3 cells   observed-with-pending-local-work   one role-first arrival review still open`
- `home-nas   12 cells   observed-and-settled   no further local action`
- `archive-vps   1 cell   offline-unknown   withdrawal recorded locally; retained-copy questions remain elsewhere`

### 5) What this mutation definitely does not prove

This section is mandatory.
It should aggressively publish non-equivalence, for example:

- applied locally does not prove remote observation yet
- narrowed role does not prove retained bytes were removed
- withdrawn publication does not erase earlier receipts
- member silence does not prove safe non-receipt
- supersession does not erase the older ledger entry from audit history

### 6) Next honest actions and follow-up receipts

This section should offer only actions that match the evidence currently held.
Examples:

- `Wait for observation`
- `Open member arrival review`
- `Open retained-copy review`
- `Open superseding mutation`
- `Export mutation receipt`

## State model

The observation-state vocabulary should be stable across UI, CLI, and API:

- `not-announced-yet` — local apply exists but announcement handoff has not yet happened
- `announced-pending-observation` — target should now be able to learn of the change, but observation is not yet proven
- `observed-no-local-claim` — target has observed the changed cell but has not taken new local action
- `observed-with-pending-local-work` — target has seen the change and still has unresolved local review or bind work
- `observed-and-settled` — target has both observed the change and cleared required local work
- `offline-unknown` — strongest honest claim remains pending because the target has not been observed recently enough
- `superseded` — a later mutation replaced the practical effect before settlement finished

## Public rules

### Rule 1 — local apply is not remote observation

The product may never flatten `mutation applied` into `all targets now know`.

### Rule 2 — observation is not recall

A member observing a narrowed or withdrawn cell is still not proof that old bytes were removed.
That stronger claim must stay delegated to retained-copy and recall surfaces.

### Rule 3 — supersession remains historical truth

A later mutation may supersede a pending one, but the earlier mutation must remain inspectable with explicit superseded status.

### Rule 4 — member rows are first-class, not drill-down trivia

The operator should not have to open per-member debug drawers merely to answer who has observed the change and who has not.

### Rule 5 — a mutation ledger may summarize current state, but may not replace the matrix

The ledger explains change over time.
The matrix explains current live publication truth.
Neither may masquerade as the other.

## Dense row contract

A dense ledger row should preserve these labels in this order:

- `Mutation`
- `Reviewed from`
- `Applied cells`
- `Observation gaps`
- `Strong non-effects`
- `Next`

## Acceptance test

The mutation ledger is good enough when a cautious operator can answer all of the following from one surface:

- what exact publication change was reviewed and then applied
- which delta preview and receipt prove that history
- which affected members have observed the new state
- which members remain pending, offline, or superseded
- what this history still does not prove about retained copies or recall
- which follow-up review is honestly appropriate next
