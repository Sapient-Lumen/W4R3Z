# meta-0458 — Transportation mobility continuity and current-matrix case-example guard

Revision: `rev0757`  
Timestamp: `2026-06-13 07:12 UTC`  
Codename: `transitcontinuity-nomobilitybytriprow-caseexampleguard`

This meta note records the rev0757 maintenance and substantive pass.

## Substance

The revision adds notes `948` and `949` for transportation, transit, paratransit, fare, accessibility, realtime, Title VI, safety, asset, rural/tribal, and rider-outcome continuity. The packet treats schedules, GTFS, NTD rows, National Transit Map rows, paratransit eligibility, fare accounts, civil-rights filings, safety plans, and asset targets as separate evidence lanes.

The governing rule is **no mobility by scheduled trip row**.

## Refactor

`tools/lint_archive.py` now requires the current-revision registered operational test matrix to include the current applied case packet as a case example in every test. This catches a real copy-forward failure: a new packet could otherwise ship with a matrix that names the current notes but does not actually exercise the applied case.

## Validation intent

Run `make lint`, then extract the linked ZIP and run `make lint` again before treating the revision as packaged.
