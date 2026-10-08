# Delta-aging review page: restore exact, promote successor, or reopen interface spec

## Purpose

After the archive learned how to register accepted return debt, it still needed one review page that answers the harder question:

> now that this changed return has aged for a while, should we restore exact parity, deliberately adopt the successor state, narrow the claim, or reopen because the debt is no longer honest?

## Core decision

AnonSync must expose one first-class **Delta-aging review** page whenever a tolerated return delta reaches its rereview point, worsens, or becomes a candidate for permanent adoption.

## Fixed page order

1. **Review header**
2. **State comparison panel**
3. **Aging pressure panel**
4. **Decision ladder**
5. **Outcome proof preview**
6. **Review sentence**

### 1) Review header

Show:

- review id
- linked return-delta id
- owner
- age since acceptance
- expiry posture
- review trigger
- current safe sentence

Supported `review_trigger` values:

- `scheduled-rereview`
- `expiry-reached`
- `delta-worsened`
- `proof-arrived`
- `same-cause-near-miss`
- `same-cause-recurrence`
- `operator-requested`

### 2) State comparison panel

Compare four columns:

- pre-bypass intended state
- current active state
- exact-restore target
- candidate successor baseline

Hard rule:

The page must make visible whether the proposed successor is identical to the current active state or still requires additional cleanup before promotion.

### 3) Aging pressure panel

Required rows:

- operational benefit of keeping current state
- surprise cost of current mismatch
- hidden survivor risk
- proof depth available
- reversibility remaining
- claim damage if left unresolved

Supported `surprise_cost` values:

- `small-and-local`
- `operator-visible`
- `user-visible`
- `cross-subject-confusing`
- `compliance-or-policy-sensitive`

Supported `proof_depth_available` values:

- `weak-observation-only`
- `moderate-usage-history`
- `strong-targeted-proof`
- `strong-repeated-proof`

### 4) Decision ladder

Present exactly five mutually exclusive outcomes:

1. `restore-exact-now`
2. `keep-temporary-with-shorter-expiry`
3. `promote-current-state-to-successor-baseline`
4. `split-state-and-narrow-the-protected-claim`
5. `reopen-linked-case-or-control`

Hard rules:

- `promote current state` must require proof that the mismatch is intentional, understood, and not a hidden leftover.
- `keep temporary` must shorten or reaffirm expiry explicitly.
- `split state` is only valid when the operator can describe the narrower truth precisely.

### 5) Outcome proof preview

For each outcome show:

- proof required
- blocked sentence removed if outcome succeeds
- blocked sentence that still remains even after success
- rollback / undo class
- who must sign off

### 6) Review sentence

Format:

> `After [age since acceptance], the current [accepted_delta_class] state is reviewed as [decision]. The safe sentence remains [current safe sentence] until [proof / exact restore / promotion] completes.`

## Required interactions

### A) `Reaffirm temporary`

Requires new expiry and explicit reason why exact restore is still postponed.

### B) `Promote successor baseline`

Requires successor description, proof basis, and explicit retirement of the old baseline sentence.

### C) `Narrow claim`

Requires new weaker stable sentence and explicit does-not-mean statement.

### D) `Reopen`

Requires trigger and linked case/control/rollout target.

## Anti-goals

Do not:

- let time alone promote a successor
- let frequent use stand in for proof that the changed state is intentional and safe
- hide claim narrowing inside a healthy badge
- allow exact-restore and successor-promotion language to blur together

## Why this page exists

Because changed-but-working states age.
Some deserve exact restoration.
Some deserve deliberate successor promotion.
Some deserve reopen.
The product must own that choice instead of leaving it to memory and habit.
