# Publication readiness page: detection, delay, lock, and commit verdict interface spec

## Purpose

The archive already had generic cadence, rescan, and queue concepts.
What it still lacked was one ordinary page for the simpler question:

> is this changed file or subject actually ready to publish right now, and if not, what exact thing is still in the way?

Current official Resilio docs make this seam concrete.
They still keep readiness truth split across change-detection FAQ prose, delay-file instructions, locked-file troubleshooting, and touch-file repair notes.
That is useful truth.
It should not remain page archaeology.

## Core decision

AnonSync must expose one first-class **Publication readiness** page for any subject or artifact whose local mutation can be delayed, blocked, or manually repaired before publication.

The page exists to answer five things in one place:

1. whether this item is publish-ready now
2. which readiness basis made that verdict true
3. whether delay, lock, degraded detection, or missing proof is blocking publication
4. what the next honest action is
5. what chronology risk a manual repair would introduce

## Fixed page order

1. **Current readiness verdict**
2. **Readiness basis**
3. **Active blockers**
4. **Commit timing and release window**
5. **Manual-repair review**
6. **Action matrix**
7. **Receipts and recent transitions**

### 1) Current readiness verdict

Show:

- `publication_readiness_page_id`
- seat and artifact in scope
- current `readiness_verdict` (`ready-now`, `waiting-for-delay`, `locked-by-writer`, `detection-degraded`, `needs-proof`, `publishing`, `unknown`)
- strongest honest summary
- last evaluated time

The operator must be able to answer:

> is this genuinely ready right now?

### 2) Readiness basis

Show the evidence stack that produced the verdict:

- last observed local mutation time
- last detection source (`filesystem-notification`, `rescan`, `manual-mark`, `imported-state`)
- current detection confidence
- whether a file-class delay applies
- whether lock evidence is present
- whether publication is waiting on queue admission or transfer class

The page must keep **basis** visible beside **verdict**.
A colored status chip alone is not enough.

### 3) Active blockers

List each blocker with:

- blocker class (`delay-window`, `active-lock`, `detection-gap`, `no-full-source`, `queue-deferred`, `manual-proof-needed`)
- strongest evidence
- whether the blocker is local-only or remote-dependent
- what would clear it naturally
- what manual action can clear it sooner

### 4) Commit timing and release window

Show:

- earliest eligible publication time
- whether further mutations extend the window
- whether the item is still changing
- whether current state came from inherited policy, subject override, or temporary hold
- whether restart, rescan, or merely waiting would change the verdict

### 5) Manual-repair review

If the likely next action is a manual repair, show:

- why the system believes publication evidence is incomplete
- whether `touch`, rescan, reopen-writer, or wait is the least-distorting repair
- whether any repair would assert newer chronology rather than merely rediscover current bytes
- what other peers would observe if the repair is applied now

### 6) Action matrix

Possible actions include:

- `Wait for natural release`
- `Open authoring delay`
- `Open lock investigation`
- `Run rescan`
- `Open touch repair`
- `Publish now with review`

Each action row must show:

- scope touched
- expected verdict change
- restart requirement if any
- chronology risk
- expected receipt

### 7) Receipts and recent transitions

Show durable rows for:

- verdict transitions
- delay expiration
- lock clearance
- rescan-triggered readiness changes
- manual repair applications
- forced publish decisions

## Public object

### Publication readiness page

Fields:

- `publication_readiness_page_id`
- `seat_ref`
- `artifact_ref`
- `readiness_verdict`
- `basis_rows[]`
- `blocker_rows[]`
- `timing_window`
- `manual_repair_review`
- `safe_next_actions[]`
- `receipt_rows[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. artifact
2. readiness verdict
3. strongest blocker or basis
4. next honest action
5. chronology risk chip

Example:

```text
budget.xlsx     waiting-for-delay     office-writer policy window still active     wait 00:00:07     low chronology risk
```

## Non-goals

This page does **not** replace deep transfer debugging or long-form conflict adjudication.
It proves only **whether this local change is ready to publish, what currently blocks it, and what repair is least misleading**.
