# Remedy-hardening-attestation-reliance contract sheet page — consumer registry, dependency coverage, and revocation owner

## Purpose

This page is the operator's compact contract for a receipt that is already speakable to some audience and now needs an explicit answer to who actually relied on it, what downstream artifacts were derived from it, what coverage remains unknown, and who owns the retraction or revalidation wave if the source ruling changes.
It exists so the product can distinguish `this ruling may be relied on` from `we know who relied on it, how far that reliance spread, and what must happen if it is no longer current`.

## Core fields

- case identifier
- source finality receipt identifier
- source ruling identifier
- current governing sentence
- allowed reliance audience class
- current dependency-governance class
- current revocation posture
- consumer registry version
- consumer coverage score
- known consumer count
- observed consumer count
- unknown-consumer risk grade
- dependent artifact count
- stale dependent artifact count
- derivative automation count
- derivative human decision count
- derivative publication count
- derivative export or handoff count
- last observed consumption time
- oldest still-live downstream artifact time
- revocation owner class
- revalidation owner class
- reseal owner class
- freeze-new-reliance flag
- superseding receipt identifier
- reopened-source-receipt flag
- strongest blocked broad-reliance sentence
- strongest blocked all-dependents-current sentence
- next evidence that upgrades dependency confidence
- next evidence that forces immediate revocation

## Dependency-governance classes

The page must model at least these distinct classes:

- audience allowed but no consumers registered
- consumers registered, consumption not yet observed
- partial observed consumption, unknown-consumer risk still open
- named-cohort coverage complete, external coverage still open
- all required dependents current on governing receipt
- superseded with revocation wave active
- reopened with outward reliance frozen
- historical-only source, dependent artifacts fully retracted or re-certified

## Consumer classes

The page must support at least these consumer or dependent classes:

- internal reviewer
- named operational automation
- named external automation
- human decision maker
- exported report or packet
- dashboard or status surface
- downstream receipt that quotes the source sentence
- policy or template derived from the receipt

## Required distinctions

The page must keep these truths separate:

- audience allowed versus consumer actually registered
- consumer registered versus consumer observed consuming
- consumer observed consuming versus dependent artifact still live
- stale derivative still visible versus derivative fully retracted
- historical source still citable versus source still dependency-owning
- revalidation pending versus retraction complete
- freeze-new-reliance now versus clean downstream state now

## Layout

The page should be organized into seven zones:

### 1) Governing sentence rail

Always print:

- the current governing sentence
- the exact allowed reliance audience
- the strongest blocked broad-reliance sentence
- the strongest blocked `all dependents are current` sentence
- the precise reason each stronger sentence is blocked

### 2) Consumer registry rail

Show a table with at least these columns:

- consumer identifier
- consumer class
- registration basis
- first eligible time
- first observed consumption time
- last observed consumption time
- current source receipt identifier consumed
- downstream artifact identifiers derived
- current stale status
- current revocation status

The page must never collapse `eligible`, `registered`, `observed`, and `current` into one badge.

### 3) Dependency coverage rail

Show coverage as a ladder, not a binary:

- allowed only
- registered
- partially observed
- named cohort covered
- required cohort covered
- all current dependents reconciled

The active rung must be highlighted and each blocked rung must show the exact missing evidence.

### 4) Unknown-consumer risk rail

Show why broad dependency certainty may still be blocked:

- short visibility horizon
- export without callback channel
- cloned or fresh-instance ambiguity
- disconnected or pending consumer possibility
- derivative artifact discovered but source registration missing
- historical logs decayed or rotated

### 5) Revocation rail

Show every active downstream obligation with status:

- freeze new reliance
- notify registered consumers
- retract stale artifact
- revalidate dependent decision
- reseal dependent receipt
- mark historical source only
- confirm completion by named owner

Status values must include:

- not started
- in progress
- blocked
- complete
- unverifiable

### 6) Ownership rail

Show exactly who owns each action class:

- registry owner
- revocation owner
- revalidation owner
- reseal owner
- escalation owner when unknown-consumer risk stays open

### 7) Actions rail

The page must support explicit actions such as:

- register consumer
- attach observed consumption evidence
- freeze new reliance
- issue revocation wave
- mark artifact retracted
- request revalidation
- issue successor receipt binding
- close wave only after evidence-backed completion

## Operator promises

The contract sheet must let the operator say things like:

- `this ruling is final for the named automation class, but only two of five eligible consumers are registered`
- `registered consumers have been notified, but one exported report remains live on the superseded receipt`
- `new reliance is frozen now, yet downstream cleanup is incomplete because an external consumer has no callback path`
- `the old receipt remains historically visible, but it no longer owns dependency precedence`

## Hard decisions frozen by this page

This interface family makes these product decisions explicit:

- no broad `people relied on this` sentence without a registry and coverage basis
- no `all dependents are current` sentence while stale derivative artifacts remain
- no silent supersession: if precedence moves, downstream obligations must be surfaced immediately
- no passive archival substitute for retraction when the source sentence was actually consumed downstream

