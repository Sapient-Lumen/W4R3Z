# Safe language substitution page — operator verb rewrite and audience fit interface spec

## Purpose

The archive already had receipts and proof pages.
What it still lacked was a first-class language surface that turns unsafe human shorthand into product-earned speech.

The page exists to answer one ordinary operator question:

> how should I say what happened without accidentally claiming more than the action proved?

## Core decision

Every high-consequence action family should have one first-class **Safe language substitution** page.
That page is the semantic home of:

- unsafe phrase detection
- approved rewrites
- audience tuning
- caveat attachment
- prohibited phrases
- copy-ready exports

The product must not assume the operator will translate precise internal state into safe external language unaided.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. requested phrase strip
2. rewrite verdict card
3. approved substitutions list
4. caveat attachment card
5. audience-fit previews
6. prohibited phrase ledger
7. recent phrase receipts
8. expert details drawer

### 1) Requested phrase strip

Show:

- raw operator phrase
- related action / object
- audience target
- strongest next-safe action

The strip should answer `what phrase am I trying to use?`

### 2) Rewrite verdict card

Show one explicit verdict:

- `phrase already safe`
- `phrase salvageable with caveat`
- `phrase requires narrower rewrite`
- `phrase blocked until stronger action`

Also show the strongest reason.

### 3) Approved substitutions list

Provide 1–3 copy-ready rewrites such as:

- `This peer will not receive future updates; files already synced remain.`
- `This seat is disconnected here; bytes remain locally.`
- `This file was removed from participating retainers and kept in archive per policy.`
- `This row is hidden from the roster view; it is not unlinked.`
- `Containment work has started; broader rotation is still pending.`

### 4) Caveat attachment card

Show any caveat that must travel with the phrase:

- landed bytes remain
- non-linked retainers may remain
- archive retains recoverable history
- device may reappear if it comes online
- rotation not yet complete

### 5) Audience-fit previews

Render the best safe rewrite for:

- self note
- teammate handoff
- admin / operator log
- external recipient / customer-facing note

All variants must preserve the same truth ceiling.

### 6) Prohibited phrase ledger

List the exact phrases the product refuses to suggest or export, along with the blocking reason.

### 7) Recent phrase receipts

Show recent phrase receipts with:

- raw phrase
- approved rewrite
- audience
- required caveat
- export status

### 8) Expert details drawer

Hide raw contradiction logic, claim-graph internals, and policy derivation behind an expert drawer.
They matter, but they are not the semantic center.

## Compact row contract

A trustworthy compact row should preserve the following order:

1. raw phrase
2. rewrite verdict
3. best approved rewrite
4. mandatory caveat

Example:

```text
“their access is gone” · requires narrower rewrite · “future updates to this peer are revoked” · caveat: already-landed files remain
```

## Acceptance criteria

This spec is satisfied when:

- unsafe shorthand gets rewritten before export
- caveats travel with the approved sentence rather than falling into footnotes
- audience variants differ in tone but not in truth ceiling
- the product can block a phrase outright when only a stronger action would make it true
