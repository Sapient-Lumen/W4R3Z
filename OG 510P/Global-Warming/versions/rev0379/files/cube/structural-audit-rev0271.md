# Structural audit — rev0271

## Audit findings from rev0270

- Numbered Markdown files ran cleanly from `00` through `315`.
- `cube/index.csv` had 316 rows and no bad numeric `routes_to` targets.
- All cited source IDs resolved in `sources/register.md`.
- Two registered sources were unused before this revision: `S336` and `S516`.
- Files `297`–`315` had H1 headings that did not begin with their numeric ID.
- Files `301`–`307` lacked the richer front matter used by `308`–`315`.
- The cube schema did not yet expose front-matter fields that newer files were already using: `bottlenecks`, `failure_modes`, and `proof_ledgers`.

## Repairs made in rev0271

- Added YAML-style front matter to `297`–`307`.
- Normalized H1 headings for `297`–`322` so they begin with the numbered ID.
- Routed previously unused `S336` into the delivery / siting doctrine and `S516` into the energy-continuity doctrine.
- Expanded `cube/schema.json` and `cube/index.csv` with `bottlenecks`, `failure_modes`, `proof_ledgers`, `restoration_conflicts`, and `assurance_tests`.
- Added `cube/hidden-rails-readiness.csv`.
- Extended `cube/interdependency-matrix.csv` and `cube/service-floor-checklist.csv` with hidden-rail rows.

## Remaining known issue

The source register still contains duplicate or near-duplicate source entries from earlier revisions. rev0271 does not renumber them because doing so would break stable source references across hundreds of files. A future source-register normalization pass should add alias/supersession metadata rather than deleting IDs.

## Readiness rule added

A service floor is no longer marked ready merely because the cube names dependencies. It should now provide a drillable assurance claim: degraded mode, excluded-user test, restoration-conflict rule, proof ledger, and correction path.

---
Citations point to `sources/register.md`.
