# Preserve-before-identity-action page: export, branch, relink, and safe sequence interface spec

## Purpose

Some identity actions should not be blocked outright, but they also should not be the first step.
This page exists to answer:

> if the requested identity action would drop governance or risk local byte loss here, what preserve-first sequence is safer and still sufficient?

## Core decision

AnonSync should make **preserve-before-identity-action** first-class.
The product must not force operators to improvise preservation around unlink / relink / rename / uninstall work.

## Required sequence choices

The page should compare at least these candidate branches when relevant:

- `Proceed now`
- `Preserve locally, then proceed`
- `Export / branch, then proceed`
- `Move action to another seat`
- `Abort`

## Fixed review order

1. **Why preserve first**
2. **Candidate safe sequences**
3. **Resulting local state after sequence**
4. **Cost / residue forecast**
5. **Final recommended rung**

### 1) Why preserve first

Show the exact trigger:

- governance-loss trigger
- platform delete-cliff trigger
- uncertain subject-class trigger
- missing recovery witness trigger

### 2) Candidate safe sequences

For each sequence show:

- ordered steps
- required seat/platform
- what is preserved before the identity action
- what still remains at risk

### 3) Resulting local state after sequence

Show:

- local bytes after sequence
- governance state after sequence
- whether receipts/history remain inspectable
- whether later relink/import is expected

### 4) Cost / residue forecast

Show:

- extra storage cost
- extra branch/residue created
- extra review work introduced
- whether cleanup will later be required

### 5) Final recommended rung

End with one explicit rung:

- `safe to proceed now`
- `preserve first on this seat`
- `use another seat`
- `block until classification improves`

## Rules

### Rule 1 — preserve-first is not an afterthought

If the product already knows a destructive identity action has a safer prerequisite sequence, it must surface that sequence before the commit gate.

### Rule 2 — another seat is a valid alternative

The page must be able to say that the right answer is to perform the identity action elsewhere.

### Rule 3 — residue must be forecast honestly

Branching/exporting may create later cleanup work; the page must say so instead of pretending preservation is free.

## Acceptance criteria

A later operator can:

- understand why preserve-first review appeared
- compare safer sequences instead of improvising
- see the expected local state after each sequence
- pick the narrowest sufficient safe rung
