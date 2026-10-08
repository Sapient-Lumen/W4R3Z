# HOLDOVER-CLASS-TEST

This note tests whether `holdover_class` should join the archive's `profile_default` tier.

## Question

Do demanding profiles require a richer reusable `holdover_class` to be default-visible,
or do they mainly require default visibility of:
- holdover state
- degraded regime
- and timing quality while in holdover?

## Comparison

### P4 — Precision network / telecom timing

Telecom timing strongly requires that downstream clocks learn when:
- the reference is no longer acceptable
- holdover has begun
- a backup path is being selected
- and quality/state messages have changed

That is strong evidence for default-visible:
- state
- quality level
- selection outcome

It is **not** yet equally strong evidence for a reusable cross-profile `holdover_class`.
The archive still sees the richer class as dependent on:
- local oscillator quality
- network design
- profile assumptions
- and implementation-specific envelopes

### P5 — Critical infrastructure precision timing

Power-profile material also strongly supports visible holdover **state**.
The sources describe indicators that become active in unlocked or holdover conditions,
and timing quality remains visible while the device is in that condition.

Again, this is strong evidence for:
- state visibility
- quality visibility
- usability consequences

It is weaker evidence for a generic reusable `holdover_class` that every demanding boundary must see by default.

### P6 — Local continuity / survival

This profile pressures holdover semantics heavily,
but mainly by showing how device capability varies with:
- oscillator type
- steering method
- learned behavior
- and outage duration

That variation makes the case for a richer class **inside** a profile or implementation.
It does not yet make the case that the same class should be default-visible across multiple profile boundaries.

## Current judgment

`holdover_class` does **not** yet join `profile_default`.

The archive should keep distinguishing:
- **holdover state / regime / quality** — often default-visible
- **holdover_class** — still richer, more contextual, and not yet proven reusable enough for the tier

## Why this matters

Without this distinction,
the archive would confuse:
- a live state transition that downstream systems must know about
with
- a richer descriptive class that may still be useful but is not equally portable

That would make the new tier too easy to enter.

## Consequence for the tier

The `profile_default` tier remains intentionally small.
Current members stay:
- `traceability_posture`
- `sync_dimension`

Still outside:
- `holdover_class`
- `validity_scope`

## Next useful move

Test `validity_scope` by the same standard:
repeated evidence of default-visible need across multiple demanding boundaries,
not merely strong importance in one branch of the archive.
