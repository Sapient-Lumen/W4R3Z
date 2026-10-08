# Read-only divergence page: suspension, overwrite, and added-file fate interface spec

## Purpose

This page answers one ordinary question:

> when a read-only seat has drifted locally, what exactly is suspended, what would be overwritten, what would remain, and what destructive policy is currently in force?

The page exists because `read-only`, `local edits present`, `overwrite any changed files`, and `safe to keep local extras` are not the same truth.

## Core decision

Every seat must render one first-class **Read-only divergence** page whenever the seat has read-only authority but local divergence exists or may exist.
That page owns:

- local divergence detection
- file-class fate under current policy
- suspension scope
- overwrite posture
- selective-sync incompatibility
- safe next actions

The workbench must not force the operator to infer destructive fate from a tiny checkbox label or a stalled file row.

## Primary layout

The page always renders the same regions in the same order:

1. subject strip
2. divergence summary card
3. fate matrix card
4. policy and incompatibility card
5. safe-action card
6. receipts

### 1) Subject strip

Show:

- subject label
- local seat label
- current verdict: `clean-ro`, `ro-diverged`, `ro-suspended-files`, `ro-overwrite-armed`, `ro-ambiguous`
- one next honest action

### 2) Divergence summary card

This card publishes:

- whether local edits, renames, deletions, or additions have been detected
- which files are currently suspended from ordinary update intake
- whether divergence is file-scoped, folder-scoped, or mixed
- last trustworthy scan/hash time

The operator must be able to answer: **what changed here locally that matters?**

### 3) Fate matrix card

This card publishes one row per divergence class:

- edited file → `kept`, `suspended`, `will revert`, or `unknown`
- renamed file → `local renamed copy remains`, `old name reappears`, `unknown`
- deleted file → `restored`, `left absent`, or `unknown`
- added file → `left local only`, `deleted`, `synced onward`, or `unknown`

The operator must be able to answer: **if I enable overwrite or leave it off, what happens to each class of local change?**

### 4) Policy and incompatibility card

This card publishes:

- current overwrite posture: `off`, `on`, `forced`, `not-available`
- whether Selective Sync currently disables overwrite behavior
- whether the seat is a special custody class that forces overwrite-like behavior
- policy provenance: local setting, inherited default, immutable seat class, or unknown

The operator must be able to answer: **why is this policy available, unavailable, or forced here?**

### 5) Safe-action card

This card publishes:

- least-destructive next actions
- copy-out or preserve-local options before enabling overwrite
- exact effect of `resume intake`, `keep local extras`, `switch posture`, or `promote to writable` if such verbs exist
- post-action retest required for a clean state

The operator must be able to answer: **what is the smallest safe move if I want updates again without accidentally losing local work?**

### 6) Receipts

Receipts show:

- when read-only divergence was first observed
- policy changes acknowledged
- preserve-local exports performed
- overwrite actions applied
- suspension cleared

## Non-negotiable rules

### Rule 1 — read-only must not imply semantically inert

Read-only authority is about outward write rights, not about whether local drift exists.

### Rule 2 — destructive overwrite must publish exact class fate

The page must never say only `changes may be overwritten`.
It must publish edited/renamed/deleted/added outcomes separately.

### Rule 3 — incompatible postures must stay explicit

If Selective Sync or another seat class makes overwrite unavailable, the page must say so directly.

## Honest outputs

The page may conclude:

- `Three files are suspended because this read-only seat edited them locally; overwrite is currently OFF.`
- `Enabling overwrite will restore two deletions, revert one edited file, and keep four added files as local-only extras.`
- `Overwrite is unavailable here because this read-only seat is currently in selective materialization posture.`

It may not collapse those outcomes into one generic `sync conflict` badge.
