# BROADER-STATE-SKETCH

This note records the thinnest plausible sketch of a broader-than-`TimeState` object.

It is not a redesign.
It is a pressure sketch.

## Why this note exists

The archive needed a concrete answer to:

If `sync_dimension` eventually stops being enough, what fields would a broader object actually need first?

## Current sketch

If a broader object becomes necessary, the first additional state families are now most plausibly:

1. **`time_error_bound`**
2. **`rate_error_bound`**

But rev0024 keeps this pair explicitly hypothetical.
The phase side still leads slightly overall.
P4 Lane A makes `rate_error_bound` the stronger candidate on that lane.

## Why these fields

### 1. `time_error_bound`
The phase-side quantity is best expressed as time error in time units.
It now survives one break attempt without forcing extra promoted decomposition.

### 2. `rate_error_bound`
Lane A cares about the trustworthiness of local rate relative to a reference.
It also now survives provisionally without forcing a second promoted Lane A semantic.

## Sketch shape

A future broader object might still preserve most of the current narrow waist, while adding:
- `time_interval`
- `time_error_bound`
- `rate_error_bound`
- `timescale`
- `freshness`
- `regime`
- `source_posture`
- `applicability`

This sketch is intentionally sparse.

## Why this is still not promoted

The archive still lacks:
- enough cross-profile evidence that the narrow waist must widen now
- enough evidence that the hook model is failing rather than merely uncomfortable
- enough interface pressure to show that a broader object would change real boundaries rather than just enrich description

## Current archive posture

Keep:
- `TimeState` as the current narrow waist
- `sync_dimension` as the strongest hook
- `time_error_bound` as the current best phase-side candidate
- `rate_error_bound` as the current best Lane A candidate
- the pair as **hypothetical** rather than structural
