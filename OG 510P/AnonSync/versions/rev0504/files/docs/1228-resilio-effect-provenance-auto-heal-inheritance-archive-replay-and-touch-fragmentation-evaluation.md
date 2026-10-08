# Resilio effect provenance, auto-heal, inheritance, archive replay, and touch-induction fragmentation evaluation

## Why this pass exists

The archive already had strong work on permission classes, non-authority convergence, mutation chronology, change witness, archive restore, and local-share inheritance.
What the current revision chain still lacked was one tighter current Resilio pass about another ordinary operator question:

> what actually **caused** the state I see right now — a direct publish, a source-authoritative cascade, an automatic overwrite-heal, a manual archive replay, an inherited local-share downshift, an encrypted-seat hard-wire, or merely a detection-induction act like `touch` that changed what the product noticed rather than what the user meant?

Current official Resilio docs are useful here precisely because they remain candid.
Today those docs still show that:

- `User Management` still says different permissions can be granted to different peers, that Read Only changes do not propagate, that changed files on a Read Only peer suspend further synchronization for that peer, and that `Disconnect` revokes future updates while leaving already-synchronized files in place;
- `Is one-way synchronization possible?` still says `Overwrite any changed files` reverts content edits to the RW version, restores deletions, re-downloads the old path after a rename, leaves added files local and unsynced, and still allows Read Only peers to transfer unmodified bytes to new peers;
- `Folder Preferences` still says `Overwrite any changed files` is potentially destructive and unavailable for Read-only folders with Selective Sync ON;
- `Sharing a folder locally` still says a local share only syncs with its parent source share, inherits the permission floor of the source, can automatically downshift when the source seat is narrowed, and for Advanced shares may need remove-and-reshare rather than in-place permission editing;
- `Encrypted folders` still says encrypted nodes are Read Only, have overwrite-heal always enabled, follow delete state from the source, and cannot republish deleted files back from their own Archive;
- `Using Archive for file versioning and restoring deleted files` still says restore is manual, requires Sync to be running if the older version is to be uploaded to others instead of being re-archived on later rescan, and still does not record in Archive which peer made the change;
- `How to touch files?` still says manual `touch` is a remediation when Sync missed the update, because Sync considers a file changed when its modified time or size changes.

That is strong operator candor.
It is also another strong reason not to clone the contract as-is.

## What current Resilio still gets right

### 1) It admits that the same visible outcome can have different origins

Current docs still make clear that a surprising state can come from different mechanisms:

- direct remote publish,
- local unauthorized edit,
- automatic source heal,
- inherited local-share cascade,
- encrypted hard-wire,
- manual archive replay,
- or touch-based detection induction.

That distinction is worth preserving.

### 2) It admits that `reverted` and `restored` are not one thing

The current docs still show that:

- a content edit can be reverted from source,
- a delete can be restored,
- a rename can produce the old name again,
- an added file can remain only local,
- a manual Archive extraction can republish older bytes,
- and `touch` can change detection posture without proving fresh author intent.

That is unusually candid and worth keeping.

### 3) It admits that some origins are direct while others are derived or hard-wired

The current linked-device, local-share, and encrypted-folder docs still show that some observed outcomes are not the result of one direct grant or one direct actor.
Some are inherited, some are hard-wired by seat class, and some are triggered by standing policy.
That distinction matters.

## Why AnonSync still should not clone it

### 1) Effect provenance truth is still too scattered

The ordinary operator still has to reconstruct whether the current state came from:

- a direct publish by some peer,
- a direct local action that did **not** publish,
- a source-authoritative overwrite-heal,
- a derived local-share cascade,
- a hard-wired encrypted-seat follow behavior,
- a manual archive replay,
- or a touch-induced detection refresh.

AnonSync should not let one vague `updated`, `restored`, `synced`, or `reverted` label hide those distinctions.

### 2) Detection induction still sits too close to content authorship

Current docs still say `touch` can be the fix when Sync missed an update.
That is a real and useful remedy.
But it also means the product needs to distinguish **content mutation** from **detection induction**.
AnonSync should not let `noticed after touch` masquerade as `new content was authored now`.

### 3) Manual replay and automatic heal still blur together

Current docs still show that Archive restore is a manual replay act while overwrite-heal is an automatic source-authoritative act.
They can both produce a file that looks `back` or `corrected`, but they are different provenance classes.
AnonSync should publish that difference directly.

### 4) Derived-source effects still blur with direct actor effects

Current docs still show that local shares inherit posture from a parent source and encrypted peers follow delete state with hard-wired overwrite-heal.
But an ordinary operator still has to remember which surprising state came from a direct peer and which came from seat-class or source-class derivation.
AnonSync should make that first-class.

## Hard decisions now locked for AnonSync

1. **Effect provenance is a first-class contract object.**
2. **Result class and origin class are separate truths.** `restored`, `reverted`, `reappeared`, `stayed local-only`, and `noticed now` must each retain a distinct origin classification.
3. **Direct publish, derived cascade, automatic heal, manual replay, and detection induction are separate origin classes.**
4. **Detection induction is weaker than content authorship.** A touched file may prove fresh notice without proving fresh user intent.
5. **Hard-wired seat behavior and inherited source behavior must stay visible as origin basis, not hide inside role labels.**
6. **Every serious surprising-state event needs one receipt that preserves result class, origin class, actor basis, mechanism class, and the blocked stronger sentence.**

## Replacement page family justified by this pass

This pass therefore justifies five more product-owned surfaces:

- **Effect-provenance contract sheet**
- **Surprising-state review**
- **State-origin proof**
- **Effect-provenance timeline**
- **Effect-provenance lineage receipt**

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still right that a current state may come from a direct publish, a source-heal, an inherited local-share cascade, an encrypted hard-wire, a manual archive replay, or a touch-induced re-detection. But it still makes one ordinary operator answer — `who or what actually caused the state I see now, and did bytes change or did only product notice change?` — depend on several articles instead of one stable product-owned family. AnonSync should keep the candor and refuse the fragmentation.
