# FIRST-MISSING-FIELD

This note records the archive's current best guess about the first field that would be forced by a broader-than-`TimeState` redesign.

## Revised judgment

The archive no longer treats this as a single universal ranking.

### Overall archive judgment
If the hook model starts to fail **across the archive as a whole**, the first likely missing field remains:

**`time_error_bound`**

### Lane-sensitive caveat
If redesign pressure is driven mainly by **P4 Lane A** — frequency continuity / syntonization — then the leading candidate remains:

**`rate_error_bound`**

with no second promoted Lane A semantic yet justified.

If redesign pressure is driven mainly by **P4 Lane B** or **P5**, then:

**`time_error_bound`** remains the leading candidate,
with no second promoted phase-side semantic yet justified.

## Why the phase side still leads overall

### 1. The hardest cross-profile operational requirements still surface as alignment requirements
Power-profile and grid material keeps surfacing sub-microsecond synchronization and phase-sensitive operation.
Telecom material also surfaces global phase requirements alongside time-of-day and frequency.

### 2. The phase-side candidate survived its first break test
The archive now has provisional stability on both sides of the pair.

## Current ranking

### Cross-profile ranking
1. `time_error_bound`
2. `rate_error_bound`

### P4 Lane A ranking
1. `rate_error_bound`
2. `time_error_bound`

### P4 Lane B / P5 ranking
1. `time_error_bound`
2. `rate_error_bound`

## What would change this next

The archive should revise this note further if:
- the phase side turns out to need more than one promoted semantic
- a decisive Lane A counterexample forces a second rate-side field
- the pair proves unnecessary because the hook model remains sufficient on both sides
