# Resilio name provenance, recipient-label issuance, and alias-residue fragmentation evaluation

## Why this pass exists

The archive already had broad name-plane doctrine in `182` and one ordinary current-state page in `280`.
What it still lacked was a narrower, more operational pass about three present-day Resilio truths that are easy to underestimate until they collide:

> when an operator asks `what is this thing called right now, to whom, and what exactly changes if I rename it or share it again?`, how many separate name answers does current Resilio still make them remember?

Current official Resilio docs are still useful because they are unusually candid about the problem.
They still openly say that:

- Sync UI names normally mirror the folder name on disk.
- a desktop share can also get a custom UI name that does **not** rename the disk folder.
- that custom UI name does **not** propagate to other peers or linked devices.
- a different label can be inserted into a generated link or QR code during sharing even though the underlying share name remains unchanged.
- if the operator changes that share-view label for QR code issuance, they may need to regenerate the QR so the new label is really encoded.
- when such a share is disconnected, the custom name can remain in the UI until the operator explicitly presses `Reset`.
- renaming the syncing folder in the filesystem affects only the local device; peers do not adopt the new name.

That is strong candor.
It is also a strong reason not to clone the exact contract.

## What current Resilio still gets right

### 1) One visible name is not enough

Resilio is right that a sync subject can honestly have several simultaneous names:

- a disk name on one device
- a local UI alias
- a label emitted in an outward invite artifact
- possibly a different seat/identity/device label elsewhere

Pretending one flat `name` field could always carry all of that would be dishonest.

### 2) Audience matters

Resilio is also right that some labels are local-only while others are recipient-facing.
The product does not become clearer by hiding that audience split.

### 3) Rename and relabel are materially different actions

Resilio's current docs still show that renaming a path on disk, changing a local UI alias, and generating a differently labeled outward artifact are not the same mutation.
That distinction is useful and AnonSync should keep it.

## Why AnonSync still should not clone it

### 1) One ordinary naming answer still leaks across too many planes

Current Resilio still makes the answer depend on remembering whether the visible label came from:

- local filesystem basename
- desktop-only custom UI alias
- a link-generation or QR-generation label
- local disconnect residue that survived until `Reset`

Those are real distinctions, but the product should own them in one ordinary naming provenance grammar rather than in separate tips, tricks, and FAQs.

### 2) Issuance-time labels are still too folklore-shaped

The `fancy trick` described in current docs is revealing.
An operator can generate one link labeled for `Server1` and another for `Server2` while the underlying share name remains unchanged.
That means outward naming is an issuance-time artifact property, not a mutation of canonical subject identity.
AnonSync should make that explicit instead of leaving it as clever operator lore.

### 3) Disconnect residue is still too easy to misread as live truth

Current docs still say the custom name remains in the UI after disconnect until the operator explicitly resets it.
That means a stale alias can survive even after continuity changed.
AnonSync should refuse any surface where a residue label can impersonate an active subject truth.

### 4) Rename preview is still under-owned

Current docs still split local disk rename, local UI alias, and outward link label behavior across separate places.
Operators deserve one preview that says exactly which audience changes now, which does not, and whether older artifacts stay stale.

### 5) Naming changes still need receipts

Once the same subject can have several labels for several audiences, later operators need a receipt that says which planes changed and which did not.
Anything less devolves back into screenshot archaeology.

## Hard decisions now locked for AnonSync

1. **Every visible serious name carries plane and audience provenance.** A naked label is not enough.
2. **Issuance-time recipient labels are first-class artifacts.** They are never treated as silent canonical subject renames.
3. **Disconnect leaves residue, not truth.** A surviving local alias after continuity break must badge itself as residue or stale local memory.
4. **Name mutation previews are explicit.** Subject retitle, local alias edit, disk rename, and recipient-label issuance are different verbs.
5. **Naming receipts preserve untouched planes.** Later operators must know not only what changed, but what definitely did not.
6. **Reset is local cleanup unless proved otherwise.** Resetting a stale alias does not retroactively mutate canonical subject history.

## Replacement page family justified by this pass

This pass therefore justifies five more product-owned surfaces:

- **Naming provenance sheet**
- **Name mutation preview**
- **Recipient-label issuance**
- **Alias drift watch**
- **Name lineage receipt**

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still right that one sync subject can legitimately wear several names for several audiences. But it still makes the operator reconstruct current naming truth from disk basename, local alias, share-view label insertion, and disconnect residue. AnonSync should keep the candor and refuse the fragmented naming contract.
