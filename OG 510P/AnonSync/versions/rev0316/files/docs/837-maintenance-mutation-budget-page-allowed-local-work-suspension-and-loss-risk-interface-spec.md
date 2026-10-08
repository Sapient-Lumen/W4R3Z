# Maintenance mutation budget page — allowed local work, suspension, and loss-risk interface spec

## Purpose

The archive already has maintenance intent, maintenance semantics, quiet receipts, non-authority edit doctrine, and cleanup review.
What it still lacked was one ordinary page for the question:

> while this maintenance posture is active, what local work is actually in budget here, what work will only strand itself, and what work is likely to be overwritten later?

Current official Resilio docs make this seam concrete.
They still show read-only suspension, optional destructive overwrite, hardwired encrypted-backup overwrite, and preservation-oriented backup semantics as separate islands.
That is useful truth.
It should not remain a memory test.

## Core decision

AnonSync must expose one first-class **Maintenance mutation budget** page whenever an operator is about to edit, stage, inspect, or clean local material inside a hold, backup-like posture, narrow-rights seat, or other maintenance-constrained context.

The page exists to answer five things in one place:

1. what local work the operator wants to perform
2. whether that work is in budget under the current maintenance contract
3. whether the work will survive, suspend continuity, or be overwritten later
4. what safer escape hatch exists if the work is out of budget
5. what sentence is honest before any local mutation begins

## Fixed page order

1. **Requested local-work verdict**
2. **Mutation-budget matrix**
3. **Continuity fate and overwrite risk**
4. **Escape hatches and safer work lanes**
5. **Actions and receipts**

### 1) Requested local-work verdict

Show:

- `maintenance_mutation_budget_page_id`
- scope (`seat`, `subject`, `path slice`, or `maintenance cohort`)
- active maintenance contract reference if any
- requested local-work class (`inspect`, `edit-existing`, `add-new`, `rename/move`, `delete-local`, `temporary-note`, `bulk-change`, `unknown`)
- current budget verdict (`in-budget`, `in-budget-but-non-continuing`, `suspends-continuity`, `overwrite-risk`, `blocked`, `unknown`)
- strongest honest summary
- stronger unsupported summary

The operator must be able to answer:

> what kind of local work am I asking to do here, in the product's language?

### 2) Mutation-budget matrix

This section is mandatory.
Show rows for at least:

- inspect/read access
- edit existing file contents
- add new local files
- rename or move within scope
- delete local copies
- metadata-only changes if supported
- clear-to-placeholder or remove-from-device style actions
- export-to-side-branch or save-elsewhere action

Each row must show one state:

- `allowed and continuing`
- `allowed but local-only`
- `allowed but suspends future continuity`
- `allowed but likely to be overwritten`
- `blocked`
- `unknown until counterpart or route review`

The page must answer:

> what local work is actually within budget during this hold?

### 3) Continuity fate and overwrite risk

Show, for the requested work class:

- continuity mode after edit (`continues`, `local-only`, `suspended`, `repaired-later`, `will-be-overwritten`, `unknown`)
- overwrite source (`remote authority`, `maintenance heal`, `hardwired backup rule`, `manual operator choice`, `none known`)
- whether newly added files behave differently from edits to existing files
- whether survival depends on export, branch, or manual repair later
- strongest safe sentence and stronger forbidden sentence

The operator must be able to answer:

> if I mutate here anyway, what fate am I buying?

### 4) Escape hatches and safer work lanes

Show safer alternatives such as:

- `Inspect only`
- `Export and edit elsewhere`
- `Create side branch / sidecar workspace`
- `Temporarily widen rights under review`
- `Accept suspend-and-repair later`
- `Accept overwrite risk`
- `Abort local work`

Each option must state:

- changed risk class
- whether continuity improves or merely moves elsewhere
- what later receipt or repair lane it opens

The page must answer:

> what is the cheapest honest way to do my work without lying about continuity?

### 5) Actions and receipts

Actions may include:

- `Proceed with in-budget work`
- `Proceed with suspend-and-repair`
- `Export to safer lane`
- `Open mutation review`
- `Choose stricter hold`
- `Cancel`

Receipts must record requested local work, budget verdict, continuity fate, overwrite risk, chosen escape hatch, and strongest safe sentence.

## Public object

### Maintenance mutation budget page

Fields:

- `maintenance_mutation_budget_page_id`
- `scope_ref`
- `active_maintenance_contract_ref`
- `requested_local_work_class`
- `budget_rows[]`
- `continuity_fate`
- `overwrite_risk_rows[]`
- `escape_hatch_rows[]`
- `strongest_safe_sentence`
- `stronger_rejected_sentence`
- `next_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. scope
2. requested work
3. budget verdict
4. strongest risk
5. next action

Example:

```text
Archive witness seat     edit-existing     suspends-continuity     later heal would overwrite local edits     Export to side branch
```

## Non-goals

This page does **not** prove that any local edit was already performed.
It proves only the reviewed **mutation budget, continuity fate, and safer-work ladder**.
