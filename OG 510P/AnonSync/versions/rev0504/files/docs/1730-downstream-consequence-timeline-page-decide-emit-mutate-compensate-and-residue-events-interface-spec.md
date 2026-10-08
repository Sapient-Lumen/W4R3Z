# Downstream-consequence timeline page — decide, emit, mutate, compensate, and residue events

## Purpose

This page gives the operator a chronological view of how a sentence version moved from being merely used into actual downstream world change and later repair or residue.
It exists so the product can show when a consequence was armed, when it emitted, when it truly mutated the world, when unwind or compensation was attempted, and when residue was finally cleared or admitted.

## Required event classes

The timeline must distinguish at least:

- sentence version used for decision
- downstream consequence armed
- consequence emitted
- local mutation started
- world mutation completed
- required-cohort mutation reached
- halt issued
- rollback issued
- inverse action started
- compensation debt opened
- compensation issued
- compensation cleared
- residue recorded
- reconnect or rescan re-materialized consequence
- stronger reversal sentence blocked or reopened

## Required event payloads

Each event must carry:

- trusted timestamp and basis
- actor or system source
- consequence family or cohort affected
- sentence version affected
- whether the event strengthens or weakens the unwind claim
- whether the event crosses from haltable to compensation-required territory
- strongest blocked stronger reversal sentence after the event

## Timeline interpretation rules

- decision use is different from emitted consequence
- emitted consequence is different from completed world mutation
- rollback issued is different from rollback reached
- inverse action is different from compensation
- compensation issued is different from compensation cleared
- residue recorded is different from residue extinguished

## Mandatory visual cues

The page must visibly distinguish:

- still-haltable intervals
- compensation-required intervals
- irreversible-crossing events
- stale-basis repairs
- the exact moment a path moved from `used` to `world-mutated`
