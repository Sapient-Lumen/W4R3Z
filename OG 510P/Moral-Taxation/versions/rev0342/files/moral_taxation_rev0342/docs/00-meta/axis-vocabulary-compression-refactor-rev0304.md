# Axis vocabulary compression refactor — rev0304

Rev0304 is the first cleanup pass after placeholder extinction and sentinel extinction. The risk was no longer missing accountability; it was that live cube axes were becoming too route-local to query.

## What changed

The pass refactors two high-noise axes across all 155 route records:

- `anti_pattern`
- `review_trigger`

Detailed scenario language remains available in golden-case contracts and route memos, but live route records now use reusable operational buckets where the narrower phrase did not add machine-routing value.

## Metrics

| Axis | Unique before | Unique after | Singletons before | Singletons after |
|---|---:|---:|---:|---:|
| `anti_pattern` | 310 | 151 | 228 | 124 |
| `review_trigger` | 270 | 117 | 206 | 93 |

Declared vocabulary also shrank even after preserving case-contract values: `anti_pattern` from 312 to 206, and `review_trigger` from 270 to 153.

## Canonical buckets added or promoted

`anti_pattern` now routes repeated failures into buckets such as `rent_extraction`, `classification_or_label_arbitrage`, `opacity_or_erasure`, `access_exclusion`, `liability_misassignment`, `data_or_confidentiality_overreach`, `harm_pricing_or_offset_theater`, `trapdoor_or_cliff`, `public_loss_private_upside`, and `cross_border_erasure`.

`review_trigger` now routes repeated recalibration events into buckets such as `protected_floor_or_incidence_shift`, `record_or_measurement_staleness`, `access_or_fallback_failure`, `remedy_or_contest_failure`, `privacy_or_confidentiality_breach`, `proceeds_or_surplus_trace_failure`, `classification_or_boundary_drift`, `capacity_or_control_shift`, and `harm_or_resilience_threshold_breach`.

## Guardrail

This is compression, not flattening. Case contracts retain sharper scenario flags where a regression needs them. Live route records should use narrower values only when the term is likely to recur as a queryable cube fact.
