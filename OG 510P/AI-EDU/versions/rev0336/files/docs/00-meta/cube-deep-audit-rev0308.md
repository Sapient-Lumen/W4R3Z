# rev0308 cube deep audit

## Highest-risk seam inspected

The highest-risk unfinished path remains the returned-owner-evidence rail. The
cube has enough machinery to prepare packets, route sends, intake returned CSVs,
seed workbench review, record first decisions, prepare post-decision tickets,
record activation receipts, bridge live windows, and prepare post-readout loops.
But no real owner packet has arrived. That makes source-chain hygiene more
important than adding more doctrine.

The `rev0307` activation-packet firebreak closed one near-acceptance argument:
`SOURCE_PACKET`. This audit found the broader version of the same flaw. Direct
CLI source paths and embedded provenance references could still point at
checker, release, legacy, smoke, test, or fixture scratch if the artifact's
embedded hashes and source fields matched. That was too much trust in content
integrity and not enough trust in lane provenance.

## Correction made

`tools/ft0181_field_guards.py` now includes `field_scratch_lane_error()`, a
shared guard for local `FT-0181` source-chain artifacts. Tools that accept source
artifacts now reject archive-local paths unless they resolve under
`scratch/field/ft0181/`. Embedded provenance checks also reject references to
non-field scratch lanes.

The validator harness was refactored so positive source chains live under
`scratch/field/ft0181/validation/...`. Checker scratch is still used for negative
cases and checker outputs, but not as the source of an artifact that would drive a
later field action.

A new regression copies a valid first-packet decision into checker scratch and
proves a post-decision change ticket rejects it with a field-lane error rather
than accepting it by hash lineage alone.

## What was intentionally not added

No schema family, branch family, or new queue item was added. The fix is
operational: one field-lane source guard, direct tool checks, embedded provenance
checks, and focused regression coverage. This keeps the cube moving toward the
real unblocker instead of expanding the bureaucracy around a missing packet.

## Next useful work

The next practical pass should continue compressing human-owned review and
decision dockets so a real returned packet can move through the field lane with
less operator friction. Do not add broad policy unless a real owner packet exposes
a concrete failure.
