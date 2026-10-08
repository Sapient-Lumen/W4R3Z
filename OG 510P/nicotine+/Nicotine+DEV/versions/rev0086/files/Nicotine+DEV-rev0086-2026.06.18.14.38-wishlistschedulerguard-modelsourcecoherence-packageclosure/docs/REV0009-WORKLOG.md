# rev0009 worklog

## Main work

- Re-ran the U-123 socket-limbo probe across the three archived source lanes.
- Built a `unittest`-style U-123 current-behavior reproducer and ran it across the same lanes.
- Wrote a concise U-123 maintainer report skeleton and fix acceptance criteria.
- Built a handler-level U-269 upload-completion lifetime probe and ran it across the three lanes.
- Performed public-overlap refresh for U-123, U-269, and U-270.
- Refactored the transfer/search lifetime cluster to prevent incoherent combined fixes.

## Outcome

- Strict document remains at **1 report-candidate**, **0 production-ready disclosure texts**.
- U-123 is materially stronger and easier to hand off.
- U-269 is confirmed but not promoted.
- U-270 is demoted from immediate strict pursuit due public-adjacent release-note overlap.

## Why this is forward movement

The cube now has an actual maintainer-grade packet for the highest-value candidate, plus a negative/pruning result for two likely distractions. This should reduce future wasted work and make the final strict document more defensible.
