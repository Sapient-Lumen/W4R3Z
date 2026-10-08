# DEFAULT-VISIBILITY-TEST

This note tests whether the greenfield `traceability_posture` hook must appear in the default client-visible state,
or whether a native optional extension preserves nearly all of the value.

## Question

Is `traceability_posture`:
- archive-core visible,
- merely optional,
- or something in between?

## Comparison

### P3 — Financial timing

Finance strongly needs timing that is accurate, traceable, and verifiable.
But much of that pressure lands on:
- service design
- calibration
- verification
- audit replay
- and compliance-facing evidence

That means a generic runtime client does not always need the hook in its smallest default state.
The boundary-bearing requirement can often be met at a stronger service or audit boundary.

### P4 — Precision network / telecom timing

This profile behaves differently.
Synchronization status and quality are used live to:
- avoid timing loops
- support reference selection
- detect status failure
- and manage holdover / backup behavior

Here, an optional traceability-like signal is too weak inside the synchronization control plane.
The relevant participants need the state by default.

### P5 — Power / synchrophasor timing

This profile is the clearest case.
The measurement boundary itself expects time quality and traceability-adjacent state.
If the hook were merely optional,
a client or measurement endpoint could see a bounded time claim without seeing whether it is UTC-traceable in the required way.
That is too lossy for this boundary.

## Current judgment

The archive does **not** yet have enough pressure to promote `traceability_posture` into the global minimal core.
But it also no longer looks correct to call it merely an optional extension everywhere.

The current best fit is:
- **not core by default across the whole archive**
- **native extension globally**
- **profile-default at boundaries where omission would mislead live control or measurement participants**

## Why this middle position is better

It preserves the reduction work:
- the minimal core does not grow yet
- the hook remains real and native
- demanding profiles are allowed to require it by default
- the archive avoids pretending that all clients are alike

## Provisional archive language

A hook may be:
- optional in the archive-wide abstract sense
- but default-visible in a profile boundary where it is operationally load-bearing

That is the current status of `traceability_posture`.

## Consequence for the greenfield track

A greenfield TimeSync design should treat `traceability_posture` as:
- natively representable everywhere
- default-visible in P4/P5-like boundaries
- and still omittable from the thinnest generic state where no concrete boundary yet forces it

## What this still does **not** justify

This still does not justify:
- adding the hook to the minimal core everywhere
- turning every profile into a status-heavy control protocol
- or inventing a larger traceability subsystem

## Next useful move

Test whether the archive now needs a small named tier between:
- minimal core
- and fully optional extensions

because `traceability_posture` may be the first hook that is **profile-default** without being core.
