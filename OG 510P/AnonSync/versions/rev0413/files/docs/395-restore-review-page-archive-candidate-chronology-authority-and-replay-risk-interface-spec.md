# Restore review page: archive candidate, chronology authority, and replay risk interface spec

## Purpose

The archive already has strong chronology, history, and conflict doctrine.
This document makes the ordinary page concrete.

The page exists to answer one ordinary operator question:

> if I revive this retained version from history or Archive, which candidate am I really choosing, what chronology will the system honor afterward, and will this replay safely or just fall back into history again?

## Core decision

Every serious history-bearing sync system must own one first-class **Restore review** page.
That page is the semantic home of:

- restore candidate choice
- chronology authority
- runtime preconditions
- propagation / replay verdict
- re-archive and overwrite risk
- strongest next-safe action

The product must not let hidden-history browsing and blind file copy stand in for this page.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. candidate strip
2. selected-candidate card
3. chronology-authority card
4. runtime-preconditions card
5. replay and overwrite card
6. destination effect card
7. strongest-next-action card
8. recent restore receipts
9. expert details drawer

### 1) Candidate strip

Show:

- destination subject
- selected retained candidate
- acting seat
- whether the candidate comes from Archive, retained history, or conflict residue
- strongest next-safe action

The strip should answer `what retained version am I considering restoring where?`

### 2) Selected-candidate card

Show:

- candidate path / label
- archived-at time
- original modified time if known
- why this candidate exists (`deleted upstream`, `overwritten by later winner`, `manual retention`)
- whether newer or competing candidates exist

This card should answer `which version am I reviving?`

### 3) Chronology-authority card

Show:

- current winner rule for this subject (`latest trusted mtime`, `latest returning offline edit`, `manual override`, `insufficient confidence`)
- confidence in local clock / mtime truth
- whether any online or offline peer state is likely to outrank the selected candidate immediately
- whether the candidate is being restored for local inspection only or intended swarm replay

This card should answer `what version does the system believe should win after restore?`

### 4) Runtime-preconditions card

Show:

- whether Sync / daemon must remain running during restore for replay to work
- whether route reachability to peers matters now
- whether destination path / bind is ready to receive the revived bytes
- whether a later rescan would likely demote the file back into history

This card should answer `what must be true for this restore to stick?`

### 5) Replay and overwrite card

Show:

- whether restore is expected to propagate to peers, stay local only, or be re-archived
- whether an offline-returning peer or newer peer state is likely to overwrite the restored candidate
- whether resulting overwrites would themselves create new retained-history entries
- whether a safer recovery path exists than replaying directly into the live subject

This card should answer `what happens after I put this version back?`

### 6) Destination effect card

Show:

- destination path and subject
- whether restore lands as live subject replacement, side-by-side recovery, or local inspection copy
- what current file / subtree will be replaced or preserved
- whether any descendants or linked derivatives inherit the replay

This card should answer `where will the restored bytes go?`

### 7) Strongest-next-action card

Show the strongest honest next action, for example:

1. `Restore as live replay now`
2. `Restore side-by-side for inspection first`
3. `Wait until daemon and peers are reachable`
4. `Open conflict / chronology review before replay`
5. `Cancel because selected candidate will immediately lose`
6. `Export retained copy without touching live subject`

This card should answer `what is the safest next move?`

### 8) Recent restore receipts

Show recent receipts with:

- candidate
- chronology verdict
- runtime-precondition verdict
- replay outcome forecast
- destination effect summary
- action taken

### 9) Expert details drawer

Hide raw tombstone traces, peer mtimes, archive index detail, and low-level route/debug fields behind an expert drawer.
They matter, but they are not the semantic center.

## Compact row contract

A trustworthy compact row should preserve the following order:

1. candidate phrase
2. chronology phrase
3. replay-risk phrase
4. destination-effect phrase
5. strongest next action

Example:

```text
notes.txt@Archive[3] · older than live winner unless replay occurs while daemon is running · offline peer may still outrank later · safest path is side-by-side restore first · Inspect before replay
```

## Mandatory fields

- `destination_subject_ref`
- `selected_candidate_ref`
- `candidate_origin_kind`
- `candidate_archived_at`
- `candidate_original_mtime` nullable
- `candidate_reason`
- `chronology_authority_verdict`
- `chronology_confidence_grade`
- `runtime_preconditions_verdict`
- `replay_outcome_forecast`
- `rearchive_risk_verdict`
- `overwrite_risk_refs[]`
- `destination_effect_verdict`
- `strongest_next_action`

## Review guarantees

This page must let the operator:

- tell exactly which retained version is selected
- tell whether current chronology rules let that version win or lose
- tell whether daemon/runtime conditions are sufficient for replay
- move directly into live replay, side-by-side recovery, wait, or deeper chronology review without reopening the world
