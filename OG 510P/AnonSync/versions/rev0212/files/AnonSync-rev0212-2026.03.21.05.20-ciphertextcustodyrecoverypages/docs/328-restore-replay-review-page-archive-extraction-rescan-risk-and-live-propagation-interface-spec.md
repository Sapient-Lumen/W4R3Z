# Restore replay review page: archive extraction, rescan risk, and live propagation interface spec

## Purpose

This page answers one ordinary question:

> if I restore an older version now, will it remain local, propagate outward, or be archived again on the next scan, and what runtime conditions must hold for the restore to behave as intended?

The page exists because `take file out of archive`, `restore`, and `make this version live again` are not the same action.

## Core decision

Every restore from preserved history or archive must compile to one first-class **Restore replay review** page.
That page owns:

- candidate version identity
- intended scope of the restore
- liveness conditions required for success
- rescan and re-archive risk
- outward propagation consequences

The operator must not have to learn from a support article that restoring while the engine is not running can simply archive the file again later.

## Primary layout

The page always renders the same regions in the same order:

1. restore strip
2. candidate card
3. liveness and timing card
4. propagation and re-archive card
5. apply-plan card
6. restore receipts

### 1) Restore strip

Show:

- subject path
- candidate version label
- intended restore scope: `local-only`, `device-live`, `share-live`, `export-copy`
- current verdict: `safe-live-restore`, `guarded-live-restore`, `local-copy-only`, `rearchive-risk`, `blocked`
- one next honest action

### 2) Candidate card

This card publishes:

- candidate origin
- when it was preserved
- retention horizon if any
- current live version it competes with
- whether the candidate is older or newer by authoritative chronology

The operator must be able to answer: **what exact version am I trying to bring back?**

### 3) Liveness and timing card

This card publishes:

- whether the engine is currently running and watching the subject
- whether the restore relies on immediate live detection versus later rescan
- freshness of the relevant scan/watch state
- confidence that the engine will treat the restored file as a new live winner instead of as an older artifact

The operator must be able to answer: **does runtime timing support the restore I think I am performing?**

### 4) Propagation and re-archive card

This card publishes:

- whether the restored file will stay local, propagate to peers, or remain an exported copy only
- what would cause it to be archived again
- whether peer chronology could reject it as older
- whether any preserved versions are at risk of being replaced by the act of replaying this one

The operator must be able to answer: **what will happen after I restore this version?**

### 5) Apply-plan card

This card publishes:

- restore as live file now
- export as detached copy
- restore locally but hold outward replay pending settlement
- delay restore until runtime/watch conditions are healthy

Each action shows the required preconditions and resulting receipt.

The operator must be able to answer: **which restore shape matches my intent without accidental re-archive or unexpected propagation?**

### 6) Restore receipts

Receipts show:

- candidate selected
- liveness state at apply time
- actual scope achieved
- whether replay occurred
- whether re-archive was avoided or later observed

## Non-negotiable rules

### Rule 1 — restore intent must name scope

`Restore` is not enough; the page must say whether the operator means export, local live restore, or share-wide replay.

### Rule 2 — runtime liveness is a precondition, not folklore

If the engine must be running or freshly watching the subject, the page must say so directly.

### Rule 3 — re-archive risk must be named before apply

Older-version replay risk must remain explicit instead of being discovered after the restored file disappears again.

## Honest outputs

The page may conclude:

- `This candidate can be restored as a detached export now, but live replay is guarded because runtime watch state is stale.`
- `Live restore is safe because the engine is currently running and can immediately observe the extraction as a new local change.`
- `If you restore this version while the engine is stopped, the next rescan may archive it again as older than the current peer state.`

It may not collapse those outcomes into one generic `version restored` toast.
