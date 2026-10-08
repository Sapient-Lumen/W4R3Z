# Fulfillment lineage receipt page: completion class, acceptance state, and residual duty interface spec

## Purpose

This receipt is the one-page carry-forward object for the next operator.
It answers:

- what was asked
- what was claimed as done
- what was accepted
- what still remains
- what stronger sentence is forbidden

## Fixed receipt fields

### Header

- receipt id
- source mandate id
- latest fulfillment attestation id
- current acceptance state
- last material change time

### Completion basis

- claimed completion class
- reviewer verdict
- acceptance class
- acceptance proof rung
- evidence freshness class

### Residual truth

- residual duty class
- residual owner
- reopen posture
- next required action
- next forbidden overclaim

### Sentence block

Render exactly three lines:

1. `Accepted truth:`
2. `Residual truth:`
3. `Blocked stronger sentence:`

## Supported `current_acceptance_state` values

- `no-return-yet`
- `return-pending-review`
- `accepted-bounded`
- `accepted-partial`
- `accepted-temporary`
- `disputed`
- `superseded`
- `reopened`

## Hard rules

- receipts may never compress `claimed`, `accepted`, and `closed` into one badge
- a superseded receipt must still show the last accepted weaker sentence
- a disputed receipt must still preserve what evidence existed, not only that dispute happened
- a reopened receipt must preserve the prior acceptance rung rather than pretending it never existed
