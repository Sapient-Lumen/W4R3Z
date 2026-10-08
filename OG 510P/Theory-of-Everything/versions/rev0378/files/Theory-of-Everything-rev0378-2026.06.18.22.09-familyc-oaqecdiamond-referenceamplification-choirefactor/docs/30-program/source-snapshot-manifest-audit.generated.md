# Source snapshot manifest audit (generated)

Generated from `SOURCE-SNAPSHOT-MANIFEST.json` plus the bibliography and source-carrying ledgers. Do not edit directly; run `make index` after changing source snapshot rows or source-role placements.

- Snapshot manifest revision: `rev0378`
- Snapshot manifest rows: `12`
- Snapshot row placements: `84`
- Zero-placement snapshot receipts: `1`
- Local retained payload files: `6`
- Local retained payload bytes: `890175`
- Local checksum-manifest files: `2`
- Local checksum-manifest entries: `6189`
- Known malformed checksum-manifest lines: `1`
- Payload component checksum records: `9`
- Payload inventory checksum records: `5`
- Local inventory-control files: `2`
- Local inventory-control entries: `91`
- Snapshot failures: `0`

## Snapshot role counts

- `acquired_support`: `5`
- `denominator_pressure`: `6`
- `forecast_runway`: `1`

## Credit-cap counts

- `S0`: `7`
- `no-new-credit`: `5`

## Placement disposition counts

- `retained_as_acquired_support`: `57`
- `retained_on_denominator_row_only`: `18`
- `route_local_handoff_only`: `9`

## Upstream checksum states

- `no-upstream-checksum-recorded`: `3`
- `upstream-file-inventory-no-checksum`: `5`
- `upstream-md5-components-recorded`: `1`
- `upstream-md5-manifest-retained`: `1`
- `upstream-sha256-manifest-retained`: `1`
- `watchlist-zero-placement-no-payload`: `1`

## Local payload states

- `not-retained`: `3`
- `not-retained-bulky-external`: `3`
- `not-retained-watchlist`: `1`
- `retained-checksum-manifest-sha256`: `2`
- `retained-inventory-control-sha256`: `2`
- `retained-small-text-sha256`: `1`

## Snapshot rows

| Source ref | Snapshot id | Role | Max cap | Placements | Payload hash status | Checksum state | Local payload | Local files |
|---|---|---|---|---:|---|---|---|---:|
| `REF-0626` | `SSM-REF-0626-DESI-DR2-CHAIN-RELEASE-CUSTODY` | `acquired_support` | `no-new-credit` | `13` | upstream-sha256-checksum-manifest-retained-local-sha256-no-chain-payloads-retained | upstream-sha256-manifest-retained | retained-checksum-manifest-sha256 | `1` |
| `REF-0627` | `SSM-REF-0627-EUCLID-Q1-ZERO-PLACEMENT-WATCHLIST` | `forecast_runway` | `S0` | `0` | watchlist-locator-only-zero-route-placement-no-local-payload-retained | watchlist-zero-placement-no-payload | not-retained-watchlist | `0` |
| `REF-0629` | `SSM-REF-0629-GWTC5-O4B-OPEN-DATA-PAYLOAD-CUSTODY` | `acquired_support` | `no-new-credit` | `12` | upstream-md5-component-hashes-and-md5sums-manifest-retained-local-sha256-exact-zenodo-v2-no-bulky-payloads-retained | upstream-md5-manifest-retained | retained-checksum-manifest-sha256 | `1` |
| `REF-0641` | `SSM-REF-0641-SPT3G-BMODE-DATA-PRODUCTS-CUSTODY` | `acquired_support` | `no-new-credit` | `11` | upstream-file-inventory-no-checksum-no-local-payload-retained | upstream-file-inventory-no-checksum | not-retained-bulky-external | `0` |
| `REF-0642` | `SSM-REF-0642-SPT3G-LAMBDA-BANDPOWERS-LIKELIHOOD-CUSTODY` | `acquired_support` | `no-new-credit` | `11` | small-local-text-sha256-retained-upstream-file-inventory-no-upstream-checksum | upstream-file-inventory-no-checksum | retained-small-text-sha256 | `2` |
| `REF-0688` | `SSM-REF-0688-DESI-DR2-CHAIN-POSTERIOR-DOC-CUSTODY` | `acquired_support` | `no-new-credit` | `10` | upstream-file-inventory-no-checksum-no-local-payload-retained | upstream-file-inventory-no-checksum | not-retained-bulky-external | `0` |
| `REF-0729` | `SSM-REF-0729-ACT-DR6-DATA-PRODUCTS` | `denominator_pressure` | `S0` | `5` | retained-inventory-control-json-sha256-upstream-file-inventory-no-checksum | upstream-file-inventory-no-checksum | retained-inventory-control-sha256 | `1` |
| `REF-0730` | `SSM-REF-0730-ACT-DR6-POWER-SPECTRA-LIKELIHOODS` | `denominator_pressure` | `S0` | `5` | locator-only-no-payload-retained | no-upstream-checksum-recorded | not-retained | `0` |
| `REF-0731` | `SSM-REF-0731-NASA-LAMBDA-ACT-DR6-LENSING` | `denominator_pressure` | `S0` | `5` | retained-inventory-control-json-sha256-upstream-file-inventory-no-checksum | upstream-file-inventory-no-checksum | retained-inventory-control-sha256 | `1` |
| `REF-0732` | `SSM-REF-0732-NANOGRAV-15YR-GWB-SUMMARY` | `denominator_pressure` | `S0` | `4` | locator-only-no-payload-retained | no-upstream-checksum-recorded | not-retained | `0` |
| `REF-0733` | `SSM-REF-0733-NANOGRAV-15YR-EVIDENCE-PAPER` | `denominator_pressure` | `S0` | `4` | locator-only-no-payload-retained | no-upstream-checksum-recorded | not-retained | `0` |
| `REF-0734` | `SSM-REF-0734-NANOGRAV-15YR-PUBLIC-DATA` | `denominator_pressure` | `S0` | `4` | exact-zenodo-v2.1.0-upstream-md5-component-inventory-no-local-payload-retained | upstream-md5-components-recorded | not-retained-bulky-external | `0` |

## Failures

None.

## Non-promotion rule

Source-snapshot rows are custody pointers and replay hooks. A locator/hash record cannot promote a route, upgrade evidence-unit credit, or substitute for a named acquired public data product; every source-custody role in this manifest is capped by the row's declared maximum route-credit cap.

