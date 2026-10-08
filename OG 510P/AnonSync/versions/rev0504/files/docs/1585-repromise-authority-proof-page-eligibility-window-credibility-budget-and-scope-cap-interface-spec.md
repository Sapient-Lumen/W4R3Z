# Re-promise authority proof page: eligibility window, credibility budget, and scope cap interface spec

## Purpose

After issuance review, the operator needs one proof page that states:

> exactly why this actor may publish this class of promise now, for what scope, during what window, with what credibility budget, and with what blocked stronger sentence still preserved?

## Core decision

AnonSync must produce one **Re-promise authority proof** whenever any promise authority is restored, narrowed, co-signed, suspended, or blocked after recovery review.

## Fixed page order

1. **Authority verdict header**
2. **Eligibility-window card**
3. **Credibility-budget card**
4. **Scope-cap and signer proof card**
5. **Blocked stronger sentence card**

### 1) Authority verdict header

Show:

- authority verdict id
- linked authority object id
- linked issuance review id
- verdict class
- strongest allowed promise class
- allowed publisher class
- required signer class
- allowed scope class
- eligibility window
- current confidence in authority verdict

Supported `authority_verdict_class` values:

- `restored-full-authority`
- `restored-under-probation`
- `restored-for-narrowed-scope`
- `restored-with-co-sign`
- `target-only-restored`
- `blocked`
- `suspended`

### 2) Eligibility-window card

Required rows:

- start event for authority window
- expiry event or condition
- whether authority expires by time, event, or both
- whether silence weakens authority
- whether fresh accepted delivery is required to keep authority
- whether any live dispute shortens the window

Supported `eligibility_window_class` values:

- `single-publication-only`
- `time-boxed`
- `until-next-miss-or-dispute`
- `until-clean-delivery-count`
- `manual-revocation-only`
- `not-open`

Hard rule:

`restored` is invalid without saying whether that restoration is permanent, time-boxed, or single-use.

### 3) Credibility-budget card

Required rows:

- starting budget basis
- penalties applied for misses or repeat failures
- credits earned for accepted recoveries or clean deliveries
- unresolved debt still consuming budget
- current budget state
- next event that would increase budget
- next event that would exhaust budget

Supported `credibility_budget_grade` values:

- `surplus`
- `adequate`
- `thin`
- `critical`
- `depleted`

Hard rule:

Budget may improve only through named events.
It may not quietly refill through operator optimism.

### 4) Scope-cap and signer proof card

Required rows:

- maximum allowed scope now
- strongest blocked scope now
- allowed promise class for that scope
- required signer set
- whether external audience publication is allowed
- whether the result is internal-only
- strongest published sentence allowed now

Hard rule:

This card must preserve the difference between `can promise something` and `can promise the original thing to the original audience`.

### 5) Blocked stronger sentence card

Show:

- next stronger sentence requested but blocked
- exact blocker facts
- exact facts needed to unblock it
- whether the block is policy, evidence, or trust based
- whether a human override exists

Supported `blocked_sentence_basis` values:

- `policy-cap`
- `trust-deficit`
- `scope-not-restored`
- `repeat-failure-history`
- `evidence-gap`
- `open-dispute`
- `version-or-world-instability`
