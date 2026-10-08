# Resilio overlapping-subject topology, nested-share shadow-seeding, and selective-sync ceiling fragmentation evaluation

## Why this pass exists

The archive already had strong work on same-host multi-instance ownership, same-path collision, path liveness, directory admission, and subject architecture.
What the current revision chain still lacked was one tighter current Resilio pass about a different ordinary question:

> when a parent and one of its descendants are both admitted as sync subjects, what topology have I created, who can seed whom, what extra cost is now real, and where does admission stop being legal at all?

Current official Resilio docs are useful here precisely because they are candid.
Today those docs still show that:

- `Is it possible to share a nested folder separately?` still says nested sharing is possible only with limitations.
- that same current nested-folder article still says **both parent and child** must have `Read & Write` or `Owner` permissions.
- the same article still says the parent and child are treated as **separate sync folders**, so additional indexing is done.
- the same article still says peers that have only the parent do **not** seed data to peers that have only the child.
- the same article still says **both** parent and child must have `Selective Sync` disabled.
- that same article still says the overlap has side effects: the child subtree is indexed and rescanned twice, and child-share changes can still reach parent-share peers through the shared ancestor path.
- `Selected folder is already added to Sync` still says a device can have only one folder with the same `.sync/ID`, and that same path or same key↔different-path collisions are blocked differently.
- `Cannot add folder. It contains a folder that is already syncing.` still says the user's home folder can be blocked because it already contains Sync's storage-folder license directory.
- `Can I connect two pre-populated pre-existing folders?` still says connecting existing material requires a manual reconnect lane and explicit confirmation for a non-empty destination.
- the Resilio change log still preserves the point that a **nested folder cannot be added in Selective Sync mode**.

That is a strong operator-truth corpus.
It is also a good reason not to clone the exact product contract.

## What current Resilio still gets right

### 1) It admits that overlap creates a different topology

Resilio still openly documents that a nested child is not just `a subfolder you also happened to share`.
Once parent and child are both admitted, there are now:

- two subject claims
- two indexing / rescan surfaces
- a seed-gap between parent-only and child-only peers
- a shadow propagation lane through the shared ancestor path

That honesty is worth borrowing.

### 2) It admits that admission legality and materialization mode are different truths

The current docs are refreshingly candid that nested overlap requires `Selective Sync` to be disabled for both parent and child.
That is more honest than pretending selective materialization is merely a storage preference with no topology consequences.

### 3) It admits that overlap conflicts can come from service interior, not just user content

The current `Cannot add folder. It contains a folder that is already syncing.` page still says the home-folder collision can be triggered because the home folder already contains Sync's own storage-folder license material.
That is a real admission-authority truth, not merely a user mistake.

## Why AnonSync still should not clone it

### 1) One ordinary answer still spans too many articles

To answer `can I safely admit this parent and child overlap here?` the operator may still need to combine:

- nested-folder FAQ guidance
- selective-sync docs
- same-ID collision errors
- home-folder overlap warnings
- pre-populated reconnect workflow
- sometimes change-log archaeology

That is too much archaeology for one ordinary answer.

### 2) overlap truth is still split between admission, topology, and residue

Current Resilio docs keep these as separate surfaces:

- is the overlap allowed at all
- who is allowed to author both sides
- whether selective materialization disqualifies the topology
- who can seed whom
- how changes can still shadow-propagate outward
- what extra indexing / rescan debt is accepted

The product truth is one compiled overlap-topology contract.
AnonSync should not inherit the split.

### 3) `both peers can see the same bytes` is still weaker than `this overlap is safe and fully understood`

Resilio's current docs still leave room for a weaker reality:

- the parent-only peer can see the child's bytes through the parent subtree
- but that same parent-only peer does not seed to a child-only peer
- and the origin peer pays extra indexing cost because the child is claimed twice

AnonSync should surface that difference before commit, not after confusing propagation or performance surprises.

## Hard decisions now locked for AnonSync

1. **Overlapping parent/child subjects are a first-class topology object, not an incidental convenience.**
2. **Subject visibility, seed authority, and shadow propagation are separate truths.**
3. **Selective materialization is weaker than overlap eligibility; if the overlap requires full subjects, the product must say so.**
4. **Interior service or license material can invalidate a larger-root claim even when the user did not create the inner subject intentionally.**
5. **Every overlap-affecting action needs one receipt that preserves claim class, seed-gap truth, dual-index cost, and the blocked stronger sentence.**

## Replacement page family

This pass therefore adds five more ordinary product-owned pages:

- **Overlapping-subject contract sheet**
- **Nested-share topology review**
- **Overlap admission review**
- **Overlapping-subject proof page**
- **Overlapping-subject lineage receipt**

## Bottom line

Resilio's current docs deserve credit for admitting that nested parent/child sharing, selective-sync exclusion, same-ID collisions, home-folder interior conflicts, and explicit reconnect of pre-populated targets are materially different.
But AnonSync should still refuse a contract where the operator must stitch together several articles to answer:

> what exact topology am I creating by admitting this overlap, who can seed whom, what extra cost and shadow propagation am I accepting, and where is this overlap blocked entirely?
