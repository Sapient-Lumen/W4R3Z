# Offer-family lineage receipt page: artifact family, claim lane, and landing survivor boundary interface spec

## Purpose

This receipt preserves the honest after-state of one issued or claimed offer so a later operator can answer:

> what family was this artifact really, how was it claimed, where did it land, what survived, and which stronger sentence was explicitly rejected?

## Receipt structure

The receipt always records:

1. artifact identity
2. governance and openness
3. claim-lane proof
4. landing and collision result
5. survivor and cleanup boundary
6. blocked stronger sentence

### 1) Artifact identity

Record:

- receipt id
- artifact family
- subject class
- carrier used at review time
- issuer or source surface if known
- freshness timestamp

### 2) Governance and openness

Record:

- approval model
- bearer openness class
- usage-ceiling verdict
- expiry posture
- fanout ceiling

### 3) Claim-lane proof

Record:

- actual intake lane
- handoff-health verdict
- whether manual fallback was required
- whether the fallback preserved the same artifact family

### 4) Landing and collision result

Record:

- destination-authority class
- chosen or default root
- collision rule
- landed name
- landed byte status

### 5) Survivor and cleanup boundary

Record:

- whether artifact expiry removes future claims only
- whether UI rows remain after byte deletion
- whether bytes remain after UI-row removal
- whether history persists
- cleanup ceiling

### 6) Blocked stronger sentence

Always preserve one rejected claim such as:

- `This was a private invite`
- `This could only be used once`
- `Opening the link proved the artifact was valid`
- `Removing the row removed all copies`
- `Expired means the bytes are gone`

## Compact summary line

Every receipt should support one compact summary such as:

- `bounded file-transfer link · open bearer · manual paste claim after browser handoff failed · desktop default landing · collision suffix (1) · landed bytes remain after row removal`

## Success condition

A later operator who never saw the original flow should still be able to tell:

1. what was actually issued or claimed
2. how open it was
3. how it got into the product
4. where it landed
5. what cleanup did and did not prove
