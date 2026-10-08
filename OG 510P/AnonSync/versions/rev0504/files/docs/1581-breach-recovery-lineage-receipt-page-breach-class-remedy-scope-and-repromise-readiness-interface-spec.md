# Breach recovery lineage receipt page: breach class, remedy scope, and re-promise readiness interface spec

## Purpose

This receipt is the durable artifact that later operators, reviewers, and downstream audiences use to understand what failed, what survived, what was offered as remedy, and whether trust was ever repaired enough to support a new promise.

## Required receipt blocks

### 1) Identity block

Show:

- recovery id
- breached commitment id
- linked deliverable id
- audience id
- owner id
- receipt generation time

### 2) Breach basis block

Show:

- breached sentence
- breach class
- breach trigger fact
- original promise window
- whether miss was declared on time

### 3) Surviving obligation block

Show:

- surviving obligation class
- full original scope still owed or not
- abandoned original scope if any
- substitute scope if any
- whether audience acknowledgement is required

### 4) Remedy block

Show:

- current make-good class
- current recovery window or checkpoint rule
- strongest fact supporting that remedy
- strongest blocked stronger remedy
- what is explicitly not promised

### 5) Trust repair block

Show:

- current trust-repair status
- strongest fact supporting requalification
- strongest fact blocking requalification
- whether new promise authority is open
- whether new promise requires a new commitment id

### 6) Lineage block

Show:

- all remedy publications
- all scope reductions or restorations
- all trust-repair events
- all re-promise gate changes
- linked replacement commitment id if any
- current strongest surviving sentence

## Hard rules

- The receipt must make `breach`, `surviving obligation`, `recovery promise`, and `trust repair` visibly non-interchangeable.
- The receipt must preserve any abandoned original scope rather than letting later recovery prose erase it.
- The receipt may never say only `recovered` when the real state is `partial make-good` or `trust not yet repaired`.
- The receipt must preserve whether new commitment authority is still blocked or already reopened.
