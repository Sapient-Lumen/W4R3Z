# Resilio cohort-census, live-set, historical-roster, and source-capability fragmentation evaluation

## What current official docs still make clear

Another current Resilio pass strengthens the archive's clone-veto line rather than weakening it.

Current official docs still say several things that are operationally real and worth borrowing:

- the main desktop view's `X of Y peers` does **not** mean one thing: current docs still say `X` is the number of online peers while `Y` is the total number of peers including offline peers
- the troubleshooting article for unsynced files sharpens that again: current docs still say `Y` is the number of peers that have **ever been connected** to the share and that gray peers in the list are disconnected
- the same desktop-view docs still say a peer that stays offline for 7 days gets disconnected from the folder, and that this threshold is configurable in power-user settings
- current device-list docs still say `Hide this device` only clears an offline record from view; it does not unlink the device, and the device reappears if it ever comes back online
- current synchronization-mode docs still say a linked-device folder may be visible in `Disconnected` mode without taking local space, and current folder-management docs still say disconnected folders may not even have a local folder path
- current local-share docs still say a local share counts as a peer, but it only connects to self and only pulls from or uploads to the parenting folder; it does not directly sync with remote peers

That is real candor.
It is useful product truth.

## What still should not be cloned

The operator is still asked to reconstruct several materially different questions from several different pages:

1. **how many participants are actually reachable right now?**
2. **how many rows are only historical roster residue?**
3. **which rows can currently serve bytes versus merely appear in the count?**
4. **which rows are only self-derived local branches rather than independent remote coverage?**
5. **which rows were hidden for decluttering and can still return on their own later?**

Current Resilio docs still spread those answers across the main view, troubleshooting, identity cleanup, synchronization-mode, and local-share guidance.

So a user can learn all the pieces and still not get one stable product answer to:

> when the product says `3 of 7 peers`, who is actually live, who merely belongs to historical memory, who can currently provide bytes, who is only a self-derived local branch, and what stronger sentence about real redundancy is still blocked?

That page-contract gap is exactly why AnonSync should not clone the behavior.

## Why this matters for AnonSync

AnonSync should borrow five habits directly:

- **say openly whether a count is live, historical, visible, source-capable, or authority-capable**
- **say openly when local self-derived branches inflate the cohort without adding independent remote resilience**
- **say openly when a row is merely hidden from view rather than severed from trust**
- **say openly when auto-expiry moved a peer out of the live set without deleting historical evidence**
- **say openly when disconnected visibility still preserves a future reconnection lane but not current byte availability**

But AnonSync should reject five weaker habits:

- one `X of Y peers` counter that silently mixes reachability and historical membership
- peer lists that let self-only local branches look like independent redundancy
- gray/offline/disconnected rows that do not publish whether they are still eligible to return automatically
- roster cleanup actions that sound like reality cleanup rather than view cleanup
- source-availability claims derived from total peer count instead of current source-capable witness

## Replacement pages added for this seam

This revision therefore adds six narrower replacement pages:

- `1253` — Cohort census contract sheet
- `1254` — Roster membership review
- `1255` — Live capability proof
- `1256` — Cohort drift timeline
- `1257` — Cohort census lineage receipt

These pages keep the Resilio candor and reject the scattered-cohort-semantics problem.

## Sharper non-clone line after this pass

The archive now has one tighter sentence for this seam:

> borrow Resilio's candor that online peers, ever-seen peers, disconnected gray rows, hidden offline devices, disconnected linked folders, and self-only local branches are different truths; refuse any interface contract where the operator must reconstruct live reachability, real source coverage, and historical roster residue from several counters and help articles instead of one explicit cohort-census object.
