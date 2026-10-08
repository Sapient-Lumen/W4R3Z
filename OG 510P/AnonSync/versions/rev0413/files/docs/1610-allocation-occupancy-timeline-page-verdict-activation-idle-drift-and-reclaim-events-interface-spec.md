# Allocation occupancy timeline page — verdict, activation, idle drift, and reclaim events

## Purpose

This page renders the life of awarded room from contention verdict through activation, stalled use, downgrade, reclaim, and any reopened contest.
It must show when room was merely promised to a winner versus when it was truly occupied.

## Required event families

### 1. Award events

- contention verdict published
- split or full allocation recorded
- reserve exception opened

### 2. Activation events

- activation window opened
- first motion seen
- first productive consumption seen
- productive occupancy confirmed

### 3. Idle-drift events

- last net advance
- idle threshold crossed
- no-net-progress churn threshold crossed
- loser starvation threshold crossed

### 4. Blocker events

- locked-file blocker observed
- no-source-peer blocker observed
- scheduler/manual pause observed
- hidden-internal-task tolerance opened
- blocker severity raised

### 5. Reclaim events

- downgrade proposed
- reclaim proposed
- reclaim approved
- room released
- contention reopened
- loser promoted or new winner selected

## Timeline obligations

- distinguish `first motion` from `first productive use`
- show how long losers stayed blocked after award
- preserve reclaim as a typed event instead of silent disappearance
- show reserve borrowing and reserve restoration explicitly
- allow operator to replay why exclusivity ended or continued

## Stronger-sentence guard

The timeline may say `winner remained assigned`.
It may not imply `winner kept honestly using the room` unless productive-occupancy events remain current and unbroken.