# INVARIANT-CORE

This note records the current provisional invariant core for TimeSync.

## Current best guess

The invariant core is still best described as:

1. a compact **TimeState**
2. plus a small family of **control surfaces**
3. with explicit **profiles** carrying scenario-specific requirements

The stress-test pass in rev0006 does **not** currently force a larger core.
It does force a clearer boundary.

## What the stress test changed

The six-scenario pass suggests:
- the core must stay small and cross-scenario
- sector thresholds and compliance logic should move outward into profiles
- some precision domains pressure the archive toward time/phase/frequency extensions, but not yet toward expanding the invariant core itself

## Current core documents

- `TIMESTATE.md`
- `CONTROL-SURFACES.md`
- `PROFILE-BOUNDARY.md`

## Current archive judgment

The strongest current posture is:
- keep the core minimal,
- let profiles carry requirement density,
- and keep the greenfield track free to revisit whether a future protocol should unify time, phase, and frequency more directly.
