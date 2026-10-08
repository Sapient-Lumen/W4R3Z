# Route-condition ceiling audit (generated)

Generated from route-local and multi-route JSON rows. Do not edit directly; run `make index` after changing route caps or condition ledgers.

- Route rows: `13`
- Authority ceiling checks: `3464`
- Single-route authority fields checked: `2133`
- Multi-route authority rows checked: `121`
- Multi-route route-spendable cap checks: `1331`
- Ceiling failures: `0`

## Rule

A single-route support, condition, forecast, decision, delta, evidence, carrier, protocol, ontology, contrast, severity, or control row may not state a recognized S-level spendable-authority field above the named route's own `promotion_ceiling`, including nested conditional clauses such as `outcome_effects[*].promotion_ceiling`. A multi-route row with any S-level authority field must carry `route_authority_ceilings`; those per-route values are the only route-spendable caps and must not exceed either the row envelope or the route's own ceiling.

## Authority fields covered

`maximum_authority_effect`, `maximum_credit`, `current_maximum_credit`, `promotion_ceiling`, `maximum_authority_credit`, `maximum_route_effect`, `maximum_credit_if_passed`, `realist_status_ceiling`, `current_update_ceiling`, `current_authority_state`, `conditional_authority_ceiling`

## Compact coverage

The full PASS table is deliberately not retained: it was mostly audit exhaust. The evaluator still checks every field above; this generated surface retains route, authority-field, file summaries, and any failures.

| Route | Checks | Failures |
|---|---:|---:|
| `R-OQ0057-AMPLITUDES-BOOTSTRAP` | `264` | `0` |
| `R-OQ0057-ASYMPTOTIC-SAFETY` | `265` | `0` |
| `R-OQ0057-CAUSAL-SET` | `268` | `0` |
| `R-OQ0057-COSMO-DARK-ENERGY-BAO` | `265` | `0` |
| `R-OQ0057-FAMILYB-THERMO-ENTROPIC` | `262` | `0` |
| `R-OQ0057-FAMILYC-EW-CODE` | `268` | `0` |
| `R-OQ0057-FAMILYC-LEARNED-INVERSE` | `260` | `0` |
| `R-OQ0057-FRAME-QRF-RELATIONAL` | `259` | `0` |
| `R-OQ0057-GW-STRONGFIELD-GR` | `266` | `0` |
| `R-OQ0057-LAB-GIE-BMV` | `279` | `0` |
| `R-OQ0057-LAB-GRAVITON-COUNTING` | `275` | `0` |
| `R-OQ0057-PRIMORDIAL-TENSOR-BMODES` | `266` | `0` |
| `R-OQ0057-STRINGM-ATLAS` | `267` | `0` |

| Authority field | Checks | Failures |
|---|---:|---:|
| `conditional_authority_ceiling` | `10` | `0` |
| `current_authority_state` | `6` | `0` |
| `current_maximum_credit` | `23` | `0` |
| `current_update_ceiling` | `10` | `0` |
| `maximum_authority_credit` | `6` | `0` |
| `maximum_authority_effect` | `1953` | `0` |
| `maximum_credit` | `13` | `0` |
| `maximum_credit_if_passed` | `10` | `0` |
| `maximum_route_effect` | `12` | `0` |
| `promotion_ceiling` | `77` | `0` |
| `realist_status_ceiling` | `13` | `0` |
| `route_authority_ceilings` | `1331` | `0` |

## File coverage summary

- Files with authority checks: `160`
- File-level failed checks: `0`
- Full per-file PASS rows are intentionally suppressed; failures, if any, are listed below.

| Top file by check volume | Checks | Failures |
|---|---:|---:|
| `CLAIM-ROUTE-BINDING-LEDGER.json` | `260` | `0` |
| `DECISION-EXPERIMENT-LEDGER.json` | `101` | `0` |
| `EMPIRICAL-DELTA-LEDGER.json` | `98` | `0` |
| `DISCRIMINATOR-FORECAST-LEDGER.json` | `86` | `0` |
| `CLAIM-LANGUAGE-PERMISSION-LEDGER.json` | `41` | `0` |
| `ONTOLOGY-COMMITMENT-LEDGER.json` | `39` | `0` |
| `PUBLIC-RECORD-CARRIER-LEDGER.json` | `37` | `0` |
| `PRIOR-SENSITIVITY-LEDGER.json` | `28` | `0` |
| `CONTRAST-CLASS-LEDGER.json` | `27` | `0` |
| `APPROXIMATION-ERROR-LEDGER.json` | `26` | `0` |
| `ASSUMPTION-DISCHARGE-LEDGER.json` | `26` | `0` |
| `ASYMPTOTIC-STATE-LEDGER.json` | `26` | `0` |

## Multi-route spend rule

Multi-route rows can still express family-level constraints, but route-local promotion or credit may spend only the named route's `route_authority_ceilings` value. This closes no-lint gaps for multi-route authority rows without requiring the archive to clone every family-level row into thirteen separate ledgers.

