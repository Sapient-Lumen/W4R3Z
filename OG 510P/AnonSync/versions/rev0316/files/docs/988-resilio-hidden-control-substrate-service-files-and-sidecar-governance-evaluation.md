# Resilio hidden control substrate, service files, and sidecar governance evaluation

## Why this seam matters

Another current official Resilio pass makes the no-clone line sharper around **where control state lives**.
The useful distinction is real: a sync subject is not just bytes.
It also has service-critical state, policy sidecars, temporary transfer residue, and metadata propagation machinery.
The current Resilio contract is still too fragmented because the ordinary operator has to reconstruct that from several FAQ and troubleshooting pages rather than from one owned interface family.

## What current official docs still say

Current official Resilio materials still openly say all of the following:

- every folder added to Sync gets a hidden **`.sync`** system folder and successful syncing depends on it
- deleting or corrupting `.sync`, especially the **ID** file inside it, suspends synchronization for that folder
- `.sync` must not be moved separately from the whole shared folder or relocated into another place inside the tree
- the same namespace also contains user-editable governance sidecars such as **IgnoreList** and **StreamsList**
- IgnoreList rules affect indexing, size accounting, and future publication behavior, but they do not retroactively unsync already-synced structure
- StreamsList is a whitelist for xattrs / alternate streams / resource forks, and when a peer cannot store an xattr directly, Sync may create a stub file in **`.sync/Streams`** so the metadata can still propagate onward
- files ending in **`.!sync`** are in-progress transfer artifacts that later rename into place
- if the same folder is added to two local Sync instances, the internal files of the former instance can be corrupted and synchronization can become impossible until the share is removed and re-added

Those are useful distinctions.
They are also a strong reason not to clone the present contract.

## Why this still fails the clone test

To answer one ordinary operator question — **`what inside this folder is user content, what is service capsule, what is editable policy, and what can break if touched or double-owned?`** — current Resilio still makes the operator combine:

- the `.sync` FAQ
- the `Service files missing` troubleshooting page
- IgnoreList timing/behavior notes
- Streams / xattr propagation notes

That is too much archaeology for a core boundary.
A hidden folder inside user content may still be a valid implementation detail.
It may not remain a hidden **contract**.

## Hard decisions now locked in for AnonSync

AnonSync should keep the real distinctions and refuse the fragmentation.
This tranche locks in five harder decisions:

1. **control substrate is first-class**
   The system must model service-critical capsule, editable sidecars, metadata stubs, and temporary transfer residue explicitly rather than flattening them into `hidden files`.

2. **hidden is not harmless**
   Anything whose corruption can suspend sync, fork lineage, or break repair may not rely on filesystem hiddenness as its only warning channel.

3. **service capsule and policy sidecars are different classes**
   ID / lineage-critical state, editable ignore rules, editable metadata-whitelists, and transient transfer artifacts must not all share one undifferentiated hidden namespace story.

4. **dual ownership is a blocked condition, not a support footnote**
   If two runtimes or seats attempt to own the same control capsule, the system must surface that as a first-class collision before corruption or silent takeover.

5. **receipts must preserve control-substrate truth**
   When a subject is created, repaired, rehomed, exported, or handed off, the product must preserve which control capsule, sidecar policy, and temporary residue classes existed and what stronger sentence it refused to claim.

## Resulting interface family

That is why this tranche adds:

- a **Control substrate contract sheet**
- a **System capsule integrity review**
- a **Twin-runtime collision warning**
- a **Sidecar governance visibility** page
- a **Control substrate lineage receipt**

The point is not to fetishize internals.
The point is to stop the ordinary operator from having to learn support-lore just to understand whether this folder is only content, or also a fragile mixed control namespace.
