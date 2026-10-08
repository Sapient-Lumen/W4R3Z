# Remedy-hardening-attestation observer-integrity proof page — log completeness, world scope, and tamper ceiling

## Purpose

This page is the evidence-heavy proof surface for determining whether the present witness set deserves trust.
It proves the exact ceiling on any sentence that tries to say current conformance or current breach status is well observed rather than merely guessed from incomplete artifacts.

## Required evidence blocks

### 1. Target-sentence basis

Preserve:

- source conformance, breach, or repair receipt
- sentence being supported or refused
- minimum evidence standard required for that sentence

### 2. Witness provenance ledger

For each witness preserve:

- witness kind
- capture start and end times
- whether restart confirmation exists where required
- whether reproduction window met the minimum
- storage world and service-user scope
- whether the witness is continuous, sampled, or after-the-fact forensic only

### 3. Retention and blind-spot ledger

Preserve:

- log size or retention ceiling relevant to the case
- rotation or discard events
- history horizon limits
- peer-visibility expiry limits
- platform or surface gaps
- missing or unavailable artifact kinds
- resulting downgrade in evidence trust

### 4. Tamper, mutation, and scope-integrity ledger

Preserve:

- any evidence of artifact replacement, truncation, or ambiguous provenance
- storage-world splits
- service-user or principal changes
- launch-path or script ambiguity
- whether manual forensic collection changed the ordinary observation path

### 5. Claim ceiling

Render:

- highest honest evidence-trust sentence
- highest honest world-scope sentence
- highest honest blind-spot-bounded sentence
- blocked stronger sentence and exact blocker

## Evidence classes

The page must distinguish at least:

- fresh artifact only
- protocol-complete witness
- sampled rather than continuous witness
- world-scope ambiguous witness
- retention gap blocks stronger sentence
- blind-spot budget exceeded
- tamper or mutation suspicion open
- trusted witness for named slice only
- evidence trust restored after fresh re-capture
- broader stronger sentence blocked

## Hard rules

The proof page must never treat:

- a present file timestamp as proof of complete capture by itself
- one world's artifact as proof for a sibling world by default
- a calm history surface as proof outside its retention horizon
- a collected dump as proof of ordinary observer continuity
- absence of visible evidence as proof that the event could not have happened
