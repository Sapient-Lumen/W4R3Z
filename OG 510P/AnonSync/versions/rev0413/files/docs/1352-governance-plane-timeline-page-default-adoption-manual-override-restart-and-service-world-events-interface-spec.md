# Governance-plane timeline page — default adoption, manual override, restart debt, and service-world events

## Purpose

This page answers one ordinary question over time:

> how did this value's governing plane change, and which events moved it from inheritance to override, from hot control to cold control, or from one world to another?

## Core decision

Every meaningful change to governance plane must write one durable timeline event.
That includes:

- inheriting a new global default
- manual subject override
- apparent neutral reset that still leaves detachment in place
- startup-config takeover
- service account or storage-world shift
- launch-switch one-shot override
- activation boundary crossing after restart

## Fixed page order

1. current governance summary  
2. timeline ledger  
3. plane-change causes  
4. activation notes  
5. reopen triggers

### 1) Current governance summary

Show:

- current winning plane
- current inheritance class
- current witness surface
- current activation boundary class

### 2) Timeline ledger

Each row must show:

- time
- event
- old plane
- new plane
- what widened or narrowed
- receipt link

Example events:

- `subject created inheriting global default`
- `manual per-subject edit: inheritance severed`
- `global default changed: detached subject unaffected`
- `config mode started: startup plane pinned winning value`
- `service account changed: new storage world adopted`
- `restart completed: cold winner became active`

### 3) Plane-change causes

For each change, classify the cause:

- broader default mutation
- local manual subject override
- colder startup-config authorship
- service-world migration
- one-shot launch switch
- explicit reset / relink / rebuild

### 4) Activation notes

For events involving cold ownership or restarts, state:

- what was merely saved
- what became active only after restart or world shift
- what old runtime debt still survived temporarily

### 5) Reopen triggers

Show what future events would force a rereview, such as:

- another per-subject manual edit
- moving service to another principal
- changing storage root
- config-file replacement
- surface handoff to a weaker witness surface