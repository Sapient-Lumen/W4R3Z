# Case-contract audit report — Rev0289

Case contracts: 82
Golden cases: 82
Routes exercised by cases: 78
Cases with raw axis obligations: 47
Cases with legacy expected flags preserved after normalization: 32

## Route-family coverage

| Family | Exercised routes |
|---|---|
| `controller_ai` | 3 |
| `cross_border_reporting` | 5 |
| `environment_climate_commons` | 9 |
| `financial_system_risk` | 6 |
| `labor_care_benefits` | 7 |
| `legal_enforcement_penalty` | 4 |
| `public_finance_core` | 15 |
| `public_procurement_industrial_policy` | 5 |
| `regulated_networks_platforms` | 4 |
| `release_integrity_currentness` | 4 |
| `social_floor_public_services` | 6 |
| `tax_administration_access` | 7 |
| `wealth_property_rent` | 3 |

## Rev0289 repair notes

- Normalized raw golden-case axis values so case contracts can validate against cube vocabulary.
- Converted generic expected flags into route-backed flags while preserving old values in `legacy_expected_flags` when useful for review.
- Added GC-082 to catch the failure mode where a prose case and route ID survive but contract obligations drift.
- Added `tools/audit_case_contracts.py` and wired it into `make audit`, `make check`, and release checks.
