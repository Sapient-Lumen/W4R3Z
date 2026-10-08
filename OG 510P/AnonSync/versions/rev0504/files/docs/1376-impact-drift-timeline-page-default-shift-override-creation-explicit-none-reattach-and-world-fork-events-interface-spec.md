# Impact-drift timeline page — default shift, override creation, explicit none, reattach, and world-fork events

## Purpose

This page keeps cohort truth chronological.
It exists so the product can explain how a settings population drifted away from a clean inheritance model over time.

## Required event classes

### 1) Default-shift event

Examples:

- desktop global default changed
- power-user default changed
- startup config default changed

Every such event must say:

- which cohort adopted immediately
- which detached subjects stayed unchanged
- whether future subjects inherit the new default

### 2) Override-creation event

Examples:

- one share manually changed
- one mobile share locally customized
- one service world diverged from interactive world

Every such event must say the subject left the inherited cohort.

### 3) Explicit-none event

Examples:

- share explicitly set to `None`
- one lane explicitly set `Off`

This event class exists so `explicit none` cannot impersonate `inherit`.
Every such event must say whether the subject is still detached from future default shifts.

### 4) Reattach event

Examples:

- operator chose `inherit default`
- override removed
- subject rejoined cohort after review

This must be its own event class.
Setting a visible value to match the default is not enough.

### 5) World-fork event

Examples:

- service installed as migrated world
- service installed as clean world
- storage path changed
- successor/imported world created

Every such event must say whether the governed cohort preserved continuity or forked.

### 6) Activation / adoption event

Examples:

- restart adopted startup-owned value
- service restart adopted service-world value
- rescan adopted route-local value

## Timeline output rules

- Every event must say whether it widened, narrowed, forked, or rejoined the target cohort.
- Every event must say whether the strongest impact sentence strengthened or weakened.
- Every event involving `None` must explicitly say whether that means inheritance, explicit none, or unknown.
- Every world-fork event must say whether prior receipts remain valid only for the old world.

## Final timeline sentence

The page must end with one summary sentence in this shape:

> `Current impact answer is the result of <latest governing event>; stronger sentence <...> remains blocked because <...>.`