# Attestation review page: live check, synthetic drill, passive witness, and claim ceiling interface spec

## Purpose

Once a control has an attestation contract, the operator still needs one decision page for the next question:

> what is the strongest honest way to verify this control now without over-claiming what the evidence proves?

## Core decision

AnonSync must expose one first-class **Attestation review** that compares witness options and selects the least-cost witness that can still justify the needed claim ceiling.

## Fixed page order

1. **Review header**
2. **Witness options table**
3. **Claim-ceiling comparison card**
4. **Selected attestation plan**
5. **Trust downgrade card**
6. **Approval sentence**

### 1) Review header

Show:

- control id
- current trust state
- target sentence to preserve or regain
- freshness deadline
- urgency class
- selected witness plan status

Supported `urgency_class` values:

- `routine-rereview`
- `drift-triggered`
- `pre-rollout-widening`
- `post-version-change`
- `post-world-fork`
- `post-near-miss`

### 2) Witness options table

Each witness row must include:

- witness class
- direct cost
- disruption cost
- proof strength
- world coverage
- stale-risk reduction
- blocked stronger sentence after pass

Supported `witness_class` values:

- `live-read-only-check`
- `paired-surface-consistency-check`
- `synthetic-drill`
- `passive-window-renewal`
- `historical-block-event`
- `manual-audit-only`

Hard rule:

`manual-audit-only` may never be the winning witness if an automated or reproducible witness is available at the same claim ceiling.

### 3) Claim-ceiling comparison card

For each available witness, publish what it can safely support:

- `configured-visible`
- `applied-probably-effective`
- `trusted-within-current-scope`
- `trusted-detective-only`
- `trusted-after-rehearsal`
- `still-blocked-from-preventive-claim`

Hard rule:

A passive window may renew freshness but may not upgrade a detective control into a preventive control by itself.

### 4) Selected attestation plan

Required rows:

- chosen witness class
- why cheaper witnesses were insufficient
- scope of the check or drill
- preconditions
- abort conditions
- resulting claim ceiling if pass succeeds
- resulting trust state if pass fails or is skipped

Supported `resulting_trust_state_if_fail` values:

- `stale-needs-rereview`
- `trust-withdrawn`
- `configured-only`
- `detective-only-untrusted-preventive`

### 5) Trust downgrade card

This section is mandatory whenever:

- freshness has expired
- a higher-strength witness is required but not run
- the environment changed materially
- a rehearsal was due but missed

Required rows:

- downgrade reason
- withdrawn sentence
- surviving weaker sentence
- next acceptable witness
- max grace period if any

### 6) Approval sentence

The page ends with one sentence in this shape:

> `To preserve <claim ceiling> for control <id>, we require <witness class>; weaker evidence would only justify <weaker sentence>.`
