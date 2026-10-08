# Effect-direction timeline page — backup enable, delete direction, disconnect, and reverse-recovery events

## Purpose

This page answers one ordinary question over time:

> how did this subject's directionality change, and which events widened, narrowed, or blocked reverse effects?

## Core decision

Every meaningful change to effect direction must write one durable timeline event.
That includes:

- entering bidirectional sync
- becoming inbound-only / read-only
- becoming storage-only backup
- entering opaque encrypted custody
- disconnect while retaining local bytes
- delete-direction change
- recovery-lane narrowing or widening

## Fixed page order

1. current lane summary  
2. timeline ledger  
3. lane-change causes  
4. survivor and delete notes  
5. reopen triggers

### 1) Current lane summary

Show:

- current effect-direction class
- current reverse-recovery class
- current delete-direction class
- current disconnect survivor class

### 2) Timeline ledger

Each row must show:

- time
- event
- old lane
- new lane
- what widened or narrowed
- receipt link

Example events:

- `subject created as bidirectional`
- `backup enabled: storage-only lane entered`
- `encrypted intake: opaque custody lane entered`
- `disconnect: future continuity stopped, local bytes retained`
- `restore attempted: reverse lane remained blocked`

### 3) Lane-change causes

For each change, classify the cause:

- subject kind
- permission / seat posture
- storage or custody mode
- recovery prerequisite gained/lost
- explicit operator choice
- lineage break

### 4) Survivor and delete notes

For events involving delete or disconnect, state:

- what bytes remained where
- which delete directions were active
- whether the event changed only continuity or also authority

### 5) Reopen triggers

Show what future events would force a rereview, such as:

- role change
- reconnect under a different lane
- saved-secret loss or gain
- same-lineage continuity loss
- source deletion followed by attempted restore

## Copy rules

- Do not compress `disconnect` and `reverse lane blocked` into one event if they changed different truths.
- Do not let `backup stopped` imply `backup bytes deleted` unless that was actually reviewed.
- Keep delete-direction and recovery-direction as separate columns.
