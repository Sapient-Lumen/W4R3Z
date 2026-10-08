# Source-role credit-cap audit (generated)

Generated from row-level and ledger-level `source_role_events`. Do not edit directly; run `make index` after changing source-role events or credit-cap wording.

- Source-role events checked: `750`
- Ledgers with source-role events: `94`
- Retained acquired-support freshness events: `36`
- Retained forecast/status custody events: `26`
- Historical non-S0 normalization events: `0`
- Credit-cap semantic failures: `0`

## Rule

`S0` means the event itself creates no route credit. `no-new-credit` is narrower: it is allowed only when a freshness replay event retains already-acquired public-record custody with `source_ref_disposition: retained_as_acquired_support`, `source_role: acquired_support`, and `credit_cap_scope: freshness_event_no_incremental_route_credit`. Forecast runway and operational-status retentions must stay `S0` with `source_role_event_no_new_route_credit` scope.

## Credit-cap counts

| Credit cap | Events |
|---|---:|
| `S0` | `714` |
| `no-new-credit` | `36` |

## Credit-cap scopes

| Scope | Events |
|---|---:|
| `<missing>` | `535` |
| `freshness_event_no_incremental_route_credit` | `36` |
| `source_role_event_no_new_route_credit` | `179` |

## Role / disposition / cap combinations

| Combination | Events |
|---|---:|
| `acquired_support / historical_source_role_normalization / S0` | `1` |
| `acquired_support / retained_as_acquired_support / no-new-credit` | `36` |
| `denominator_pressure / excluded_from_acquired_source_refs / S0` | `67` |
| `denominator_pressure / historical_source_role_normalization / S0` | `17` |
| `denominator_pressure / retained_on_denominator_row_only / S0` | `411` |
| `denominator_pressure / route_local_handoff_only / S0` | `152` |
| `forecast_runway / excluded_from_acquired_source_refs / S0` | `3` |
| `forecast_runway / retained_as_forecast_runway / S0` | `15` |
| `forecast_runway / retained_on_denominator_row_only / S0` | `2` |
| `forecast_runway / route_local_handoff_only / S0` | `3` |
| `metadata_wrapper / forbidden_on_metadata_wrapper / S0` | `30` |
| `metadata_wrapper / historical_source_role_normalization / S0` | `1` |
| `operational_status / excluded_from_acquired_source_refs / S0` | `1` |
| `operational_status / retained_as_operational_status / S0` | `11` |

## `no-new-credit` custody events

These rows retain existing public-record support custody for freshness replay. They do not grant incremental route authority beyond the owning row's already-declared support state.

