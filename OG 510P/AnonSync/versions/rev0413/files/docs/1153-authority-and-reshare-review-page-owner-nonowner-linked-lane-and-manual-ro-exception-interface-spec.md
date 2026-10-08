# Authority and re-share review page: Owner, non-owner, linked lane, and manual RO exception interface spec

## Purpose

This page exists whenever the operator needs to answer:

> who can author changes here, who can delegate onward access, what does linked-device membership silently grant, and when does a desired low-authority outcome require leaving the linked lane entirely?

## When this page must appear

Trigger this page for:

- sharing a subject onward
- changing or reviewing authority lanes
- deciding whether linked devices should receive a subject automatically
- attempting to create a read-only linked-device outcome
- evaluating encrypted-derivative propagation rights

## Fixed page order

1. authority claim header
2. lane comparison card
3. linked-lane default card
4. manual exception card
5. receipt/export rail

### 1) Authority claim header

Show:

- subject family
- current lane (`ro`, `rw`, `owner`, `encrypted-derivative`, `unknown`)
- requested lane or exception
- strongest safe sentence
- stronger rejected sentence

### 2) Lane comparison card

Render rows for:

- may edit shared truth
- may invite or re-share onward
- may change permissions later
- may only seed ciphertext / cannot decrypt
- local divergence behavior class if the lane is non-authoritative

### 3) Linked-lane default card

Show explicitly:

- whether linked-device arrival defaults to owner-lane semantics
- whether all linked devices act as Owners for this family
- whether this family supports a native RO linked-device lane
- whether linked devices merely choose mode (`Disconnected`, `Selective`, `Synced`) while authority stays owner-default

### 4) Manual exception card

If a desired outcome requires leaving linked auto-arrival, publish:

- `manual Standard RO key required`
- `disconnect linked arrival first`
- `manual path choice required`
- `subject now lives in a different governance family than the linked-source default`

### 5) Receipt/export rail

Offer:

- `Emit subject architecture lineage receipt`
- `Open subject architecture contract sheet`
- `Open architecture migration watch`

## Rules

### Rule 1 — write power and delegation power may not collapse

A peer that can write is not automatically a peer that can delegate.

### Rule 2 — linked-device arrival must publish its hidden authority default

Mode choice alone is not enough if authority defaults to owner-lane.

### Rule 3 — exceptions must name the family jump

If a real RO result requires a Standard-key exception, the page must say that the exception leaves the default linked Advanced lane.
