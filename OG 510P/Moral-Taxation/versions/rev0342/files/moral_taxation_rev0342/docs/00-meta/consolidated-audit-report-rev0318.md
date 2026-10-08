# Consolidated semantic audit report — rev0318

This single current report replaces ten separate release-current audit notes. Historical reports remain available, while all active `cube-index.json` audit pointers resolve here.

## Release invariants

- Cube route records: 155
- Required axes: 23
- Source records: 666
- Source-currentness entries: 51
- Remedy profiles: 155
- Policy-action profiles: 155
- Actor-accountability profiles: 155
- Case contracts: 84
- Route coverage: 80/155 (51.6%)
- Uncovered routes: 75
- Coverage floor: 80
- Runtime status: declarative_only_no_answer_router
- Case-only axis values: 239

## Integrity repairs

- Canonical scorecard criteria: 98
- Canonical score extrema: ±196
- Remedy `new_calibration_file` escalation placeholders: 0
- Policy-action `new_calibration_file` escalation placeholders: 0
- Semantic audits included in `make package`: yes
- Current audit report mode: consolidated

## Existing semantic gates

- Cube schema, route IDs, required axes, and semantic contamination: pass when `tools/audit_cube.py` exits zero.
- Axis hygiene and vocabulary ceilings: pass when `tools/audit_axis_hygiene.py` exits zero.
- Prose compactness metrics and watched ladder distinctness: pass when `tools/audit_prose_bloat.py` and `tools/check_archive.py` exit zero.
- No negative bytes-saved metrics remain.
- Source currentness claims and registry refs: pass when `tools/audit_source_currentness.py` exits zero.
- Procurement memo slack and currentness refs: pass when `tools/audit_procurement_risk.py` exits zero.
- Remedy, case-contract, policy-action, and actor-accountability profile bijections: pass when their named audits exit zero.

## Coverage by family

| Family | Covered | Total |
|---|---:|---:|
| `controller_ai` | 3 | 21 |
| `cross_border_reporting` | 5 | 6 |
| `environment_climate_commons` | 9 | 10 |
| `financial_system_risk` | 6 | 8 |
| `labor_care_benefits` | 7 | 11 |
| `legal_enforcement_penalty` | 4 | 11 |
| `public_finance_core` | 17 | 44 |
| `public_procurement_industrial_policy` | 5 | 5 |
| `regulated_networks_platforms` | 4 | 4 |
| `release_integrity_currentness` | 4 | 4 |
| `social_floor_public_services` | 6 | 8 |
| `tax_administration_access` | 7 | 17 |
| `wealth_property_rent` | 3 | 6 |

## Deliberate limitations

A passing release proves internal consistency, currentness obligations, profile bijection, manifest integrity, and a non-regressing declarative case baseline. It does **not** yet prove that a natural-language or structured input is routed correctly by an answer engine, because no answer router is invoked. It also does not estimate revenue, distribution, behavior, administrative cost, or uncertainty.
