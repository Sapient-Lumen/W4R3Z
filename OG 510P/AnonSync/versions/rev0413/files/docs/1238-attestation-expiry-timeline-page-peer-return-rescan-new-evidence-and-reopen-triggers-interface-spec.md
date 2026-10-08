# Attestation expiry timeline page: peer return, rescan, new evidence, and reopen triggers

This page exists because a human assertion is not timeless.
A judgment that was reasonable five minutes ago can become stale the moment a peer returns, a rescan finds contradiction, or new history evidence appears.

## Operator question

> when does this attestation stop carrying decision weight, what events reopen it, and what previously hidden contradiction could surface later?

## When this page must appear

Render whenever an operator attestation remains active after commit, especially for:

- hidden ghost/no-source warnings
- local-newest republish claims
- same-tree reconnect claims
- destructive recreate after archive review
- overwrite-risk acceptance on occupied targets

## Fixed page order

1. **Current attestation status**
2. **Expiry ladder**
3. **Reopen triggers**
4. **Automatic downgrades**
5. **Historical branch changes**

## 1) Current attestation status

Show:

- attestation id
- currently active / expired / contradicted / superseded status
- strongest safe sentence right now
- next likely invalidator
- current risk if left unreviewed

## 2) Expiry ladder

Every attestation must have one explicit expiry rung:

- `session-only`
- `until next scan`
- `until absent peers return`
- `until path lineage changes`
- `until successor-epoch commit`
- `until stronger machine proof arrives`
- `manual expiry only`

The operator must be able to answer: **what event naturally ends the validity of this attestation?**

## 3) Reopen triggers

Render trigger rows such as:

- offline peer observed online again
- new chronology evidence conflicts with local-newest claim
- folder tree rescan reveals contradiction
- Archive/history contents change or become visible
- path bind no longer matches the attested same-tree target
- recreated subject obtains a new spine witness
- another operator requests stronger claim language

Each row must show severity and whether it changes only wording or also action safety.

## 4) Automatic downgrades

The system must automatically downgrade previous claims when expiry happens.
Examples:

- `ignored ghost warning` downgrades back to `visibility choice only; world absence unproved`
- `local-newest` downgrades to `republished on stale operator evidence`
- `same-tree reconnect` downgrades to `path continuity requires rereview`
- `archive reviewed clear` downgrades to `destructive step completed; no continuing proof of universal emptiness`

The operator must be able to answer: **what safe sentence survives after expiry?**

## 5) Historical branch changes

Show a timeline of:

- attestation issued
- attestation committed
- contradiction seen
- claim downgraded
- attestation superseded by stronger proof
- attestation reopened for human rereview

## Main surface

The subject workspace should expose a compact **Human assertions** card with:

- active attestation count
- contradicted attestation count
- nearest expiry trigger
- action: `Review assertion timeline`

## What this page prevents

Without this page, the product quietly carries stale human certainty forward as if it were durable system truth.
AnonSync must instead age operator assumptions openly and on schedule.
