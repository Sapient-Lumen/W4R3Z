# RECURRENCE-TEST

This note asks whether the first widened boundary found in rev0025 recurs strongly enough to justify archive-wide promotion.

## Question

After finding P5 as the first clear profile-local widened boundary,
do the same bound-bearing semantics recur strongly enough elsewhere to justify hardening a broader object?

## Current result

**Recurrence is still weak.**

P5 remains the cleanest runtime widened boundary.
P3 and P4 both add real pressure,
but not yet in the same way.

## Comparison pass

### Case A — P3 traceable finance
P3 clearly needs more than a casual notion of time quality.
The source base is explicit that financial markets depend on precise timestamps,
traceable calibration,
and verifiable timing for fairness and auditability.

But the boundary pressure here is not yet best described as the same runtime widened pair.
The strongest pressure is instead on:
- traceability to a recognized reference
- verifiability of timestamp accuracy
- calibration and audit evidence

That makes P3 a strong **boundary case**,
but not yet a clean recurrence of the P5 runtime `time_error_bound` boundary.

### Case B — P4 telecom / precision network
P4 also has real boundary semantics.
The source base includes synchronization status messaging,
backup-path determination,
holdover transitions,
and phase/time profile limits.

But again,
this does not yet look like the same recurrence.
The pressure lands more on control/distribution semantics and profile-specific network behavior than on a clean generic widened client-facing object.

### Case C — P5 synchrophasor / power timing
P5 remains unusually explicit.
The clock/distribution system carries time-quality and maximum-time-error style information toward the receiving side,
and that information directly affects measurement usability.
This is still the clearest case where the widened semantic is part of a live runtime boundary.

## What changed in archive understanding

rev0025 found a first widened boundary.
rev0026 now says that finding a first case was not the same as finding recurrence.

The archive's current picture is:
- **P5** — clean runtime widened boundary
- **P3** — strong evidence / traceability boundary
- **P4** — strong control / distribution boundary

These are all important.
They are not yet the same enough to force one broader archive object.

## Archive judgment

Do **not** promote the broader object yet.

The archive now has stronger justification for saying why:
- the strongest repeated pressure is still not a repeated **same-shape** pressure
- what recurs is boundary seriousness,
not yet one clearly recurring widened semantic contract

## Most important consequence

The next likely boundary-bearing hook outside the provisional pair is now `traceability_posture`.

Why:
- P3 keeps pressing traceability and verifiability
- P5 also cares about reference quality and time quality
- this may become the next cross-profile boundary signal before the broader object itself becomes structural

## Next useful move

Test whether `traceability_posture` becomes a boundary-bearing hook in P3 strongly enough to deserve tighter treatment than the archive currently gives it.
