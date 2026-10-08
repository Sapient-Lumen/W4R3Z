# PAIR-VS-APPLICABILITY

This note asks whether the provisional pair actually earns its place relative to the existing `applicability` signal.

## Question

If the archive already has `applicability`,
do `time_error_bound` and `rate_error_bound` add anything important,
or can applicability absorb most of their practical value?

## Current judgment

The provisional pair **does** earn its place.

But its role is narrower than a second decision system.

### Division of labor
- `applicability` says what downstream systems should do
- the provisional pair says why that judgment is currently justified and where thresholds come from

## Why applicability alone is not enough

### 1. Applicability is consequence-facing and coarse by design
A label like "usable for X, not for Y" is valuable,
but it intentionally compresses information.
That compression becomes a problem when different profiles apply different thresholds to similar timing states.

### 2. Some profiles already expose bound-like usability signals
The source base includes profile-local time-quality indications and explicit timing tolerances that are plainly about bounded usability, not just a categorical yes/no state.
That means bound-bearing information is already doing real work in the world.

### 3. Bounds travel better across profiles than sector-specific applicability labels
A telecom-oriented applicability label and a power-oriented applicability label are not naturally interoperable.
A bound gives those profiles something more shared to reason from.

## Minimal comparison

### Case 1 — P5 synchrophasor / phase-angle use
`applicability` can say whether the state is usable.
But a time-error-oriented bound explains why the state crossed the usability line and allows profile-specific thresholds to be interpreted consistently.

### Case 2 — P4 Lane A base-station frequency tolerance
`applicability` can say whether telecom use remains acceptable.
But a rate-oriented bound carries the actual tolerance-facing signal that explains the judgment.

### Case 3 — P1 general computing
Here `applicability` often does most of the practical work.
The provisional pair may remain latent or implementation-local.
This is a feature, not a problem.

## What the pair is not

The pair is **not** a replacement for applicability.
It is a more reusable substrate beneath it.

## Current archive posture

Keep:
- `applicability` as the coarse consequence signal
- `time_error_bound` and `rate_error_bound` as the current best explanatory bound layer if the archive ever widens

Do **not** yet promote the pair into the core.
This note only argues that the pair adds real value beyond applicability.
