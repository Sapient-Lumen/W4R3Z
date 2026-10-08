# FIRST-BOUNDARY-CASE

This note asks the rev0024 frontier question directly.

## Question

What is the first concrete scenario in which the current narrow waist plus `applicability` is not enough,
and a broader object built around the provisional pair would actually change a boundary?

## Current result

**The first clear boundary-changing case is P5, and it is currently profile-local.**

That matters because it resolves two things at once:
- there really is a case where the broader-object pressure becomes operational rather than merely explanatory
- but that case still does **not** force archive-wide promotion

## Comparison pass

### Case A — P2 distributed coordination / TrueTime-like systems
The current narrow waist already exports an interval.
That means the central client-facing uncertainty-bearing contract is already present at the core.

A wider object may still help explain more,
but it does not yet obviously change the boundary.
The narrow waist already carries the main contract-relevant move.

### Case B — P5 synchrophasor / power-profile timing
This is different.
The live interface between clock/distribution system and PMU/application already wants more than a coarse applicability label.
It wants an explicit time-quality / maximum-time-error style signal that can travel with measurements and determine usability.

In this case, a promoted `time_error_bound` is not just explanatory.
It changes the boundary because the receiving side uses that bound-like information to decide whether the measurement stream remains usable.

### Case C — P4 Lane A telecom frequency continuity
The pressure is real,
but the archive does not yet have a similarly decisive boundary change.
Existing quality classes, telecom-specific metrics, and neighboring semantics still absorb more of the work.
`rate_error_bound` remains plausible,
but not yet as decisively boundary-changing as the P5 time-error case.

## Archive judgment

The first boundary-changing case is:
- **profile:** P5
- **kind of boundary:** clock/distribution to measurement/application contract
- **first widened semantic:** `time_error_bound`

## Why this still does not justify global promotion

### 1. The first case is profile-local
The P5 case is strong,
but it is also unusually explicit about timing usability and traceable time quality.
That makes it excellent evidence for a widened profile boundary,
not yet for a universal object.

### 2. The narrow waist still works elsewhere
P2 still fits the current core well.
P4 still has real but less decisive pressure.
This is not yet enough recurrence.

### 3. The promotion threshold should be recurrence, not mere existence
One real widened boundary is enough to justify keeping the pair alive.
It is not yet enough to justify hardening the archive-wide object.

## New structural rule

The archive should distinguish between:
- a **profile-local widened boundary**, where one profile needs explicit bound-bearing semantics at an interface
- an **archive-wide broader object**, which should be promoted only when the same widened semantics recur across multiple independent profiles or boundary types

## Consequence

The archive should now be willing to say:
- the first real widened boundary exists
- it belongs to P5 for now
- the broader object still remains hypothetical at archive scope

## Next useful move

Do not ask only whether the pair is conceptually attractive.
Ask whether the same widened boundary recurs elsewhere strongly enough to become structural.
