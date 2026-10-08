# Rematch worlds should treat full precision exact-uncertainty relaxed release as a two-bundle composition

## Claim

The current exact-uncertainty weakening menu has only two primitive recovered savings bundles: middle-band precision relief and relaxed-suffix release. The full precision-anchor relaxed release is not a third primitive; it is the exact composition of those two primitive bundles.

## Why this matters

- It shrinks the inheritor's mental model from three apparently unrelated value classes to two primitives plus one composite.
- It explains why the full precision release threshold is exactly `23`: it is `11 + 12`, the sum of the primitive leg burdens `2→13` and `13→25`.
- It gives a clean audit target: if a future redesign breaks vector additivity or scalar burden additivity here, the weakening menu changed in substance rather than only in labeling.

## Current exact relation

- primitive bundle A: middle-band precision relief (`budget step 2`, threshold `11`)
- primitive bundle B: neutral-anchor relaxed release (`budget step 3`, threshold `12`)
- composite bundle C: full precision-anchor relaxed release (`budget step 5`, threshold `23`)

And exactly:

- `savings(C) = savings(A) + savings(B)`
- `threshold(C) = threshold(A) + threshold(B)`
- `route_shift(C) = route_shift(A) + route_shift(B)`

## Operational reading

The one-shot direct precision-to-relaxed route may compress the transient path and omit an explicit neutral-anchor stop, but its scalar move burden and recovered steady-state value remain exactly equal to the two primitive legs composed.
