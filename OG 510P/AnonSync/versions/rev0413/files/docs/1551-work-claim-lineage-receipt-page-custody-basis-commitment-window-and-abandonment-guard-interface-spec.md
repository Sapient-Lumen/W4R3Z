# Work claim lineage receipt page: custody basis, commitment window, and abandonment guard interface spec

## Purpose

Later operators need one small durable artifact that answers:

> who had custody, why we believed that, how long the commitment lasted, and what abandonment guard or reclaim route protected the work when custody weakened?

## Receipt fields

The **Work claim lineage receipt** must contain exactly these fields in this order:

1. claim id
2. linked portfolio id
3. dispatched work id
4. final custody status
5. strongest evidence for custody
6. current or last named custodian
7. commitment-window class
8. expiry or return route
9. abandonment-guard status
10. surviving weaker sentence
11. blocked stronger sentence

## Supported `final_custody_status` values

- `never-claimed`
- `claimed`
- `claimed-and-started`
- `redelegated`
- `returned`
- `expired`
- `reclaimed`
- `superseded-before-claim`
- `closed-after-safe-return`

## Supported `abandonment_guard_status` values

- `healthy`
- `aging`
- `near-expiry`
- `expired-and-visible`
- `reclaimed-to-portfolio`
- `unknown-because-review-missed`

## Receipt rules

### Rule 1: `selected-now` may not appear as a custody status

Dispatch belongs to the portfolio receipt.
This receipt starts only at work claim truth.

### Rule 2: the strongest evidence must be public enough for later review

Examples:

- explicit acceptance record
- explicit start record
- explicit return record
- explicit reclaim event

`Notification existed` is never enough.

### Rule 3: surviving weaker sentence is mandatory

Examples:

- `The work is still real but currently unowned.`
- `The work was accepted once but the claim expired and returned to the portfolio.`
- `Execution began, then custody moved to a successor custodian.`

### Rule 4: blocked stronger sentence is mandatory

Examples:

- `This work is continuously owned.`
- `The assigned person still has it.`
- `This dispatch is safely covered.`
- `No abandonment risk remains.`

### Rule 5: abandonment guard must survive success-looking states

A receipt may show useful progress and still preserve `aging` or `near-expiry` if the current claim is still at risk.

## Display note

This receipt should be short enough to travel with portfolio, mandate, and fulfillment receipts without losing the custody story.
