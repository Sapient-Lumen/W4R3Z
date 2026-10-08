# Remedy-substrate timeline page — mutation, archive expiry, restore, and cure-collapse events

## Purpose

This page tracks the time-ordered events that strengthen or weaken cure capability after harm already occurred.

## Required event families

- downstream mutation started
- downstream mutation completed
- compensation debt opened
- repair material first evidenced
- source peer lost
- source peer returned
- placeholder-only state entered
- no-source warning raised
- archive version created
- archive restore attempted
- archive restore succeeded
- archive horizon shortened or extended
- archive item expired
- version-size exclusion discovered
- free-space block entered
- free-space block cleared
- platform/runtime repair lane opened
- platform/runtime repair lane closed
- cure verdict strengthened
- cure verdict weakened
- cure collapsed
- cure proven

## Timeline questions

The page must make it easy to answer:

- when did cure first become plausible?
- when did it become partial only?
- when did it become required-cohort capable?
- what exact event collapsed the stronger cure sentence?
- what remaining horizon is left before the current cure lane decays?

## Invariants

- timeline entries must preserve both strengthening and collapse events
- timeline entries must distinguish evidence arrival from actual cure execution
- timeline entries must preserve expiry events even if later compensation narrows harm
- timeline entries must not erase earlier windows where a cure lane existed but was not used
