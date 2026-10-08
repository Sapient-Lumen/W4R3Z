# Resilio priority, residency, and placeholder-promise fragmentation evaluation

## Why this pass exists

The archive already had strong doctrine for fetch intent, hydration engines, inbound priority, placeholder eviction, and disconnected return contracts.
What it still lacked was one direct evaluation for another ordinary seam that current official Resilio docs make sharper rather than simpler:

> when the product shows a file as visible, lets the operator click `Sync to this device`, offers a priority rule, and keeps a placeholder around, what exact promise has actually been made about local presence?

Current official Resilio docs still answer pieces of that question, but not in one place.
Across current Sync materials they still say all of the following:

- `File download priority` is available in Sync `3.1.0`.
- download priority can be set globally and per share.
- once a share's priority has been manually changed, later global changes stop applying to it even if the share is later set back to `None`.
- only the active queue is prioritized, with a 50k-file cap, suspension behavior, and internal exceptions.
- a running large-file transfer can be suspended immediately when a higher-priority file appears.
- single-file sending uses the default priority and cannot be changed after it starts.
- placeholders are still 0-byte local stand-ins for non-local data.
- fetching a subtree can later auto-download new descendants there.
- `Remove from this device` and `Remove from all devices` are still materially different actions.
- removing or disconnecting a Selective Sync share can remove placeholders from the local filesystem.
- at least one destructive guardrail is still explicitly ignored in Linux WebUI.
- some announced files can still become ghost items because no full-copy source remains online or alive.

That is useful product honesty.
It is also exactly why AnonSync should not clone the contract as-is.

## What Resilio gets right

### 1) It admits that queue order and local presence are not the same truth

This is important.
A product that pretends `priority` means `guarantee` teaches operators the wrong mental model.
Resilio does not quite do that.
Its current docs admit:

- priority applies only to active queue membership
- queue exceptions exist
- large transfers can be interrupted and rebuilt
- source availability still matters

That candor is worth borrowing.

### 2) It admits that placeholders and local bytes are materially different states

Current placeholder docs still make clear that names-only visibility, subtree fetch, local reversion to placeholders, and all-device deletion are different actions with different outcomes.
That is better than a flat `available offline` badge.

### 3) It admits that future-descendant behavior matters

Current Selective Sync and RSLS docs still say that fetching or syncing a subtree can change later behavior under that subtree.
That is exactly the sort of detail serious products often hide.
AnonSync should keep that candor.

### 4) It admits that source absence can invalidate an apparently normal fetch path

Current ghost/no-source warnings still tell the truth that a visible name is not enough.
If nobody retains the full bytes, a later download promise collapses.
That is important and worth preserving.

## Why this is still a strong reason not to clone them

The ordinary operator answer is still too scattered.
Current official Resilio docs still force too much reconstruction before the product fully owns these questions:

- is this subject merely visible, or already guaranteed local?
- is the current `priority` value a queue preference, a standing local override, or a true local-availability commitment?
- if the operator returns to `None`, did inheritance actually resume or did a sticky local contract remain frozen?
- will later descendants under this fetched subtree also materialize here?
- does `Remove from this device` merely free space, or can the operator accidentally destroy the last full copy?
- is a pending fetch only delayed, or already source-impossible because the remaining witnesses are placeholders or offline ghosts?

That should not require stitching together a priority article, power-user defaults, Selective Sync docs, RSLS docs, disconnect/remove docs, and warning prose.

## The tighter AnonSync conclusion

AnonSync should borrow the following from current Resilio more boldly:

- explicit candor that queue order and residency guarantee are different things
- explicit candor that placeholders, hydrated bytes, and future-descendant auto-hydration are different things
- explicit candor that source-witness loss can collapse a fetch promise
- explicit candor that surface and settings inheritance matter

But AnonSync should refuse the exact contract whenever one ordinary answer still depends on several pages.
The product should not let `priority`, `Sync to this device`, `keep local`, or `remove from this device` stand without one owned surface that states:

- current residency intent
- current guarantee class
- inheritance versus override basis
- budget / subtree expansion consequences
- source-witness count and ghost-risk basis
- strongest safe sentence and stronger forbidden sentence

## Replacement pages added for this seam

This pass therefore adds five more page-shaped obligations:

1. **Residency intent** — what the product is trying to make true locally, and how strong that claim currently is.
2. **Residency policy review** — how inheritance, override, and neutral/default actually behave before commit.
3. **Residency budget** — what local byte budget, subtree expansion, and future auto-hydration the promise consumes.
4. **Hydration queue admission** — whether this pending local promise still has enough surviving source proof to be honest.
5. **Residency promise receipt** — what later proves whether the product merely queued, actually guaranteed, or already completed local presence.

## Bottom line

The tighter no-clone reason is now this:

> Resilio is current evidence that priority, placeholders, and no-source warnings are operator-worthy truths; it is also current evidence that one ordinary local-presence question can still require several articles before the product clearly says whether a thing is visible, queued, guaranteed, or already impossible. AnonSync should copy the candor and refuse the fragmented promise contract.
