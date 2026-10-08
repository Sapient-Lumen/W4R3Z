# Resilio presence, materialization, source guarantee, and ghost-fetch fragmentation evaluation

## Why this pass exists

The archive already had doctrine for queueing, chronology, archive survival, and change witness.
What the current revision chain still lacked was one tighter current Resilio pass about another operator-real question:

> when the product shows a file or folder name, what actually exists here: only a row, a path with placeholders, real local bytes, or merely a remembered object whose bytes may no longer exist on any reachable source?

Current official Resilio docs are useful here precisely because they are candid.
Today those docs still show that:

- disconnected folders can still appear in the UI even when they do not yet have any local folder path;
- Selective Sync and Connected-mode entries can expose names through 0-byte placeholder files that are not the actual data;
- a placeholder can later be materialized only if at least one peer that still has the bytes is online;
- `Remove from this device` changes local residency back into a placeholder while `Remove from all devices` is a deletion operation with archive consequences;
- disconnecting a Selective Sync folder removes placeholders from the filesystem on that device;
- a peer can announce a file and later leave only placeholders behind, creating a `no source peers online for too long time` warning for a ghost file that nobody actually has anymore;
- local shares depend on the parent source share for actual data, so if the parent has only placeholders the local share cannot materialize the file either;
- power-user switches like `disable_remove_from_all_devices` and `recreate_placeholders_on_removal` materially change what a delete gesture is allowed to mean.

That is strong operator candor.
It is also another strong reason not to clone the contract as-is.

## What current Resilio still gets right

### 1) It admits that visible namespace is not the same as local bytes

Resilio does not pretend that seeing a name means possessing the file.
Its current docs still admit that a disconnected folder can exist as a future action row, and that Selective Sync can expose placeholder names without byte residency.
That distinction is worth keeping.

### 2) It admits that materialization needs a live source, not just a remembered name

The current placeholder and synchronization-mode docs still say on-demand fetch depends on at least one online peer with the file.
The ghost-file warning article is especially valuable because it tells the truth that a remembered file can outlive the actual last byte source.

### 3) It admits that residency-changing gestures are not the same as deletion

Current docs still separate `Remove from this device` from `Remove from all devices`, and the power-user preferences still expose extra safety rails around placeholder deletion.
That matters because a very similar gesture can either free local space or propagate a destructive delete.

### 4) It admits that downstream copies can depend on upstream materialization

The local-share article is unusually candid that local shares only get data from their parent source share and that placeholders upstream mean no bytes downstream.
That is exactly the sort of dependency many products would hide.

## Why AnonSync still should not clone it

### 1) Presence truth is still too scattered

The ordinary operator still has to reconstruct whether a shown object is:

- only a disconnected row,
- a placeholder path,
- a fully materialized local copy,
- or a fetch candidate with no currently proven byte source.

AnonSync should not let one `available` or `connected` badge hide those distinctions.

### 2) Fetchability and visibility are still too easy to overmerge

Current docs still require the operator to stitch together placeholder help, synchronization modes, and ghost-file warnings to answer one basic question:

> can I actually get the bytes for this thing right now, or do I merely know its name?

AnonSync should keep `source guarantee` as first-class state.

### 3) Space-saving gestures and destructive gestures still sit too close together

Resilio is better than many products here, but the operator still has to piece together placeholder semantics, archive behavior, and power-user safety toggles to know what delete-like actions are allowed to mean.
AnonSync should publish gesture authority and deletion blast radius directly on the review surface.

### 4) Parent/child byte dependency still reads more like a tip than a durable contract

The current local-share article states the truth, but the operator still has to remember it from documentation rather than see it as stable product-owned state.
AnonSync should publish source dependency continuously whenever a local or derived view cannot materialize bytes on its own.

## Hard decisions now locked for AnonSync

1. **Presence is a first-class contract object, not a side effect of sync mode and placeholder mechanics.**
2. **Disconnected row, bound path, placeholder namespace, local byte residency, and source guarantee are separate truths.**
3. **Visible name is weaker than local path, local path is weaker than local bytes, and local bytes are weaker than durable future fetchability.**
4. **`Remove from this device` is a residency mutation, not a deletion claim.**
5. **Delete authority, placeholder safety rails, and source dependency must be visible as typed state, not buried in tips and preferences.**

## Replacement page family justified by this pass

This pass therefore justifies five more product-owned surfaces:

- **Presence contract sheet**
- **Residency-mode review**
- **Materialization proof**
- **Parent-source dependency review**
- **Presence lineage receipt**

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still right that disconnected rows, placeholders, materialized bytes, online sources, and delete-like gestures are materially different truths. But it still makes one ordinary operator answer — `what actually exists here right now, and can I really fetch it later?` — depend on several pages instead of one stable product-owned family. AnonSync should keep the candor and refuse the fragmentation.
