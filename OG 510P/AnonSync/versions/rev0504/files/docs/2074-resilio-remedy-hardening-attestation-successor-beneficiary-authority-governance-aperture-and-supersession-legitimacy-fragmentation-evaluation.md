# Resilio remedy-hardening attestation successor beneficiary authority, governance aperture, and supersession-legitimacy fragmentation evaluation

## Why this seam matters now

The archive can already say:

- the beneficiary is legitimate
- the successor action was legitimate
- the landed result conforms closely enough
- the beneficiary can use the result now
- the beneficiary can hold a durable self-sufficient copy
- the beneficiary may even remain attached to a future-update lane

That is still weaker than a sharper question:

**whose future updates, supersessions, withdrawals, or permission changes count as canonical for this beneficiary now, and what actor set is actually empowered to issue them?**

A beneficiary can remain attached to a live lane and still not have one explicit, bounded answer to **which authority set owns that lane**.
`still receiving updates` is weaker than `still receiving the right authority's updates under the reviewed governance boundary`.

## Why current Resilio still leaves this too diffuse to clone

Current official Resilio material is candid about authority ingredients, but it still spreads them across several pages:

- Advanced folders use PKI and digital certificates, can reflect user identity, allow on-the-fly permission changes, and only Owners can share them further
- Standard folders use keys instead, lack the Owner concept, allow anyone with the key to share further, and cannot change permissions on the fly without removing and re-adding with a new key
- linked devices under one identity automatically receive folders, all act as Owners, and any eligible linked device can approve future connections
- approval can be remembered because the system stores certificates of previously dealt-with users, and approval can be widened across linked devices
- Owners can revoke access to future updates, alter permissions, and delegate further sharing power
- file modification requests are validated cryptographically, but the ordinary operator still has to assemble `who exactly can legitimately issue the next binding change for this beneficiary?` from folder-type, owner, identity, approval, and sharing material rather than from one canonical governance object
- a beneficiary may remain on an update lane even while the authority aperture for that lane is wider, narrower, or differently attributed than the review assumed

This is good security and good candor.
It is not yet one first-class answer to **what authority set can legitimately supersede or withdraw the beneficiary-facing result now**.

## The non-clone line

AnonSync should not clone a contract where all of these are allowed to blur together:

- the beneficiary is still subscribed to updates
- the subscribed lane is governed by the reviewed canonical authority set
- any current Owner can supersede, withdraw, or re-share further
- linked devices silently widen the effective owner surface
- remembered approvals silently widen future admission scope
- Standard-folder key holders can continue onward sharing without one visible authority receipt
- future changes remain cryptographically valid yet still lack one explicit product object for reviewed governance aperture

Those are separate truths.

## Product decision frozen in this tranche

This revision freezes a stronger line:

- **beneficiary continuity enrollment is weaker than beneficiary-facing canonical-authority clarity**
- **receiving future updates is weaker than receiving future updates from the reviewed authority set under the reviewed governance aperture**
- **folder type, owner set, linked-device owner spread, approval memory, and re-share rights must degrade into first-class authority facts instead of dissolving into support folklore**
- **`the beneficiary stays current`, `the lane is live`, and `the change is signed` may never impersonate `the reviewed canonical sovereign set still exclusively governs this beneficiary result`**

## What AnonSync should model explicitly instead

AnonSync should add one first-class family for:

- source beneficiary-continuity receipt identifier
- named beneficiary and governed slice
- intended canonical authority set
- actual currently empowered authority set
- authority aperture class
- share / re-share / delegate / revoke / supersede rights matrix
- linked-device owner spread
- approval-memory or certificate-carry-forward scope
- standard-key onward-share risk or equivalent onward-legitimation risk
- strongest honest authority-legitimacy sentence
- blocked stronger authority-legitimacy sentence

## Interface consequence

That is why this tranche adds five more first-class pages:

- **successor beneficiary-authority contract sheet**
- **successor beneficiary-authority review**
- **successor beneficiary-authority proof**
- **successor beneficiary-authority timeline**
- **successor beneficiary-authority lineage receipt**
