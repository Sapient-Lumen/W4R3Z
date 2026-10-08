# Mandate timeline page: issue, acknowledgement, execution, supersession, and cancel events interface spec

## Purpose

Operators need one event timeline that answers:

> when did this instruction become real, when did someone accept it, when did work start, and when did later supersession or cancellation change what was still safe to do?

## Core decision

AnonSync must give action mandates the same event rigor as incidents, campaigns, and certificates.

## Timeline event classes

Supported event classes:

- `issued`
- `delivered`
- `read`
- `accepted-duty`
- `counter-signed`
- `execution-started`
- `checkpoint-passed`
- `checkpoint-blocked`
- `execution-paused`
- `execution-completed`
- `proof-uploaded`
- `superseded`
- `cancelled`
- `revocation-acknowledged`
- `stale-copy-discovered`
- `reopened`

## Fixed page order

1. **Timeline header**
2. **Live mandate lane**
3. **Recipient acknowledgement lane**
4. **Execution lane**
5. **Supersession / cancel lane**
6. **Decision footer**

### 1) Timeline header

Show:

- mandate id
- source reliance charter id
- current state
- first unsafe stale point
- next required event

### 2) Live mandate lane

Show all issuance and expiry transitions with:

- event time
- actor
- summary
- sentence that became newly safe
- stronger sentence still blocked

### 3) Recipient acknowledgement lane

Show:

- which recipients only received
- which recipients accepted duty
- which recipients counter-signed
- which recipients never acknowledged
- which recipients were later recalled successfully

Hard rule:

A timeline that hides non-acknowledging recipients is too optimistic for serious delegated work.

### 4) Execution lane

Show:

- start time
- critical checkpoints
- proof attachments
- stop/hold points
- final bounded outcome
- residual debt or follow-on requirement

### 5) Supersession / cancel lane

Show:

- superseding mandate ids
- recall or cancellation issue time
- recipients reached versus not reached
- stale-copy discovery events
- surviving safe fallback instruction

Hard rule:

Supersession is not complete just because a newer mandate exists.
The timeline must show whether holders of the older one were actually reached.

### 6) Decision footer

Use:

> Timeline shows mandate [id] became actionable at [time], was accepted by [scope], executed to [bounded result], and was later [superseded/cancelled] with [remaining stale risk].
