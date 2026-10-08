# Release refresh asset-index repair audit rev0834

This audit records and validates a concrete release-refresh repair: asset indexes are archive-identity inputs and must be rebuilt before `RELEASE_MANIFEST.json`, RO-Crate, `INDEX/files.*`, and `MANIFEST.sha256` are emitted.

- Status: `asset_index_refresh_cycle_repaired`
- Blockers: none

## Pre-repair observation

- validate_asset_indexes.py was not part of the rev0833 selected release-refresh validation set.
- asset-index-validate failed on artifacts/curated/zkrtp_v2/policy_report.json after prior payload rewrites changed the file without refreshing artifacts/ARTIFACTS_INDEX.*.

## Current asset-index file snapshot

| File | Rows | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `artifacts/ARTIFACTS_INDEX.json` | 219 | 55806 | `2c5ed7dba1eb9b197f8dd2f51ae9cabfc1b2b5569ecffbfc2e63ced5223aaa4d` |
| `artifacts/ARTIFACTS_INDEX.csv` | 219 | 36781 | `058d36b4fe885ad7d6f40e9578088a7025d4d8f7ace76eaf9fcd9923c2548a9a` |
| `certs/CERTS_INDEX.json` | 116 | 30013 | `ac633c40ce8df25aad31e12de53c51d0d3d989c5d2c9253314b86c4e0df2cbf7` |
| `certs/CERTS_INDEX.csv` | 116 | 19949 | `b2babcf1447fd39747fcc992b94c3a403c36a7caf3437ecce192988c155b8671` |

## Refresh order

- `rebuild_indexes.py` includes `build_asset_indexes.py`: `true`
- Required order satisfied: `true`

Required order:

1. refresh_cycle_safe_material_surfaces() including build_asset_indexes
1. refresh_release_manifest_identity()
1. refresh_ro_crate_metadata()
1. final INDEX/files.* and MANIFEST.sha256 emission

## Final manifest/index checks

MANIFEST.sha256 and INDEX/files.* are emitted after material audit builders run; embedding their currentness here would create a generated-surface ordering false positive.

Checked by `scripts/validate_release_refresh_asset_index_rev0834.py`.
