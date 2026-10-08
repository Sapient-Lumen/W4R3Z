# Remedy-cutover timeline page — land, freeze, switch, conflict, and rebound events

## Purpose

This page shows the event chain that turned a landed cure into an authoritative live state — or failed to do so.
It exists so later readers can see where cutover weakened: open editor, missing lock coverage, timestamp race, read-only reversion, conflict artifact, or rebound overwrite.

## Required event classes

The timeline must support events such as:

- cutover requested
- landing verified
- live lock holder detected
- writer freeze requested
- writer freeze confirmed
- reader switch confirmed
- read-only follower invalidated
- conflict artifact created
- timestamp or database-time winner changed
- unlocked edit detected
- pilot cutover completed
- required-cohort cutover completed
- rebound overwrite detected
- cutover collapsed
- cutover verification collapsed

## Timeline rules

- every event must record actor, cohort, object, and observed cutover class
- the timeline must separate `landed` from `writer frozen` from `authoritative switch complete`
- the timeline must preserve whether rebound risk came from locks, timestamps, offline return, read-only overwrite, or conflict residue
- the timeline must keep manual freeze or switch actions explicit rather than hiding them inside a final verdict

## Output sentence family

The timeline summary must support statements such as:

- `the cure landed, but one editor stayed live and blocked authoritative cutover until the writer freeze completed`
- `pilot writers switched cleanly, while a required non-locking cohort kept cutover at the weaker pilot-only rung`
- `a conflict artifact appeared after landing, so the cure never reached clean authoritative cutover`
- `the landed repair became current briefly, then collapsed when a later database-time winner rebound overwrote it`
