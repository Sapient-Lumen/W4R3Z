# Resilio remedy cutover, authoritative switch, and conflict-rebound fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials are candid that a landed file is not automatically a safely switched live state.
That candor is useful.

The strongest ingredients from the present contract are:

- current Sync docs still say a locked file means another application has blocked access, making it impossible for Sync to transfer data, and Sync still cannot tell which application owns the lock
- current conflict-file docs still say multiple versions can attempt to copy to a single file or folder, producing `.Conflict` variants under case, encoding, linked-junction, or filesystem constraints
- current Active Everywhere multiuser guidance still says agents technically cannot prevent two users from editing the same file on different workstations at the same time and will synchronize the file with the latest timestamp, overwriting others
- current `What if several users edit the file at the same time?` guidance still says agents may choose by latest database timestamp while offline return falls back to comparing mtimes, and that an open local copy can stall accept-or-decline decisions until the file becomes available
- current file-locking docs still say locking support is limited to Windows x64, other operating systems can participate without imposing locks, and only one of two agents on the same device can talk to the file-lock driver
- current file-locking best-practices docs still say locking semantics depend heavily on native application behavior and sometimes require excluding file types from locking to preserve workable collaboration
- current access-permissions docs still say a file changed on a Read-Only agent becomes invalidated and can later be overwritten or re-downloaded from a Read-Write source rather than participating as a symmetric cutover vote

## Where the current contract still fragments

The problem is not that Resilio hides cutover risk.
The problem is that it still lacks a first-class, case-scoped **remedy-cutover** object.

Today the operator can often infer only weaker facts such as:

- the repaired file landed in the intended place
- one visible copy is now newer than another visible copy
- a conflict file appeared, implying somebody disagreed with the switch
- a lock exists, implying somebody still has the object open
- read-only clients will eventually revert toward the read-write source
- some Windows nodes may have locking while other platform participants do not

Those are useful operational clues.
They are not a cutover contract.

## Why that matters for AnonSync

AnonSync needs to support stronger claims than `the cure landed`.
It needs to support claims such as:

- the cure became the authoritative live state and legacy writers were fenced before rebound risk could overwrite it
- named pilot writers switched, but all-required-writer cutover stays blocked because one cohort still edits an unlocked live copy
- the repaired object landed, but the stronger sentence `authoritative cutover complete` stays blocked because latest-timestamp overwrite rules can still rebound the old state
- conflict artifacts exist, so the honest sentence is `split live state` rather than `successful cutover`
- read-only or placeholder-bearing cohorts may display the repaired object without yet being cut over as safe live participants

AnonSync therefore needs a first-class object for **remedy cutover** rather than merely borrowing locks, conflict files, permissions, or timestamp rules.

## Non-clone conclusion

Borrow the ingredients.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `did the landed repair actually become the authoritative live state for the required writer and reader cohorts without immediate overwrite or split-state rebound?` — only by making the operator combine several operational surfaces:

- locked-file warnings
- conflict-file rules
- timestamp and database-time tie-breaking
- file-locking availability and limitations
- app-dependent locking semantics
- read-only invalidation and overwrite rules

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model the following as separate public truths:

- cutover requested
- landed pending writer freeze
- split live state detected
- authoritative pilot cutover
- authoritative required-cohort cutover
- cutover blocked by live lock holder
- cutover blocked by unlocked writer risk
- cutover blocked by timestamp-rebound risk
- cutover collapsed by conflict rebound
- cutover verification collapsed

That is why this tranche adds five more first-class pages: **Remedy-cutover contract sheet**, **Remedy-cutover review**, **Remedy-cutover proof**, **Remedy-cutover timeline**, and **Remedy-cutover lineage receipt**.