| Ledger | Row | Events |
|---|---|---:|
| `ACQUISITION-PROTOCOL-LEDGER.json` | `AP-CMB-POLARIZATION-PIPELINE` | `1` |
| `ACQUISITION-PROTOCOL-LEDGER.json` | `AP-DESI-LIKELIHOOD-REPLAY` | `1` |
| `ACQUISITION-PROTOCOL-LEDGER.json` | `AP-GW-CATALOG-REANALYSIS` | `1` |
| `CALIBRATION-TRACEABILITY-LEDGER.json` | `CAL-0009-GW-STRONGFIELD-GR` | `1` |
| `CALIBRATION-TRACEABILITY-LEDGER.json` | `CAL-0012-COSMO-DARK-ENERGY-BAO` | `1` |
| `CALIBRATION-TRACEABILITY-LEDGER.json` | `CAL-0013-PRIMORDIAL-TENSOR-BMODES` | `1` |
| `CONTRAST-CLASS-LEDGER.json` | `CC-0008-GW-STRONGFIELD-MODIFIED-GR` | `1` |
| `CONTRAST-CLASS-LEDGER.json` | `CC-0011-DESI-DARK-ENERGY-PRIOR-CONTRAST` | `1` |
| `CREDIT-ALLOCATION-LEDGER.json` | `CA-PRIMORDIAL-TENSOR-BMODES` | `1` |
| `DECISION-EXPERIMENT-LEDGER.json` | `DX-0003-GW-STRONGFIELD-DEVIATION-OR-POLARIZATION` | `1` |
| `DECISION-EXPERIMENT-LEDGER.json` | `DX-0004-DESI-LATE-TIME-DARK-ENERGY-DYNAMICS` | `1` |
| `DECISION-EXPERIMENT-LEDGER.json` | `DX-0005-CMB-PRIMORDIAL-TENSOR-BMODE` | `1` |
| `DISCRIMINATOR-FORECAST-LEDGER.json` | `DF-0013-DESI-DR2-COSMOLOGY-TENSION-SPLIT` | `1` |
| `EMPIRICAL-DELTA-LEDGER.json` | `ED-0004-GWTC5-STRONGFIELD-GR-CONSTRAINTS` | `1` |
| `EMPIRICAL-DELTA-LEDGER.json` | `ED-0009-DESI-DR2-COSMOLOGY-CONSTRAINT-CORRIDOR` | `1` |
| `EMPIRICAL-DELTA-LEDGER.json` | `ED-0016-SPT3G-BMODE-BANDPOWER-LIKELIHOOD-PRESSURE` | `1` |
| `EVIDENCE-SEVERITY-LEDGER.json` | `SV-0005-GW-STRONGFIELD-SEVERITY` | `1` |
| `EVIDENCE-SEVERITY-LEDGER.json` | `SV-0006-DESI-DARK-ENERGY-SEVERITY` | `1` |
| `EVIDENCE-SEVERITY-LEDGER.json` | `SV-0007-CMB-PRIMORDIAL-TENSOR-SEVERITY` | `1` |
| `EVIDENCE-UNIT-LEDGER.json` | `EU-0009-GW-STRONGFIELD-CATALOG` | `1` |
| `EVIDENCE-UNIT-LEDGER.json` | `EU-0012-DESI-BAO-LIKELIHOOD` | `1` |
| `EVIDENCE-UNIT-LEDGER.json` | `EU-0013-CMB-BMODE-PRIMORDIAL` | `1` |
| `INDEPENDENCE-ASSUMPTION-LEDGER.json` | `IA-0007-CMB-FOREGROUND-DELENSING-REHEATING` | `1` |
| `LIKELIHOOD-UPDATE-LEDGER.json` | `LU-0009-GW-STRONGFIELD-GR` | `1` |
| `LIKELIHOOD-UPDATE-LEDGER.json` | `LU-0012-COSMO-DARK-ENERGY-BAO` | `1` |
| `MEASUREMENT-MODEL-LEDGER.json` | `MM-0009-GW-STRONGFIELD-GR` | `1` |
| `MEASUREMENT-MODEL-LEDGER.json` | `MM-0012-COSMO-DARK-ENERGY-BAO` | `1` |
| `MEASUREMENT-MODEL-LEDGER.json` | `MM-0013-PRIMORDIAL-TENSOR-BMODES` | `1` |
| `PRIOR-SENSITIVITY-LEDGER.json` | `PS-0008-WAVEFORM-MODEL-PRIORS` | `1` |
| `PRIOR-SENSITIVITY-LEDGER.json` | `PS-0012-DESI-COSMOLOGY-PRIOR-BOUNDS` | `1` |
| `PUBLIC-RECORD-CARRIER-LEDGER.json` | `PRC-CMB-LAMBDA-MAPS-LIKELIHOODS` | `1` |
| `PUBLIC-RECORD-CARRIER-LEDGER.json` | `PRC-DESI-BAO-LIKELIHOOD` | `1` |
| `PUBLIC-RECORD-CARRIER-LEDGER.json` | `PRC-GWOSC-STRAIN-CATALOG` | `1` |
| `SYSTEMATIC-UNCERTAINTY-LEDGER.json` | `SYS-0009-GW-STRONGFIELD-GR` | `1` |
| `SYSTEMATIC-UNCERTAINTY-LEDGER.json` | `SYS-0012-COSMO-DARK-ENERGY-BAO` | `1` |
| `SYSTEMATIC-UNCERTAINTY-LEDGER.json` | `SYS-0013-PRIMORDIAL-TENSOR-BMODES` | `1` |

## Failures

None.

## Compression note

The evaluator scans every event but retains only counts, grouped no-new-credit rows, historical non-S0 exceptions, and failures. This avoids another large all-pass table while keeping the risky credit-cap boundary visible.

