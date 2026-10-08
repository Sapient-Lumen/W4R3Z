# Axis sentinel extinction refactor — rev0303

Rev0303 clears the remaining live-axis sentinels left after the public-finance-focused Rev0302 cleanup.

## Before / after

| Signal | Before | After |
|---|---:|---:|
| `floor_risk=no_specific_floor_risk` | 31 | 0 |
| `burden_mechanic=not_incidence_specific` | 33 | 0 |
| `delivery_channel=not_channel_specific` | 22 | 0 |
| `market_structure=not_market_specific` | 2 | 0 |
| `rights_affected=not_rights_specific` | 18 | 0 |

## Substantive refactor

The cleanup touched 60 route records across controller-AI, tax-administration access, public-finance-core, social-floor/public-services, procurement/industrial policy, and labor/care/benefits. It replaced mature sentinels with concrete floor-risk groups, burden mechanics, delivery rails, institutional structures, and rights markers.

The highest-impact corrections were controller-map and model-assisted-administration routes, which now expose controller-map packets, attestation channels, event logs, redaction tiers, contest portals, model-governance notice channels, and black-box decision burden; tax-administration routes, which now expose access-channel failure, refund delay, record lock-in, legal-risk transfer, fee/paywall burdens, and contest-window lock-in; and public-service/procurement routes, which now expose public-service access, public-value integrity, worker voice, fiscal capacity, and source-integrity rights.

## Release rule

`tools/audit_axis_hygiene.py` now treats the retired sentinels as release-fatal in live route records. Case-contract required axes remain the only additional vocabulary source used to declare formal axis values.
