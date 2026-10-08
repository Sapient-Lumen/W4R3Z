# Resilio rollback witness locality and archive-bearing asymmetry evaluation

## Why this pass exists

The archive already had strong doctrine for restore review, history browsing, chronology authority, encrypted recovery, and post-action claim ceilings.
What it still did not own tightly enough is a simpler operational question:

- where does the prior version actually live now
- which seat can honestly perform the recovery work
- which seat cannot because it never kept the earlier bytes
- which facts come from Archive and which still need History to explain authorship

Current official Resilio docs still make that seam very real.
They are candid that Archive is useful.
They are also candid that it is **not** a universal local rollback ledger.

## What current Resilio still gets right

Current official docs still publish several truths that are unusually operationally useful.

- **Prior-version custody is peer-local and asymmetric.** Current Archive docs still say older or deleted copies are moved to Archive on *other* peers connected to the share, not on the peer that made the change.
- **Manual restore is treated as real work.** Current Archive docs still say only manual restoring is possible.
- **Restore success still depends on runtime state.** Those same docs still warn that Sync should already be running when a file is taken out of Archive, otherwise the restored file may later be archived again as older during rescan.
- **Archive is operationally important even for rename continuity.** Current rename docs still say remote peers move the old name into Archive and then restore it under the new name when the matching hash appears, avoiding re-transfer; without Archive the bytes are re-synced again.
- **Retention and access are platform-shaped.** Current Archive docs still say defaults are 30 days on desktops and 1 day on mobiles, Android Archive on SD cards does not work, and Archive is not accessible on iOS.
- **Archive is not provenance-complete.** Current docs still say Archive does not tell you which peer changed a file and sends operators to History for that.

That is good candor.
Resilio is not pretending that a `restore` affordance means one omniscient rollback system.

## Where current Resilio still stays too article-shaped

### 1. Recovery bytes still live in the wrong place for ordinary intuition

Ordinary operators often assume one of these stronger stories:

- the device that changed the file kept the old version too
- the device where the problem is visible is naturally the best place to restore from
- every connected seat has equivalent rollback evidence
- `restore` means the product already knows the best witness host

Current docs still undercut those assumptions.
The older version usually lives on *other* peers.
That is useful truth, but it still means the operator may have to reason about witness locality before even starting recovery.

### 2. Recovery is still split between bytes, authorship, and runtime timing

Current official docs still make the operator assemble three different answers:

- Archive answers whether prior bytes still exist on some seat
- History answers who changed the file
- live daemon/watch state answers whether replay will stick or simply be archived again later

Those are three materially different objects.
Current Resilio still tends to publish them across different places rather than one stable recovery-locus page family.

### 3. Platform reach still changes what `recoverable` means

Current official docs still keep restore access different across desktop, WebUI, Android, and iOS.
The bytes might exist, but the recovery lane and ergonomics still differ by seat class.
That matters for the operator question `where should I perform this restore?`

### 4. Archive still silently carries two jobs at once

Current docs still make Archive both:

- a recovery store for previous versions and deletes
- a rename/move continuity mechanism used to avoid re-download

That is a useful implementation choice.
But it also means the operator may not know whether Archive is presently being relied on for continuity, recovery, or both.
AnonSync should not clone a product where one hidden directory carries both meanings without one product-owned witness map.

## What AnonSync should do instead

AnonSync should treat rollback and restore as a **witness-locality** problem before it treats them as a generic restore verb.
The product should own four page families:

1. **Witness locality map**
   - which seats hold prior bytes now
   - retention horizon, platform reach, and confidence
   - whether the current seat is the right recovery host

2. **Recovery host choice**
   - choose where recovery work will actually run
   - expose daemon/watch prerequisites and replay locus
   - separate export, local inspection, and live replay

3. **Archive / history bridge**
   - join Archive byte candidates with History authorship evidence
   - publish gaps instead of pretending Archive already knows who acted

4. **Recovery locus receipt**
   - record the witness seat, candidate source, replay scope, and proof limits

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that recovery witnesses are peer-local, manual, and runtime-sensitive. But it is not worth cloning the way current operators still have to infer *which seat actually holds the rollback witness, which seat should perform the restore, and which facts still come from History rather than Archive* by stitching together several help articles.

## New replacement pages added in this revision

- `537` Witness locality map
- `538` Recovery host choice
- `539` Archive / History bridge
- `540` Recovery locus receipt
