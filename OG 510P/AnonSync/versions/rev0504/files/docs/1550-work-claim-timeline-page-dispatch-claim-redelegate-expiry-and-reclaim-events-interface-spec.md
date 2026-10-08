# Work claim timeline page: dispatch, claim, redelegate, expiry, and reclaim events interface spec

## Purpose

Custody truth changes over time.
The timeline page must answer:

> when was the work dispatched, when was custody requested, when was it accepted or started, and when did return, expiry, redelegation, or reclaim change who owned the next move?

## Core timeline rule

AnonSync must treat custody changes as first-class events, not as comments tucked inside the work item.

## Fixed event order

1. **Dispatch event**
2. **Claim-request event**
3. **Acceptance or decline event**
4. **Start or watch-engaged event**
5. **Renewal, redelegation, or blocker event**
6. **Expiry, return, or reclaim event**
7. **Aftermath event**

## Supported event types

- `dispatched-now`
- `claim-request-sent`
- `claim-request-delivered`
- `acknowledged`
- `accepted`
- `declined`
- `started`
- `watch-engaged`
- `renewed`
- `redelegated`
- `split-custody-opened`
- `returned`
- `expired`
- `reclaimed`
- `superseded`
- `closed-after-return`

## Required fields per event

- timestamp
- acting party
- evidence basis
- resulting custody state
- next expiry boundary if any
- what stronger sentence became allowed or blocked

## Timeline obligations

### A) Dispatch must stay visible even after several handoffs

The page may not hide the original dispatch winner once re-delegation starts.
Later readers must still be able to see how the work entered custody land at all.

### B) Silence is represented only through explicit expiry or missed-deadline events

The product may not let missing events imply successful continuation.
If nothing happened and the clock ran out, the timeline must show an expiry or missed-commitment event.

### C) Re-delegation must preserve both sides of the handoff

Every redelegation event must show:

- old custodian
- new custodian
- whether the old custodian retained residual duty
- whether the new custodian accepted immediately or remains pending

### D) Return and reclaim are not synonyms

`returned` means the current custodian deliberately gave work back or declined it.
`reclaimed` means the system or owner pulled work back because the live claim expired or had to be revoked.
The timeline must keep those routes separate.

### E) Partial progress must survive custody collapse

If an item returns after some work happened, the timeline must preserve that partial-progress event before the return.

## Footer sentence

Render exactly one line:

**Current custody consequence:** followed by the next live ownerless risk or next live custodian.

Hard rule:

A timeline that ends with `reclaimed` or `returned` must still say what re-entered risk exists now.
