# Execution custody proof page: assignee claim, expiry, and safe unclaim interface spec

## Purpose

After claim review, the product needs one durable proof page that answers:

> who currently has custody, what commitment is live, when does it expire, and what exactly survives if the work is safely unclaimed or reclaimed?

## Core decision

AnonSync must expose one first-class **Execution custody proof** page for every dispatched item that has entered accepted, committed, in-progress, returned, expired, or reclaimed state.

## Fixed page order

1. **Custody verdict banner**
2. **Proof basis card**
3. **Commitment-state card**
4. **Expiry-and-renewal card**
5. **Safe-unclaim outcome card**
6. **Blocked stronger claim card**

### 1) Custody verdict banner

Show:

- current custody verdict
- current named custodian
- whether backup custody exists
- active commitment window
- abandonment risk grade
- current return or reclaim route if no custodian is live

Supported `custody_verdict` values:

- `not-yet-claimed`
- `claimed-not-started`
- `claimed-and-started`
- `shared-custody`
- `redelegation-pending`
- `returned-safely`
- `expired-unclaimed`
- `reclaimed-after-expiry`
- `superseded-before-claim`

Hard rule:

A verdict may not say `claimed-and-started` without explicit start evidence.
Acceptance alone is insufficient.

### 2) Proof basis card

Required rows:

- acceptance evidence
- start evidence
- renewal evidence if any
- re-delegation evidence if any
- return or decline evidence if any
- last operator who validated the proof

Supported `proof_basis_class` values:

- `explicit-acceptance`
- `explicit-start`
- `standing-rotation-claim`
- `renewed-commitment`
- `return-confirmed`
- `reclaim-confirmed`

Hard rule:

The page must not let a passive status light masquerade as acceptance evidence.

### 3) Commitment-state card

Required rows:

- current expected work posture
- whether active progress is required
- what would count as breach
- what is allowed to remain idle
- what would force immediate reevaluation

Supported `expected_work_posture` values:

- `acknowledged-awaiting-start-window`
- `active-execution`
- `active-watch`
- `waiting-on-external-blocker`
- `returned-for-reassignment`
- `expired`

Hard rule:

The card must distinguish a healthy waiting state from silent drift.

### 4) Expiry-and-renewal card

Required rows:

- expiry timestamp
- whether expiry is hard or renewable
- renewal owner
- renewal evidence required
- grace treatment if any
- what claim survives if renewal never lands

Supported `expiry_class` values:

- `hard-expiry`
- `renewable-expiry`
- `watch-renewal`
- `manual-release-only`
- `no-live-claim`

Hard rule:

A renewed claim must produce a new visible window.
Rolling implied renewals are not allowed.

### 5) Safe-unclaim outcome card

Required rows:

- why the claim is ending
- whether work is partially complete
- whether residual duty survives with the old custodian
- where the item returns
- whether dispatch must be recomputed
- what weaker sentence remains true afterward

Supported `safe_unclaim_route` values:

- `return-unworked`
- `return-with-partial-progress`
- `handoff-to-new-custodian`
- `escalate-before-return`
- `close-no-further-action`

Hard rule:

Unclaiming may never imply that the work stopped mattering.
The surviving weaker sentence must remain visible.

### 6) Blocked stronger claim card

Render exactly one line beginning:

**Blocked stronger claim:**

Examples:

- `This work is owned until completion.`
- `This shift has permanent custody.`
- `The item is safe because someone saw the notification.`
- `The work can be forgotten because it was returned.`

Hard rule:

Every custody proof must preserve one blocked stronger claim.
