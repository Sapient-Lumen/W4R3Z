# Transfer eligibility proof page: current gate basis, next wake, and why-not-moving interface spec

## Purpose

This page is the evidence surface for an operator who wants proof rather than a badge.
It exists to answer:

> why is nothing moving right now, what evidence supports that answer, and what event would change it?

## Core decision

Every serious `not moving now` state can be opened into a first-class **Transfer eligibility proof** page.

## Fixed page order

1. proof header
2. gate evidence timeline
3. current context witness
4. next wake / resume witness
5. claim ceiling

### 1) Proof header

Show:

- current verdict
- strongest safe sentence
- stronger rejected sentence
- evidence freshness
- proof grade (`direct`, `derived`, `stale`, `conflicted`, `unknown`)

### 2) Gate evidence timeline

Include evidence items such as:

- share pause asserted
- scheduler zero window entered
- current network classified as forbidden
- battery threshold crossed
- core entered sleep
- background priority dropped
- last successful transfer
- last local detection
- last wake cycle

### 3) Current context witness

Show what the product currently knows about:

- network class
- battery / charging state
- runtime awake/asleep state
- whether peers can currently see the subject
- whether local detection is still running

### 4) Next wake / resume witness

Show:

- scheduled next wake if known
- event needed for resume
- whether resumption is automatic
- what remains unprovable now

### 5) Claim ceiling

Explicitly forbid overclaim language when evidence is insufficient.
Example forbidden claims:

- `This subject is fully stopped`
- `Nothing can change`
- `No peer can observe anything further`

## Rules

### Rule 1 — proof must answer `why not now`

A badge alone is not evidence.

### Rule 2 — proof must publish the future trigger

`Not now` without `what would change it` is incomplete.

### Rule 3 — stale evidence weakens the sentence immediately

The page must degrade the claim ceiling when current context is uncertain.
