# Delivery commitment proof page: promise window, risk budget, and surviving sentence interface spec

## Purpose

This page is the durable proof that a commitment was actually publishable at the time it was made, what risks it absorbed, and what weaker sentence survives later if conditions fail.

## Fixed page order

1. **Proof header**
2. **Promise-window proof**
3. **Risk-budget proof**
4. **Surviving-sentence proof**
5. **Proof ceiling**

### 1) Proof header

Show:

- proof id
- linked commitment id
- linked forecast id
- commitment class proven
- proof freshness window
- proof owner
- proof audience
- current proof status

Supported `proof_status` values:

- `provisional`
- `published`
- `under-renegotiation`
- `downgraded`
- `breached`
- `superseded`
- `withdrawn`

### 2) Promise-window proof

Required rows:

- promised earliest finish
- promised latest finish
- source of the window
- whether the window is absolute or relative
- explicit room for tolerated slip
- named conditions attached to the window

Hard rule:

The proof may not present a promise window without also preserving the condition basis that made it truthful at publication time.

### 3) Risk-budget proof

Required rows:

- total named risk budget
- risks already absorbed into the promise
- risks excluded from the promise
- current leading risk to window survival
- event that burns the remaining budget fastest
- whether the risk budget is still positive

Supported `risk_budget_posture` values:

- `ample`
- `tight`
- `fragile`
- `burned-through`
- `unknown`

Hard rule:

A commitment may not quietly spend through its entire risk budget while still speaking in the original promise voice.

### 4) Surviving-sentence proof

Required rows:

- strongest sentence that survives if all conditions hold
- strongest sentence that survives after widening only
- strongest sentence that survives after miss
- strongest sentence that survives after breach
- whether the audience must be re-notified at each downgrade

Hard rule:

The proof must preserve the weaker surviving sentence before failure occurs.
That sentence may not be invented after the promise collapses.

### 5) Proof ceiling

Required rows:

- strongest allowed public statement now
- strongest blocked stronger statement
- exact fact blocking the stronger statement
- next event that would raise the ceiling
- next event that would lower the ceiling

Hard rule:

`we promised` is not automatically the strongest surviving sentence once invalidators turn active.
