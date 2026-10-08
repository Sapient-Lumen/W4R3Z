# Destination commit receipt page — world choice, path intent, and branch proof interface spec

## Purpose

`500` created the typed intake receipt.
This document defines the later receipt that proves where the artifact was intentionally sent next.

The page exists to answer one ordinary support and audit question:

> after typing the artifact but before or during bind, which destination world did we actually choose, what path intent did we review, and what competing branch did we decline?

## Core rule

Every reviewed destination-world choice must emit one durable **Destination commit receipt**.
That receipt is distinct from:

- the typed intake receipt
- the later existing-bytes bind receipt
- the later encrypted-custody commitment receipt
- the later identity-join successor receipt

It is the bridge proving how the artifact left intake and entered one concrete destination branch.

## Required receipt fields

### Artifact basis

Include:

- typed intake receipt reference
- artifact family verdict
- carrier class
- parse-confidence class

### Chosen destination world

Include:

- seat label
- world label / world ID when available
- world posture at commit time
- chosen bind lane

### Path intent

Include:

- `no path yet`
- `standing default root`
- `remembered continuity root`
- `manual root under further review`
- `fresh empty ciphertext root`

Also include whether path intent was fully committed here or only handed off to a deeper page.

### Rejected alternatives

When relevant, include:

- interrupted auto-land world
- rejected default root
- blocked worlds shown during review
- strongest reason each was rejected or blocked

### Next reviewed handoff

Include:

- next page/object ID
- handoff class (`existing-bytes intake`, `encrypted target admission`, `identity successor review`, etc.)
- any proof still required before byte movement or live mutation

### Safety and export

The receipt must:

- preserve semantics without preserving bearer secrets
- be safe to hand to support or another operator
- name any redacted fields explicitly

## Page layout

Always render the same sections in the same order:

1. **Outcome strip**
2. **Artifact basis**
3. **Chosen world and lane**
4. **Path-intent and branch comparison**
5. **Next handoff**
6. **Export and redaction**

### 1) Outcome strip

Show:

- receipt ID
- current verdict (`world chosen`, `rerouted`, `kept unplaced`, `blocked`)
- timestamp
- actor

### 2) Artifact basis

Show the typed intake receipt summary plus immutable artifact-family truth.

### 3) Chosen world and lane

Show:

- world label
- posture
- chosen lane
- strongest warning still in force

### 4) Path-intent and branch comparison

Show:

- selected path intent
- rejected path intents or worlds
- interruption reason if auto-land was refused
- whether byte movement has happened yet

### 5) Next handoff

Show:

- next page/object
- remaining proof work
- conditions that could still block completion

### 6) Export and redaction

Show:

- safe export formats
- redacted fields
- why secrets are omitted

## Acceptance criteria

This spec is satisfied when:

- support can reconstruct which world the operator chose without replaying the UI from memory
- the receipt distinguishes chosen world from chosen path intent
- the receipt preserves rejected alternatives when they mattered
- the receipt bridges typed intake truth to deeper bind/custody truth without carrying secrets
- the operator can safely attach the receipt to later escalation or handoff flows
