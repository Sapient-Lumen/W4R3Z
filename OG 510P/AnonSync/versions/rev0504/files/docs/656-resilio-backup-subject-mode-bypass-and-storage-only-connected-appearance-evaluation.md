# Resilio backup-subject mode bypass, storage-only connected appearance, and subject-kind override evaluation

## Why this pass exists

The archive already had strong doctrine for capture-only ingest, mobile source/sink truth, future-arrival defaults, bind-right review, and seat-role meaning.
What it still lacked was one direct current Resilio evaluation for a narrower but important question:

> when a subject is *special by kind* — especially mobile backup — does the product keep that exception explicit, or can the subject silently bypass the seat's advertised arrival default and still look like an ordinary connected share?

Current official Resilio docs still show a useful, living product, but they also still show that one ordinary answer is spread across several article families at once:

- `Synchronization Modes`
- `How to use Camera Backup (all mobiles)?`
- `How to Back up data (Android only)`
- `Can I connect two pre-populated pre-existing folders?`
- `Sync Private Identity & Linking My Devices`
- `Sync functionality in detail`

## Current official Resilio evidence that matters here

Current official docs still show an active v3 line through `3.1.2.1076`.
They also still say all of the following:

- `Synchronization Modes` still says linked devices can be set to `Disconnected`, `Selective Sync`, or `Synced` to control how much data is moved to each device.
- `How to use Camera Backup (all mobiles)?` still says camera backup is for storage purposes, creates `1.4` folders with Read Only keys, auto-creates a backup folder on the destination desktop, and leaves already-present pictures on both devices when the backup is stopped/disconnected.
- `How to Back up data (Android only)` still says backup is not ordinary bidirectional sync: desktop has Read Only access, desktop-side changes do not sync back, and deleting files on the desktop does not delete them on the phone.
- `Can I connect two pre-populated pre-existing folders?` still says that when using mobile's backup with linked devices, the share will always appear connected on destination desktops regardless of the syncing mode, and that the operator must disconnect and reconnect it.
- `Sync Private Identity & Linking My Devices` and `Sync functionality in detail` still say linked devices share a common folder list and can rely on linked-device arrival convenience.

So current Resilio still contains a real but scattered answer to `does this seat default still matter for this subject, or is this share kind quietly stronger than the default story?`

## What Resilio still gets right

### 1) It is candid that backup is not ordinary sync

The docs do not pretend backup is merely a marketing name for collaborative sync.
They openly say the desktop side is Read Only, that deletions do not mirror back symmetrically, and that the flow exists for storage purposes.
That honesty is valuable.

### 2) It still admits that subject kind can matter more than mode labels

The docs do not hide that backup behaves differently from ordinary linked-folder arrival.
They openly describe a real exception where mobile backup can land connected on a linked desktop regardless of the chosen syncing mode.
That candor matters.

### 3) It still publishes the repair ritual instead of silently ignoring the mismatch

The `disconnect and reconnect it` instruction is awkward, but it is explicit.
Resilio does not merely let the mismatch persist without explanation.

## Why this is still a good reason not to clone them

### 1) Seat default can be bypassed by subject kind without one native exception object

Current docs still let the operator believe that `Disconnected`, `Selective Sync`, or `Synced` is the arrival contract for linked devices in general.
Then a backup subject can still appear connected regardless of that mode.

AnonSync should not inherit a model where a subject-kind carve-out silently outruns the seat default and only later reveals itself through support prose.

### 2) Connected appearance still overstates collaborative meaning

Current docs still allow a storage-only backup subject to appear `connected` on the destination desktop even though:

- the desktop is Read Only
- sink-side changes do not flow back
- the flow is for storage purposes only
- disconnect/reconnect may be needed merely to reassert the operator's intended placement or posture

A serious sync product should not let `connected` flatten together collaborative sync, storage-only sink, and subject-kind override.

### 3) The remedy is still a ritual rather than a first-class policy exception

Current docs still route the correction through `disconnect and reconnect` instead of one explicit page that says:

- this subject kind overrides your current seat default
- here is why
- here is the real role/writeback/materialization contract
- here is the least-strong remedy if you want a different posture

That is not just a wording problem.
It means the exception is implemented, but not owned.

### 4) Later operators still have to reconstruct why the share looked ordinary

Current Resilio still leaves later operators to reconstruct whether the honest sentence is:

- `the seat default was bypassed for this subject kind`
- `this connected-looking share is actually storage-only`
- `desktop writeback is intentionally blocked`
- `disconnect/reconnect was only a posture repair, not a lineage break`

That sentence should belong to one product-owned page and one durable receipt.

## The tighter AnonSync conclusion

AnonSync should borrow the following from Resilio more boldly:

- candid admission that backup is a different contract from collaborative sync
- candid admission that seat defaults can have carve-outs
- explicit publication of the workaround when the current product shape forces one

But AnonSync should refuse the exact page contract whenever one ordinary answer still depends on:

- seat-wide mode labels
- backup-specific help pages
- storage-only caveats
- desktop Read Only exceptions
- disconnect/reconnect ritual to repair an unexpected connected-looking arrival

## The replacement pages this evaluation justifies

This pass therefore makes four page-shaped obligations concrete:

1. **Subject-kind override** — what special subject contract is outriding the seat default, and why?
2. **Arrival-exception review** — does this subject keep the seat default or carve out its own arrival/role/writeback posture?
3. **Storage-only arrival posture** — if the subject looks connected, what collaborative powers are actually absent?
4. **Subject-kind override receipt** — what default was in scope, what exception won, and what remedy remains available?

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still good evidence that backup and storage-only subjects are real and useful, but it is also current evidence that one ordinary question — `does this seat default still apply to this subject?` — can still require mode docs, backup docs, Android asymmetry notes, and a reconnect ritual just to learn that the subject kind silently bypassed the default and only *looks* like an ordinary connected share. AnonSync should copy the candor and refuse the silent-override contract.
