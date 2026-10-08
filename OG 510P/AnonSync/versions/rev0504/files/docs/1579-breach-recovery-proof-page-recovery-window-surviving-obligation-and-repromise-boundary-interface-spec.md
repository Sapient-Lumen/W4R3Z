# Breach recovery proof page: recovery window, surviving obligation, and re-promise boundary interface spec

## Purpose

This page is the durable proof that a recovery statement was actually publishable, what obligation survived the failed promise, and what exact boundary still blocks or allows a fresh commitment.

## Fixed page order

1. **Proof header**
2. **Surviving-obligation proof**
3. **Recovery-window proof**
4. **Trust-repair proof**
5. **Proof ceiling**

### 1) Proof header

Show:

- proof id
- linked recovery id
- linked breached commitment id
- current recovery class proven
- proof freshness window
- proof owner
- proof audience
- current proof status

Supported `proof_status` values:

- `provisional`
- `published`
- `under-repair`
- `re-promise-blocked`
- `re-promise-authorized`
- `closed`
- `superseded`

### 2) Surviving-obligation proof

Required rows:

- exact breached sentence
- exact surviving obligation now
- whether full original scope survived
- abandoned scope if any
- whether substitute scope was accepted
- whether the audience was notified of the downgrade

Hard rule:

The proof must preserve the duty that survived the breach.
`Recovery underway` is invalid unless the surviving obligation is named.

### 3) Recovery-window proof

Required rows:

- current recovery class
- current recovery window or checkpoint rule
- what facts justify that window
- what is explicitly not promised
- whether the window is contingent on external unblockers
- event that collapses the recovery window fastest

Hard rule:

A recovery window may not masquerade as a fresh full-scope commitment.

### 4) Trust-repair proof

Required rows:

- current trust-repair status
- strongest fact supporting requalification
- strongest fact still blocking requalification
- whether new promise authority is open
- whether a new promise requires a new id
- weaker sentence that survives if trust repair fails

Hard rule:

`Eligible for new promise` must be blocked until the proof says more than `motion resumed`.

### 5) Proof ceiling

Required rows:

- strongest allowed public statement now
- strongest blocked stronger statement
- exact fact blocking the stronger statement
- next event that would raise the ceiling
- next event that would lower the ceiling

Hard rule:

A proof may not jump from `breach open` to `trust repaired` without preserving the intermediate recovery posture.
