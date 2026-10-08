# Resilio remedy hardening attestation successor action authorization quorum, step-up, and high-risk-gate fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials still deserve credit for exposing several ingredients of action authorization inside the surviving world, even if they do not yet elevate them into one typed high-risk-action gate verdict.
That is useful.

The strongest present ingredients are:

- current `User Management` docs still say only users with Owner permission can invite new users to the folder and revoke access rights from other peers, while on-the-fly permission changes are available for Advanced folders
- current `User Management` docs still say that when you share data across your own devices linked to one identity all of your devices act as Owners
- current `Sync Private Identity & Linking My Devices` docs still say approvals for new peers can be issued from any device where the folder is present and that a remote user may choose to automatically approve all your linked devices for future sharing
- current `Sync functionality in detail` docs still say by default you only need to approve a person once because Sync retains a certificate with their identity, though the folder link security options can require approval every time
- current `Sync Share Dialog (Desktop)` docs still say unchecked approval means a peer who gets the link will connect and start syncing automatically, while a stricter option can require approval for all peers and can impose expiration and click-use limits on links
- current `What's the difference between Standard and Advanced folders?` docs still say Standard folders let peers share the key they have without limitation, while Advanced folders add owner semantics and on-the-fly permission changes

## Where the current contract still fragments

The problem is not that Resilio lacks any authorization controls.
The problem is that it still does not produce one first-class, case-scoped **successor action authorization and high-risk-gate legitimacy** object.

Today an operator can often infer only weaker truths such as:

- the successor controller roster is known, but any single eligible Owner may still act unilaterally
- approval can be required, but the product does not promote one typed distinction between low-risk actions, high-risk actions, and actions that should need a second controller or step-up check
- remembered approvals reduce friction for future actions, but that memory is not surfaced as a delegated standing authorization budget for later review
- approval can happen from any linked device where the folder is present, but the exact binding between `this risky action` and `this specific approving controller context` remains diffuse
- some links can be forced through a fresh approval path, while unchecked links auto-connect, but the blast-radius consequences of those choices are not preserved in one durable action receipt
- Standard-folder shareability and Advanced-folder owner semantics differ materially, yet the operator still reconstructs action legitimacy by combining architecture, link settings, and convenience defaults instead of opening one typed verdict

Those are useful clues.
They are not the same as an explicit answer to `may this specific controller or controller set perform this specific risky action now, under what quorum or step-up burden, for what purpose, with what expiry, and with what stronger action-legitimacy sentence still blocked?`

## Why that matters for AnonSync

AnonSync needs a stronger sentence than `the surviving world has a narrow controller roster`.
It needs to support claims such as:

- one accountable controller exists for routine reads, but peer admission still requires dual control
- a controller may revoke for containment alone, but may not broaden sharing without fresh purpose review
- remembered approval is acceptable for low-risk re-entry, but not for successor-world authority expansion after sensitive recovery
- a link may be issued, yet automatic connection is blocked because the action class exceeds the current one-person budget
- the strongest honest sentence is `controller roster narrow, high-risk share action still single-actor and therefore not yet legitimacy-complete`

AnonSync therefore needs first-class objects for **action class, purpose basis, actor set, quorum rule, step-up proof, approval freshness, remembered-authorization exposure, expiry horizon, blast-radius estimate, fallback manual review, and blocked stronger action-legitimacy sentence** rather than leaving operators to reconstruct action legitimacy from Owner semantics, remembered approvals, link checkboxes, and folder-architecture differences.

## Non-clone conclusion

Borrow the candor.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `may this risky action happen now, by this actor set, under a burden appropriate to its blast radius?` — only by making the operator combine several partially overlapping mechanics:

- Owner permission semantics
- linked-device automatic owner expansion
- any-device approval surfaces
- remembered approval defaults
- optional every-time approval settings
- unchecked auto-connect behavior
- expiration and click-use limits on links
- Standard-versus-Advanced architecture differences

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model **successor action authorization quorum and high-risk gate legitimacy** directly.
Its interface family should let the product separate at least these truths:

- controller roster narrow, action gate unreviewed
- routine action allowed, high-risk action blocked pending step-up
- single-controller action allowed for named low-risk class only
- remembered approval usable for return path only
- fresh second-controller quorum required
- quorum satisfied, execution window still open only
- automatic-link path forbidden for this action class
- action legitimacy achieved for named action once only
- broader standing authorization sentence blocked

That is why this revision adds five more first-class pages:
**Remedy-hardening-attestation successor-action-authorization contract sheet**, **successor-action-authorization review**, **successor-action-authorization proof**, **successor-action-authorization timeline**, and **successor-action-authorization lineage receipt**.
