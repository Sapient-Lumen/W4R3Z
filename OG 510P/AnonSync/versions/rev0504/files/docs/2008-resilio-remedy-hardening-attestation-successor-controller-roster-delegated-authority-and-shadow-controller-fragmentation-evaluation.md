# Resilio remedy hardening attestation successor controller roster, delegated authority, and shadow-controller fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials still deserve credit for acknowledging several ingredients of authority inside the surviving world, even if they do not yet elevate them into one typed controller-roster verdict.
That is useful.

The strongest present ingredients are:

- current `User Management` docs still say only users with Owner permission can invite new users to a folder and revoke access rights from other peers, and that when you share across your own devices linked to one identity all of your devices act as Owners
- current `Sync Private Identity & Linking My Devices` docs still say all folders automatically become available on all linked devices, approvals for new peers can be issued from any linked device where the folder is present, and a remote user may choose to auto-approve all your linked devices for future sharing
- current `Sync functionality in detail` docs still say folder list is common across linked devices and that you can approve connections from any of your linked devices instead of only the original sharer
- current `Comprehensive guide to syncing (Desktop-Desktop)` docs still say linked-device mode gives every folder automatic full read-write access while manual sharing is the lane where explicit per-folder privileges are chosen
- current `How to create a Read Only folder while syncing across linked devices?` docs still say linked-device sync gives Owner permission by default and that achieving read-only on a linked device requires a Standard-folder manual-key detour
- current `Sharing a folder locally` docs still say local shares cannot receive Owner permission, inherit only the source permission level, cannot have their access level changed through user management, and must be removed and re-shared for some permission changes
- current `Folder Types and Management` docs still say Owner, Read & Write, Read Only, selective, full, pending, and disconnected states are materially distinct folder behaviors rather than one flat control state

## Where the current contract still fragments

The problem is not that Resilio hides the ingredients.
The problem is that it still does not produce one first-class, case-scoped **successor controller roster and delegated-authority discipline** object.

Today an operator can often infer only weaker truths such as:

- the predecessor world is retired for the named slice, so the successor world is now the only legitimate world-level controller
- all linked devices under one identity can act as Owners, but the actual live controller roster is implicit rather than enumerated
- a remote approval can widen into future auto-approval across linked devices, but the authority expansion is not surfaced as a bounded delegation event
- local shares cannot be Owners, yet they still form local derivative control surfaces that can survive until manually re-shared or reconnected
- some folders live under manual per-folder privilege choices while linked-device mode bypasses per-folder narrowing by granting automatic world-wide ownership inside that identity family
- read-only outcomes sometimes require architectural detours rather than being expressible as a simple narrowing inside the existing controller set

Those are useful clues.
They are not the same as an explicit answer to `who inside the surviving world may currently write, delete, share, approve, revoke, or further delegate; which of those controllers were intentionally designated; and is the live controller set still narrow enough that one accountable actor can honestly speak for it?`

## Why that matters for AnonSync

AnonSync needs a stronger sentence than `the predecessor is retired` and stronger still than `the successor is exclusive controller for the named slice`.
It needs to support claims such as:

- the predecessor is retired, but the successor world still has too many live Owners for a single-accountable-controller sentence
- world-level exclusivity is true, yet authority minimization failed because every linked device can still approve or extend trust
- the controller set is intentionally narrow for one object family, while another family still inherits broad linked-device ownership by default
- a shadow controller exists through auto-approval memory, copied trust handles, or a still-live delegated owner that the interface must keep visible
- the strongest honest sentence is `exclusive surviving world, controller roster still broad and delegation-heavy`, not because the old world persists but because successor-side authority is itself fragmented

AnonSync therefore needs first-class objects for **controller roster, designation basis, delegation chain, auto-expansion policy, shadow-controller exposure, local derivative surfaces, revocation path, minimum-accountable-controller claim, and blocked stronger single-controller sentence** rather than leaving operators to reconstruct controller truth from Owner semantics, linked-device defaults, approval conveniences, manual read-only detours, and local-share caveats.

## Non-clone conclusion

Borrow the candor.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `who inside the surviving world can really act right now, and is that controller set intentionally narrow enough to deserve a strong accountability sentence?` — only by making the operator combine several partially overlapping mechanics:

- Owner permission semantics and revocation rights
- linked-device automatic Owner expansion
- any-device approval for present folders
- future auto-approval across linked devices
- linked-device automatic full read-write access
- manual Standard-folder detours to achieve one read-only outcome
- local-share inheritance and non-Owner limitations
- folder-state distinctions that change practical control surfaces

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model **successor controller roster and delegated-authority discipline** directly.
Its interface family should let the product separate at least these truths:

- successor exclusive world, live controller roster unreviewed
- controller roster enumerated, designation basis mixed
- controller roster broad by linked-family default
- controller roster intentionally narrowed for named slice only
- delegated owner chain present
- auto-expanding approval memory present
- shadow controller suspected through derivative or local surfaces
- single accountable controller blocked
- bounded controller quorum achieved for named slice only
- broader unique-controller claim blocked

That is why this revision adds five more first-class pages:
**Remedy-hardening-attestation-successor-controller-roster contract sheet**, **successor-controller-roster review**, **successor-controller-roster proof**, **successor-controller-roster timeline**, and **successor-controller-roster lineage receipt**.

