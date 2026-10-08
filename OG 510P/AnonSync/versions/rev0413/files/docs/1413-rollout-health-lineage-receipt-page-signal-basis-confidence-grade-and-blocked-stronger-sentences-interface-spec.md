# Rollout-health lineage receipt page: signal basis, confidence grade, and blocked stronger sentences interface spec

## Purpose

The **Rollout-health lineage receipt** is the durable artifact proving what health judgment was made, on what basis, and with what confidence ceiling.

## Required fields

The receipt must preserve at minimum:

- `rollout_health_receipt_id`
- rollout id
- predecessor / successor revision
- focused ring boundary
- evidence window
- freshness grade
- signal classes used
- adjudication verdict classes used
- promotion-confidence outcome
- resulting action
- strongest safe sentence
- blocked stronger sentence
- missing evidence list
- causal-confidence ceiling

## Supported resulting actions

- `promote`
- `promote-guarded`
- `hold`
- `freeze`
- `rollback`
- `observe-only`
- `unknown`

## Hard rules

- receipts must preserve both what was known and what remained unknown
- receipts must preserve the evidence window, not just the decision time
- receipts must preserve blocked stronger sentences so later operators do not overread a past green or hold judgment
- receipts must distinguish `no regression observed in window` from `regression disproven`
