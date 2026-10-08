# Approval memory, scope recall, and one-time trust interface spec

## Purpose

The archive already had pending-share and seat-approval language.
What it still lacked was one stricter contract for a question current sync tools still leave fuzzy:

> when I approve one arrival or one peer once, what future arrivals does that approval silently widen, across which seats, and how do I later narrow or revoke that remembered trust without rebuilding everything?

Current Resilio docs make this seam concrete.
Their current linking guide still says that once a remote user approves one of your devices, they can choose to automatically approve all your linked devices for future sharing.
Their current folder-management docs also still say that a previously approved sharer can cause a pending folder to connect automatically once one of that user's devices is online.

That means approval is not only a one-time event.
It can become remembered trust with future-arrival consequences.

## Core decision

AnonSync must split **one-time approval** from **remembered trust**.
No approval affordance may silently widen into future admission unless the operator reviews and accepts the broader scope.

Every approval surface must answer three questions explicitly:

- what is being approved right now
- whether this creates remembered trust for future arrivals
- what later action revokes or narrows that remembered trust

## Why this matters

Current Resilio behavior still spreads the answer across several pages:

- approval can be granted from any linked seat that currently hosts the subject
- approval can be remembered across all linked devices for future sharing
- a later pending folder may auto-connect when one remembered approver comes online

That is convenient.
It is also exactly the kind of trust broadening AnonSync should force into the open.

AnonSync should therefore hold one stronger rule:

> remembered trust is a first-class object with visible scope, expiry posture, and recall controls.

## Fixed review order

Every approval or trust-widening event should render the same sections in the same order:

1. **Requested trust now**
2. **Remembered scope**
3. **Future-arrival consequences**
4. **Recall / narrowing actions**
5. **Trust receipt**

### 1) Requested trust now

Show:

- requesting peer or constellation
- subject being requested (`share`, `offer`, `seat link`, `future-arrival policy`, `other`)
- requested capability (`see`, `fetch`, `write`, `seed`, `govern`, `other`)
- whether the decision is local to this seat or applies constellation-wide

### 2) Remembered scope

Show one explicit scope choice:

- `this request only`
- `this subject only`
- `this issuer for future arrivals on this seat`
- `this issuer for future arrivals across this constellation`
- `custom reviewed scope`

If the surface cannot support remembered trust on the current seat, it must say so plainly.

### 3) Future-arrival consequences

Show:

- whether future arrivals may auto-appear
- whether future arrivals may auto-bind or only auto-enter inbox
- which seats will honor the remembered trust
- whether online presence of one remembered issuer is enough to trigger auto-arrival

The operator must be able to answer:

> what exactly will happen later that would not have happened if I approved only this request?

### 4) Recall / narrowing actions

Allow:

- revoke remembered trust entirely
- narrow remembered trust to one subject or one seat
- force future arrivals back to inbox-only
- expire trust after time or after first use
- export current remembered-trust ledger

### 5) Trust receipt

The receipt must preserve:

- decision time
- acting seat and actor
- scope chosen
- future-arrival consequences shown
- recall or narrowing actions later taken

## Main surface

Every seat should expose one **Remembered trust** page with fixed rows:

- issuer / fingerprint
- current scope
- subjects covered
- future-arrival posture
- last use
- expiry / recall controls

No inline checkbox should be the only home of this meaning.

## Command surface

The command model should expose verbs like:

- `approve --once`
- `approve --remember subject`
- `approve --remember seat`
- `trust list`
- `trust narrow`
- `trust revoke`
- `trust receipt show`

## Acceptance criteria

This spec is satisfied when:

- one-time approval and remembered trust are never conflated
- future auto-arrival is never enabled by implication alone
- recalled trust is visible as recalled, not silently missing
- operators can explain why an arrival auto-entered instead of landing in inbox
