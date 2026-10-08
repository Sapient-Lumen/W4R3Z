# Action authority proof page: issued mandate, acceptance, execution, and revocation interface spec

## Purpose

Operators need one durable proof object for the harder question:

> what exact mandate was issued, who accepted it, what did they actually do, and what later revoked or superseded that authority?

## Core decision

AnonSync must preserve mandate truth as a lineage-bearing proof object rather than scattering it across tickets, chat, and memory.

## Fixed page order

1. **Mandate proof header**
2. **Authority issuance card**
3. **Acceptance-and-custody card**
4. **Execution-and-proof card**
5. **Revocation-and-aftereffects card**
6. **Decision footer**

### 1) Mandate proof header

Show:

- action mandate id
- live link to source reliance charter
- live link to source certificate / case / campaign
- current mandate state
- active strongest safe execution sentence
- blocked stronger sentence

Supported `current_mandate_state` values:

- `issued-not-yet-received`
- `received-not-accepted`
- `accepted-not-started`
- `executing`
- `executed-awaiting-proof`
- `executed-proved`
- `revoked-before-start`
- `revoked-mid-flight`
- `superseded`
- `expired`

### 2) Authority issuance card

Required rows:

- issuer
- issuance basis
- authority class granted
- scope granted
- explicit exclusions
- expiry / cancel condition

Hard rule:

A downstream action proof is incomplete unless the original authority boundary is preserved alongside the execution story.

### 3) Acceptance-and-custody card

Required rows:

- delivery state
- acceptance state
- accepted by
- delegated onward
- onward authority basis
- missing acknowledgement risk

Supported `acceptance_state` values:

- `not-required`
- `receipt-only`
- `accepted-duty`
- `counter-signed`
- `rejected`
- `timed-out`

Hard rule:

`sent` is weaker than `received`, and `received` is weaker than `accepted duty`.
A mandate cannot overclaim execution authority if custody was never accepted.

### 4) Execution-and-proof card

Required rows:

- execution status
- steps attempted
- proof attached
- outcome class
- residual debt created
- follow-on recheck due

Supported `outcome_class` values:

- `not-started`
- `attempted-no-change`
- `partial-execution`
- `bounded-success`
- `success-with-delta`
- `blocked`
- `stopped-on-recall`

Hard rule:

Execution proof must stay weaker than source truth when the result leaves residual delta, excluded scope, or unclosed reconciliation work.

### 5) Revocation-and-aftereffects card

Required rows:

- superseded by mandate id
- revocation event
- time of revocation
- queued work still exposed
- in-flight stop class used
- surviving weaker sentence after revocation

Hard rule:

Revocation must explain not only that the mandate died, but what surviving partial work, stale expectation, or weakened sentence remains afterward.

### 6) Decision footer

Use:

> Mandate [id] granted [authority] to [recipient], accepted at [state], executed to [outcome], and is now [current state]. Surviving weaker sentence: [sentence].
