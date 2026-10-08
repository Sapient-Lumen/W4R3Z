# Identity merge receipt page: seat lineage, certificate takeover, and residue boundary interface spec

## Purpose

This receipt preserves the meaning of a completed or attempted identity-link action.
It exists so later operators do not need screenshot memory or device folklore to answer:

> which seat adopted which lineage, what certificate fate occurred, what subjects were inherited or displaced, and what residue boundary still survives?

## Required receipt fields

The receipt must preserve at minimum:

- receipt id and timestamp
- source seat lineage
- target seat lineage
- resolved adoption direction
- certificate fate (`unchanged`, `adopted`, `superseded`, `blocked`, `unknown`)
- inherited subject set summary
- displaced / evicted subject set summary
- filesystem-risk class
- version-compatibility posture
- unlink / hide / residue verdict
- strongest safe sentence
- stronger rejected sentence
- reopen triggers

## Receipt body order

1. outcome header
2. lineage summary
3. subject impact summary
4. residue boundary summary
5. reopen triggers

### 1) Outcome header

Show the final verb family, verdict, and proof ceiling.

### 2) Lineage summary

Show which seat won, which seat adopted, and whether certificate replacement occurred.

### 3) Subject impact summary

Show what was inherited, what was displaced, and what stronger filesystem risk was in play.

### 4) Residue boundary summary

Show whether the seat is hidden, locally unlinked, remotely untouched, or fully detached as far as the product can honestly prove.

### 5) Reopen triggers

Include triggers such as:

- dormant seat returns online
- later manual reconnect or export occurs
- version mismatch resolved or worsens
- another adoption or detach action supersedes this receipt

## Rules

### Rule 1 — the receipt must preserve directionality

`Seats linked` is not enough.

### Rule 2 — residue verdict must survive the happy path

Later operators need to know whether a hidden member can return.

### Rule 3 — proof ceiling must survive success wording

A successful action may still have a narrow claim.
