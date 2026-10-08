# Offer issuance, reissue, and audit surface interface spec

## Purpose

The archive already has an offer object model.
What it still lacked was a concrete sender-side answer to this question:

> if I am about to let someone else in, what exact surface tells me **what authority I am offering**, **how it is constrained**, and **whether I am reissuing the same thing or broadening it**?

This matters because current Resilio flows still teach that meaning through a mix of share dialog, key-vs-link-vs-QR differences, approval options, and separate help pages.
That is practical.
It is not the contract AnonSync should clone.

## Core decision

Every outward capability must originate from one explicit **offer composer** and remain inspectable through one durable **offer detail** page.
The surface must decide authority first and delivery encoding second.

The operator should never have to infer from `Copy link`, `Show QR`, or `Save file` whether they just created:

- equivalent access in another wrapper
- a broader role
- a different approval posture
- a reusable artifact instead of a one-time one
- a narrower reissue versus a truly new offer family

## The fixed composer order

Every non-trivial sender-side issuance flow should render the same sections in the same order:

1. **Subject and offered capability**
2. **Eligible redeemers**
3. **Approval, expiry, and redelegation policy**
4. **Receiver outcome hints**
5. **Delivery encoding**
6. **Resulting audit and reissue posture**

If the surface skips straight to delivery, it is already teaching the wrong model.

## 1) Subject and offered capability

Show:

- subject label and stable handle
- acting seat
- offer class (`share-access`, `observe`, `device-relationship`, `successor-handoff`, etc.)
- maximum role or capability set being offered
- whether the offer is visibility-only, mount-capable, authority-widening, or relationship-forming

The operator must be able to answer:

> what power is inside this offer before I care whether it becomes a file, URI, QR code, or clipboard string?

## 2) Eligible redeemers

Show:

- whether any peer may redeem
- whether one peer fingerprint or contact is pinned
- whether redemption is restricted to a constellation, trust class, or candidate successor
- whether this is for same-person convenience, another operator, or a bounded delegate

This prevents the common drift where a delivery artifact looks universally sharable even though the operator intended it for one known subject only.

## 3) Approval, expiry, and redelegation policy

Show:

- whether claim review is mandatory
- whether issuer approval is mandatory
- expiry window
- redemption budget
- whether equivalent redelegation is forbidden, narrowed, or explicitly allowed
- whether the offer is revoked automatically after first successful claim

This section should read like policy, not checkbox trivia.

## 4) Receiver outcome hints

Sender-side issuance should state what the receiver is expected to do locally:

- `visibility only`
- `local adoption expected`
- `path choice required`
- `local bind likely to need compare review`
- `no authority widening beyond local access`
- `relationship join only; no identity replacement`

This matters because a good sender surface should warn when the receiver will later face a non-trivial local decision.

## 5) Delivery encoding

Only after the above should the surface ask how to package the offer:

- file
- URI / local-web link
- QR
- clipboard string
- local handoff to another seat on the same machine

Changing encoding must not silently change the authority payload.
If the operator wants different authority, they should leave the delivery step and edit the offer itself.

## 6) Resulting audit and reissue posture

Before the issuer commits, the surface should say:

- whether this creates a brand-new offer or a reissue of an existing semantic offer
- whether the next surface will show one active offer with multiple encodings or several separate offers
- where later redemption receipts will appear
- whether revoking this offer revokes only future claims or also cancels still-pending delivery windows

This is the answer to:

> what durable thing will I be auditing after this convenience step is over?

## Reissue rules

Reissue is not the same thing as recreate.
The interface should distinguish these actions clearly:

### `Reissue same offer`

Use when authority, constraints, and eligible redeemers stay the same but encoding or expiry window needs refresh.

### `Narrow and reissue`

Use when delivery is being regenerated with less power, tighter peer pinning, shorter lifetime, or fewer uses.

### `Create broader sibling offer`

Use when the operator is intentionally widening role, redelegation, or redemption scope.
This should create a new offer identity, not silently overwrite the old one.

## Primary labels

Good primary actions include:

- `Create offer`
- `Reissue same offer`
- `Create narrower offer`
- `Create broader sibling offer`
- `Save encoding`

Poor labels include:

- `Share`
- `Copy`
- `Done`

when those labels are the only place where issuance semantics could have been learned.

## Offer detail page anatomy

The durable offer page should keep six areas visible:

1. **What this offer grants**
2. **Who may redeem it**
3. **Which constraints apply**
4. **Which encodings currently exist**
5. **Who already redeemed it**
6. **What revocation now would and would not change**

The issuer should not need to reopen the composer merely to answer what a previously sent artifact still means.

## Audit shelf rules

The workbench should include an `Offers` family that can answer:

- active offers nearing expiry
- one-time offers not yet redeemed
- offers redeemed more times than the operator expected
- offers reissued in multiple encodings
- revoked offers with surviving receipts

The point is to keep issuance visible as a governed surface rather than something that disappears into chat history or clipboard memory.

## Cross-projection rules

GUI, local web, TUI, and CLI may differ in density.
They must preserve:

- authority payload
- eligible redeemers
- approval / expiry / redelegation policy
- reissue versus recreate distinction
- audit / receipt destination

If one surface keeps these distinctions while another collapses them into `copy link`, the product no longer has one truthful issuance model.

## Result

A good issuance surface prevents five failures:

- delivery method standing in for authority semantics
- accidental widening during reissue
- one-time intent drifting into indefinitely reusable artifacts
- sender inability to audit what was actually sent later
- re-share convenience becoming a trust expansion the issuer never consciously reviewed

If the sender-side product still teaches `how to send` before it teaches `what is being sent`, AnonSync has not yet fixed the seam that current sync products leave exposed.


## Companion

- `253-shareable-artifact-carryforward-delta-ledger-and-refresh-notice-interface-spec.md`
