# Rematch worlds should treat one-shot exact uncertainty anchor retuning as a small exact route atlas

## Claim

For the current saved exact uncertainty menu, steady-mode changes among the canonical anchors `{2, 13, 25}` should be handled as six exact ordered routes rather than as fresh dwell search.

## Why this matters

The archive already knows the canonical anchors and the boundary compass.
What was missing was the chained route picture for one-shot floor changes.
That picture matters because weakening and strengthening are not path-symmetric even when the total dwell shift is symmetric.
Weakening from precision widens in stages.
Strengthening to precision can collapse directly.

## Current exact route atlas

- `near_exact -> near_optimal`: `2 -> 8 -> 13`.
- `near_exact -> lower_guarantee`: `2 -> 8 -> 19 -> 25`.
- `near_optimal -> near_exact`: `13 -> 2`.
- `near_optimal -> lower_guarantee`: `13 -> 19 -> 25`.
- `lower_guarantee -> near_exact`: `25 -> 2`.
- `lower_guarantee -> near_optimal`: `25 -> 18 -> 13`.

## Practical rule

Use the route atlas when a floor change implies a new steady anchor under the current menu.
Do not reopen full dwell search.
If the archive weakens away from precision, widen through `8` first.
If the archive strengthens to precision, collapse straight to `2`.
If the archive weakens into the relaxed suffix, enter `19` before recentering to `25`.

## Status

Derived exactly from the saved boundary-stabilization protocol, floor-retuning compass, boundary-target snapshots, and canonical-anchor labels on 2026-03-08.
