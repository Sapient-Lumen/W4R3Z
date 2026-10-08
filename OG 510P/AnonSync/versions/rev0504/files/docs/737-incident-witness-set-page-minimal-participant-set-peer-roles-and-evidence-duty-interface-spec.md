# Incident witness set page — minimal participant set, peer roles, and evidence duty interface spec

## Purpose

Give the operator one durable page that answers:

- whose evidence matters for this incident
- why each participant matters
- what role each participant currently plays
- which evidence class is owed by each participant
- which participants are required versus optional

This page exists so `collect logs from all peers` and `collect logs from two peers` stop being article folklore and become reviewable product state.

## Inputs

- incident identifier
- current incident headline and strongest explanation
- subject/share identifiers
- relevant peer inventory
- current route/topology view
- recent source and destination witnesses
- current failure class (`connectivity`, `delivery`, `speed`, `conflict`, `continuity`, `other`)
- known peer roles and confidence
- current evidence already received per participant

## Primary questions this page must answer

1. Which participants are in scope for this incident?
2. Which participants are required witnesses versus optional witnesses?
3. What role does each participant play in the current explanation?
4. What artifact or proof is owed by each participant?
5. When is the witness set complete enough for an honest conclusion?

## Layout

### A. Incident scope strip

Fields:

- incident headline
- subject scope
- current strongest explanation
- current witness-set strategy (`local-only`, `pairwise`, `route-segment`, `share-wide`, `other`)
- freshness of the witness decision

### B. Candidate participants table

Columns:

- participant
- current role (`source`, `destination`, `observer`, `bridge`, `alternate-source`, `controller`, `unknown`)
- role confidence
- witness duty (`required`, `optional`, `excluded-for-now`)
- requested evidence family
- why this participant matters

### C. Minimal witness set card

Show:

- smallest currently defensible witness set
- what question that set is meant to answer
- stronger question that still needs a wider set if any
- strongest safe sentence the current set could support if fully collected

### D. Exclusions and deferrals card

List peers not currently requested and why, such as:

- outside affected route
- redundant with a stronger source witness
- currently unreachable and not blocking the next claim
- useful later only if contradiction persists

### E. Request plan card

For each required participant show:

- artifact family needed
- time window or reproduction window
- privacy/disclosure posture
- expected completion proof
- link to open witness request page

## Required interactions

- `Confirm witness set`
- `Promote participant to required`
- `Downgrade participant to optional`
- `Open witness request`
- `Mark participant unreachable`
- `Open witness completeness review`
- `Issue witness-set receipt`

## Guardrails

- Never default to `all peers` without naming the unanswered question that requires that width.
- Never say `two peers are enough` without identifying the exact pair and their roles.
- Never treat missing witnesses as negative evidence.
- Never collapse role into prose if the product can infer it from current route/source state.
- Never let an excluded participant disappear silently; exclusions must stay inspectable.

## Output

A reviewed witness plan that makes participant scope, role typing, and evidence duty explicit before heavier capture or escalation.
