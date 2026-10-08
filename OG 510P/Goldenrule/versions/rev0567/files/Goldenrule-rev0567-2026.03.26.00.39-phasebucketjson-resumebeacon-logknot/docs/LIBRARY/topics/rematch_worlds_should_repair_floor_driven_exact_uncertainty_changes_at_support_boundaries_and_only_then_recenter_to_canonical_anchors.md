# Rematch worlds should repair floor-driven exact uncertainty changes at support boundaries and only then recenter to canonical anchors

## Claim

When a floor change forces retuning on the current saved exact uncertainty menu, the first move should land on the nearest surviving support boundary, and only a second, optional stabilization move should recenter to the destination band's canonical anchor if that band becomes the new steady operating mode.

## Why this matters

The boundary compass `{2, 8, 18, 19}` solves a different problem from the canonical labels `{2, 13, 25}`.
The boundary points restore feasibility quickly.
The canonical anchors give stable inheritor-facing names for steady modes.
Mixing those two jobs causes unnecessary interior search and brittle handoffs.

## Current exact protocol

- Strengthening from the relaxed suffix `[19,32]` into the strong non-fragile band lands on boundary `18` first; steady operation in that band recenters to canonical anchor `13`.
- Weakening from precision singleton `{2}` into the strong non-fragile band lands on boundary `8` first; steady operation in that band also recenters to canonical anchor `13`.
- Weakening from the strong non-fragile band `[8,18]` into the relaxed suffix lands on boundary `19` first; steady operation in the relaxed suffix recenters to canonical anchor `25`.
- High-floor strengthening above `0.980481` lands directly on `2`, because the boundary and the canonical anchor coincide in the precision singleton.

## Practical rule

Use the boundary compass for the first repair step.
Treat `8`, `18`, and `19` as transient feasibility landings by default.
Only after the destination band is chosen as the new steady mode should the archive stabilize inward to `13` or `25`.

## Status

Derived exactly from the saved floor-retuning compass, target-dwell atlas, and canonical-anchor snapshots on 2026-03-08.
