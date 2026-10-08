# PROFILE-DEFAULT-TIER-TEST

This note decides whether the archive should name a small tier between the minimal core and fully optional extensions.

## Question

Does the archive now have enough evidence to name a middle tier for hooks that are:
- not archive-core,
- but default-visible in some profile boundaries?

## Comparison by hook

### H1 — `traceability_posture`

rev0034 already established the middle-case pattern here.
This hook is:
- not justified as archive-core everywhere
- but too important to remain merely optional in some P4/P5 boundaries

### H2 — `sync_dimension`

This hook now looks like the second real member of the same family.

Why:
- telecom timing explicitly separates frequency transfer and phase/time transfer
- smart-grid / critical-infrastructure timing explicitly distinguish time, phase, and frequency categories
- some P4 Lane A systems care first about frequency continuity,
  while Lane B and many P5 systems care directly about phase/time alignment

That means omission is not neutral.
A client or operator can see a "good timing" state without knowing whether the system is actually promising:
- frequency only
- time only
- phase alignment
- or a combination

For P4/P5-like boundaries, that is too much ambiguity.

### H3 — `holdover_class`

This hook does **not** yet show the same pattern.
The source base strongly supports default visibility of:
- holdover state
- degraded regime
- status change

But that is not the same thing as default visibility of a richer `holdover_class`.
So far the archive still reads that richer class as profile-local and context-dependent.

### H4 — `validity_scope`

This hook also does **not** yet show the same pattern.
Locality, partition, and recovery semantics matter,
but the archive still lacks repeated evidence that this hook needs default visibility across multiple demanding profile boundaries.

## Current judgment

The archive now has **two** hooks with the same middle-case pattern:
- `traceability_posture`
- `sync_dimension`

That is enough to justify a very small named tier.

## Minimal new tier

The archive should name this tier:

## `profile_default`

Meaning:
- not part of the archive-wide minimal core
- natively representable
- expected by default at specific profile boundaries where omission would mislead clients, operators, or control logic

This is not a new subsystem.
It is just a more honest classification.

## Proposed architecture

1. **Minimal core**
   The six-part archive-wide TimeState.

2. **Profile-default hooks**
   Small hooks that are not universal,
   but are default-visible in specific demanding profile boundaries.

3. **Optional/profile-local extensions**
   Everything else.

## Current members of `profile_default`

Provisional current members:
- `traceability_posture`
- `sync_dimension`

Not yet admitted:
- `holdover_class`
- `validity_scope`

## Why this helps

It lets the archive say:
- the core stays small
- some hooks are stronger than optional
- not every demanding profile has to force core growth

That is a cleaner result than pretending the archive only has two levels.

## Consequence for profiles

P4 and P5 should now be read as the main homes of `profile_default` pressure.
P3 still carries strong traceability pressure,
but often at service / audit boundaries rather than the thinnest generic runtime client boundary.

## Next useful move

Test whether `holdover_class` remains outside this tier after one direct comparison pass,
or whether the archive has now underestimated how often holdover semantics need to be default-visible.
