# Evidence synthesis lineage receipt page: packet set, weighted basis, and blocked stronger sentences interface spec

## Purpose

Once a multi-packet reading has produced a merged sentence, later operators need one durable receipt that answers:

> exactly which packet set produced this claim, what weight basis was used, what conflicts remained open, and what stronger sentence stayed blocked?

## Core decision

AnonSync must issue one first-class **Evidence synthesis lineage receipt** for every integrated claim proof that can influence later dispute, escalation, precedent, certification, or reliance work.

## Fixed page order

1. **Receipt header**
2. **Packet-set snapshot**
3. **Weighted-basis snapshot**
4. **Conflict-and-gap snapshot**
5. **Claim-envelope snapshot**
6. **Successor-proof hook**
7. **Receipt sentence**

### 1) Receipt header

Show:

- receipt id
- source synthesis id
- source proof id
- issued time
- receipt owner
- current receipt posture

Supported `receipt_posture` values:

- `active-reference`
- `reference-with-reservations`
- `superseded-reference`
- `expired-reference`
- `recalled-reference`

### 2) Packet-set snapshot

Required rows:

- active source ids at issuance
- held-out source ids at issuance
- superseded source ids already known
- source relation summary

Hard rule:

The receipt must preserve the actual packet set used at issuance even if later packets arrive.

### 3) Weighted-basis snapshot

Required rows:

- lead-basis sources
- corroborating sources
- duplicate clusters not counted twice
- discounted sources and reasons
- stale sources still tolerated and why

Hard rule:

A later reader must be able to tell why the issued claim did not simply track source count.

### 4) Conflict-and-gap snapshot

Required rows:

- unresolved conflict ids
- missing independence still desired
- missing source class still desired
- blocked stronger sentences

Hard rule:

If the issued claim was conflict-capped, the receipt must preserve the capped alternative sentence in plain language.

### 5) Claim-envelope snapshot

Required rows:

- exact issued integrated sentence
- scope covered
- worlds covered
- excluded scope
- freshness horizon
- downgrade or recall triggers

### 6) Successor-proof hook

Required rows:

- next proof id if any
- what changed
- whether the new proof strengthened, weakened, narrowed, or only refreshed the old sentence

Hard rule:

The successor hook must preserve continuity without erasing the older synthesis basis.

### 7) Receipt sentence

Render exactly three lines:

- **This is the integrated sentence that was actually issued**
- **This is the weighted packet basis that made it safe**
- **This is the stronger sentence that remained blocked and why**
