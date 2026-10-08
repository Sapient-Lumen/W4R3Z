# Changelog rev0324

- Added packet dry-run bundle catalog, field-value rows, validator result, adjudication queue, chain-of-custody break audit, loss-cap application, public-claim state, and negative controls.
- Added executable `tools/import_nuclear_emergency_bvps_packet_bundle_rev0324.py`.
- Added scoped SQLite mirror `cube/datacube-rev0324-emergency.sqlite`.
- Corrected root-level `schema.json`, which lagged at rev0322 in the rev0323 package.
- Preserved no-real-readiness-claim boundary for `REAL_BVPS_PUBLIC_ONLY`.
