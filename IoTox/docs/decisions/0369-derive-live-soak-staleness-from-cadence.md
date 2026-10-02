# ADR 0369: Derive live soak staleness from cadence

Status: accepted and implemented
Date: 2026-09-10

## Context

The retuned 24-hour three-writer soak emits normal progress at cycle 1 and then
every tenth writable cycle.  With the ADR 0368 cadence, that can leave the VM
console intentionally quiet for roughly three quarters of an hour even when the
guest is healthy.  The live status helper still used the older fixed
twenty-minute stale threshold, so it reported a healthy retuned run as
`health=stale`.

## Decision

`tools/inspect-sync-three-writer-soak.py` now derives a soak-specific stale
window from the observed requested duration and minimum cycle count.  Newer
proof logs also include the explicit cycle delay, hard timeout, and
stalled-restart threshold; when those fields are present, the status helper uses
them to estimate the sparse tenth-cycle reporting window.  During
`soak-running`, it keeps the caller's base stale threshold for fast profiles,
but widens the live-progress window for long soaks, bounded at two hours.

For the ADR 0368 active-recovery 24-hour profile, this produced a one-hour
stale window.  For the ADR 0371 passive 24-hour profile with a 900-second hard
cycle timeout, it reaches the two-hour operator-alarm cap.  Startup, shadow,
failed, completed, and receipt phases still use the caller's ordinary stale
threshold.

## Consequences

The live status display now distinguishes an intentionally quiet 24-hour soak
from a genuinely stalled VM.  This is operator evidence only; the authoritative
gate remains the final signed/content-free receipt and verifier result.  A soak
can still reject if a writable cycle exceeds the hard convergence timeout or if
a profile that explicitly enables bounded stalled-cycle recovery cannot restore
convergence.
