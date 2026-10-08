# Claim acceptance review page: inform, request, accept, redelegate, and decline routes interface spec

## Purpose

The work claim contract sheet defines what custody would mean.
The next page must answer the live operational question:

> are we merely informing someone, requesting that they take custody, recording actual acceptance, re-delegating to another custodian, or declining and returning the work to the portfolio?

## Page promise

The **Claim acceptance review** page must be the place where the product decides whether custody is merely proposed, actually accepted, or visibly returned.

## Fixed page order

1. **Current route banner**
2. **Acceptance-difference card**
3. **Route table**
4. **Claim-expiry preview**
5. **Re-delegation review**
6. **Decline-and-return review**
7. **Blocked stronger sentence**

### 1) Current route banner

Show:

- current candidate route
- current requested custodian
- whether acknowledgement has landed
- whether actual start has landed
- current expiry pressure
- whether another route is still live

Supported `claim_route` values:

- `inform-only`
- `request-claim`
- `accept-claim`
- `commit-start`
- `re-delegate`
- `decline`
- `return-with-comment`
- `force-reclaim`

Hard rule:

The banner may not show `accepted` unless explicit acceptance evidence exists.
Notification delivery is insufficient.

### 2) Acceptance-difference card

This card must show one row for each of the following and whether it is currently true:

- person was selected
- notification was sent
- notification was received
- acknowledgement was received
- claim was explicitly accepted
- work actually started
- completion is already expected from this custodian

Hard rule:

The page must make `selected`, `notified`, `acknowledged`, `accepted`, and `started` visibly different.

### 3) Route table

Render a row for every still-available route.
Required fields:

- route name
- what new truth it creates
- what old truth it cancels
- what evidence is required
- what risk remains after choosing it
- whether it changes the expiry clock

Hard rule:

At least one non-winning route must remain visible unless the choice is mechanically forced.
Review pages are not allowed to pretend inevitability when real choice remains.

### 4) Claim-expiry preview

Required rows:

- current expiry deadline
- whether grace exists
- whether renewal is allowed
- what event pauses the expiry clock
- what event does not pause the expiry clock
- what reclaim route will fire

Hard rule:

A read receipt or passive observer presence may not pause expiry unless the rule explicitly says it does.

### 5) Re-delegation review

Required rows:

- proposed new custodian
- authority basis for re-delegation
- reason re-delegation is needed
- residual duty left with old custodian
- whether the new custodian must accept afresh
- what survives if the new custodian also declines

Hard rule:

Re-delegation must open a fresh acceptance question unless the system has an explicit standing delegation rule.

### 6) Decline-and-return review

Required rows:

- reason for decline
- whether the item returns immediately or after review
- whether dispatch order must be recomputed
- whether the same custodian may be asked again
- whether the decline weakens any outward claim
- what new risk becomes visible

Hard rule:

Decline is not failure by default.
But the page must still name what risk re-enters the portfolio.

### 7) Blocked stronger sentence

Render one sentence beginning:

**Still not allowed to say:**

Examples:

- `This work is owned` when it was only announced.
- `This team has it` when no named custodian accepted.
- `Execution is underway` when acknowledgement landed but start did not.
- `The handoff is complete` when re-delegation is proposed but not accepted.

Hard rule:

Every review must block one stronger sentence explicitly.
