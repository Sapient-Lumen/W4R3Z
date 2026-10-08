# Remedy-hold timeline page — arm, extend, breach, release, and expiry events

## Purpose

This page tracks the time-ordered events that determine whether remedy substrate was actually protected after cure capability became visible.

## Required event families

- cure capability first evidenced
- preservation hold requested
- preservation hold armed
- hold coverage widened
- hold coverage narrowed
- retention override applied
- retention override activated
- restart or scan needed
- restart or scan completed
- storage reservation opened
- storage reservation lost
- source peer reserved
- source peer lost
- archive item placed under hold
- archive item manually cleared
- version-size exclusion discovered
- platform hold ceiling discovered
- hold extended
- hold review missed
- hold breached
- hold released intentionally
- archive item expired
- preservation collapsed

## Timeline questions

The page must make it easy to answer:

- when did cure first become preservable?
- when did a real hold start, versus merely being requested?
- which exact event breached the hold?
- how long did the protected window actually remain open?
- what next review or expiry point will weaken the current preservation sentence?

## Invariants

- timeline entries must distinguish `hold requested` from `hold active`
- timeline entries must preserve breach causes even if later compensation narrows the case
- timeline entries must preserve moments where preservation was possible but not armed
- timeline entries must not erase prior windows where a hold existed and was later lost
