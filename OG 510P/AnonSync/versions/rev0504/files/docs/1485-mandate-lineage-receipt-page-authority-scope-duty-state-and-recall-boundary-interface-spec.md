# Mandate lineage receipt page: authority, scope, duty state, and recall boundary interface spec

## Purpose

Later operators need one receipt that answers:

> what exact authority was issued here, to whom, for what scope, with what duty state, and what weaker sentence survived once the mandate expired or was recalled?

## Core decision

AnonSync must emit one durable **Mandate lineage receipt** whenever a meaningful action mandate is issued, superseded, or cancelled.

## Fixed page order

1. **Receipt header**
2. **Authority summary**
3. **Duty-state summary**
4. **Execution summary**
5. **Recall boundary summary**
6. **Next-operator sentence**

### 1) Receipt header

Show:

- mandate id
- receipt id
- issuer
- recipient / cohort
- issue time
- current archival state

Supported `current_archival_state` values:

- `historical-active-when-issued`
- `historical-superseded`
- `historical-cancelled`
- `historical-expired`
- `historical-retired`

### 2) Authority summary

Required rows:

- authority class granted
- source basis
- scope covered
- excluded scope
- re-delegation right
- expiry rule

### 3) Duty-state summary

Required rows:

- delivery state
- acceptance state
- execution state
- proof state
- unresolved acknowledgement gap

### 4) Execution summary

Required rows:

- action taken
- bounded outcome
- residual delta
- follow-on obligation
- strongest sentence earned

### 5) Recall boundary summary

Required rows:

- superseding mandate id if any
- cancel / recall event
- surviving weaker sentence after recall
- stale-copy risk that may persist
- next forbidden overclaim

Hard rule:

A receipt must preserve not just what was authorized once, but what became unsafe to assume later.

### 6) Next-operator sentence

Use:

> This receipt proves that [recipient] was granted [authority] for [scope], accepted duty at [state], reached [bounded outcome], and after [supersession/cancel] only [weaker sentence] remained safe.
