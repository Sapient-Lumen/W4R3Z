# rev0013 worklog

## Goal

Work the rev0012 next target, SEARCH-RESP-01, without broadening into every search-result backlog row.

## Completed

- Built and ran a current-behavior probe for U-163, U-262, U-267, and U-266 support checks.
- Converted the probe into a maintainer-style pytest witness.
- Ran the witness against 3.3.10, 3.3.x, and master.
- Traced token creation, allowed-response gating, FileSearchResponse parsing, response handling, and GUI materialization order across all lanes.
- Refreshed public-overlap status for search-result limits, private-result display, and source/scope binding.
- Refactored the search-response cluster so U-163 is the lead and parser-ordering rows are support/backlog.

## Test result

```text
github-tag-3.3.10: 6 passed
github-branch-3.3.x: 6 passed
github-branch-master: 6 passed
```

## Decision

Promote SEARCH-RESP-01 / U-163 as the third strict report-candidate. Do not promote U-262/U-267/U-266 separately.

## Next

Start FOLDER-RESP-01, led by U-167. Keep U-255/U-260/U-268 as support checks unless source/probe work proves a separate root.
