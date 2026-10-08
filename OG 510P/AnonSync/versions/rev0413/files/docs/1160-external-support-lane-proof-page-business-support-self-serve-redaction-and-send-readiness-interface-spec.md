# External support lane proof page: business support, self-serve, redaction, and send readiness interface spec

## Purpose

This page answers:

> who can actually receive this evidence from this product line right now, what route is admissible, and what stronger support sentence is still blocked?

The page exists because `Contact support` and `send logs` are not self-justifying phrases.

## Why this must be explicit

Current official Resilio docs still say Business has direct technical support while Sync v3 does not; v3 users are directed toward the forum and Help Center; payment or licensing questions use a separate web form; automatic feedback and manual attachment are different routes; and manual attachments above 20 MB need a different upload path.

AnonSync should therefore expose one dedicated **External support lane proof** page.

## Fixed page order

1. support-lane verdict
2. recipient and entitlement card
3. packet and redaction card
4. route-readiness card
5. proof and receipt rail

### 1) Support-lane verdict

Show:

- current lane (`staffed vendor support`, `self-serve community/help-center`, `billing/licensing form`, `private handoff only`, `unknown`)
- entitlement basis
- strongest safe sentence
- stronger rejected sentence

Example safe sentence:

- `This product line currently supports self-serve evidence preparation and community/help-center escalation, not direct staffed technical support.`

### 2) Recipient and entitlement card

Show:

- target audience class
- why that audience is or is not admissible
- whether the lane is public-ish, private vendor, or private internal
- what proof supports the lane choice

### 3) Packet and redaction card

Show:

- packet membership summary
- redaction state (`not reviewed`, `reviewed-minimized`, `raw local only`, `unknown`)
- whether heavy artifacts are included
- whether the current lane blocks raw send

### 4) Route-readiness card

Show:

- route class (`automatic feedback`, `manual attachment`, `upload link`, `manual local extraction`, `unknown`)
- route blockers (`awaiting sufficiency`, `attachment-too-large`, `no staffed lane`, `cleanup-first`, `unknown`)
- send-readiness verdict (`blocked`, `review first`, `ready`, `sent`, `unknown`)

### 5) Proof and receipt rail

Only show actions such as:

- `Open packet redaction review`
- `Switch to private archive only`
- `Proceed with automatic send`
- `Prepare manual upload package`
- `Emit diagnostic lane receipt`

## Rules

### Rule 1 — product/support lane must be public truth, not hidden policy

The page must say whether staffed vendor support exists for this line instead of implying it through generic UI text.

### Rule 2 — community and vendor routes must stay distinct

A public or semi-public forum lane must not inherit the assumptions of a private vendor lane.

### Rule 3 — readiness must include both evidence sufficiency and route admissibility

A packet can be locally complete yet still blocked from send on the chosen lane.

## Acceptance test

This page is good enough when a cautious operator can answer all of the following without leaving it:

- whether staffed vendor support is actually available here
- what outbound audience is admissible now
- whether the packet has been redaction-reviewed for that lane
- what route is available and what blocks it
- what stronger support sentence the product still refuses to make
