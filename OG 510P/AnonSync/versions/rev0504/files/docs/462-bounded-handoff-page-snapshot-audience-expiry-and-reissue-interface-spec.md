# Bounded handoff page: snapshot, audience, expiry, and reissue interface spec

## Purpose

This page answers:

> is this a live shared subject or only a bounded handoff, who may redeem it, when does it expire, and when must it be reissued?

The page exists because `Share file`, `Send file`, `drag here`, `copy link`, and `scan QR` are not the same contract as creating a live shared subject.

## Core rule

Every one-off transfer or file-send issuance must expose one first-class **Bounded handoff** page before issue.
That page owns:

- handoff kind
- audience ceiling
- expiry contract
- mutation invalidation
- reissue threshold

## Primary layout

The page always renders the same regions:

1. handoff verdict
2. snapshot contract card
3. audience and expiry card
4. invalidation and reissue card
5. next review and receipt

### 1) Handoff verdict

Show:

- handoff label
- handoff verdict: `bounded-snapshot`, `bounded-snapshot-never-expires`, `bounded-snapshot-mobile-fixed-expiry`, `live-subject`, `unknown`
- strongest honest operator summary
- one next honest action

### 2) Snapshot contract card

Show:

- whether later source changes automatically sync or not
- whether the claim is one-way or two-way
- whether the handoff is one file, multi-file pack, or mixed selection
- whether unchanged bytes only are still claimable

The operator must be able to answer: **is this live sync or just a bounded snapshot?**

### 3) Audience and expiry card

Show:

- who can redeem: `whoever possesses the link`, `reviewed recipients only`, `unknown`
- whether use count can be restricted
- whether device bans or audience narrowing exist
- current expiry state: fixed duration / sender-chosen duration / never expires / unknown
- whether the recipient can alter expiry

The operator must be able to answer: **how open is this handoff, and when will its claim die?**

### 4) Invalidation and reissue card

Show:

- whether later source edits invalidate the current handoff
- whether reissue is required after content change
- whether expiry also forces reissue
- whether re-share by recipients creates the same snapshot or a new snapshot lineage

The operator must be able to answer: **when must this handoff be regenerated instead of trusted as still current?**

### 5) Next review and receipt

Show links to:

- Redemption lane
- Receive inbox
- Transfer history

After issue, emit a receipt that preserves:

- handoff kind
- audience ceiling
- expiry contract
- invalidation rule
- reissue threshold

## Honest outputs

This page may conclude:

- `bounded one-way handoff · open-link audience · 3-day expiry`
- `bounded one-way handoff · never-expiring desktop link`
- `bounded one-way handoff · mobile fixed-expiry lane`
- `content changed · current handoff stale · reissue required`
- `live subject required instead of bounded handoff`

It may not collapse these into one generic `share link` verdict.

## Rules

### Rule 1 — bounded handoff must never masquerade as live sync

The page must not rely on icons or share placement to signal that later source edits do **not** keep flowing.

### Rule 2 — audience ceiling must sit next to expiry

An open-link audience plus a long-lived or never-expiring claim is a stronger contract than either fact alone.
They must remain adjacent.

### Rule 3 — stale handoffs must fail honestly

If the source changed or the expiry elapsed, the page should prefer `reissue required` over vague language like `try again` or `refresh`.

## Acceptance test

This page is good enough when a cautious operator can answer all of the following without leaving it:

- whether this is live sync or bounded handoff
- who can redeem it
- whether use count or audience can be narrowed
- when it expires and whether never-expire is allowed here
- what exact event makes reissue necessary
