# Resilio placeholder materialization, eviction, delete, and archive-replay evaluation

## Why this pass exists

The archive already had strong doctrine for availability, chronology, conflict review, and retained history.
What it still lacked was one direct current Resilio evaluation for another ordinary seam:

> when an operator fetches a placeholder, reverts bytes back to placeholders, disconnects a selectively synced folder, deletes a placeholder, or restores a retained version from Archive, where does the product itself own the answer to `what exactly changes here and only here?`

Current official Resilio docs still show a useful, living product, but they also still show that ordinary byte-presence truth leaks across several different article families at once:

- synchronization modes
- Selective Sync
- RSLS / placeholder instructions
- disconnect / reconnect notes
- Archive / restore notes
- overwrite / pre-populated-folder and conflict FAQs

## Current official Resilio evidence that matters here

Current official docs still show an active v3 line through `3.1.2.1076`.
They also still say all of the following:

- `Disconnected`, `Selective Sync`, and `Synced` remain the three linked-device postures; connecting a disconnected folder asks for a local path and then represents the subject as placeholders on that seat.
- Placeholder files are still explicit 0-byte stand-ins in Selective Sync or `Connected` mode.
- Double-clicking a placeholder, or using `Sync to this device`, still materializes a file or subtree locally; if you sync a subfolder, later files added under that subtree are also automatically downloaded there.
- `Remove from this device` still reverts a file or subfolder back to a placeholder locally.
- The same system Delete gesture can still mean different things: used as local reclaim while reverting a file to a placeholder, but if the operator has Read & Write access and deletes a placeholder, the file is removed permanently from all peers.
- Disconnecting a folder still affects only one device and keeps the folder in the file system, but on selective-sync folders it also removes placeholder files from the folder on that device.
- Archive still stores deleted or older versions on other peers, keeps them for 30 days on desktops and 1 day on mobiles by default, and supports only manual restore.
- A restored archived file can still fall back into Archive if Sync was not running when the operator copied it out, because the restored file can look older than competing peer state.
- Current conflict and pre-populated-folder docs still say latest-timestamp / latest-online-return behavior can overwrite another peer's later online work, with overwritten versions placed in Archive.

So current Resilio still contains a real but scattered answer to `did I materialize bytes, reclaim them locally, delete them globally, or merely browse retained history?`

## What Resilio still gets right

### 1) It gives operators practical byte-posture language

`Disconnected`, `Selective Sync`, placeholders, and full sync remain useful concepts.
They are practical, operator-facing vocabulary rather than purely internal implementation terms.
AnonSync should keep that level of candor.

### 2) It admits that local materialization has future-arrival consequences

Current docs still plainly say that syncing a subfolder means later added files in that subtree will also arrive automatically.
That is a real semantic consequence, not a cosmetic download helper.

### 3) It is honest that retained history is not magic undo

Current Archive docs still say restore is manual and runtime-sensitive.
That honesty matters.
A sync product should not pretend that retained history automatically replays safely.

### 4) It preserves useful local-reclaim workflows

Current docs still let operators fetch only what they need and reclaim local bytes later.
That is a strong product idea worth preserving.

## Why this is still a good reason not to clone them

### 1) The same ordinary verb still has too many meanings

Current docs still let the operator discover too late that `Delete`, `Remove`, and `Disconnect` can mean materially different things depending on:

- placeholder versus full copy
- file versus subtree versus whole folder
- local browser versus WebUI versus folder menu
- read-only versus read-write authority
- whether the seat is simply reclaiming space or issuing a wider mutation

AnonSync should not ask the operator to infer that scope from folklore.

### 2) Materialization scope and future-arrival policy are still too implicit

Current docs do explain that syncing a subfolder causes later descendants to auto-download.
But the answer still lives in placeholder instructions rather than one stable product-owned page that says exactly what this fetch choice commits the seat to afterward.

### 3) Local reclaim and global deletion are still too easy to blur together

Current docs are candid, but the product contract still leaves too much scope hiding behind gesture interpretation.
That is a strong reason not to clone the page or gesture contract, even while borrowing the underlying capability.

### 4) Restore replay still depends on support-note reconstruction

Archive is useful, but the operator still has to cross-read Archive instructions, overwrite behavior, and timestamp-winner notes to answer one ordinary question:

- if I copy this retained version back now, will it actually replay into the swarm, stay local, or simply be re-archived?

That should be a first-class page, not article archaeology.

## The tighter AnonSync conclusion

AnonSync should borrow the following from Resilio more boldly:

- explicit byte-posture vocabulary
- selective materialization and local reclaim as first-class workflows
- retained history that admits manual review and restore
- honest warnings that chronology and runtime state matter during replay

But AnonSync should refuse the exact page contract whenever one ordinary answer still depends on:

- placeholder-state folklore
- access-dependent Delete semantics
- folder-menu versus file-browser differences
- hidden `.sync/Archive` browsing
- timestamp / runtime caveats only discovered after an attempted restore

## The replacement pages this evaluation justifies

This pass therefore makes four page-shaped obligations concrete:

1. **Fetch intent** — what materializes now, what remains placeholder-only, and what future arrivals follow from this fetch choice?
2. **Local eviction** — what leaves this seat only, what remains remotely, and does this strand the last full copy?
3. **Delete consequence** — is this local-only or global, what authority makes it so, and what retained-byte residue survives?
4. **Restore review** — which retained version is being revived, what chronology wins, and what replay risk follows from current runtime state?

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still good evidence that selective materialization, local reclaim, and retained history are worth building, but it is also current evidence that ordinary byte-presence truth still leaks across mode docs, placeholder docs, disconnect notes, and Archive instructions. AnonSync should copy the practicality and refuse the scattered verb contract.
