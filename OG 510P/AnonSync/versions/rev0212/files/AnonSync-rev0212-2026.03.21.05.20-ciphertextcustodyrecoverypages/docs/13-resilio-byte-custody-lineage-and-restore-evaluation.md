# Resilio byte-posture, encrypted-custody, same-host-lineage, and restore evaluation

## Bottom line

The further official Resilio pass strengthens the archive's position.
Resilio still deserves respect on four lines that matter in real deployments:

- byte-posture language that ordinary operators actually understand
- encrypted custody on an untrusted intermediary
- same-host local copies as a deliberate workflow
- archive/versioning as a practical recovery aid

But the same docs also show why AnonSync still should not clone the interface contract.
The pain is not that these features are bad.
The pain is that several of the most safety-relevant answers are still spread across mode selectors, hidden directories, key/database caveats, or support-style warnings rather than one ordinary page.

## What current Resilio docs still get very right

### 1) Byte posture is a first-class operator idea

`Disconnected`, `Selective Sync`, and `Synced` remain unusually strong product language.
They compress real differences in local visibility and materialization without drowning the operator in architecture.
That is worth borrowing.

### 2) Ciphertext-only custody is real work, not edge theater

The encrypted-folder docs still describe a real and useful pattern:
keep one peer on an untrusted VPS/NAS/public machine, store ciphertext only there, and let it seed continuously without exposing plaintext.
That is not a toy use case.
It is one of the clearest reasons Resilio still matters.

### 3) Same-host derivation is normal

The local-share docs still acknowledge something many products either hide or forbid:
operators really do want one same-machine downstream copy, cache, mirror, or alternate working root.
That is worth copying as a first-class concept.

### 4) Archive/versioning is operationally useful

The Archive docs still show a real product virtue.
A sync product should help with accidental deletes, rename/move churn, and prior-version recovery.
That is also worth copying.

## Why this still is not a clone vote

### 1) Mode still carries too many truths at once

The current linked-device docs still tie mode to more than current byte posture.
They also influence when a path is chosen, whether the default folder is used, whether the operator gets a custom-location prompt, and how later arrivals behave.
That means one helpful selector still speaks for too many facts:

- current share visibility
- current local bind
- current byte materialization
- future default for later arrivals
- sometimes path-collision behavior

AnonSync should borrow the posture language while refusing that fused selector contract.

### 2) Encrypted custody still hides recovery truth inside caveats

The encrypted-folder docs are candid, but the practical recovery story still depends on remembering that:

- the encrypted node is read-only and cannot decrypt locally in ordinary use
- `Overwrite any changed files` is always on
- restoring from the encrypted node depends on saved RW/RO keys and the original database continuity
- local CLI decryption is possible, but only through a support-style command path
- restoring from encrypted Archive does **not** restore the file back into the live share from that node

That is exactly the kind of family AnonSync should remodel as one ordinary encrypted-custody page.

### 3) Same-host continuity still lives in a caveat cluster

The local-share docs still package a lot of meaning as exceptions the operator must remember:

- only `self` is the peer
- child only talks to the parent, not remote peers directly
- no ancestor/descendant loops
- no local Owner grant
- permission changes may require remove/re-share
- child disappears when the source is removed
- source reconnect does not auto-reattach the child
- source placeholders can limit child availability

That is a strong non-clone reason.
The workflow is good; the page contract is still too exception-shaped.

### 4) Restore and fetchability truth are still split across several places

The Archive docs still make recovery possible, but they also show a scattered model.
The operator may have to reason across:

- UI-only versus hidden `.sync/Archive` access paths
- desktop/UI versus WebUI versus mobile availability differences
- manual restore only
- timestamp behavior where a restore can be re-archived if Sync is not running
- Archive history lacking peer-authorship, which then lives in History instead

That is useful capability, but not one stable recovery page.
AnonSync should keep the capability while making `who still has bytes`, `what can be restored`, and `what happens if I evict now` one ordinary answer.

## The sharper AnonSync line

The second-wave Resilio answer is now:

> borrow the operator ideas, not the page boundaries.

More concretely:

- borrow **byte posture names**
- borrow **ciphertext-only custody**
- borrow **same-host derivation**
- borrow **archive/versioning usefulness**
- refuse any contract where those ideas still depend on fused mode labels, hidden recovery preconditions, or family-specific caveat memory

## Replacement-page obligations created by this pass

If AnonSync is serious about not cloning, it now owes four more ordinary pages.

### 1) Byte posture

One page should answer, for one share on one seat:

- what is visible here now
- what is bound here now
- what bytes are here now
- what later arrivals would do by default

That is the role of `273`.

### 2) Encrypted custody

One page should answer, for one ciphertext-only seat:

- what this node can do
- what it can never do
- what keys/database continuity are required for recovery
- what stronger state the operator could upgrade toward

That is the role of `274`.

### 3) Same-host lineage

One page should answer, for one local derivation family:

- who the parent is
- what rights and bytes can flow down
- whether the topology is safe
- whether the child is healthy, detached, or reattachable

That is the role of `275`.

### 4) Fetchability

One page should answer, for one visible path or subtree:

- who still definitely has the bytes
- whether Archive is part of the honest recovery path
- whether the requested eviction would remove the last easy recovery route
- what later receipt will prove the operator made that choice knowingly

That is the role of `276`.

## Result

This pass makes the archive's Resilio stance tighter, not looser.
The product ideas are strong enough that weak caricature would be dishonest.
The page contracts are still weak enough that cloning them would also be dishonest.

That is exactly the kind of tension a good planning archive should be able to name.
