# Record denominator and route-ledger schema

## Purpose

`rev0260` made the candidate-identifiability denominator explicit in prose. This surface makes it executable. A route can now be inspected in three layers:

1. `schemas/record-denominator.schema.json` — the required fields every route denominator must expose.
2. `CANDIDATE-ROUTE-STATE-LEDGER.json` — current route rows with state, denominator, earliest blocker, score codes, and caps.
3. `NEGATIVE-CONTROL-LEDGER.json` and `EMPIRICAL-DELTA-LEDGER.json` — hostile decoys and evidence deltas that determine whether a row may move.

The state machine remains the semantic owner. These ledgers make the state machine replayable.

## Required denominator

A row is incomplete unless it names all of the following:

```yaml
record_id:
candidate_family:
target_claim:
target_grain:
record_object:
record_production_process:
observer_or_frame:
public_access_mode:
candidate_native_definition:
borrowed_bridge_fields:
equivalence_relation:
forward_acquisition_map:
inverse_map:
inverse_deficiency:
stability_margin:
abstention_or_no_verdict_rule:
adversarial_countermodels:
residual_cap:
promotion_ceiling:
rollback_or_quarantine_handle:
public_record_carrier_ids: []
acquisition_protocol_ids: []
```

The denominator deliberately separates `record_object`, `record_production_process`, `public_access_mode`, `public_record_carrier_ids`, and `acquisition_protocol_ids`. A paper, dataset, waveform catalog, boundary correlator, reconstructed bulk operator, simulation output, or lab trace may be public in ordinary practice while still failing candidate-native public-bridge ownership.

## Route-state fields

`CANDIDATE-ROUTE-STATE-LEDGER.json` adds:

| Field | Use |
|---|---|
| `route_id` | stable row handle for cross-file references |
| `authority_state` | one of `S0`–`S5`, `AT`, `AR`, `Q`, `T` from the state machine |
| `owner_surface` | canonical prose owner for the row |
| `earliest_blocker` | first unpaid obstacle that prevents promotion |
| `score_codes` | field-level `N/P/B/M` scores inherited from the route ledger |

This converts broad statements like “Family C is strongest” into a row-level comparison: strongest at what state, under what target grain, with which borrowed fields, and capped by which blocker.

## Promotion rule

A prose surface may sharpen a route, but it does not move a route unless the machine-readable row changes. A route that lacks any of the following remains below `S4` by rule:

- complete denominator;
- declared public-record carriers and acquisition protocols that exist in their ledgers;
- declared adversarial countermodels that exist in `NEGATIVE-CONTROL-LEDGER.json`;
- empirical delta or formal delta that touches an actual row field;
- earliest blocker;
- residual cap;
- rollback or quarantine handle.

## Lint boundary

The linter now checks existence, required fields, legal authority states, route/control cross-references, and basic score-code vocabulary. This is intentionally not a proof of correctness. It is a guard against the archive drifting back to persuasive prose without replayable route rows.
