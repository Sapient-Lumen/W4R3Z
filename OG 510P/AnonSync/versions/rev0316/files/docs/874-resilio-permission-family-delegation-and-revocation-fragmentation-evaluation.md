# Resilio permission-family, delegation, and revocation fragmentation evaluation

## Why this pass exists

The archive already had strong work on artifact families, intake, approval, epoch rotation, residency promises, destructive healing, and maintenance semantics.
What it still lacked was one explicit evaluation of a narrower but highly consequential seam:

> when an operator asks `who can do what, can they delegate it onward, can I change that later, and what still remains after revocation?`, how many different present-day Resilio contracts do they have to remember?

Current official Resilio docs are still useful because they are candid about the real differences.
They still openly say that:

- **Advanced** folders have `Read Only`, `Read & Write`, and `Owner`, while only Owners can share onward, change permissions, and revoke access
- **Standard** folders do not have an Owner concept, any peer can share the key it has, and on-the-fly permission changes are not possible without removing and re-adding the share with a new key
- linked devices under one identity all act as **Owners**, so `my own seats` and `someone I granted access to` are not the same authority plane
- revoking a peer stops **future updates**, but files already synchronized remain in that peer's folder
- Read Only is not merely `can't upload`; changed files suspend further synchronization for that peer unless overwrite-heal policy is separately enabled
- a **local share** cannot be granted Owner, cannot exceed the permission of its source, may need re-sharing to change permissions, and can automatically lower if the remote Owner lowers the source seat
- source removal or disconnect can remove the derivative local share as a consequence of source continuity loss

That is good candor.
It is also strong evidence that AnonSync should not clone the exact contract.

## What current Resilio still gets right

### 1) Permission is not one flat yes/no bit

Resilio is right that `can view`, `can write`, `can delegate`, and `can administer later` are different powers.

### 2) Revocation is not magic deletion

Resilio is also right that revoking future updates is not the same as reaching back and erasing material that already arrived.
That retained-material truth matters.

### 3) Derived seats can have narrower authority than their source

Resilio is right that a local derivative share should not silently exceed its source authority.
A copied projection can be narrower than the upstream seat.

## Why AnonSync still should not clone it

### 1) The answer depends too much on artifact family folklore

Current Resilio still makes one ordinary operator question depend on remembering whether the subject is:

- Standard or Advanced
- one of my linked devices or another person's identity
- a directly shared seat or a derivative local share
- a live peer policy or a new key issuance problem

Those are real distinctions, but the product should own them in one policy grammar rather than forcing article archaeology.

### 2) Live policy and artifact replacement are still too entangled

In Advanced folders, some permission changes are live policy mutation.
In Standard folders, permission change means remove and re-add with a new key.
That is not a detail.
That is a first-class difference between `edit the rule` and `mint a successor artifact`.
A serious product should preview that difference before the operator clicks anything.

### 3) Revocation still sounds stronger than it is

`Disconnect` and revoke language in current docs can be read quickly as if access was simply removed.
But the same docs still say already synchronized files remain on the peer.
So the real answer is:

> future updates stop, retained bytes stay, and later cleanup or successor policy is a separate matter.

That deserves a dedicated revocation-impact object, not just a peer-row verb.

### 4) Linked-own-device semantics are still too easy to confuse with granted rights

Current docs still say linked devices under one identity act as Owners.
That may be useful, but it means `my second seat` and `external owner-like collaborator` are not interchangeable governance stories.
AnonSync should never hide that difference behind one generic `owner` row.

### 5) Local derivatives still inherit awkwardly rather than legibly

Current local-share docs still show a derivative that cannot exceed source permissions, can be auto-lowered by source changes, may require re-share to change access, and disappears when the source disappears.
Useful truth, but too much of it still lives in caveat prose.
A derivative seat should publish its narrowing and dependence explicitly.

## Hard decisions now locked for AnonSync

1. **Authority policy is a first-class object.** Operators should not have to infer policy from artifact family alone.
2. **Live mutation and reissue are different verbs.** The product must say whether a requested change edits an existing policy or requires successor issuance.
3. **Revocation always publishes retained-material truth.** `Stops future updates` and `already-held bytes remain` must stay adjacent.
4. **Own-seat linkage and granted external rights stay separate.** Internal seat-family expansion is not the same workflow as granting another principal.
5. **Derivative seats can only narrow, never silently widen.** Any downstream or local derivative must publish the source ceiling and its own stricter floor.
6. **Every policy action emits a receipt.** Later operators should not have to reconstruct whether a change was live, reissued, downgraded, or merely announced.

## Replacement page family justified by this pass

This pass therefore justifies five more product-owned surfaces:

- **Authority contract**
- **Permission change preview**
- **Delegation boundary review**
- **Revocation impact**
- **Authority policy receipt**

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still right that read, write, delegate, owner-like administration, revocation, linked-seat ownership, and derivative-local narrowing are genuinely different truths. But it still makes the operator reconstruct those truths from folder family, identity family, derivative-share caveats, and key-vs-policy semantics. AnonSync should keep the candor and refuse the fragmented permission contract.
