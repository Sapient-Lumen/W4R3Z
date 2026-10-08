# Resilio sync-mode meaning, current-vs-future split, and clear/disconnect return-contract evaluation

## Why this pass exists

The archive already had strong abstractions for share-local presence, byte posture, future-arrival defaults, disconnected rows, placeholder eviction, and destination-world review.
Those were necessary, but another current Resilio pass still exposes a more ordinary operator seam.
The problem is no longer only `does this seat have bytes` or `what is the future-arrival default`.
It is now:

- what exactly a visible `Disconnected`, `Selective Sync`, or `Synced` label means **for this share right now**
- what that same label also implies **for future linked-device arrivals on this seat**
- whether the current local state is names-only, placeholder-backed, or fully materialized
- whether `Clear`, `Remove from this device`, and `Disconnect` preserve the same path and return contract
- whether reconnect will actually restore the prior bind or instead propose a default path that can create a `(1)` duplicate

That seam is still materially real in current official Resilio docs.
They still document three synchronization modes for linked devices.
They still tie default connect mode and default folder location to future arrivals.
They still document placeholders as zero-byte proxies created by Selective Sync or Connected mode.
They still distinguish `Remove from this device` from `Remove from all devices`.
They still show mobile `Clear` actions that revert local bytes to placeholders and separate disconnect/remove actions that preserve different things.
They still say reconnect can propose a different default path and can create `(1)` duplicates.
The current v3 line still appears active through `3.1.2.1076`.

That is useful candor.
The non-clone problem is workflow ownership.
Resilio still leaves the ordinary sentence `what exactly does this mode mean here, right now, and what happens if I clear or disconnect?` split across mode docs, placeholder docs, mobile interface docs, reconnect docs, and mobile default-folder docs.

## What current Resilio gets right

Current official docs still deserve credit for saying plainly that mode and local-presence behavior are not flat.
They still connect useful operator concepts to real product consequences:

- `Disconnected` really is different from `Selective Sync` and `Synced`
- placeholders really are zero-byte proxies, not hidden full copies
- device-level mode defaults really do affect later linked-device arrivals
- mobile `Clear` really does revert local bytes to placeholders instead of implying the share vanished
- disconnect really does preserve filesystem material while ending sync participation
- reconnect really can be a path-choice event rather than a simple `resume exactly where I was`

That is better than pretending all local presence is one status bit.
AnonSync should keep that candor.

## What current Resilio still leaves fragmented

Current official docs still make the operator reconstruct one ordinary answer from several pages:

- `Sync functionality in detail` and `Synchronization Modes` explain the three mode families.
- `Sync Preferences`, `Settings on mobile platforms`, and `Simple Mode (Android)` explain how defaults and auto-placement affect future arrivals.
- `What Is an RSLS File?` explains placeholder, local revert, and all-devices delete semantics.
- `Sync interface on Android` and `Sync Interface on iOS devices` explain `Clear`, `Disconnect`, and `Remove from this device` affordances.
- `Disconnecting and Removing Folders`, `How to manually set the location...`, and `Folders are duplicating with an index (i)` explain reconnect and duplicate-path fallout.

The operator therefore still has to do archaeology to answer a simple question:

> this share says `Selective` or `Disconnected` and I can clear or disconnect it here; what exact current-share truth, future-default truth, byte truth, and return-path truth does that sentence actually earn?

## Why this is a strong non-clone reason

This is not a cosmetic labeling issue.
It changes the product's claim ceiling and can distort local actions.
Without a first-class mode-meaning object, the product can accidentally let operators say things that are stronger than the evidence supports, such as:

- `this share is disconnected` when only the current share is disconnected and future linked-device arrivals will still auto-land
- `Selective Sync means placeholders` when some subtrees are already fully materialized locally
- `Clear is basically disconnect` when the path, row, and reconnect contract stay materially different
- `Reconnect returns to the same place` when the product may propose a default path and create `(1)` duplicates
- `same name means same bind` when the path was auto-proposed, suffix-adjusted, or default-routed rather than reviewed

All of those can be false for reasons the docs themselves already admit are real.

## Better product move for AnonSync

AnonSync should not clone a contract where mode meaning remains scattered across linked-device, placeholder, mobile, and reconnect help.
It should instead make **sync mode meaning and return contract** first-class.

That means every serious mode-bearing share should publish, in one stable reviewed object:

- current-share posture
- future-arrival default in the relevant scope
- current byte posture
- current path basis
- return contract after clear / local remove / disconnect
- strongest safe sentence
- stronger forbidden sentence
- receipt showing what current-vs-future meaning was actually reviewed

## New page family required

This pass therefore adds four explicit replacements:

1. **Current sync mode** — what this mode means for the current share, future arrivals, bytes, and path basis.
2. **Sync mode change review** — what exactly changes if the operator edits current mode or future default.
3. **Clear-versus-disconnect review** — what survives, what returns as placeholders, what leaves sync, and what reconnect will later need.
4. **Sync mode receipt** — durable safe language and return-contract proof.

## Condensed design verdict

Borrow Resilio's candor that sync modes, placeholders, and reconnect behavior are real and useful operator concepts.
Do not clone a product contract where one mode chip still makes operators reconstruct current-share posture, future-arrival default, byte materialization, path basis, and return contract from several help articles.
