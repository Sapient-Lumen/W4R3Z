# CHANGELOG rev0312

Created: 2026-06-04T07:03:56-04:00

## Added

- Corrected emergency-readiness scorecard recomputed from mutually exclusive local evidence statuses.
- Score-state mutual-exclusion audit showing rev0311 scorecard overlap/omission rows.
- Twelve minimum viable readiness thresholds.
- Executable public-signal ingest contract, fixture, validator script, validator result table, and run summary.
- Public-signal source register, conflict resolver, scorecard overlay, and blocker-to-signal map.
- Eight compact closure workpacks for open counterevidence.
- Scoped rev0312 emergency SQLite mirror and query views.

## Changed

- Current emergency-readiness queries should use `nuclear-emergency-readiness-scorecard-corrected-rev0312.csv`, not the rev0311 adjudicated scorecard.
- Public records can cap/reopen/readiness-check claims but cannot satisfy local capacity/closure thresholds alone.

## Not changed

- The three 114,494-row universal nuclear crossproduct tables remain compatibility surfaces only.
- The package still does not claim any real nuclear site is ready or unready.
