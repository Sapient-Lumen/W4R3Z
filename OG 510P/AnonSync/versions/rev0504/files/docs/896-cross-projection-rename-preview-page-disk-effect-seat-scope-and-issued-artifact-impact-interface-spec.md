# Cross-projection rename preview page: disk effect, seat scope, and issued artifact impact interface spec

## Purpose

Once intent is resolved and projection differences are understood, the operator still needs one final preview:

> what exactly will change across seats, disk paths, and already-issued artifacts if I execute this rename-like action from this projection right now?

## Core decision

Every serious rename-like action must compile into one first-class **Cross-projection rename preview** before apply.

The preview owns:

- chosen verb family
- executing projection
- changed planes
- unchanged planes
- seat scope
- disk effect
- issued-artifact impact
- receipt consequences

## Fixed page order

1. chosen action summary
2. plane delta map
3. seat and audience scope
4. disk and path consequences
5. issued-artifact impact
6. apply verdict

### 1) Chosen action summary

Show:

- chosen typed action
- executing projection
- strongest safe sentence
- stronger rejected sentence

### 2) Plane delta map

Render one row per naming plane with:

- current value
- resulting value
- changes? (`yes`, `no`)
- why not, if unchanged

### 3) Seat and audience scope

Show:

- this seat only
- selected seats
- all active seats
- future artifact recipients
- holders of already-issued artifacts

The preview must make audience boundaries ordinary and explicit.

### 4) Disk and path consequences

This section is mandatory whenever path/basename might change.
Show:

- whether any real filesystem rename occurs
- mount/root boundaries if relevant
- whether remote seats stay on the old path/name
- whether path continuity or repair follow-up is required

### 5) Issued-artifact impact

Show:

- whether already-issued artifacts keep older labels
- whether future artifacts adopt a new template
- whether one-off outward wording is being issued now
- whether any artifact must be regenerated to carry the new wording

### 6) Apply verdict

Possible outcomes:

- `apply now`
- `apply only on this seat`
- `switch to broader projection`
- `issue outward relabel instead`
- `cancel; wrong verb`

## Rules

### Rule 1 — preview must include untouched serious planes

A rename preview that shows only changed fields is incomplete.

### Rule 2 — path effects and label effects never collapse

Filesystem rename and outward wording change must stay visibly separate even if triggered from nearby controls.

### Rule 3 — prior artifacts keep lineage

Already-issued artifacts are not silently rewritten by later subject rename unless a separate reviewed mechanism says so.

## Acceptance criteria

A later operator can:

- tell which planes changed
- tell whether any actual filesystem rename happened
- tell who saw the new wording
- tell whether older artifacts stayed old
- tell why this projection was sufficient or insufficient
