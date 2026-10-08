# Claim lane page: link, key, QR, browser-open, and manual intake equivalence interface spec

## Purpose

The archive already has strong offer-artifact, preview, and manual-claim doctrine.
This document makes the ordinary page concrete.

The page exists to answer one ordinary operator question:

> are these intake lanes truly equivalent, or do they differ in approval, expiry, budget, browser dependence, or resulting review strength?

## Core decision

Every subject that can be claimed through more than one lane must own one first-class **Claim lane** page.
That page is the semantic home of:

- lane comparison
- artifact-versus-wrapper truth
- approval and budget deltas
- browser or scanner dependence
- typed fallback order
- recent lane receipts

The product must not let `link`, `key`, `QR`, `open in app`, and `paste manually` look interchangeable unless they really are.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. lane-set strip
2. canonical-artifact card
3. lane comparison matrix
4. browser/scanner dependence card
5. typed fallback-order card
6. resulting-review-strength card
7. recent lane receipts
8. expert details drawer

### 1) Lane-set strip

Show:

- subject or artifact family
- lanes currently available
- strongest next-safe action
- whether the page is comparing issuance lanes, claim lanes, or both

The strip should answer `what exact lanes are on the table?`

### 2) Canonical-artifact card

Show:

- whether the lanes wrap one canonical artifact or several different artifact families
- which lanes are pure wrappers (`QR encodes link`, `browser wrapper around local app open`, etc.)
- which lanes materially change governance (`raw key bypasses approval`, different budget, different expiry)

This card should answer `what is the same here, and what is only superficially similar?`

### 3) Lane comparison matrix

For each lane, show:

- artifact family actually conveyed
- approval model
- expiry or use budget
- identity proof expected at claim time
- browser/OS/scanner dependence
- resulting seat-rights ceiling
- best use case

This matrix should answer `how do these lanes differ in real terms?`

### 4) Browser/scanner dependence card

Show:

- whether the lane depends on protocol-handler registration
- whether the lane depends on a browser launching a local app
- whether current surface kind can consume it directly
- whether QR scan is merely convenience or the only practical route on this seat

This card should answer `what outside cooperation does this lane require?`

### 5) Typed fallback-order card

Show the strongest honest fallback order, for example:

1. continue with canonical lane here
2. switch to equivalent wrapper
3. fall back to manual typed claim of the same artifact
4. fall back to different reviewed artifact with explicitly different governance

Each row must show:

- whether semantics stay the same
- whether approval behavior changes
- whether browser/scanner dependence disappears
- whether resulting review strength changes

This card should answer `if the fast lane fails, what exact meaning survives the fallback?`

### 6) Resulting-review-strength card

Show:

- whether the chosen lane produces strong pre-claim preview, medium preview, or minimal preview
- whether lane change weakens the operator's pre-commit understanding
- whether the lane is acceptable only because the canonical artifact has already been reviewed elsewhere

This card should answer `how much reviewed clarity does this lane preserve?`

### 7) Recent lane receipts

Show recent receipts with:

- lane chosen
- canonical artifact identity
- semantic-equivalence verdict
- approval/budget posture in force
- fallback used, if any
- resulting success or refusal

### 8) Expert details drawer

Hide raw encodings, protocol-handler diagnostics, QR payload details, and parse traces behind an expert drawer.
They matter, but they are not the semantic center.

## Compact row contract

A trustworthy compact row should preserve the following order:

1. lane phrase
2. equivalence phrase
3. approval/budget phrase
4. dependence phrase
5. strongest next action

Example:

```text
Copied link   canonical reviewed artifact   approval required for new peers; expiry budget active   browser-independent; manual paste available without semantic loss   Claim here
```

## Acceptance criteria

This spec is satisfied when:

- wrapper-equivalent lanes and governance-different lanes are visibly different answers
- browser-open failure and semantic artifact failure are visibly different answers
- approval and budget deltas are shown before claim
- typed fallback order states whether semantics change or not
- the product emits receipts for meaningful lane choices rather than outsourcing memory to browser history or clipboard archaeology
