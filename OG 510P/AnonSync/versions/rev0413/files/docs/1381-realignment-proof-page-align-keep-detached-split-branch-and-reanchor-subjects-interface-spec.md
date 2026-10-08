# Realignment proof page — align, keep detached, split branch, and re-anchor subjects

## Proof question

> if I want these subjects to conform to one baseline, which ones can safely align, which ones should stay detached, which ones belong to another branch, and which ones are not even the same subject anchor yet?

## Core decision

Realignment is never a blind bulk write.
The page must prove the difference between:

- changing a visible value
- restoring inheritance
- preserving an intentional override
- adopting a baseline in one world only
- splitting a new baseline branch
- correcting subject identity / anchor confusion

## Fixed proof blocks

### 1) Candidate matrix

One row per subject with columns for:

- subject id
- local label
- current grade
- divergence reason
- proposed action
- governance-state delta
- world delta
- activation rung

### 2) Safe-to-align block

Subjects may enter this block only if the page can prove:

- canonical subject identity
- same governing world or explicitly scoped branch
- no hidden detached exception that would be erased accidentally
- no stronger evidence gap

### 3) Keep-detached block

Use when the subject intentionally diverges from the baseline.
For each row show:

- exact reason to preserve detachment
- whether visible value currently matches anyway
- next event that would cause future drift
- why bulk `align all` excludes it

### 4) Restore-inheritance block

Use when the operator explicitly wants baseline governance, not just baseline value.
Required outputs:

- current explicit override proof
- exact action that removes detachment
- future default shift that would now reach the subject
- warning if the action changes meaning beyond current visible value

### 5) Split-branch block

Use when the subject or world should intentionally keep a distinct baseline.
Required outputs:

- reason for branch
- new branch scope
- inheritance boundary between branches
- blocked `single universal baseline` sentence

### 6) Re-anchor block

Use when local names or route hints are insufficient to prove subject identity.
Required outputs:

- conflicting labels or aliases
- canonical id evidence still needed
- actions withheld until re-anchored

### 7) Commit summary

Before any realignment commit, publish:

- count aligning by value only
- count restoring inheritance
- count preserved as detached
- count forked to another branch
- count blocked for re-anchoring or missing evidence

## Hard rules

- Never collapse `match value` and `restore inheritance` into one action.
- Never include another world in batch alignment by implication.
- Never treat a local alias as sufficient proof of subject identity.
- Never offer `align all` while unresolved false-friend cases remain.

## Example strongest-safe sentence patterns

- `18 subjects can align to the baseline without changing governance state; 4 detached subjects are excluded.`
- `3 subjects require explicit restore-inheritance if you want future default changes to reach them.`
- `2 rows are blocked because local custom names are not enough to prove canonical subject identity.`
- `The service world remains on its own branch; this realignment affects only the interactive desktop world.`
