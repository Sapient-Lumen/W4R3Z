# Resilio path continuity, relocation, disconnected presence, and rename semantics evaluation

## Purpose

The archive already has stronger answers for intake, target reconciliation, name planes, same-host lineage, fetchability, shell parity, and repair ladders.
This document asks a narrower but still ordinary question that current Resilio docs keep making visible:

> when a shared thing changes *where it lives* or *what it is called on disk*, where does the product itself own the answer, and where does the operator still have to remember move/rename/disconnect/reconnect folklore?

This is not a complaint that Resilio lacks path flexibility.
It does have path flexibility.
The problem is that the operator truth still leaks across too many different articles.

## Current Resilio evidence that matters

Current official docs still show all of the following at once:

- renaming a syncing folder is local-only; peers do not inherit the new name
- Windows and macOS allow move tracking only within the same logical drive, while cross-partition moves fall into `Folder not found`
- Linux is stricter and does not support moving the sync share itself outside the parent-folder expectation
- mobile platforms do not support moving sync shares at all
- disconnected folders are pathless objects in the UI, not bound local mounts
- removing a disconnected folder removes it from all linked devices
- new linked-device arrivals go to the default folder when the seat is in `Selective Sync` or `Synced`
- choosing a custom arrival path still depends on switching the seat to `Disconnected`, then later pressing `Connect`
- same-name arrivals in the default location can create indexed duplicates such as `(1)`
- reconnecting to an old location can legitimately trip `Folder not empty`, while binding to some unrelated non-empty tree can still overwrite or delete bytes
- rename propagation on remote peers can reuse bytes through Archive/hash continuity instead of re-transmitting, but that truth still depends on Archive being enabled and on the operator understanding the remote replay shape

These are all useful facts.
The problem is that they still do not add up to one stable product-owned answer for ordinary path continuity.

## Where Resilio is genuinely good

### 1) It admits that path and title are not the same thing

Resilio's docs are better than many products at quietly revealing that a local path basename is not a universal subject title.
A folder rename on one seat remains local to that seat.
That is useful honesty and AnonSync should keep it.

### 2) It does not lie about cross-volume limits

The docs also do not pretend all moves are equivalent.
Cross-volume and cross-partition changes really can break the mount relationship and fall into repair or reconnect work.
That is much better than silently re-importing or silently making a duplicate.

### 3) It exposes pathless presence as a real state

`Disconnected` is not merely a cosmetic pause.
The docs make clear that a disconnected folder can still be represented in the product without a local path.
That is useful and AnonSync should keep the idea.

### 4) It gives a real remote-rename optimization story

The Archive/hash explanation for file rename propagation is one of the better pieces of product candor in the category.
It tells the operator that some `rename` stories are really `archive old name, notice new name, restore same bytes under new name` stories.
AnonSync should keep that honesty too.

## Why this still does not earn cloning

### 1) Arrival path choice is still ritualized

Current docs still make custom arrival placement depend on mode switching, later `Connect`, default-folder behavior, and duplicate cleanup ritual.
That means the answer to `where will this mount land here?` is still not one ordinary page.

### 2) Disconnected presence is still semantically overloaded

Current docs still make `Disconnected` carry too many meanings at once:

- no local path
- still known subject
- future connect opportunity
- removable everywhere if you choose `Remove`
- possible source for reconnect to old material
- possible source of later duplicate/default-path accident

That is too much meaning for one little state chip without a stable page behind it.

### 3) `Folder not empty` still mixes safe and unsafe cases

Resilio's own docs admit that the same warning can mean:

- harmless reconnect to the very place that previously synced
- deliberate merge into an already existing non-empty folder where pre-existing bytes may be overwritten or deleted

That is exactly the kind of overloaded review answer AnonSync should refuse to clone.

### 4) `Folder not found` is honest, but still not one path-continuity page

The repair advice is practical.
But the answer still lives across move/rename docs, folder-not-found troubleshooting, duplicate-folder docs, and disconnect/reconnect docs.
The product idea is right.
The page contract still is not.

### 5) Remote rename consequences are still support-lore shaped

Resilio explains the remote replay story in a separate article.
That means one ordinary operator question — `if I rename or move this here, what exactly happens elsewhere?` — still is not owned by the same page where the rename or move decision would naturally live.

## What AnonSync should borrow

AnonSync should borrow all of these ideas:

- local path rename does not imply global subject rename
- path continuity must distinguish same-volume tracking from rebind/reconnect work
- pathless known-subject presence is a real state
- default/suggested arrival roots are useful
- duplicate-path accidents should be typed, not hand-waved
- remote rename/move can sometimes be replayed from retained bytes rather than retransmitted

## What AnonSync should refuse to clone

AnonSync should refuse these interface shapes:

- mode-switching as the main way to express arrival-path intent
- pathless disconnected presence without one page that explains its scope
- one `folder not empty` answer that has to cover both safe reconnect and dangerous merge
- path repair that begins with article archaeology instead of a reviewed relocation page
- rename behavior explained only in a separate FAQ rather than adjacent to the action and receipt

## The replacement page family this evaluation now requires

This pass therefore adds four more ordinary pages:

1. `305-share-path-page-current-bind-root-volume-and-relocation-eligibility-interface-spec.md`
2. `306-relocate-review-page-same-lineage-cross-volume-and-peer-continuity-interface-spec.md`
3. `307-disconnected-share-page-pathless-presence-connect-choice-and-removal-scope-interface-spec.md`
4. `308-rename-move-explanation-page-local-path-change-remote-replay-and-archive-dependence-interface-spec.md`

The sharpened line is now:

> when Resilio keeps path continuity honest only by splitting it across move/rename FAQs, disconnected-folder semantics, duplicate-folder repair, and archive-replay explanations, AnonSync should copy the honesty and replace the pages.
