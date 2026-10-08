# Remedy-hardening-attestation successor beneficiary-custody contract sheet page — retention anchor, self-sufficiency, and withdrawal sensitivity

## Purpose

This page is the operator-facing sheet for deciding whether a beneficiary who can currently use a landed result also actually holds a durable copy under their own control.
It exists to prevent `opened once`, `hydrated once`, `present in app storage`, or `visible in the share` from being mistaken for `custodied independently by the beneficiary`.

## Core question

The page must answer:

**does the named beneficiary now hold the bytes in a way that remains under their control without depending on upstream peers, fragile mode wiring, revocable local-share topology, or ephemeral app storage?**

## Minimum fields

The contract sheet must show at least:

- action identifier
- source beneficiary-usability receipt identifier
- named beneficiary identifier
- intended custody class
- intended retention horizon
- current byte-possession class
- retention anchor or storage world
- self-sufficiency versus upstream-dependency state
- source-withdrawal sensitivity state
- placeholder-reversion or local-eviction sensitivity state
- app-sandbox, license, or topology fragility summary
- export or handoff state
- strongest honest custody sentence now
- blocked stronger custody sentence now

## Standing ladder

The page must support at least these distinct standings:

- beneficiary usability proved, custody still unproven
- placeholder-only or source-dependent access only
- local bytes present, but reversion or storage cleanup can remove beneficiary custody cheaply
- local bytes present only inside upstream-fragile topology or app sandbox
- one-time received copy present, but future lineage and update relation severed
- beneficiary holds bytes locally for named seat only
- beneficiary holds self-sufficient custody for named slice only
- beneficiary custody later narrowed by contradiction or withdrawal
- receipt superseded

## Required comparisons

The sheet must compare:

- beneficiary-usability standing versus beneficiary-custody standing
- intended custody class versus actual byte-possession class
- expected self-sufficiency versus actual upstream dependency
- expected durable retention anchor versus actual storage or sandbox anchor
- expected withdrawal independence versus actual source-withdrawal fragility
- expected portability or exportability versus actual handoff posture

## Required layout

### Header

Show:

- action name
- beneficiary name
- custody posture
- byte-possession badge
- strongest honest sentence now

### Left column — intended custody

Show:

- named beneficiary
- intended custody class
- intended retention horizon
- expected self-sufficiency
- forbidden substitute states

### Right column — actual current custody

Show:

- current byte-possession class
- retention anchor
- upstream dependency class
- withdrawal and eviction sensitivity
- export or handoff state
- topology, license, or sandbox fragility summary

### Footer decision rail

The footer must make it impossible to flatten these into one answer:

- usable only
- usable while source remains available
- local copy present but easily revertible
- local copy present only inside fragile topology or app storage
- self-sufficient custody for named slice only
- durable beneficiary custody sentence still blocked
