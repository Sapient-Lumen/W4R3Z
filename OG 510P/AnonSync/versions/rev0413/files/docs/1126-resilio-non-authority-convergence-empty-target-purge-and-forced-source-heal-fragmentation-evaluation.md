# Resilio non-authority convergence, empty-target purge, and forced source-heal fragmentation evaluation

## Why this pass exists

The archive already has strong work on repair ladders, placeholder materialization, permission classes, encrypted custody, and path repair.
What it still lacked was one tighter current Resilio pass about another ordinary operator question:

> this seat is not allowed to author shared truth here — will it suspend, auto-heal from source, keep local strays, purge unknowns, or force the source state back down onto this path?

Current official Resilio docs are useful here precisely because they are candid.
Today those docs still show that:

- `Folder Types and Management` still says a **Read Only** folder cannot send changes, additions, or deletions to the rest of the swarm, and also says that if you do change local copies you may no longer receive updates to those files.
- `Sync Share Dialog (Desktop)` still says a **Read Only** peer can make deletes, edits, and additions locally, but none of those changes sync outward.
- `Folder Preferences` still says `Overwrite any changed files` is potentially destructive, restores source authority on a Read Only folder, and is disabled for Read-only folders with Selective Sync ON.
- current Resilio guidance for encrypted folders still says encrypted backup peers are Read Only, always have `Overwrite any changed files` activated, and do not support Selective Sync.
- `Power user preferences` still publishes hidden posture-shaping settings including `overwrite_changes false`, `folder_defaults.delete_unknown_files false`, and `sync_ro_delete_unknown_file false`, with the last one described as working for Sync jobs on an **empty folder on an RO agent** and as **not optimized for pre-seeded folders**.

That is a good reason to keep studying Resilio.
It is also another good reason not to clone the exact interface contract.

## What current Resilio still gets right

### 1) It admits that non-authority local change does not have one fate

Current docs still distinguish:

- per-file suspension / no further updates
- source-authoritative overwrite heal
- local-only survivor files
- restored deletions
- rename duplication / re-download of old path
- hidden empty-target delete posture
- encrypted seats that hardwire overwrite

That honesty is valuable.

### 2) It admits that recovery posture is role-shaped

A regular RO peer, a config-authored RO peer, an encrypted F-key peer, and an empty RO target with special defaults do not share one convergence contract.
That distinction is worth preserving.

### 3) It admits that destructive heal may depend on hidden defaults or role hardwire

Current docs still keep some of the most important destructive posture in power-user tables or seat-class caveats rather than on the ordinary folder page.
That means `ordinary RO`, `RO with overwrite`, `encrypted RO`, and `empty-target purge-capable RO` are materially different worlds.

## Why AnonSync still should not clone it

### 1) One ordinary answer still spans too many pages

To answer `what will happen to non-authority local changes here?` the operator may still need to combine:

- folder-type / permission docs
- share dialog docs
- folder preferences
- encrypted-folder caveats
- power-user defaults

That is too much archaeology for one ordinary decision.

### 2) `Overwrite any changed files` still compresses too many distinct outcomes

The same label can mean:

- restore a deletion
- revert content
- keep a renamed survivor while re-downloading the old name
- keep a newly added file local-only and unsynced
- act as a standing destructive-heal posture on encrypted peers
- maybe widen into empty-target unknown-file deletion when power-user posture changes

AnonSync should not inherit that compression.

### 3) Hidden default posture still matters too much

`overwrite_changes`, `folder_defaults.delete_unknown_files`, and `sync_ro_delete_unknown_file` can materially change what happens before an ordinary operator opens one folder card.
Current Resilio docs still leave too much of that truth in power-user tables.

### 4) Empty-target purge and pre-seeded caution are still under-owned

Current docs are candid that `sync_ro_delete_unknown_file` works for an empty folder on an RO agent and is not optimized for pre-seeded folders.
That is an operationally real edge.
It should not stay a one-line power-user footnote.

## Hard decisions now locked for AnonSync

1. **Non-authority convergence is a first-class contract object.** `suspends-on-local-change`, `source-heal-enabled`, `forced-source-heal`, `local-only-survivor`, `rename-duplicate`, `empty-target-purge`, and `unknown` are separate verdicts.
2. **Seat class and posture origin stay visible.** Standard RO, encrypted custody, default-derived RO, and empty-target RO bootstrap do not share one sentence.
3. **Heal posture is separate from survivor posture.** A seat can auto-heal edits while still leaving additions local-only.
4. **Empty-target purge is a reviewed destructive posture, not a hidden convenience default.**
5. **Proof matters.** `documented default`, `visible option`, `seat-class hardwire`, and `runtime behavior witnessed` are separate truths.
6. **Receipts preserve the strongest safe sentence and the blocked stronger sentence.**

## Replacement page family justified by this pass

This pass therefore justifies five more product-owned surfaces:

- **Non-authority convergence contract sheet**
- **Read-only divergence review**
- **Empty-target purge review**
- **Forced source-heal proof**
- **Non-authority convergence lineage receipt**

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still right to admit that a non-authority seat can suspend, auto-heal, preserve some local survivors, or even purge unknown files under hidden posture. But it still makes one ordinary operator answer — `what exactly happens to my local divergence on this seat, and what destructive heal posture is really active?` — depend on permission docs, folder preferences, encrypted-folder caveats, and power-user tables instead of one stable page family. AnonSync should keep the candor and refuse the archaeology.
