# Allocation envelope timeline page — award, activation, overdraw, correction, and restored conformance events

## Purpose

This page renders the life of awarded room from arbitration through activation, edge drift, overdraw, reserve breach, correction, reclaim, and restored conformance.
It must show when room was merely awarded, when it was activated, and when active use stopped matching the award.

## Required event families

### 1. Award-envelope events

- contention verdict published
- awarded room recorded
- split allocation recorded
- reserve exception opened

### 2. Activation and conformance-start events

- first activation seen
- first productive occupancy seen
- first in-envelope conformance confirmed
- first edge-of-envelope warning

### 3. Overdraw events

- ordinary overdraw detected
- cross-claim bleed detected
- protected-reserve floor touched
- protected-reserve breach confirmed
- exception expired while use continued

### 4. Correction events

- corrective throttle proposed
- narrowed allocation applied
- emergency borrow renewed or denied
- conformance restored
- stronger sentence widened or stayed blocked

### 5. Escalation events

- reclaim proposed
- reclaim approved
- contention reopened
- new claimant promoted
- reserve restored

## Timeline obligations

- distinguish `active` from `within-envelope`
- show when reserve borrowing began and when it ended
- show how long impacted claimants carried the consequence of overdraw
- preserve correction as a typed event instead of inferring it from later lower usage
- allow operator to replay exactly when honest award use turned into leakage and whether correction truly fixed it

## Stronger-sentence guard

The timeline may say `winner kept running`.
It may not imply `winner kept honoring the award` unless in-envelope or valid exception events remain current and unbroken.
