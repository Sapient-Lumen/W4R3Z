# Recovery locus receipt page: witness seat, restore shape, and proof limits interface spec

## Purpose

This page defines the durable receipt emitted after any recovery action whose truth depended on witness locality.

The receipt exists to answer a later reader's question:

> which seat actually supplied the recovered bytes, what kind of recovery was performed, and what could the product honestly prove versus merely infer?

## Core decision

Every distributed restore or rollback action must emit one first-class **Recovery locus receipt**.
That receipt records:

- witness seat used
- candidate source and type
- recovery host used
- achieved recovery shape
- propagation scope
- authorship / chronology proof limits
- residual risks or stronger blocked claims

## Receipt sections

The receipt always renders the same sections in the same order:

1. receipt strip
2. witness-source card
3. recovery-host card
4. achieved-scope card
5. proof-limit card
6. follow-up card

### 1) Receipt strip

Show:

- receipt ID
- subject path
- chosen candidate
- witness seat
- achieved recovery shape (`exported`, `restored-local`, `restored-side-by-side`, `replayed-live`, `blocked`)
- strongest safe summary sentence

### 2) Witness-source card

Show:

- where the prior bytes came from
- why that seat held them
- retention/access facts at apply time
- whether the witness was plaintext, ciphertext-only, or metadata-only

### 3) Recovery-host card

Show:

- which host executed the recovery action
- whether that host was also the witness seat
- engine/watch liveness state at apply time
- whether replay depended on immediate observation or only produced an export

### 4) Achieved-scope card

Show:

- whether the result stayed local, affected the live subject, or propagated to peers
- whether side-by-side preservation occurred
- whether the result is best understood as inspection, recovery, or distributed mutation

### 5) Proof-limit card

Show:

- actor attribution quality
- chronology confidence
- forbidden stronger claims
- remaining residue or unresolved gaps

### 6) Follow-up card

Show the strongest next honest step, for example:

- `Share receipt only, no actor claim`
- `Complete History join before incident statement`
- `Observe replay propagation`
- `Preserve exported bytes separately`
- `Rotate to stronger recovery lane`

## Non-negotiable rules

### Rule 1 — receipts must name witness seat

A later reader must not have to infer where recovered bytes came from.

### Rule 2 — receipts must distinguish executed host from witness source

Those may be the same host, but the receipt must not assume it.

### Rule 3 — proof ceilings belong in the receipt itself

The durable record must preserve not only what succeeded, but also what the product refused to claim.

## Honest outputs

The receipt may say:

- `Recovered side-by-side from remote desktop witness; actor attribution remained partial.`
- `Export completed from Android-hosted witness bytes; no share-wide replay was attempted.`
- `Live replay was blocked because the only remaining witness lacked a safe recovery surface.`
