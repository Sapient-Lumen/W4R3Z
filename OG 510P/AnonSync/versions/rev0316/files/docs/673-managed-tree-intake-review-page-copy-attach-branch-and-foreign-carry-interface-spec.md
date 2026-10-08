# Managed-tree intake review page — copy, attach, branch, and foreign-carry interface spec

## Purpose

This page exists for the commit moment that follows copied-tree posture.
It answers the operator's narrower question:

> now that I know this tree carries more than ordinary bytes, what exactly am I asking the product to do with it?

## Core decision

Any copy-looking intake that discovered controller state, subject identity, or contradictory continuity evidence must compile to one reviewed **Managed-tree intake** object before commit.

The product must not reduce this to ordinary verbs such as `Use folder`, `Import`, `Reconnect`, or `Delete hidden files and continue`.

## Fixed review order

1. **Requested interpretation**
2. **Continuity consequences**
3. **Hidden-state fate**
4. **Rejected alternatives**

### 1) Requested interpretation

Show the exact request as one of:

- `treat as same managed subject`
- `treat as copied payload branch`
- `keep for inspect only`
- `strip controller state and adopt payload`
- `quarantine foreign managed tree`

The operator must be able to answer:

> what claim am I making about this tree?

### 2) Continuity consequences

Show:

- whether the current subject epoch is preserved
- whether a successor epoch is created
- whether the tree becomes a new clean branch with no continuity claim
- whether history/Archive witnesses become weaker or orphaned

The operator must be able to answer:

> am I continuing one story, creating a successor, or creating a clean copy?

### 3) Hidden-state fate

Show the planned fate of each carried control family:

- preserve in place
- preserve but quarantine
- export then detach
- destroy after acknowledgement
- leave untouched because no commit occurs

The operator must be able to answer:

> what happens to the hidden managed state if I proceed?

### 4) Rejected alternatives

Show the safer rejected lanes adjacent to the requested one, for example:

- `Inspect only would preserve all witnesses`
- `Clean branch would avoid foreign continuity claim`
- `Same-subject attach is blocked because owner proof is contradictory`

The operator must be able to answer:

> what less-stronger alternative did I decline?

## Public object

### `managed_tree_intake_review`

Fields:

- `managed_tree_intake_review_id`
- `tree_ref`
- `carry_verdict`
- `requested_interpretation`
- `continuity_outcome_preview`
- `hidden_state_fate_rows[]`
- `rejected_alternative_rows[]`
- `generated_at`

## Design test

This page is not explicit enough if the operator can still accidentally turn a copied managed tree into a same-subject claim without seeing both the hidden-state fate and the strongest rejected safer lane.
