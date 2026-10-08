# Transfer history page: UI removal, local byte, and expired-row residue interface spec

## Purpose

This page answers:

> if I clear this transfer entry, delete these received bytes, or wait for expiry, what exactly remains true afterward?

The page exists because `Downloads`, `Shared links`, `remove from UI`, `delete from device`, and `expired` are not the same residue contract.

## Core rule

Every bounded-handoff product surface must expose one first-class **Transfer history** page.
That page owns:

- transfer row family
- local-byte relationship
- still-live claim status
- expired-row retention
- later resend / reissue consequence

## Primary layout

The page always renders the same regions:

1. history verdict
2. row-family card
3. local-byte card
4. expiry and residue card
5. next action and receipt

### 1) History verdict

Show:

- history label
- history verdict: `row-only`, `row-and-bytes-coupled`, `bytes-gone-history-remains`, `expired-row-retained`, `unknown`
- strongest honest operator summary
- one next honest action

### 2) Row-family card

Show:

- whether this row is `shared-link`, `download`, `download-history`, `expired-transfer`, or `unknown`
- whether it represents sent, received, or both
- whether removing the row changes send/receive ability
- whether the row still points to local bytes

The operator must be able to answer: **what kind of transfer row is this really?**

### 3) Local-byte card

Show:

- whether local bytes are present now
- whether deleting bytes removes the row, the history, both, or neither
- whether removing the row removes bytes, both, or neither
- whether resend / re-share still requires current local bytes

The operator must be able to answer: **what happens to the actual bytes if I clean this up?**

### 4) Expiry and residue card

Show:

- whether the claim is live, expired, or invalidated by source change
- how long expired rows may remain visible
- current retention basis for expired rows
- whether a fresh link / reissue is required for future claims

The operator must be able to answer: **what remains after expiry or stale-content invalidation?**

### 5) Next action and receipt

Show actions such as:

- `remove row only`
- `remove local bytes only`
- `open landed bytes`
- `reissue handoff`
- `clear expired history`

After apply, emit a receipt that preserves:

- row family
- byte effect
- claim status before/after
- residue summary

## Honest outputs

This page may conclude:

- `shared-link row only removed · local bytes remain`
- `downloads cleanup removes device bytes and corresponding downloads row`
- `download history remains after local deletion`
- `expired transfer retained in UI under history policy`
- `source changed · current row no longer represents a live claim · reissue required`

It may not collapse these into one generic `clear transfer` verdict.

## Rules

### Rule 1 — row residue and byte residue must render separately

A history row, a live claim, and local bytes are three different things.
The page must keep them separate even when one action affects two of them.

### Rule 2 — expiry must not pretend to be cleanup

An expired transfer may still persist as row history.
`Expired` is not the same thing as `gone`.

### Rule 3 — reissue must sit next to invalidation

If source change or expiry killed the original claim, the page should point directly to reissue rather than ambiguous retry language.

## Acceptance test

This page is good enough when a cautious operator can answer all of the following without leaving it:

- what kind of transfer row they are looking at
- whether local bytes still exist
- what removing the row changes
- what deleting bytes changes
- whether the claim is still live or needs reissue
