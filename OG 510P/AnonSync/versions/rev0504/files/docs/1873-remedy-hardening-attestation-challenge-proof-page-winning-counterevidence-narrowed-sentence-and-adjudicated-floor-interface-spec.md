# Remedy-hardening-attestation-challenge proof page — winning counterevidence, narrowed sentence, and adjudicated floor

## Purpose

This page is the durable proof that a typed challenge was reviewed under explicit burden, witness priority, and sentence-floor rules.
It must let a later verifier see not only that evidence exists, but which evidence actually won and what sentence honestly survived.

## Sections

### 1) Challenge header

Publish:

- case identifier
- challenged sentence identifier
- challenge type
- challenger class
- challenge opened at
- current ruling posture

### 2) Winning and losing witnesses

List:

- decisive witness family
- supporting witness families
- losing witness families
- excluded or contaminated witness families
- whether any witness was captured only after restart, reconnect, re-add, or fresh-world rebuild

### 3) Surviving sentence ladder

The proof must print the sentence ladder explicitly:

- pre-challenge strongest sentence
- sentence allowed while challenge remained open
- adjudicated surviving sentence
- strongest blocked stronger sentence

Example proof outputs:

- `freshness challenge upheld; historical sealed-integrity sentence survives, current-trust sentence does not`
- `continuity challenge upheld; prior world-specific sentence overturned, successor-world sentence pending reseal`
- `stale-presentation challenge rejected; storage, runtime, and log witnesses outrank the stale UI`
- `support-only evidence captured; provisional floor raised, but final restoration still blocked`

### 4) Consequence rail

The proof must record downstream consequence classes:

- automation suspended or restored
- consumer-facing sentence narrowed or restored
- rework required or not required
- reseal required or not required
- appeal or reopen trigger still active

### 5) Claim ceilings

The page must explicitly forbid false upgrades such as:

- `challenge resolved` when only a workaround was applied
- `same sentence restored` when only a weaker sentence survived
- `continuity preserved` when the ruling depended on fresh instance creation
- `adjudicated` when the decisive witness is still missing or contaminated
