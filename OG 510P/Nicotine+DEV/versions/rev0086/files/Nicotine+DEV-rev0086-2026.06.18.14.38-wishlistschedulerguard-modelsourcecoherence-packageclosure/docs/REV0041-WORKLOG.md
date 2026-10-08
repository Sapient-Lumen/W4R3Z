# rev0041 worklog

## Inputs

- Continued from rev0040 linked cube.
- Used the external rev0003 upstream source bundle for source traces and lane verification.

## Work performed

1. Selected the held search-response parser-budget row instead of the room-source row.
2. Split the row into a promotable pre-token username-prefix cap and a held accepted-list materialization row.
3. Added `test_search_response_prefix_budget_fixed_regression.py`.
4. Selected a parser-local `MAX_SEARCH_RESPONSE_USERNAME_LENGTH = 255` guard.
5. Generated selected patch diffs for `github-tag-3.3.10`, `github-branch-3.3.x`, and `github-branch-master`.
6. Source-traced the legacy and master parser shapes.
7. Recorded lane-by-lane rerun evidence: current witness, current fixed regression failure, selected patch pass, and old-witness inversion.
8. Added production report, fix skeleton, queue deltas, strict-promotion data, public-overlap note, and coherence refactor.
9. Repackaged as a compact cube with no embedded source tree.

## Result

`SEARCH-RESP-PARSE-BUDGET-A` is now production-gated inside the cube. `SEARCH-RESP-PARSE-BUDGET-B`, `SEARCH-RESP-01C-ROOM`, and `U-138` remain held/deferred.
