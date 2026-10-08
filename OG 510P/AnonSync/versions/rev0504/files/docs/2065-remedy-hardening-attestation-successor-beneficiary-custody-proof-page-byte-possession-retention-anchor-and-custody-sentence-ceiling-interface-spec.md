# Remedy-hardening-attestation successor beneficiary-custody proof page — byte possession, retention anchor, and custody-sentence ceiling

## Purpose

This page is the durable proof artifact that preserves what the beneficiary could use, what bytes they actually held, where those bytes lived, what upstream dependencies still mattered, and what stronger custody sentence therefore stayed blocked.

## Minimum proof bundle

The proof page must preserve at least:

- source beneficiary-usability receipt identifier
- named beneficiary identifier
- intended custody class
- intended retention horizon
- current byte-possession evidence
- retention-anchor evidence
- self-sufficiency versus upstream-dependency evidence
- source-withdrawal sensitivity evidence
- placeholder-reversion or local-eviction sensitivity evidence
- app-sandbox, license, topology, or share-removal fragility evidence
- export or handoff evidence if any
- strongest safe custody sentence at proof time
- strongest blocked stronger custody sentence at proof time

## Proof sections

### 1. Claimed custody summary

Show:

- what custody class the beneficiary was supposed to end up with
- what retention anchor would have justified that claim
- what independence from upstream withdrawal was assumed
- what evidence would have justified upgrade

### 2. Observed custody trace

For each observed custody-shaping component show:

- event time
- source actor or process
- source world
- touched subject
- before state
- after state
- observer quality
- whether this widened or narrowed custody confidence

### 3. Fragility ledger

For each fragility family show:

- why it matters
- whether it stayed hypothetical or became evidenced
- whether it is absolute, conditional, or operator-induced
- whether it alone blocks the stronger custody sentence

### 4. Custody ceiling statement

The page must end with a bounded statement such as:

- `beneficiary can use result now, but durable-custody sentence still blocked`
- `beneficiary has bytes only while upstream share or source remains available; self-sufficient custody sentence blocked`
- `beneficiary has local bytes, but they remain anchored only in app storage or fragile topology; portable-custody sentence blocked`
- `beneficiary holds self-sufficient custody for named seat only; broader custody sentence blocked`
- `later contradiction or withdrawal narrowed prior custody confidence`

## Evidence grading

The proof page must support at least these grades:

- beneficiary usability proved, custody still unproven
- source-dependent or placeholder-recoverable only
- local bytes present, but withdrawal or eviction fragile
- local bytes present in sandbox or topology-bound anchor only
- self-sufficient custody for named seat only
- later contradiction narrowed prior custody confidence
