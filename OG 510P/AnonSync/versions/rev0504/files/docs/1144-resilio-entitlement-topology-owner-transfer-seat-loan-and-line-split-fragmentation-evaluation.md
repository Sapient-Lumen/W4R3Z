# Resilio entitlement-topology, owner-transfer, seat-loan, and line-split evaluation

## Why this pass exists

The archive already had strong work on capability gating, entitlement basis, linked identity, and upgrade gating.
What it still lacked was one explicit evaluation of a narrower but highly consequential seam:

> when an operator asks `who actually owns this entitlement graph, who is merely borrowing a seat, what explodes if ownership moves, and can this cohort even cross the v2/v3 line safely?`, how many current Resilio articles do they still have to mentally join?

Current official Resilio docs are still useful because they are candid about real distinctions.
They still openly say that:

- a **Business** license in v2 has exactly one **License Owner** identity
- all devices linked under one identity consume **one seat**, not one seat per device
- a seat can be **shared** to another identity, but that seat borrower cannot manage other seats
- directly applying the Business key to another identity can **steal ownership** from the prior owner
- removing the Business license from the owner does **not** remove it from License Users
- if the Business owner's license or trial expires, the **shared seats expire with it**
- v2 and v3 remain sync-compatible at byte level, yet **linked** mixed-version identities can suffer **license conflicts** and even lose access to UI and share configuration
- Sync Business cannot be updated to **v3**, and attempting it can lose configured shares while keeping files on disk
- v3 licensing redefines the personal / family / non-commercial story, so line family is not a cosmetic release label

That is good candor.
It is also a strong reason not to clone the exact contract.

## What current Resilio still gets right

### 1) Entitlement topology is real topology

Resilio is right that `licensed`, `borrowing one seat`, `linked under the owner`, and `compatible with the current product line` are not equivalent truths.
They have different failure modes and different blast radii.

### 2) Ownership transfer is not just another apply-key action

Resilio is right that directly applying a Business key to another identity is governance-changing.
That is not a mere activation convenience.
It changes who the owner is.

### 3) Line family is continuity-bearing

Resilio is also right that v2 and v3 are not one flat upgrade lane.
The byte protocol may remain compatible while the entitlement and linked-identity contract changes enough to create conflicts.

## Why AnonSync still should not clone it

### 1) The operator still has to reconstruct one ordinary answer from several article families

Current Resilio still makes the ordinary answer depend on combining:

- business license seat-management docs
- generic apply-license docs
- identity-link docs
- v3 FAQ and upgrade-block docs
- host / install guidance where Business is blocked on v3

That means one ordinary operator question still lacks one stable page answer:

> what exact entitlement topology do I have, who owns it, who is borrowing it, what can revoke it, and which line-upgrade paths are actually safe?

### 2) Owner transfer still hides inside `apply key`

Current Resilio is candid in prose that a direct key application elsewhere can steal Business license ownership.
But that truth still feels more like support lore than a first-class reviewed mutation.
A serious product should surface owner-transfer blast radius before the mutation, not after.

### 3) Borrowed-seat instability is still too implicit

Current Resilio separately says shared seats depend on owner approval and owner expiry, and that removing the owner license does not automatically strip existing license users.
Useful truth, but too much of it still requires cross-reading.
A borrowed seat should publish its dependency graph plainly.

### 4) Line-split migration still sounds safer than it is

Current Resilio separately says Business cannot go to v3, linked mixed-version identities should all move together to avoid license conflicts, and wrong-line upgrades can lose share configuration.
That is not generic upgrade caution.
That is cohort-topology truth.
A product should own that in one migration family.

## Hard decisions now locked for AnonSync

1. **Entitlement topology is a first-class object.** `licensed` is not enough.
2. **Owner transfer is a reviewed governance mutation.** A direct key apply that can rehome ownership must preview borrower fallout and cohort blast radius.
3. **Borrowed seats publish their dependency graph.** `working now` is weaker than `independent`.
4. **Line family is topology-bearing.** Byte compatibility does not erase entitlement or linked-cohort migration risk.
5. **Business / personal / family / non-commercial lanes must stay explicit.** The product may not let one badge flatten these usage claims.
6. **Every serious entitlement mutation emits a receipt.** Later operators should not need licensing folklore to reconstruct what changed.

## Replacement page family justified by this pass

This pass therefore justifies five more product-owned surfaces:

- **Entitlement topology contract sheet**
- **License owner transfer review**
- **Seat loan and reclaim review**
- **Line-split migration watch**
- **Entitlement topology lineage receipt**

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still right that license owner, linked-seat collapse, borrowed seats, owner-expiry cascade, and v2/v3 line compatibility are genuinely different truths. But it still makes the operator reconstruct those truths from licensing, identity, and upgrade articles. AnonSync should keep the candor and refuse the fragmented entitlement-topology contract.