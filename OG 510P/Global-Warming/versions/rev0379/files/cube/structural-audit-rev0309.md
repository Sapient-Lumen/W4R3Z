# Structural audit rev0309

Created: 2026-06-04T04:31:00-04:00

## Highest-risk correction

Rev0308 created a necessary local-evidence spine but it still had no localized rows. Rev0309 adds a worked, synthetic localization layer so the cube can actually fail rows, cap maturity, and prioritize closure work.

## What is now executable

- 4 synthetic site fixtures.
- 14 synthetic offsite-jurisdiction fixtures.
- 1,056 synthetic local evidence rows generated from the 264 sparse emergency-preparedness proof slots.
- 124 computed readiness scorecard rows: 120 site/floor rows and 4 site-overall rows.
- 857 open fixture gap burn-down rows.
- 80 exercise-result rows.
- 33 emergency-plan change-effectiveness review rows.
- 16 performance-objective metric rows.

## Remaining structural debt

The three 114,494-row universal nuclear crossproduct tables remain in the package for compatibility. They should not be used as canonical emergency-preparedness applicability or readiness proof. The canonical emergency path is now sparse applicability -> local evidence -> exercise/CA closure -> scoring -> gap burn-down.

## SQLite scope

`cube/datacube-rev0309-emergency.sqlite` is a scoped emergency mirror, not a full archive mirror. It exists to make the new high-risk surfaces queryable without expanding the package by hundreds of megabytes.
