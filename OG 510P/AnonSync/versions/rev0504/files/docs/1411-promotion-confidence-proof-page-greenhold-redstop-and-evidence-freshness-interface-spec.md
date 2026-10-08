# Promotion-confidence proof page: green, hold, red-stop, and evidence-freshness interface spec

## Purpose

The **Promotion-confidence proof** is the durable decision page that justifies why a rollout may widen, must hold, must freeze, or must roll back.
It sits between the health review and the actual ring-promotion step.

## Core operator question

> what exact evidence standard did this rollout satisfy before we widened or refused to widen it?

## Required sections

### 1) Confidence basis

Show:

- rollout id
- current ring
- candidate next ring
- current confidence grade
- freshness gate verdict
- adjudication summary

### 2) Evidence sufficiency verdicts

Separate these explicitly:

- enough live observation
- enough cohort coverage
- enough artifact freshness
- enough causal confidence
- enough recovery proof
- enough regression exclusion

Each must show `pass`, `partial`, `fail`, or `unknown`.

### 3) Promotion outcome

Supported outcomes:

- `promote-next-ring`
- `promote-next-ring-guarded`
- `hold`
- `freeze`
- `rollback`
- `unknown`

### 4) Rejected stronger outcomes

Examples:

- `broad promotion` rejected in favor of `pilot only`
- `green promotable` rejected in favor of `guarded promotable`
- `recovered` rejected in favor of `recovered-but-unexplained`

### 5) Fastest path to stronger sentence

Show the smallest missing ingredients that would allow a stronger decision, such as:

- 24-hour service-cohort evidence window
- fresh logs after restart-bound repro
- clear separation of host-load from product-regression signal
- confirmation that warning is not a known-version defect

## Hard rules

- proof pages must preserve why a weaker outcome won
- `no blocker observed` must stay weaker than `healthy enough to widen`
- freshness failure alone may be sufficient to block promotion even when current symptoms look quiet
- recovery proof must name whether it proves symptom disappearance, root-cause removal, or both
