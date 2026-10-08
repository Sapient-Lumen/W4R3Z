# rev0024 audit/refactor notes

## Focus refactor

The priority list and porch docs were refreshed so the active P0 list is performance-core again: routing, sparse attention, decomposition, speed guards, and native phase diagrams.

## Native refactor

- Added five C++ probes and marked them as fresh current-revision code in `REVISION-RECEIPT.json`.
- Carried forward previous native smoke artifacts with explicit `carry_forward_from: rev0023` markers.
- Updated native probe output mapping for the new probes.
- Extended the performance core report to include the new rev0024 performance probes.

## Watch item

Carry-forward artifacts remain useful for continuity, but the next full hardening turn should rerun or HPO-sweep one P0 family rather than growing the probe count indefinitely.
