# Archive salvage proof page: remote-change origin, encrypted-seat limit, and survivor map interface spec

## Purpose

This page exists where historical bytes look promising but their actual salvage strength is still uncertain.
It answers one ordinary question:

> what does this archived version prove about the past, what recovery route is still honestly available, and which stronger recovery sentence remains blocked?

## When this page must appear

Trigger this page for:

- deleted-file recovery discussions
- encrypted-seat recovery attempts
- post-uninstall cleanup review
- any dispute about whether archive history still counts as a recoverable survivor

## Fixed page order

1. salvage-proof header
2. provenance and survivor map card
3. encrypted-seat / authority-limit card
4. proof ladder
5. receipt/export rail

### 1) Salvage-proof header

Show:

- subject / seat / archived object
- provenance (`remote-modified copy`, `remote-deleted copy`, `unknown`)
- current salvage verdict (`restorable-here`, `visible-here-but-rw-seat-required`, `expired-or-excluded`, `local-only salvage`, `unknown`)
- strongest safe sentence
- stronger rejected sentence

### 2) Provenance and survivor map card

Render rows for:

- why this version landed in Archive
- whether local self-deletes are expected in trash/recycle instead
- whether other candidate survivor seats are known
- whether retention/size ceilings may already have eliminated older siblings

### 3) Encrypted-seat / authority-limit card

Show consequences such as:

- `encrypted seat can hold archived bytes`
- `encrypted seat follows deleted authoritative state`
- `encrypted seat is read-only and cannot upload restored bytes back`
- `other connected RW peer may be required for authoritative recovery`

### 4) Proof ladder

Possible rungs:

- `documented archive behavior only`
- `archived bytes visible on disk`
- `seat authority known`
- `runtime restore tested locally`
- `authoritative republish witnessed`

### 5) Receipt/export rail

Offer:

- `Emit archive lineage receipt`
- `Open archive restore review`
- `Open archive retention and visibility page`

## Rules

### Rule 1 — provenance belongs in proof

The page must say whether the archived bytes witness remote modification or remote deletion.

### Rule 2 — encrypted-seat visibility is weaker than restore authority

Seeing archived bytes on an encrypted seat must not be allowed to imply recoverability through that seat.

### Rule 3 — survivor maps must stay explicit

The page must separate `this seat still holds bytes` from `the mesh still has an authoritative recovery route`.
