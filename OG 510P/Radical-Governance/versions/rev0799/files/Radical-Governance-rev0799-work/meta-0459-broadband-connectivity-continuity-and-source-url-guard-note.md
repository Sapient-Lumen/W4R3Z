# meta-0459 — Broadband connectivity continuity and source URL guard

Revision: `rev0758`  
Timestamp: `2026-06-13 07:49 UTC`  
Codename: `broadbandcontinuity-noaccessbycoveragepolygon-sourceurlguard`

This meta note records the rev0758 maintenance and substantive pass.

## Substance

The revision adds notes `950` and `951` for broadband, telecommunications, digital access, provider availability, Lifeline, ACP, BEAD, outages, public-service portals, devices, community anchors, complaints, and connectivity remedy continuity. The packet treats coverage maps, provider availability claims, speed tiers, broadband labels, subsidy rows, dashboards, outage filings, and portal uptime as separate evidence lanes.

The governing rule is **no access by coverage polygon**.

## Refactor

`tools/lint_archive.py` now checks that current-revision source-catalog group values match the canonical source-key registry for `title`, `publisher`, and `url`. This catches a real copy-forward failure: a new packet could previously pass with matching source-key names while silently pointing a key at the wrong URL or publisher string.

## Validation intent

Run `make lint`, then extract the linked ZIP and run `make lint` again before treating the revision as packaged.
