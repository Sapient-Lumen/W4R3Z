# Partial-transfer survivor proof page — resume witness, cleanup boundary, and leftover residue interface spec

## Purpose

This page exists because `there are partial bytes here` is weaker than `resume will safely continue`.
AnonSync should require one **Partial-transfer survivor proof** page whenever local partial residue, interrupted transfer state, or cleanup of unfinished temp material becomes operator-visible.

## Core distinctions

The page must keep these truths separate:

- partial residue exists
- partial residue is actively progressing
- resume is plausible
- resume has been proven after restart or observation
- residue is stuck
- cleanup deletes only temp transfer state
- cleanup may discard reusable progress

## Object model

### `partial_transfer_survivor_proof`

- `partial_transfer_survivor_proof_id`
- `scope_ref`
- `residue_family` (`temp-piece-file`, `placeholder-plus-temp`, `mixed`, `unknown`)
- `residue_presence` (`none`, `present`, `stuck`, `cleaned`, `unknown`)
- `resume_witness` (`none`, `pre-restart-only`, `post-restart-progress`, `completed`, `unknown`)
- `cleanup_boundary` (`temp-only`, `may-drop-progress`, `unknown`)
- `survivor_map` (`local-temp-only`, `local-reusable-progress`, `archive-related`, `unknown`)
- `recommended_next_step` (`wait-observe`, `restart-and-watch`, `cleanup-temp-and-restart`, `full-redownload-branch`, `unknown`)
- `safe_sentence`
- `blocked_sentence`

## Required sections

### 1) Residue inventory

Show:

- what partial residue exists
- where it lives
- whether it is still changing

### 2) Resume witness

Show exactly one:

- `resume not yet witnessed`
- `resume plausible but not proven`
- `resume observed after restart / observation`
- `transfer completed`
- `residue appears stuck`

### 3) Cleanup boundary

Show whether proposed cleanup deletes:

- only temporary transfer residue
- temporary residue plus reusable progress
- an unknown amount of useful progress

### 4) Safe sentence

Examples:

- `Partial residue is present, but safe resume is not yet proven.`
- `Progress resumed after restart, so residue now has resume witness.`
- `Residue appears stuck; cleanup is a manual boundary that may discard reusable progress.`

## Interaction rules

1. Presence of partial residue may not be labeled `resumable` without resume witness.
2. A cleanup action must show the survivor map before the operator commits.
3. If the honest next branch is full redownload, say so explicitly.
4. The page must link to the lineage receipt after any cleanup or restart action.

## Acceptance bar

The page is good enough when a cautious operator can answer:

- what partial residue exists
- whether resume is proven or only hoped for
- what cleanup would discard
- whether the honest next branch is continued transfer or redownload
