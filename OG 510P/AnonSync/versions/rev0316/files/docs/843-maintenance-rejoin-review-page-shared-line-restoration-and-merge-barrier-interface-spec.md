# Maintenance rejoin review page — shared-line restoration and merge-barrier interface spec

## Purpose

A rejoin plan is still too abstract unless the product shows what each restoration move actually means for continuity.
This page exists to prevent the classic lie:

> the work still existed locally, so we could obviously put it back later.

## Core decision

AnonSync must expose one first-class **Maintenance rejoin review** page whenever local work from a narrow maintenance posture is being considered for promotion, restoration, comparison, or abandonment.

The page exists to answer five things in one place:

1. which restoration moves are actually on the table
2. what each move does to shared-line authority
3. whether any move silently overwrites or demotes the local work
4. which move best preserves intent without overclaiming continuity
5. what claim ceiling survives afterward

## Fixed page order

1. **Requested restoration verdict**
2. **Per-path restoration matrix**
3. **Merge and overwrite explanation**
4. **Best-fit successor recommendation**
5. **Actions and receipts**

### 1) Requested restoration verdict

Show:

- `maintenance_rejoin_review_page_id`
- scope
- governing maintenance or narrow-seat basis
- requested restoration set
- current best-fit restoration class (`restore-in-place`, `restore-after-widening`, `promote-successor`, `preserve-without-rejoin`, `abandon-local`, `blocked`, `unknown`)
- strongest honest summary

The operator must be able to answer:

> what restoration class does this local work actually fall into?

### 2) Per-path restoration matrix

This section is mandatory.
Show action rows for at least:

- resume under widened write authority
- compare then promote local candidate as winner
- export branch and publish successor artifact
- restore source-authoritative version and discard local candidate
- keep local residue only for evidence or archive
- reconnect / reattach without promoting local work
- abandon or overwrite the local work knowingly

For each row show:

- resulting continuity class
- whether shared history remains one line or becomes successor lineage
- whether local work stays canonical, derivative, or discarded
- whether more evidence is needed before the move is honest
- whether a cheaper safer substitute exists

The operator must be able to answer:

> which exact restoration move preserves the work honestly, and which one only feels like restoration?

### 3) Merge and overwrite explanation

This section is mandatory whenever any row is not plainly `restore-in-place`.
Show:

- what blocks straight rejoin now
- what would cause the local work to be overwritten or superseded
- what would convert the local work into a successor artifact instead of the same shared line
- whether remote source, preserved archive, or reviewed human compare is the stronger authority
- what proof would upgrade or downgrade that verdict

This is the authoritative explanation for:

> why is this rejoin a straight restoration, a promotion, or an abandonment?

### 4) Best-fit successor recommendation

Show one ranked ladder:

1. reviewed in-place restoration
2. rights/posture widening then restoration
3. compare and promote as reviewed winner
4. publish successor branch / artifact
5. preserve as local evidence only
6. abandon or overwrite knowingly

For each rung show:

- continuity quality
- overwrite risk
- governance cost
- strongest safe sentence after choosing it

### 5) Actions and receipts

Actions may include:

- `Restore in place`
- `Request widening and retry`
- `Open candidate compare`
- `Publish successor`
- `Preserve as evidence only`
- `Accept overwrite / abandonment`
- `Open rejoin ledger`
- `Cancel`

Receipts must record restoration class, merge barrier, chosen successor lane, claim ceiling, and successor or reopen boundary.

## Public object

### Maintenance rejoin review page

Fields:

- `maintenance_rejoin_review_page_id`
- `scope_ref`
- `maintenance_or_narrow_posture_ref`
- `requested_restoration_rows[]`
- `restoration_class`
- `path_rows[]`
- `merge_barrier_rows[]`
- `successor_recommendation_rows[]`
- `claim_ceiling`
- `strongest_safe_sentence`
- `stronger_rejected_sentence`
- `next_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. requested restoration path
2. restoration class
3. strongest merge or overwrite barrier
4. strongest safe sentence
5. next action

Example:

```text
promote local read-only edit     promote-successor     same-line restore would be overwritten by remote authority     local work can survive only as reviewed successor     Open candidate compare
```

## Non-goals

This page does **not** prove that shared-line restoration is already complete.
It proves only the reviewed **restoration class, merge barrier, and best-fit successor ladder**.
