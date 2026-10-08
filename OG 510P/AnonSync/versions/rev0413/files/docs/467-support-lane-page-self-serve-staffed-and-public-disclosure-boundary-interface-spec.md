# Support lane page: self-serve, staffed, and public disclosure boundary interface spec

## Purpose

This page answers:

> who can actually receive diagnostic evidence from this seat and this product line, and what disclosure boundary am I crossing if I send it there?

The page exists because `Help`, `Forum`, `Contact support`, `upload logs`, and `attach to email` are not the same recipient contract.

## Core rule

Every outward diagnostic or evidence-send action must expose one first-class **Support lane** page before send.
That page owns:

- recipient lane class
- entitlement / availability basis
- private versus public disclosure boundary
- admissible send routes
- next reviewed action

## Primary layout

The page always renders the same regions:

1. lane verdict
2. entitlement and boundary card
3. admissible routes card
4. disclosure consequence card
5. next review and receipt

### 1) Lane verdict

Show:

- lane label
- lane verdict: `self-serve-private`, `self-serve-public`, `staffed-vendor-private`, `local-only`, `unknown`
- strongest honest operator summary
- one next honest action

### 2) Entitlement and boundary card

Show:

- how the lane was determined (`product line`, `license posture`, `manual recipient choice`, `ticket-linked`, `forum route`, `unknown`)
- whether the target is public, semi-public, or private
- whether the lane is staffed or self-serve
- whether the lane is reversible or effectively non-recallable once posted

The operator must be able to answer: **am I sending to a staffed private lane, or am I really publishing to a self-serve/public lane?**

### 3) Admissible routes card

Show:

- routes allowed now: `in-product send`, `manual attachment`, `upload-link handoff`, `forum/minimized post`, `local archive only`
- routes currently blocked and why
- whether route choice changes artifact minimization requirements
- whether larger artifacts require a different send method

### 4) Disclosure consequence card

Show:

- default disclosure class for this lane
- strongest likely audience (`vendor-only`, `known operator`, `public forum readers`, `unknown`)
- whether redaction or minimization is mandatory before continuing
- what follow-up proof counts as successful delivery here

### 5) Next review and receipt

Show links to:

- Log capture window
- Report send
- Crash artifact

After any outward send, emit a receipt that preserves:

- lane class
- entitlement basis
- disclosure boundary
- selected route
- completion or partial-failure state

## Honest outputs

This page may conclude:

- `self-serve forum lane · public minimized packet required`
- `staffed vendor lane · private packet allowed`
- `local-only review · outward send unavailable or unreviewed`
- `route ambiguous · choose recipient class before packet assembly`

It may not collapse these into one generic `contact support` verdict.

## Rules

### Rule 1 — staffed and self-serve lanes must never be implied by button text alone

If the product line or target class changes the real lane, the page must say so explicitly.

### Rule 2 — public versus private boundary must remain adjacent to route choice

The operator must not choose a route first and learn later that it widened the audience radically.

### Rule 3 — route availability must never silently inherit ticket or target state

A stale ticket, copied email address, or browser-open forum link is not sufficient proof that the lane is still the same reviewed target.

## Acceptance test

This page is good enough when a cautious operator can answer all of the following without leaving it:

- whether this is self-serve or staffed
- whether the target is private or public
- which send routes are actually admissible now
- which disclosure boundary the chosen route crosses
- what proof will count as a successful send
