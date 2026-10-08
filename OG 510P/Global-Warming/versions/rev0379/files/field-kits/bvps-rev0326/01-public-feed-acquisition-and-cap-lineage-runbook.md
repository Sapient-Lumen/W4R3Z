# BVPS rev0326 public-feed acquisition and CAP-lineage runbook

This runbook is for the public-feed side of the June 2026 Beaver Valley evidence capture path.
It does not authorize any readiness, safety, pass/fail, green, or closure claim.

## Sequence

1. Preserve local/anonymized alert-originator, EAS, WEA/IPAWS, siren/SNB, JIC, county alert, and evaluator artifacts first.
2. After the archive-delay window, run the OpenFEMA county-window IPAWS queries in `cube/nuclear-emergency-bvps-ipaws-archive-query-set-rev0326.csv`.
3. Run the state-prefix and geospatial backstops if county queries return no rows or incomplete geocodes.
4. Hash the raw response before parsing.
5. Normalize with `tools/normalize_ipaws_cap_archive_rev0326.py`.
6. Resolve CAP `Update`, `Cancel`, `Error`, duplicate, expired, and geocode-gap states before any public-message board.
7. Join public archive context to local custody packets. Archive-only evidence remains no-upgrade context.

## Invariants

- No public archive record closes local alert readiness.
- No missing public archive record proves no alert occurred.
- CAP Update/Cancel/Error rows can reopen or hold claims.
- Source aliases count once via `source-canonical-url-map-rev0326.csv`.
- Synthetic fixtures in this revision are parser tests only.

## Live command shape

```bash
python tools/acquire_nuclear_emergency_bvps_public_feeds_rev0326.py   --contract cube/nuclear-emergency-bvps-public-feed-acquisition-live-contract-rev0326.csv   --output cube/nuclear-emergency-bvps-public-feed-acquisition-live-result-rev0326.csv   --raw-dir quarantine/public-feed-raw-rev0326   --live
```

Then normalize IPAWS JSON artifacts:

```bash
python tools/normalize_ipaws_cap_archive_rev0326.py   --input quarantine/public-feed-raw-rev0326/<raw-ipaws-file>.json   --output cube/nuclear-emergency-bvps-cap-normalized-live-rev0326.csv
```
