# Remedy-hardening-attestation observer-integrity review page — do we trust the current witnesses enough to make this conformance or breach sentence?

## Purpose

This page is the operator-facing review that answers the practical evidence question after conformance review: are the current witnesses good enough to support the sentence the product wants to publish, or do capture gaps, world ambiguity, rotation loss, or blind spots block it?

## Primary review prompts

The review must answer these prompts in order:

1. **Which current sentence is the product trying to support or rule out?**
2. **Which witness lanes are supposed to support that sentence?**
3. **Was the capture protocol for those lanes actually completed?**
4. **Do the preserved artifacts come from the right world, service user, and storage scope?**
5. **Which blind spots or retention gaps still matter?**
6. **What is the strongest sentence the product may honestly say now?**

## Review sections

### 1. Target-sentence board

Show:

- source conformance or breach receipt
- target sentence under review
- minimum witness standard required for that sentence

### 2. Witness-provenance board

Show:

- each witness lane and artifact
- when and how it was captured
- whether restart, reproduction, or collection protocol was confirmed
- which world and scope each artifact belongs to

### 3. Blind-spot board

Show:

- retention horizons
- rotation or discard risk
- missing surfaces
- platform-specific observation gaps
- whether any known instrumentation omission applies

### 4. Trust-ceiling board

Show:

- current observer-integrity class
- highest evidence-trust-safe sentence
- blocked stronger sentence
- exact blocker for the stronger sentence

### 5. Recovery chooser

The review must output one and only one primary sentence class such as:

- evidence present, protocol incomplete
- fresh witness, world scope ambiguous
- fresh witness with retention gap
- calm surfaces only, no authoritative observer set
- trusted witness for named slice only
- tamper suspicion under review
- evidence trust restored after re-capture
- broader stronger sentence blocked

## Hard rules

The review must never let an operator hide:

- restarted capture uncertainty behind a fresh log timestamp
- one retained file behind `complete capture` wording
- sibling-world artifacts behind `same deployment observed`
- UI calm behind `no breach evidence exists`
- manual forensic heroics behind `ordinary continuous observer coverage exists`
