# Rev346: make plain `marks` inventory legible too

Rev337 made **placing** a mark explicit, and rev333 already made **jumping** to one explicit.
That left one small low-frequency-but-important gap: the plain `marks` command still flattened everything to `name -> buffer:line:col` tuples.

That message was technically correct, but lower-fidelity than the rest of the current navigation story:

- `mark NAME` already says exactly what target it anchored
- `markjump NAME` / `markpick` already say exactly where they landed
- `buffers` and `recent` already grew tiny inspectable inventories instead of raw names/paths

Rev346 keeps the change deliberately small.

## What changed

`marks` now formats each entry as a tiny inspectable target instead of a raw tuple:

- owning buffer gets the same `*` active marker used elsewhere
- the mark that matches the **current primary cursor** also gets a `[here]` cue
- locations keep the existing `@ line:col` target spelling

Example:

- `marks: 2 mark(s), here -> *alpha [here] @ 2:0; there -> beta @ 1:1`

## Why this matters

The point is not to make `marks` flashy.
The point is to keep plain inventory from being the lowest-fidelity dialect in the feature.

A user glancing at `marks` should be able to tell:

- which marks belong to the active buffer
- whether one of those marks is exactly the cursor they are standing on now
- where the other anchors live

That keeps the tiny navigation loop coherent:

- **place a mark** → explicit anchor target
- **list marks** → explicit, glanceable inventory
- **jump to a mark** → explicit landed target

## Scope discipline

This is intentionally not grouped sections, persistence, or richer bookmark management.
Those may still come later.

For now the goal is simpler:
plain mark inventory should be legible without opening a picker or reverse-engineering raw tuples.
