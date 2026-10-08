# Resilio subject-class cliff, upgrade, and linked-read-only ritual evaluation

## Why this pass matters

Current official Resilio Sync docs are again useful precisely because they are candid about one of the hardest ordinary product truths:

- Standard folders and Advanced folders are not merely two skins for the same subject.
- Standard folders use keys; Advanced folders use PKI and certificates.
- Owner and on-the-fly permission mutation are Advanced-only.
- Standard peers can re-share the key they have without the same bounded Owner model.
- Standard folders cannot be upgraded in place; the documented path is remove on all peers and re-add as Advanced.
- If one linked device should behave as read-only, current docs still push the operator toward a separate Standard-folder read-only-key ritual with manual reconnect and path choice.
- The peer list itself changes meaning: Advanced can show one linked user's device family as one user with descendant devices, while Standard shows peer/device entries separately.

That is strong product honesty.
It is also another concrete reason not to clone the page contracts.

## What Resilio gets right

### 1) It admits that subject class is a real semantic cliff

Current docs do not pretend that Standard and Advanced differ only cosmetically.
They still say the architecture differs, the authority model differs, mutable grants differ, and peer-list identity rendering differs.
That honesty is worth borrowing.

### 2) It admits that migration is a cutover, not a toggle

Current upgrade docs still say there is **no way to upgrade in place** from Standard to Advanced.
The operator must disconnect/remove the Standard folder on all peers and add the folder back as Advanced.
That is exactly the kind of discontinuity many products try to hide.

### 3) It admits that `linked read-only` is not a natural fit for the linked-owner model

Current docs still say all linked devices under one identity act as Owners.
If the operator wants one linked device to be read-only, the documented path is not a simple per-device exception.
Instead, the operator must use a Standard folder with a Read Only key, disconnect the already connected folder, paste the RO key, and choose a path manually.
That is extremely valuable evidence about the real authority model.

## Why we still should not clone it

The problem is not that Resilio lacks semantics.
The problem is that the operator still has to reconstruct one ordinary answer from several article families:

1. what class of subject is this, really?
2. what cliffs come with that class for identity, sharing, mutation, and peer views?
3. when is `upgrade` actually a successor cutover rather than a state change?
4. when a linked device should be read-only, is the product narrowing one subject or creating a separate lower-governance subject?
5. why does the peer list look like user families in one case and raw device rows in another?

Today those answers still live across the Standard-vs-Advanced article, upgrade how-to, linked-read-only how-to, user-management guidance, and broader linking docs.
That is not a strong ordinary page contract.

## The AnonSync borrow line

Borrow from current Resilio:

- subject-class honesty
- explicit cutover honesty when the class must change
- visible ownership/mutation cliffs
- willingness to admit that some requests are really separate-subject rituals rather than simple toggles
- candor that peer-list aggregation depends on deeper identity/certificate structure

Adapt into AnonSync:

- one page for **subject class and cliffs**
- one page for **class-upgrade review and peer-epoch cutover**
- one page for **linked read-only exception review**
- one page for **peer identity view and aggregation basis**

## The replacement principle

AnonSync should never let the operator discover subject-class truth indirectly from which buttons are missing, which peer rows collapse, or which support article recommends a raw-key workaround.

Any surface that creates, upgrades, narrows, or inspects a subject should be able to answer:

- what class this subject belongs to
- what that class implies for identity, authority, mutability, and aggregation
- whether a proposed change preserves the subject or creates a successor epoch
- whether a requested per-seat exception is really a side-door separate subject
- what the current peer view is actually grouping by

That is the tighter reason not to clone current Resilio page contracts in this part of the product.
