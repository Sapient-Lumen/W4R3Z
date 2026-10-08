# Preserve-before-adopt page — copy-aside, quarantine, and side-branch choice interface spec

## Purpose

Current warning language often tells the operator there is some overwrite risk and then immediately asks for commitment.
This page exists to force one explicit question into the ordinary workflow:

> before adopting or merging into this non-empty target, what local material should be preserved, copied aside, quarantined, or branched so the easiest recovery path is not silently destroyed?

## Core decision

Whenever local existing material could be deleted, overwritten, reclassified, or made harder to recover by a bind/adopt action, the product must offer one first-class **Preserve-before-adopt** page before final commit.

This page is not only for emergencies.
It is an ordinary bridge between divergence review and merge/adopt commit.

## Fixed page order

1. **At-risk material strip**
2. **Preservation shapes**
3. **Reversibility and storage cost**
4. **Chosen pre-commit plan**
5. **What commit will still not prove**
6. **Receipt promise**

### 1) At-risk material strip

Show:

- target path
- at-risk classes (`local-only`, `losing divergent candidate`, `ambiguous lineage`, `unknown unreadable bytes`)
- strongest current loss risk
- strongest safe sentence

### 2) Preservation shapes

Offer only typed options such as:

- `Copy aside to reviewed safety path`
- `Quarantine in place and continue reviewed bind`
- `Create side branch instead of merge`
- `Snapshot and then continue`
- `No extra preservation; accept reviewed risk`

Each option must show:

- what classes it preserves
- whether the preserved copy remains inside governance or outside as a local safety artifact
- whether later automatic convergence still touches it

### 3) Reversibility and storage cost

For each option show:

- reversibility class (`easy`, `guarded`, `hard`)
- estimated storage cost
- later cleanup burden
- whether it narrows or widens later proof

### 4) Chosen pre-commit plan

After selection, show one plain-language commitment sentence, for example:

- `Local-only material will be copied aside before adopt proceeds.`
- `A side branch will be created; merge into the current tree will not occur.`
- `No preservation copy will be made; guarded overwrite risk remains reviewed and accepted.`

### 5) What commit will still not prove

This section explicitly blocks overclaim.
Examples:

- `Adopt after preserve does not prove the old tree was restored.`
- `Copy-aside does not prove divergent local bytes were authoritative.`
- `Side branch does not prove attach/merge equivalence.`

### 6) Receipt promise

The resulting receipt must prove:

- at-risk classes
- preservation shape chosen
- whether commit continued or stopped
- stronger sentence rejected

## Public object

### `preserve_before_adopt_review`

Fields:

- `preserve_before_adopt_review_id`
- `subject_ref`
- `target_path`
- `at_risk_classes[]`
- `preservation_options[]`
- `chosen_option`
- `reversibility_class`
- `estimated_storage_cost`
- `commit_continuation` (`pending`, `continued`, `stopped`)
- `generated_at`

## Result

A good preserve-before-adopt page prevents five failures:

- local material disappearing because the only visible choice was `OK`
- recovery paths narrowing silently during a merge/reconnect action
- side-branch creation happening accidentally instead of deliberately
- operators thinking preservation means authority was already proven
- later audits losing the fact that a safer preservation step was offered and either chosen or declined
