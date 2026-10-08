# Resilio share-artifact, approval, and mutable-grant evaluation

## Why this pass matters

Current official Resilio Sync docs are again useful for AnonSync precisely because they are candid about capability artifacts and approval.
They still say all of the following:

- Advanced folders are ordinarily shared by link or QR, while Standard folders also expose raw keys and do not offer Owner permission in the same way.
- In the desktop Share dialog, approval policy, expiry period, and click-budget are part of the link story, and `Only new peers` versus `All peers` changes how remembered approval is reused.
- Keys and links are not merely two skins for the same thing: current docs still say the major difference is the approval mechanism, and the key architecture article still makes raw key type part of the capability itself.
- Link flow is real protocol work, not just URL cosmetics: the landing page shows only basic preview info, the link carries a temporary key after `#`, the requester sends a locally generated public key, approval shows a user name plus fingerprint, and successful approval mints certificate-backed access plus an ACL entry.
- User Management still says rights can be edited on the fly only for Advanced folders, while `Disconnect` revokes future updates but leaves already synchronized files where they are.
- Mobile sharing is real too, but current docs still phrase it as `send the key or link`, then let the receiving side pick location and connect, which means the actual capability family and approval path are still easy to over-compress.

That is strong product substance.
It is also a concrete reason not to clone the page contracts.

## What Resilio gets right

### 1) It admits that capability artifacts are not interchangeable

Current docs still distinguish:

- raw key material
- links with approval-capable flow
- QR as another delivery carrier for the same basic share intent
- different rights ceilings depending on Standard versus Advanced folder type

That is useful honesty.
A product that hides all of those under one generic `Share` button would be weaker.

### 2) It admits that approval is a real identity-bearing event

Current docs still describe approval as:

- a real incoming request
- from a concrete requester
- carrying a locally generated public key
- reviewed by user name and fingerprint
- followed by certificate and ACL mutation on success

That is exactly the kind of substance AnonSync should keep.

### 3) It admits that post-share mutability is asymmetric

Current docs still say:

- not every folder type supports the same grant editing story
- Owner has onward-share power while ordinary RW does not
- revoking future updates is not the same as clawing back already synchronized bytes

That is also the right kind of candor.

## Why we still should not clone it

The core problem is not that Resilio lacks semantics.
The core problem is that the ordinary answer is still fragmented across several article families.

Today the operator still has to reconstruct one answer from the Share dialog docs, key architecture docs, link-flow docs, user-management docs, and mobile sharing docs:

- what exact capability artifact am I issuing here?
- what approval path does that artifact imply, if any?
- who is actually asking for access right now, and why was this auto-approved or gated?
- what part of the grant remains editable later?
- what part of `disconnect` or revoke only stops future updates rather than reclaiming already landed bytes?

Those should not be support-navigation questions.
They should be ordinary product pages.

## The AnonSync borrow line

Borrow from current Resilio:

- artifact-family candor: key, link, QR, and rights ceiling are distinct facts
- approval candor: requester identity, fingerprint, and approval reuse basis are real operator truths
- mutable-grant candor: grant editability and revoke consequences are not universal across subject kinds
- mobile/desktop carrier candor: issuance carrier and receiving path choice are separate from capability semantics

Adapt into AnonSync:

- one first-class page for **share capability**
- one first-class page for **incoming share request**
- one first-class page for **member access**
- one first-class page for **manual claim**

## The replacement principle

AnonSync should never let `Share`, `Copy link`, `Scan QR`, `Paste key`, `Approve`, or `Disconnect` stand in for the whole capability story.
Any surface that issues, receives, approves, edits, or revokes share authority should be able to answer five questions directly:

1. what exact artifact family is in play?
2. what approval model comes with it?
3. which requester is actually present now, and what evidence identifies them?
4. what later edits are still allowed for this grant?
5. what exactly stops on revoke, and what already-landed bytes remain outside that future-update boundary?

That is the tighter reason not to clone current Resilio page contracts in this part of the product.
