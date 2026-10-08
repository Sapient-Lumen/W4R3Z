# Branch consequence compare page — attach, merge, fork, and blocked alternatives interface spec

## Purpose

The bind-outcome review names the current draft.
The existing-tree evidence page proves why it looks that way.
What still needs one explicit page is the operator comparison question:

> which branch consequence is actually best here once I compare attach, merge, deliberate fork, or stop-and-rechoose?

This page exists so operators do not have to mentally simulate different target choices from warnings and folklore.

## Core decision

Whenever more than one plausible branch remains live, the product should expose one first-class **Branch consequence compare** page.

This page owns counterfactuals.

## Fixed page order

1. **Current draft and competing alternatives**
2. **Lineage consequence compare**
3. **Namespace and byte consequence compare**
4. **Risk and reversibility compare**
5. **Recommended branch**
6. **Commit and receipt promise**

### 1) Current draft and competing alternatives

Show the current draft beside plausible alternatives:

- `attach same lineage`
- `merge into existing tree`
- `fork deliberately`
- `choose different target`
- `require empty ciphertext root`
- `stop and leave unbound`

### 2) Lineage consequence compare

For each alternative, show:

- whether one current lineage remains
- whether a second sibling branch is created
- whether same-subject ambiguity persists
- whether later repair workload increases or decreases

### 3) Namespace and byte consequence compare

For each alternative, show:

- whether bytes land immediately
- whether same-name `(1)`-style divergence risk exists
- whether existing bytes remain in place, merge, or are rejected
- whether hidden service-state conflict is likely

### 4) Risk and reversibility compare

For each alternative, show:

- strongest current risk
- reversibility class (`easy`, `reviewed rollback`, `costly`, `blocked`)
- whether later evidence could still upgrade confidence
- whether the alternative is policy-blocked for this world or artifact family

### 5) Recommended branch

The page must name one recommended alternative and at least one explicit non-recommended alternative.
It should answer:

- why this recommendation is safest now
- what would have to change for another branch to become primary

### 6) Commit and receipt promise

Before exit, show:

- the branch class that will be committed
- the alternatives that were considered and rejected
- the next page handed off to

## Main surface

A compact **Branch consequence compare** card should show:

- current draft
- best alternative if different
- strongest risk delta
- recommended action

## Detailed surface

The detailed page should provide four tables.

### Table A — Lineage table

Columns:

- alternative
- lineage count after commit
- ambiguity class

### Table B — Namespace table

Columns:

- alternative
- path/tree consequence
- duplicate-sibling risk

### Table C — Byte/risk table

Columns:

- alternative
- byte behavior
- strongest risk
- reversibility

### Table D — Commit preview

Columns:

- chosen branch
- rejected alternatives
- next handoff

## CLI parity

Minimum commands:

- `anonsync branch-compare show <review-id>`
- `anonsync branch-compare choose <review-id> --branch <branch>`
- `anonsync branch-compare receipt <receipt-id>`

## Acceptance criteria

A user can:

- compare attach, merge, fork, blocked, and rechoose outcomes side by side
- see when a duplicate sibling is a counterfactual they can still avoid
- commit one branch with rejected alternatives preserved in the receipt
