# SYNC-DIMENSIONS

This note records the current archive judgment on time, phase, and frequency as distinct synchronization dimensions.

## Why this note exists

The archive kept encountering pressure that did not fit comfortably inside a pure timestamp story.
This pressure is now strong enough to name directly.

## Current judgment

TimeSync should **not** yet broaden its core object.
But it should explicitly admit that some profiles are not only about time-of-day.

The archive therefore keeps `sync_dimension` as a hook while postponing any broader redesign.

## Dimension distinctions

### Time
Alignment of epoch / time-of-day claims.

### Phase
Alignment of signal or cycle relationship in time.
Often matters when coordinated action depends on precise relative timing.

### Frequency
Alignment of rate or syntonization, even when absolute time-of-day is not the main concern.

## Why this matters

Different profiles pull on different combinations:
- finance pulls hardest on time and traceability
- telecom often pulls on phase, frequency, and time-of-day together
- grid / infrastructure can pull on all three
- ordinary computing often needs only bounded time with honest degradation

## Why the hook survives

The sources used in this revision do not merely imply this distinction.
They state it:
- NIST smart-grid work explicitly targets precision **time, phase, and frequency** synchronization
- NIST timing/CPS material explicitly names **time, phase, and frequency** as distinct synchronization types
- packet-synchronization analysis distinguishes **one-way frequency** synchronization from **two-way time/phase** synchronization

## Why the core does not yet broaden

The archive still lacks a compact and obviously better broader object.
A premature redesign would risk widening the narrow waist before the rest of the archive has earned it.

## What to watch next

A broader redesign becomes more likely if:
- multiple profiles need non-time dimensions in first-class ways
- `sync_dimension` begins to carry too much hidden semantics
- the archive needs state fields that cannot be expressed as profile-local attachments to TimeState

## Current archive posture

Keep:
- `TimeState` as the narrow waist
- `sync_dimension` as the strongest hook
- profile-specific phase/frequency density outside the core for now
