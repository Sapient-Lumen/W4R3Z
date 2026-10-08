# Redemption lane page: open-link claim, path choice, and name-collision truth interface spec

## Purpose

This page answers:

> how will this seat redeem the handoff, where may it land, and what exactly happens if local names already collide?

The page exists because `Enter a key or link`, `Scan QR`, and `Download` are not sufficient claim contracts by themselves.

## Core rule

Every receive flow for a bounded handoff must expose one first-class **Redemption lane** page before the claim is accepted.
That page owns:

- claim method
- recipient power and limits
- path-choice availability
- collision behavior
- resulting landed name

## Primary layout

The page always renders the same regions:

1. redemption verdict
2. claim-basis card
3. path-choice card
4. collision-result card
5. next review and receipt

### 1) Redemption verdict

Show:

- lane label
- redemption verdict: `desktop-link-claim`, `mobile-qr-claim`, `desktop-open-link-claim`, `path-fixed-claim`, `claim-expired`, `unknown`
- strongest honest operator summary
- one next honest action

### 2) Claim-basis card

Show:

- how the handoff is being claimed: paste link / scan QR / other
- whether possession of the link is sufficient
- whether claim requires any approval, identity, or usage slot
- whether this recipient may re-share after receipt
- whether this recipient may alter expiry or audience

The operator must be able to answer: **what exactly lets this seat claim the handoff, and what powers does receipt grant?**

### 3) Path-choice card

Show:

- whether this surface permits choosing the destination path now
- whether the current path is explicit, defaulted, or fixed
- whether a different lane would permit a different location choice
- whether this receive will land as one file, many files, or a packed result

The operator must be able to answer: **can I choose the landing path here, or is the receive lane opinionated?**

### 4) Collision-result card

Show:

- whether same-name entries already exist in the target
- the exact collision rule (`add-index`, `replace`, `merge`, `block`, `unknown`)
- the resulting landed names
- whether the operator must review before claim continues

The operator must be able to answer: **what exact local name will appear after claim if something already exists here?**

### 5) Next review and receipt

Show links to:

- Receive inbox
- Transfer history

After apply, emit a receipt that preserves:

- claim method
- landing path state
- collision verdict
- recipient power ceiling

## Honest outputs

This page may conclude:

- `desktop open-link claim · path chooser available`
- `mobile QR claim · landing path fixed by lane`
- `claim expired · reissue required from sender`
- `same-name collision detected · landed name will gain (1)`
- `recipient may re-share after receipt but may not alter expiry`

It may not collapse these into one generic `receive file` verdict.

## Rules

### Rule 1 — possession of the link must be named plainly

If possession of the link is the actual claim authority, the page must say that directly.
Do not replace it with soft language like `invited` unless some real recipient narrowing exists.

### Rule 2 — path choice and lane choice must stay separate

A flow that fixes the destination is not equivalent to a flow that merely defaults it.

### Rule 3 — collision semantics must be previewed, not merely reported afterward

If a claim will produce `name(1)` or similar landed names, that result must be visible before apply.

## Acceptance test

This page is good enough when a cautious operator can answer all of the following without leaving it:

- how this seat is claiming the handoff
- whether possession of the link is enough
- whether this surface allows path choice
- whether the recipient may re-share or mutate expiry
- what exact landed name appears if a collision already exists
