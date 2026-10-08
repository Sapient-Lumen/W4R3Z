
# Mutability lineage receipt page: birth commitment, live edit, and successor boundary interface spec

## Purpose

A later operator should not need memory or support notes to answer:

> was this thing edited in place, changed only for the future, deferred until later proof, or replaced by a successor because the old object was birth-locked?

## Receipt fields

- receipt id
- predecessor object ref
- successor object ref nullable
- acting seat
- field family
- prior value(s)
- requested value(s)
- resolved mutability class per field
- effect timing per field
- birth-commitment rows consulted
- carryforward decisions
- strongest safe sentence
- stronger rejected sentence
- superseded-by nullable

## Required views

### Header

Show one plain summary sentence such as:

- `Edited live in place.`
- `Deferred until restart.`
- `Changed only for future descendants.`
- `Could not be changed in place; successor object created.`

### Field verdict table

Each row should show:

- field
- old value
- new value
- mutability class
- actual effect result

### Boundary truth

Show explicitly whether this was:

- `same object`
- `same object, new policy epoch`
- `successor object`
- `unknown / partial`

### Carryforward truth

Show preserved, translated, historical-only, and lost elements.

## Rules

- never emit a receipt that implies in-place edit when successor cutover happened
- never collapse `deferred` into `done`
- keep rejected stronger language visible for audit and later repair work
