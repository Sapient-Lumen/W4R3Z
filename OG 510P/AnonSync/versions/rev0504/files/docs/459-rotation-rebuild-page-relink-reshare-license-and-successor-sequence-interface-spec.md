# Rotation rebuild page: relink, reshare, license, and successor sequence interface spec

## Purpose

This page answers:

> if a broader rebuild is necessary, what exact order preserves trusted continuity while cutting away the old authority epoch?

The page exists because `unlink everything`, `reinstall`, `relink`, and `reshare` are not a trustworthy sequence by themselves.

## Core rule

Whenever incident response crosses into broader identity or authority rotation, the product must expose one first-class **Rotation rebuild** page.
That page owns:

- survivor cohort
- rebuild sequence
- continuity boundaries
- reissue obligations
- post-rotation proof goals

## Primary layout

The page always renders the same regions:

1. rebuild verdict
2. survivor-cohort card
3. ordered sequence card
4. continuity and reissue card
5. completion proof card

### 1) Rebuild verdict

Show:

- whether rebuild is `required`, `recommended`, `optional`, or `deferred`
- strongest reason broader rotation is needed
- whether the new state will be a preserved successor or a deliberate clean break
- strongest current risk if rebuild is delayed

### 2) Survivor-cohort card

Show:

- trusted seats that survive into the new epoch
- seats excluded from relink or waiting for proof
- subjects that will be carried forward, reissued, or intentionally retired
- any encrypted or storage-only peers that need special treatment

The operator must be able to answer: **who is coming forward into the rebuilt trust world?**

### 3) Ordered sequence card

Render the sequence as reviewed steps, such as:

1. preserve trusted local bytes and evidence
2. cut off or retire old authority epoch
3. generate or adopt new identity material
4. relink trusted survivor seats
5. reattach or reshare subjects in reviewed order
6. re-home entitlement or license if needed
7. verify new cohort posture

Each step must show:

- purpose
- exact target scope
- whether it preserves continuity or rebuilds it
- what later step depends on it

The operator must be able to answer: **what exact order avoids recreating the old risk?**

### 4) Continuity and reissue card

Show:

- which approvals, grants, subjects, or receipts carry forward
- which must be reissued under the new epoch
- whether old artifact links, linked arrivals, or owner rights remain invalid afterward
- which already-landed local copies survive only as historical bytes, not live membership

The operator must be able to answer: **what survives, and what has to be explicitly reissued?**

### 5) Completion proof card

Show the proof goals for calling rebuild complete:

- old epoch disabled or retired
- trusted cohort linked to new epoch
- expected subjects reattached or reshared
- entitlement/seat state re-homed if applicable
- residual authority page reduced to only accepted residue

Emit a receipt that preserves:

- survivor cohort
- rebuild sequence used
- continuity versus clean-break verdict
- items reissued or intentionally abandoned

## Honest outputs

This page may conclude:

- `successor cohort rebuilt under new identity; three subjects reissued`
- `clean break chosen; no continuity claims preserved`
- `license re-home completed; old stolen seat should fall back on next online contact`
- `subject continuity preserved for data, but approvals and offers were intentionally reissued`

It may not collapse these into one generic `setup complete` statement.

## Rules

### Rule 1 — preserve and rebuild must be separately named

The page must say when it is carrying trusted continuity forward and when it is intentionally rebuilding from a new authority epoch.

### Rule 2 — the order itself is part of the truth

A rebuild page without an ordered sequence is not trustworthy enough.

### Rule 3 — reissue obligations must be explicit

If grants, offers, or linked arrivals need new issuance under the rebuilt epoch, the page must say so directly.

## Acceptance test

This page is good enough when a cautious operator can answer all of the following without leaving it:

- whether broader rotation is actually necessary
- which trusted seats survive into the rebuilt cohort
- what exact order the rebuild follows
- what continuity survives versus what is reissued
- what proof marks the rebuild complete

