# rev0093 audit/refactor note — temporal coherence reuse

## Problem

The archive had strong temporal-coherence rules for scope composition, but other surfaces still encoded timestamp relationships inline. That made it easy to miss one relationship per feature. The highest-risk misses were post-evaluation observations being used as if they supported earlier current state.

## Implemented

- `tools/temporal_coherence.py` now provides small timestamp-relation helpers.
- `tools/validate_archive.py` imports `parse_dt` from that module instead of maintaining a duplicate local parser.
- Replay transparency now rejects checkpoint consistency checks after anchor evaluation.
- Witness/monitor evaluation now rejects observations after anchor evaluation.
- Transparency trust-policy lifecycle now rejects revocation or drift checks after the lifecycle evaluation.
- Aggregate lifecycle rollups now reject rollup windows ending after aggregate artifact creation/publication.
- The helper has a self-test entry point and is invoked from the main validator.
- The scope-composition decision-matrix path remains single-pass; the next decomposition pass should continue removing redundant validation paths where they appear.

## Why this was prioritized

Digest canonicalization had already been made executable in rev0092. The remaining high-risk class was temporal backfill: evidence collected later but accepted as support for an earlier current decision. The change is narrow, executable, and verified with negative fixtures.

## Non-goals

- No new registry.
- No new TimeState field.
- No promotion of transparency, witness, lifecycle, or aggregate metadata into provenance.
- No broad rewording of every spec file.
