# Resilio creditor representation, delegation, and release-authority fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- open burst debt and embargo future bursts while debt remained live
- stage repair through a creditor waterfall
- separate verified creditors from contested or stale-evidence residue
- reopen release when later evidence changed the creditor set

What it still lacked was the next hard operator answer when **the creditor set is known enough, but the speaker for that creditor is not**:

> who is actually allowed to accept settlement, waive residue, absorb unresolved harm, keep probation alive, or reopen a supposedly closed case on the creditor's behalf?

That is the seam this pass locks.
A product that can say `named harmed claimant verified` but cannot say `manager may accept repayment up to this cap but may not waive reopen rights`, or `device owner can route bytes but cannot extinguish creditor residue`, is still leaving decisive fairness truth in operator reconstruction.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose several real **identity, permission, and resharing authority fragments**, but not one operator-facing settlement-authority contract:

- `Sync Private Identity & Linking My Devices` still says every Sync installation gets a unique digital certificate, linked devices automatically receive all folders, approvals can happen from any linked device, and once one device is approved others linked to that identity may be approved automatically in future sharing.
- The same article still says linking two already-running devices can cause one to lose its certificate, take over the other device's identity, and replace its Advanced-folder roster with the other instance's folders.
- `User Management` still says only users with Owner permission can invite new users to an Advanced folder, that Owners can revoke peer access, and that when devices are linked under one identity all of those devices act as Owners.
- `Sync Share Dialog (Desktop)` still says Advanced folders can be shared only by peers with Owner access, while Standard folders have no Owner permission level and all peers can share the folder further.
- `What's the difference between Standard and Advanced folders?` still says Advanced folders use PKI and store certificates of previously dealt-with users, while Standard folders do not reflect user identity in the peer list and any peer can share the key further without limitation.
- `Sync functionality in detail` still says a folder can be shared and approvals granted from any linked device rather than the specific device that shared the folder initially.

## What current Resilio still gets right

### 1) It has real identity and permission machinery

PKI-backed identities, Owner / Read & Write / Read Only distinctions, peer approval memory, and revocation are all meaningful. That is worth borrowing.

### 2) It is honest about delegated operational control

A linked-device family can approve access from any linked device, and Owner status can be changed on the fly for Advanced folders. That is useful operator candor.

### 3) It distinguishes some governance surfaces across folder types

Advanced folders have Owner gating and certificate memory; Standard folders do not. That asymmetry is informative and valuable.

## Where current Resilio still fragments the operator answer

### A) Folder-owner authority is not the same as creditor-release authority

Resilio's Owner permission tells you who may share or revoke folder access.
It does not tell you who may settle debt, waive harmed-creditor residue, accept narrowed restoration, or sign away reopen rights.

### B) Linked-device blanket ownership overstates who is speaking

When linked devices all act as Owners and approvals can be granted from any linked device, the system is expressing operational continuity.
It is not proving that every such device or operator has equal authority to extinguish a creditor claim.

### C) Standard-folder resharing is especially weak as a settlement model

Standard folders have no Owner permission level and any peer can share the key further.
That is workable for propagation but too weak to stand in for a representation and release contract.

### D) Certificate takeover and relinking complicate long-lived authority stories

If linking already-running devices can cause one instance to lose its certificate and adopt another instance's identity and folder roster, then authority lineage can change materially.
Current docs still do not provide one typed page saying whether an earlier representative mandate survives, narrows, expires, or must be revalidated after identity takeover.

### E) Approval memory is not settlement memory

Storing certificates of previously dealt-with users and approving from any linked device helps future connection approval.
It still does not amount to a first-class contract for `who may accept partial relief`, `who may waive residue`, or `who may reopen after a premature closure`.

## Resulting product decision

AnonSync should borrow Resilio's PKI, owner/permission distinctions, and candid linked-device operational control.
It should **not** clone a product shape where the identity that can route, approve, or re-share content is casually treated as the same identity that can release a creditor claim.

AnonSync should instead expose:

- one first-class **Creditor authority contract sheet**
- one **Creditor representation review** page
- one **Settlement authority proof** page
- one **Creditor authority timeline**
- one durable **Creditor authority lineage receipt**

## Hard decisions locked by this pass

- **ability to observe, route, or report harm is weaker than authority to release or waive that harm**
- **device identity, folder owner, human principal, delegated representative, and residual absorber must remain distinct objects**
- **delegation scope must be typed: receive payment, negotiate, accept capped settlement, waive residue, lift probation, and reopen are separate powers**
- **expired, revoked, role-exited, or certificate-takeover-touched authority downgrades into explicit challenge or revalidation state; it may not silently remain valid**
- **acceptance of partial relief is weaker than full release unless the authority scope explicitly permits full closure**
- **a release signed by a stale or over-scoped representative can reopen the case and re-freeze restoration or future-burst posture**
