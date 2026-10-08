# Mutation chronology contract sheet page — online order, offline winner, and time basis

## Purpose

Give the operator one first surface for any serious `which version wins` claim.
The page must stop the product from collapsing chronology, clock trust, offline rejoin effects, archive fallback, and republish authority into one vague `newer file` sentence.

## The page must answer

1. What chronology class is currently in play?
2. What exact basis is being used to decide `newer` right now?
3. Is the current verdict trustworthy, blocked, or only provisional?
4. If another version lost, where did it go?
5. If the operator wants an older version to win instead, what proof is still missing?
6. What stronger sentence is blocked?

## Core model

### A. Chronology class

Represent exactly one current class:

- **Online ordered progression**
- **Offline-return winner**
- **Time-skew blocked / chronology suspended**
- **Manual older-byte republish in progress**
- **Detection uncertainty / chronology not yet recomputed**

### B. Winner basis

Represent one or more basis elements explicitly, never as hidden inference:

- disk mtime comparison
- UTC-normalized peer clock comparison
- offline-return precedence rule
- manual restore from Archive
- manual touch / rescan trigger
- file-class delay mitigation in force
- operator override not present

### C. Time-authority class

Represent exactly one current class:

- **Clock-trusted**
- **Clock-warning but still below hard-stop**
- **Hard blocked by time difference**
- **Disk mtime unreliable / database fallback in effect**
- **Detection path incomplete / needs touch or rescan**

### D. Loser survivor map

Represent exactly what happened to the displaced version:

- still live on another peer
- placed in Archive on this peer
- placed in Archive on remote peers
- unknown / not yet witnessed
- operator parked it outside the subject

## Required warnings

The page must warn when:

- a peer edited offline and its later return can outrank subsequent online edits
- time-zone or clock drift is large enough to weaken or block the verdict
- the product is relying on mtime while the platform cannot faithfully preserve it
- manual touch/rescan is the only present way to force detection
- a delay profile exists for this file class and could change future conflict risk but not retroactively fix the current verdict
- the losing version is merely archived, not endorsed as a rollback candidate

## Required blocked stronger sentences

The page must explicitly refuse to imply any of these unless separately proven:

- `this was the true real-world latest edit`
- `the winning version is correct because clocks are fine`
- `the losing version is gone`
- `restoring the archived version will automatically become authoritative`
- `delay settings guarantee conflicts cannot recur`

## Required outputs

This page must emit a compact contract object preserving:

- chronology class
- winner basis
- time-authority class
- loser survivor map
- next proof required for republish or rollback
- blocked stronger sentence

