# Remedy-hardening-attestation successor beneficiary-usability proof page — materialization, openability, access blockers, and usable-sentence ceiling

## Purpose

This page is the durable proof artifact that preserves what landed, what the named beneficiary was expected to do with it, what bytes and affordances were actually available, and what stronger usability sentence therefore stayed blocked.

## Minimum proof bundle

The proof page must preserve at least:

- source outcome-conformance receipt identifier
- source execution-run identifier
- named beneficiary identifier
- intended beneficiary action class
- intended usable-result class
- current materialization evidence
- online-source dependency evidence
- shell or handler readiness evidence
- access-permission evidence
- update-receipt posture evidence
- lock, path, encoding, and filesystem blocker evidence
- source-peer absence or ghost-file evidence if applicable
- strongest safe sentence at proof time
- strongest blocked stronger sentence at proof time

## Proof sections

### 1. Claimed beneficiary-usable summary

Show:

- what the beneficiary was supposed to be able to do
- what byte posture was required
- what affordance or handler path was assumed
- what evidence would have justified upgrade

### 2. Observed usability trace

For each observed usability-shaping component show:

- event time
- source actor or process
- source world
- touched subject
- before state
- after state
- observer quality
- whether this widened or narrowed beneficiary-usability confidence

### 3. Blocker ledger

For each blocker family show:

- why it matters
- whether it stayed hypothetical or became evidenced
- whether it is absolute, conditional, or workaround-only
- whether it alone blocks the stronger usable sentence

### 4. Usability ceiling statement

The page must end with a bounded statement such as:

- `reviewed result landed, but beneficiary currently has placeholder-only representation; stronger usable sentence blocked`
- `beneficiary can fetch bytes only while source peer is online; self-sufficient usability sentence blocked`
- `bytes local, but handler or shell integration missing; ordinary-use sentence blocked`
- `bytes local, but access or update posture degraded; full intended-use sentence blocked`
- `named beneficiary can use result for named slice only; broader usable sentence blocked`

## Evidence grading

The proof page must support at least these grades:

- landed result exists, beneficiary usability still unproven
- placeholder or disconnected visibility only
- source-dependent retrievability only
- local bytes, workaround-required use only
- local bytes, degraded update posture
- named-slice beneficiary usability only
- later contradiction narrowed prior beneficiary-usability confidence
