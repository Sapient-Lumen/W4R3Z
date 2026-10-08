# Consumer-uptake timeline page — fetch, pin, decide, act, and rollback-reach events

## Purpose

This page gives the operator a chronological view of how a sentence moved from being merely current into actual consumer use and later rollback or supersession.
It exists so the product can show when a version was first seen, when it was pinned, when decisions bound to it, when acts began, and when rollback or correction reached each cohort.

## Required event classes

The timeline must distinguish at least:

- sentence became current
- consumer rendered sentence
- consumer fetched sentence version
- consumer cached sentence version
- consumer opened sentence
- consumer pinned sentence version
- bound decision recorded
- downstream action started
- downstream action completed
- superseding sentence became current
- rollback issued
- rollback reached consumer
- compensation completed
- irreversible residue recorded
- rollback cleared for cohort

## Required event payloads

Each event must carry:

- trusted timestamp and basis
- actor or system source
- consumer or cohort affected
- sentence version affected
- whether the event strengthens or weakens rollback difficulty
- lower sentence or superseding sentence relationship after the event
- strongest blocked rollback sentence after the event

## Timeline interpretation rules

- currentness is different from rendering
- rendering is different from pinning
- pinning is different from bound decision
- bound decision is different from downstream action
- rollback issued is different from rollback reached
- supersession is different from compensation and different from residue clearance

## Mandatory visual cues

The page must visibly distinguish:

- cheap-rollback intervals
- expensive-rollback intervals
- irreversible-crossing events
- stale-version decisions
- the exact moment a cohort moved from merely seeing a sentence to actually using it
