# TIME-ERROR-BOUND

This note proposes the archive's thinnest current candidate for a first-class phase-side field.

## Why this note exists

The archive needed to bring the same semantic discipline to the phase side that it had started to apply on Lane A.

The older phrase **bounded phase error** was useful, but still too loose.

## Current best candidate

**`time_error_bound`**

### Proposed meaning
A bound on the deviation, in time units, between the practical clock signal and the relevant reference over the current validity window and under the current regime.

## Current confidence

rev0022 pressure-tested this candidate.
It now survives provisionally as the archive's best phase-side field candidate.
It survives because richer time-error decomposition and quality encodings have not yet forced another promoted generic field.

## Why this name is better

### 1. It matches the source language
The source base repeatedly treats **time error** as the phase-side quantity, often explicitly saying that time error and phase error are synonymous.
The time-oriented wording is useful because the quantity is expressed in time units.

### 2. It is thinner than a metric catalog
This note does **not** promote:
- MTIE bundles
- TIE traces
- static/dynamic decomposition as separate first-class fields
- full packet-clock test surfaces

Those remain profile-local.

### 3. It is more honest than a vague phrase
"Bounded phase error" names a family of concerns.
`time_error_bound` names a candidate field.

## Boundary with existing fields and hooks

### Not the same as `rate_error_bound`
`rate_error_bound` is about rate alignment relative to a reference.
`time_error_bound` is about phase/time deviation relative to a reference.

### Not the same as `sync_dimension`
`sync_dimension` says which synchronization kind matters.
`time_error_bound` is a first-class bound when the phase/time side needs more than a hook.

### Supported by existing state
This candidate also leans on neighboring semantics already present in the archive:
- `freshness`
- `regime`
- `holdover_class`

## Current archive posture

If the phase side ever forces the archive beyond the hook model, the current best first candidate remains:

**`time_error_bound`**

with no second promoted phase-side semantic yet justified.
