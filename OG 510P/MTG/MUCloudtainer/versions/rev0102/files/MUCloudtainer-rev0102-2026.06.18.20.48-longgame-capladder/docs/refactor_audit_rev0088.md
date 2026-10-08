# rev0088 refactor audit

## Code refactor

`src/muc5/population_candidate_gate.py` now owns three reusable surfaces:

1. dynamic candidate-gate family discovery,
2. explicit false/metadata schema checks for adaptive candidate evidence,
3. the previous score/mechanism/pool-leak gate.

This avoids adding another one-off script for the next candidate. New adaptive sampling designs now produce their own component rows and tighten the family correction automatically.

## Evidence footprint

rev0088 ships compact CSV/JSON only:

- 1 gate summary row
- 6 component rows
- 8 leak-audit rows
- 4 schema-contract rows

It does not ship new games, replay traces, or transition logs.

## Cold evidence

The rev0072 cold sidecar remains immutable and unchanged. rev0088 carries forward the latest evidence tiering catalog under a rev0088 filename so finalization can validate latest-catalog semantics without materializing cold raw evidence.
