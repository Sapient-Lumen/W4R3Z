# Attribute-courier evidence page — native support, stub residue, and round-trip ceiling interface spec

## Purpose

If a seat is not a native preserver, the product must prove what kind of weaker seat it is.

## Core decision

AnonSync should expose an **Attribute-courier evidence** page whenever any seat is acting as a courier-only relay or reduced-fidelity holder for required metadata channels.

## Fixed page order

1. **Seat capability evidence**
2. **Courier residue / surrogate state**
3. **Round-trip ceiling**
4. **Local edit warning**
5. **Migration / waiver actions**

### 1) Seat capability evidence

For each channel, show why the seat is not native:

- filesystem cannot store channel
- provider API cannot round-trip channel
- platform strips channel on local edit
- capability unknown, currently unverified

### 2) Courier residue / surrogate state

Show whether the seat holds:

- no surrogate material
- local courier cache / sidecars
- pending relay-only state
- stale residue requiring cleanup

The product should use its own terms, not require the operator to know implementation paths.

### 3) Round-trip ceiling

For each channel, state the highest honest claim:

- `native round-trip`
- `relay onward only`
- `one-way preservation risk`
- `cannot preserve`

### 4) Local edit warning

If local edits here would change meaning fidelity, say so directly:

- `safe to edit locally`
- `edits may narrow meaning`
- `edits blocked until migration`

### 5) Migration / waiver actions

Allow only grounded actions:

- `Move subject to native seat`
- `Keep as courier-only relay`
- `Block local edits here`
- `Accept reduced-fidelity waiver`

## Acceptance criteria

A user can answer, without filesystem archaeology:

- why this seat is not native
- whether it still carries meaning onward
- whether local edits are safe here
- what the maximum honest preservation claim is
