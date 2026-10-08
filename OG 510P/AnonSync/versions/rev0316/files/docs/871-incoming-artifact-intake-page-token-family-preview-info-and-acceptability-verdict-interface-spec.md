# Incoming artifact intake page: token family, preview info, and acceptability verdict interface spec

## Purpose

This page exists because `paste token`, `open link`, and `scan QR` are intake actions, not immediate acceptance.
An incoming artifact may be valid, stale, stronger than intended, or continuity-changing.

The operator question is:

> what did I just receive, what can I safely know before consuming it, and is it acceptable to proceed on this seat right now?

## Core decision

Every incoming invite or authority artifact must render one first-class **Incoming artifact intake** page before commit.

## Fixed page order

1. intake strip
2. parsed-family card
3. preview-info card
4. acceptability verdict card
5. seat-fit card
6. continuity consequence card
7. intake receipt summary

### 1) Intake strip

Show:

- intake carrier
- parsed artifact family or `unknown`
- current seat
- strongest next-safe action

### 2) Parsed-family card

Publish:

- artifact family
- whether parsing is complete, partial, or failed
- whether local semantic inspection succeeded without secret reveal
- whether the artifact appears superseded, exhausted, stale, or revoked

### 3) Preview-info card

Show the strongest safe preview available before commit:

- candidate subject or seat family label
- approximate scope / size / class when known
- requested right or ceiling
- approval path expected
- issuer identity proof when available

The page must also show what is still unknown until deeper review or approval.

### 4) Acceptability verdict card

Show one explicit verdict:

- `safe to continue to review`
- `safe to continue and claim`
- `requires stronger identity proof`
- `blocked by local policy`
- `blocked by stale or exhausted artifact`
- `blocked because artifact family is not allowed on this seat`

### 5) Seat-fit card

Show:

- whether this seat may consume the artifact
- whether another seat is the safer claimant
- whether local storage / capability / trust posture is insufficient
- whether this intake would unexpectedly join a seat family rather than one subject

### 6) Continuity consequence card

Publish:

- whether acceptance preserves current continuity
- whether it creates a new subject presence only
- whether it links the entire seat into a broader family
- whether it risks replacing a current identity or creating a fork

### 7) Intake receipt summary

Preview the receipt that will survive accept, defer, or reject.

## Rules

### Rule 1 — intake is not auto-commit

Opening or pasting an artifact may not silently finalize the join.

### Rule 2 — strongest safe preview only

The page must show useful preview information without pretending unknowns are known.

### Rule 3 — seat-link surprises must be loud

If the artifact would link or replace seat identity rather than merely add one subject, the page must say so before acceptance.

### Rule 4 — stale or exhausted artifacts stay visible as blocked artifacts

The product must not flatten them into generic parse failure.

## Acceptance criteria

A later operator can:

- tell what kind of artifact arrived
- see what is known before acceptance
- understand whether this seat should consume it
- distinguish local policy block from artifact invalidity
- reopen the right approval or continuity page without repeating intake folklore