# Resilio effective seat posture, writeback, auto-heal, serve-right, and derivation fragmentation evaluation

## Why this pass exists

The archive already had doctrine for permission planes, revocation, non-authority edits, encrypted custody, and local derivation.
What the current revision chain still lacked was one tighter current Resilio pass about another ordinary operator question:

> what *is* this peer actually allowed to do right now — write back, onward-share, auto-heal my local edits, keep unsynced local additions, or merely serve unchanged bytes — and is that posture directly granted, inherited from some other seat, or hard-wired by the share family itself?

Current official Resilio docs are useful here precisely because they remain candid.
Today those docs still show that:

- `User Management` still says different permissions can be issued to different identities, all linked devices under one identity act as Owners, Read Only changes do not propagate, changed files on a RO peer suspend further synchronization for that peer, Read & Write propagates mutations, and Owner additionally grants onward sharing and revocation rights;
- `Is one-way synchronization possible?` still says Read Only peers can trigger per-file suspension when they edit, rename, delete, or modify files, while the optional `Overwrite any changed files` behavior re-downloads the old name after a rename, restores deletions, reverts content edits to the RW version, but leaves added files local and unsynced; the same article still says RO peers may nevertheless transfer unmodified files to new peers because of normal P2P serving behavior;
- `Folder Preferences` still says `Overwrite any changed files` is potentially destructive and is disabled for Read-only folders with Selective Sync ON;
- `Sharing a folder locally` still says local shares can only inherit the permission floor of the source, can never receive Owner, cannot have access level changed through user management for Advanced shares, automatically downshift if the source seat is narrowed by a remote Owner, and sync only with the parent source share rather than directly with remote peers;
- `Encrypted folders` still says the encrypted F-key node is Read Only, has `Overwrite any changed files` always enabled, does not support Selective Sync, follows delete state from the source, and cannot restore deleted files back from its Archive because it is both RO and delete-following;
- `How to create a Read Only folder while syncing across linked devices?` still says linked devices default to Owner posture, so obtaining a RO posture inside one linked family requires breaking out into a separate Standard-folder-plus-RO-key path rather than just flipping one linked seat.

That is strong operator candor.
It is also another strong reason not to clone the contract as-is.

## What current Resilio still gets right

### 1) It admits that permission label and effective behavior are not the same truth

The current docs still make clear that `Read Only`, `Read & Write`, and `Owner` are not only labels about who may edit.
They also shape onward sharing, revocation, suspension, and repair behavior.
That distinction is worth preserving.

### 2) It admits that unauthorized local mutation has different fates

The current one-way and folder-preferences docs still show that RO rename, delete, edit, and add are not handled the same way.
Some actions suspend the file, some can be auto-healed, and added files can remain local-only.
That is unusually candid and worth keeping.

### 3) It admits that a RO seat can still serve bytes

The current one-way docs still say RO peers can transfer unmodified files to other peers in ordinary swarm behavior.
That matters because `cannot write back` is not the same as `cannot contribute bytes`.

### 4) It admits that some postures are inherited or hard-wired rather than directly chosen

The current linked-device, local-share, and encrypted-folder docs still show that some seats are not simple direct grants:
linked devices collapse into Owner by default, local shares inherit and can downshift, and encrypted nodes are hard-wired into RO + auto-heal posture.
That is another distinction worth preserving.

## Why AnonSync still should not clone it

### 1) Seat posture truth is still too scattered

The ordinary operator still has to reconstruct whether a peer can:

- mutate bytes and publish them,
- share onward,
- revoke others,
- keep local divergences unsynced,
- auto-heal those divergences,
- or merely serve already-approved bytes.

AnonSync should not let one vague `Read Only` or `Owner` badge hide those distinctions.

### 2) Local divergence fate still sits too far from grant review

Current docs do tell the truth that rename, delete, content edit, and local add have different fates on a narrow seat.
But the operator still has to learn that from a FAQ plus preferences article instead of one owned product review.
AnonSync should publish local-divergence fate directly on the seat page.

### 3) Derived posture and direct posture still blur together

Current docs still show linked-device defaults, local-share inheritance, and encrypted hard-wiring as special cases.
But an ordinary operator still has to remember which ones are directly editable, which ones downshift automatically, and which ones require remove-and-reshare.
AnonSync should make derived posture first-class.

### 4) Byte-serving truth is still too easy to overclaim

Current docs still say a RO peer may serve unmodified files to a newly connected peer.
That means `cannot publish new mutations` is weaker than `cannot help anyone else`.
AnonSync should publish serve-right explicitly rather than letting operators infer it from writeback authority.

## Hard decisions now locked for AnonSync

1. **Grant label is a first-class but insufficient field; effective seat posture is the real contract object.**
2. **Writeback authority, onward-share authority, byte-serve eligibility, and local-divergence fate are separate truths.**
3. **A narrowed seat's local changes must classify by fate: suspended, auto-healable, local-only residue, or ordinary allowed mutation.**
4. **Derived posture is first-class state: direct grant, linked-family default, local-share inheritance, encrypted hard-wire, or unresolved derivation.**
5. **`Read Only` is weaker than `cannot publish mutations`, and `cannot publish mutations` is weaker than `cannot contribute bytes`.**

## Replacement page family justified by this pass

This pass therefore justifies five more product-owned surfaces:

- **Effective-seat-posture contract sheet**
- **Narrow-seat mutation review**
- **Delegation-and-serve proof**
- **Derived-seat review**
- **Effective-seat-posture lineage receipt**

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still right that grant label, local divergence fate, auto-heal posture, serve-right, onward-share authority, and derived-seat inheritance are materially different truths. But it still makes one ordinary operator answer — `what can this peer really do, what happens to unauthorized local edits, and is this posture directly granted or inherited?` — depend on several articles instead of one stable product-owned family. AnonSync should keep the candor and refuse the fragmentation.
