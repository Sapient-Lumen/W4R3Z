# Promotion timeline page — eligibility, review, promotion, override, and demotion events

## Purpose

This page gives the operator a chronological view of how a case moved from lower-sentence truth toward or away from a stronger sentence.
It exists so the product can show when review opened, when automation armed, when promotion occurred, when override was invoked, and what later re-closed the gate.

## Required event classes

The timeline must distinguish at least:

- promotion review became eligible
- review blocked by missing proof
- review blocked by missing authority
- manual-review opened
- auto-promotion became eligible
- auto-promotion armed
- auto-promotion executed
- manual promotion executed
- override requested
- override granted
- override expired
- promotion denied
- promotion demoted
- promotion re-armed

## Required event payloads

Each event must carry:

- timestamp and trusted time basis
- actor or system source
- stronger sentence affected
- whether the event strengthens, weakens, or merely annotates the gate
- whether automation changed state
- strongest blocked sentence after the event

## Required event examples

The page must be able to render events like:

- `stability-earned recorded; stronger sentence entered review but remained manual-only`
- `hidden-work warning reopened uncertainty; auto-promotion disarmed`
- `all gate prerequisites satisfied; auto-promotion armed for the next dwell checkpoint`
- `named reviewer manually promoted the stronger sentence while leaving normalization blocked`
- `override granted for emergency release; probation and 24-hour re-review scheduled`
- `no-source residue surfaced; stronger sentence demoted while earlier lower sentence remained intact`

## Timeline interpretation rules

- eligibility is different from approval
- approval is different from actual promotion
- override is different from ordinary promotion
- demotion weakens a stronger sentence without erasing the lower truth that supported review
- the viewer must always be able to tell whether the next likely move is arm, promote, deny, demote, or re-arm
