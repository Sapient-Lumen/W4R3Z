# P4-LANES

This note splits the current precision-network profile into its two strongest pressure lanes.

## Why this note exists

rev0015 showed that telecom pressure was no longer helping as a single block.
It was producing contradictory signals because it bundled together two different demands.

This note makes that split explicit.

## Lane A — frequency continuity / syntonization

### What it is
A lane where the primary demand is that distributed oscillators or network elements maintain sufficiently aligned **rate**.
Absolute time-of-day or exposed phase alignment may be secondary, unavailable, or only indirectly relevant.

### What the source pattern looks like
This is where SyncE-like distribution, stratum-style quality language, one-way packet frequency pathways, and rate masks or ppm-style requirements show up.

### What it pressures first
If this lane drives redesign, the first missing field is more likely:

**bounded frequency state**

than bounded phase error.

### What it especially cares about
- continuity of rate reference
- stability / drift class
- holdover quality
- whether the frequency story is still traceable or only locally sustained

## Lane B — phase / time alignment

### What it is
A lane where neighboring or distributed nodes must stay aligned in relative time / phase closely enough for coordinated operation.
Time-of-day and frequency still matter, but exposed alignment error is the sharper external concern.

### What the source pattern looks like
This is where TDD coordination, phase-sensitive transfer, two-way packet timing, and sub-microsecond alignment requirements show up.

### What it pressures first
If this lane drives redesign, the first missing field is more likely:

**bounded phase error**

than bounded frequency state.

### What it especially cares about
- relative alignment error
- topology/path effects on transfer
- holdover plus re-entry semantics after loss of reference
- whether the current claim is globally grounded or only locally serviceable

## Structural judgment

rev0017 keeps these as lanes inside one profile rather than promoting them into two profiles.
See `P4-COHESION.md`.

## Current archive judgment

P4 is one profile with two lanes:
- Lane A = frequency-first pressure
- Lane B = phase-first pressure

That means P4 no longer counts as evidence for a single uniform answer to the first-missing-field question.
