# RATE-ERROR-BOUND

This note proposes the archive's thinnest current candidate for a first-class Lane A field.

## Why this note exists

The archive no longer needed another structural split.
It needed a smaller semantic answer to this question:

If P4 Lane A ever forces a field beyond the current hook model, what is the smallest useful field?

## Current best candidate

**`rate_error_bound`**

### Proposed meaning
A bound on how far the local rate may differ from the relevant reference rate over the **current validity window** and under the **current regime**.

This is intentionally thinner than a full telecom clock-quality model.

## Current confidence

rev0019 and rev0020 pressure-tested this candidate.
It now survives provisionally as the archive's best Lane A field candidate.
It survives because neighboring semantics appear to carry the rest of the pressure without yet forcing another promoted field.

## Why this candidate beats vaguer alternatives

### 1. Better than a bare `frequency_offset`
A bare offset says where the rate is pointed right now.
It does not say enough about uncertainty, continuity, or what holdover is doing to trust in that rate.

### 2. Better than a bare `stability_class`
A stability label says something about consistency.
It does not by itself say whether the local rate is acceptably near the reference rate over the present validity window.

### 3. Better than a boolean syntonized / not-syntonized flag
Lane A pressure is too consequence-sensitive for a binary flag.
The archive needs something bounded, not merely categorical.

## Why this candidate fits the source pattern

The recurring source pattern is not one metric name.
It is a family of concerns:
- frequency accuracy or offset
- stability over an interval
- drift under holdover
- continuity of the delivered rate

`rate_error_bound` is an attempt to compress that family into one thin externalized field.

## Boundary with existing fields and hooks

### Not the same as `holdover_class`
`holdover_class` describes the expected holdover posture or envelope.
`rate_error_bound` describes the currently claimable bound on rate error.

### Not the same as `sync_dimension`
`sync_dimension` says which synchronization kind matters.
`rate_error_bound` is a first-class bound when Lane A needs more than a hook.

### Supported by existing state
This candidate depends on neighboring semantics already present in the archive:
- `freshness`
- `regime`
- `holdover_class`

## Current archive posture

If Lane A ever forces the archive beyond the hook model, the current best first candidate remains:

**`rate_error_bound`**

with no second promoted Lane A semantic yet justified.
