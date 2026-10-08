# Resilio remedy hardening change governance, regression gate, and reseal fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials are still usefully candid about how much future change authority exists *after* a case already looks hardened and retained.
That candor matters.

The strongest present ingredients are:

- current `User Management` docs still say Advanced-folder permissions can be changed on the fly without disrupting sync, and that all linked devices under one identity act as Owners
- current `What's the difference between Standard and Advanced folders?` docs still say Standard folders have no Owner layer, any peer can share the key it has, and on-the-fly permission changes are not possible there because the share must be removed and re-added with a new key
- current `Sync Share Dialog (Desktop)` docs still say Standard-folder keys do not use the approval mechanism, all Standard peers can share onward, and approval can be required only for new peers or for all peers
- current `Comprehensive guide to syncing (Desktop-Desktop)` docs still say linked devices automatically receive every folder with full read-write access
- current `Running Sync in configuration mode` docs still say config mode applies configured settings at program start and can set up only Standard folders, not Advanced
- current `Folder Preferences` docs still say important behavior remains folder-by-folder and desktop-only
- current `Ignoring files in Sync (Ignore List)` docs still say same IgnoreList across peers is advisable rather than compulsory
- current `File download priority` docs still say a manually altered share stops following later global default changes, even if later set back to `None`

## Where the current contract still fragments

The problem is not that Resilio lacks knobs for later change.
The problem is that it still lacks a first-class, case-scoped **remedy-hardening-change-gate** object.

Today the operator can often infer only weaker truths such as:

- one owner still has authority to change permissions
- one linked device can still approve or share
- one Standard key can still be handed onward
- one folder preference still looks aligned
- one config deployment still exists at startup
- one manual override already detached a lane from later defaults

Those are useful operational clues.
They are not the same as an explicit answer to `can this proposed future change be admitted without reopening the cause family that the case was hardened against?`

## Why that matters for AnonSync

AnonSync needs to support stronger post-hardening claims than `the hardened state still exists right now`.
It needs to support claims such as:

- the case remains hardened-and-retained, but any permission, share, or topology mutation now requires regression review before it may go live
- one change is safe for ordinary throughput but unsafe for the original cause family, so it stays blocked despite broad operational authority
- one change may proceed only if the case is re-sealed afterward because its safety depends on new cohort proof rather than inherited trust
- one linked-device or Standard-folder sharing surface leaves broad operational convenience intact while still blocking the stronger sentence that future mutation is safely governed for this case
- one manual override or per-folder tweak may be harmless for sync, but not harmless for this specific recurrence class

AnonSync therefore needs a first-class object for **hardening change governance and reseal discipline** rather than merely borrowing owner, permission, config, link, or preference language.

## Non-clone conclusion

Borrow the ingredients.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `may this already-hardened case safely change now without reopening the cause family?` — only by making the operator combine several operational surfaces:

- live Advanced-folder permission edits
- Standard-folder onward sharing without an Owner layer
- optional approval rules at share time
- linked-device automatic full-RW spread
- startup-scoped Standard-only config deployment
- per-folder desktop-only preferences
- peer-local IgnoreLists that only "should" match
- sticky manual-override exceptions to later defaults

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model the following as separate public truths:

- recurrence hardening retained, but future changes ungated
- proposed change outside cause-safe envelope
- proposed change safe only after required-cohort review
- proposed change approved with mandatory reseal
- proposed change applied under temporary regression debt
- bypassed change reopened the cause family
- reseal completed after change
- hardening change gate intact
- recurrence-hardened-retained-and-change-gated discharge achieved

That is why this tranche adds five more first-class pages: **Remedy-hardening-change-gate contract sheet**, **Remedy-hardening-change-gate review**, **Remedy-hardening-change-gate proof**, **Remedy-hardening-change-gate timeline**, and **Remedy-hardening-change-gate lineage receipt**.
