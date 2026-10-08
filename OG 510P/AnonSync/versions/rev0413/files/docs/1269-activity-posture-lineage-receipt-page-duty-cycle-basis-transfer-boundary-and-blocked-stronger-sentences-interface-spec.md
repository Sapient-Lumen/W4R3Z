# Activity-posture lineage receipt page: duty-cycle basis, transfer boundary, and blocked stronger sentences interface spec

## Purpose

The archive repeatedly chooses receipts whenever a user may later need to prove not just *what happened*, but *what the product was willing to claim at the time*.
This receipt is the durable output for the activity-posture family.

## Core decision

AnonSync must emit one **Activity-posture lineage receipt** whenever a user-visible activity sentence depends on pause, schedule, rate limit, sleep, battery, or network policy.

## Receipt layout

1. **Receipt header**
2. **Activity basis block**
3. **Residual-work block**
4. **Budget / scope block**
5. **Blocked stronger sentences block**

### 1) Receipt header

Show:

- `activity_receipt_id`
- subject ref
- issued-at time
- receipt freshness horizon
- strongest safe sentence
- blocked stronger sentence

### 2) Activity basis block

Must preserve:

- governing cause class
- visibility state
- detection mode
- upload allowance
- download allowance
- expected wake/resume basis if known

### 3) Residual-work block

Must preserve whether these were still allowed when the receipt was issued:

- indexing / rescan
- delete propagation
- zero-byte / metadata movement
- upload service to other peers
- peer discovery / announcement

This block exists so that future readers do not misread a historical `paused` or `offline` sentence as `nothing could happen`.

### 4) Budget / scope block

Must preserve:

- active upload cap
- active download cap
- whether caps applied to Internet only
- whether LAN remained exempt
- whether zero-rate came from manual pause or scheduler rule

### 5) Blocked stronger sentences block

Each receipt must preserve at least one blocked stronger sentence, for example:

- `Nothing could move during this interval.`
- `This device was continuously visible to peers.`
- `The stated cap governed all network paths.`
- `This was an operator pause rather than a battery or network policy stop.`

## Hard rules

- receipts may never serialize `paused` without its reviewed meaning
- receipts must preserve residual work, not just blocked work
- receipts must state whether the strongest sentence depended on runtime observation or only configuration evidence
- receipts must remain readable without cross-referencing the full sheet
