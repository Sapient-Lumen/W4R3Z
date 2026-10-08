# Maintenance mutation review page — write tolerance, overwrite fate, and escape hatches interface spec

## Purpose

A mutation budget is still too abstract unless the product shows what each candidate local action actually means.
This page exists to prevent the classic lie:

> it was a safe maintenance seat, so editing there could not hurt anything important.

## Core decision

AnonSync must expose one first-class **Maintenance mutation review** page whenever requested local work is not trivially `inspect-only`.

The page exists to answer five things in one place:

1. which local mutation classes are being considered
2. what each class does to continuity and later repair burden
3. whether any class is likely to overwrite or strand work
4. which safer lane best preserves operator intent
5. what claim ceiling survives afterward

## Fixed page order

1. **Requested mutation verdict**
2. **Per-action fate matrix**
3. **Overwrite / suspension explanation**
4. **Safer-lane recommendation**
5. **Actions and receipts**

### 1) Requested mutation verdict

Show:

- `maintenance_mutation_review_page_id`
- scope
- active maintenance contract or narrow-rights basis
- requested action set
- current best-fit fate class (`safe-local`, `local-only`, `suspend-and-repair`, `overwrite-likely`, `blocked`, `unknown`)
- strongest honest summary

The operator must be able to answer:

> what fate class does my proposed local work fall into?

### 2) Per-action fate matrix

This section is mandatory.
Show action rows for at least:

- edit existing shared file
- create new local file in scope
- rename / move local file
- delete local file or clear local copy
- restore from archive / older copy
- bulk-tool rewrite
- export-copy then edit elsewhere

For each row show:

- effective fate class
- continuity outcome
- whether remote or later maintenance healing can replace it
- whether the action creates later ambiguity for diagnostics or proof
- whether a cheaper safer substitute exists

The operator must be able to answer:

> which exact action keeps me safe, and which action only feels safe?

### 3) Overwrite / suspension explanation

This section is mandatory whenever any row is not plainly `safe-local`.
Show:

- what would suspend continuity
- what would keep local bytes but outside the shared line
- what would later overwrite local work
- whether overwrite is optional, automatic, hardwired, or counterpart-driven
- what evidence would upgrade or downgrade that risk

This is the authoritative explanation for:

> why would my local work be stranded or replaced later?

### 4) Safer-lane recommendation

Show one ranked ladder:

1. inspect without mutation
2. export / duplicate to side branch
3. temporary reviewed wider lane
4. accept local-only scratch with repair later
5. accept overwrite risk knowingly
6. block the operation

For each rung show:

- continuity quality
- data-loss risk
- later repair burden
- strongest safe sentence after choosing it

### 5) Actions and receipts

Actions may include:

- `Use safer lane`
- `Proceed with local-only scratch`
- `Proceed with overwrite risk`
- `Request wider reviewed lane`
- `Open mutation ledger`
- `Cancel`

Receipts must record action class, fate class, overwrite explanation, chosen safer lane, and claim ceiling.

## Public object

### Maintenance mutation review page

Fields:

- `maintenance_mutation_review_page_id`
- `scope_ref`
- `maintenance_or_rights_basis_ref`
- `requested_action_rows[]`
- `fate_rows[]`
- `overwrite_explanation_rows[]`
- `safer_lane_rows[]`
- `claim_ceiling`
- `strongest_safe_sentence`
- `stronger_rejected_sentence`
- `next_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. requested action
2. fate class
3. strongest overwrite or suspension risk
4. strongest safe sentence
5. next action

Example:

```text
edit existing shared file     overwrite-likely     later heal follows remote authority     edit elsewhere or accept replacement     Export to side branch
```

## Non-goals

This page does **not** prove which edits have already landed.
It proves only the reviewed **write tolerance, overwrite logic, and safer-lane recommendation**.
