# Topology measurement receipt page — covered peer pairs, supported generalization, and reopen boundary interface spec

## Purpose

The archive already had a measurement receipt.
What it still lacked was the durable receipt for the next question:

> after we ran or reviewed a pairwise measurement, what exact topology slice did it cover, how far were we allowed to generalize, and what would force the claim back open?

AnonSync should therefore issue a dedicated **topology measurement receipt** whenever a pairwise result is promoted beyond pure local observation.

## Receipt fields

The receipt must preserve:

- receipt id
- incident id
- topology slice version
- measurement/run ids used
- covered peer pairs or cohorts
- direction coverage
- route-class coverage
- representative-pair verdict
- generalization ceiling
- strongest allowed sentence
- stronger rejected sentence
- required widening step if unresolved
- reopen conditions
- issuance timestamp

## Required sections

### 1) Covered topology slice

Show exactly which peer pairs, uploader cohorts, and receiver cohorts were covered.
Do not reduce this to `share X`.

### 2) Measurement basis

Show whether the conclusion came from:

- live peer rows
- sidecar benchmark
- mixed live + benchmark evidence
- widened counterexample checks

### 3) Supported generalization

Publish the strongest safe sentence, for example:

- `For uploader A to receivers B and C over relayed WAN paths, relay penalty is the dominant observed limiter.`
- `This result does not yet generalize to direct-path receivers or to uploader D.`

### 4) Rejected stronger claim

State the stronger claim the receipt explicitly refuses to make.
This is mandatory.

### 5) Reopen boundary

The receipt must say the claim reopens if any of these happen:

- topology slice changes materially
- a previously missing counterexample seat becomes available
- route class changes for covered peers
- uploader role distribution changes
- workload shape changes enough to alter applicability
- new contradictory measurement arrives

## Compact rendering obligations

Any compact receipt chip must still preserve:

- covered slice label
- representative-pair verdict
- generalization ceiling
- reopen trigger summary

## Anti-clone rule

Do not clone receipts that merely say `network looks fine` or `speed issue likely relay-related` without preserving which peers that sentence covered and which wider claim remained unsupported.
