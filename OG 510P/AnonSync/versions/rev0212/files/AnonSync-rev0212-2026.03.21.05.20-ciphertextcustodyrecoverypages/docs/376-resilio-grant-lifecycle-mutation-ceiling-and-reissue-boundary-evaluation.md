# Resilio grant lifecycle, mutation ceiling, and reissue-boundary evaluation

## Why this pass exists

The archive already had strong doctrine for capability artifacts, incoming requests, member access, subject class, and linked-seat authority.
What it still lacked was one direct current Resilio evaluation for another ordinary seam:

> after access already exists, what exactly can I still change in place, what must be re-issued as a new grant epoch, and what residue survives any revocation?

Current official Resilio docs still show a useful, living product, but they also show that ordinary grant-lifecycle truth still leaks across several different article families at once:

- share-dialog security and permission controls
- Advanced-folder user management
- Standard-vs-Advanced class fences
- local-share special cases
- key-flow and link-flow mechanics
- disconnect / reconnect notes

## Current official Resilio evidence that matters here

Current official docs still show an active v3 line through `3.1.2.1076`.
They also still say all of the following:

- Advanced folders can change member permissions on the fly, including Owner, Read & Write, and Read Only, while Standard folders cannot do that and instead require removing the share and re-adding it with a new key.
- In the desktop Share dialog, links can carry approval requirements, expiry, and use limits, while Standard-folder raw keys do not use the approval mechanism at all.
- If you hit `Disconnect` in user management, Resilio revokes future updates for that peer, but all files that were already synchronized remain in the folder.
- A local share inherits the source-share ceiling, cannot receive Owner, and for Advanced shares cannot have its access changed through user management; to change permissions you must remove the local share and re-share it again.
- If the upstream source right is lowered, the local share lowers with it, but if the source is disconnected and later reconnected the local share is removed and does not automatically reconnect.
- In Standard key flow, if a user changes the Key on one peer, the change is not distributed automatically; peers with the old key continue syncing with each other, but no longer with the peer who changed the key.

So current Resilio still contains a real but scattered answer to `am I editing this grant, or creating a successor grant epoch?`

## What Resilio still gets right

### 1) It admits that not all grants are equally mutable

Current docs still plainly say that live right changes are available only for Advanced folders, while Standard folders need remove-and-readd behavior.
That honesty matters.
A weaker product would hide the class fence.

### 2) It admits that revocation is not byte recall

Current docs still distinguish `stop future updates` from `already landed bytes remain`.
That is the right kind of candor.
A sync product should not pretend that disconnect or revoke can un-send replicated data.

### 3) It admits that descendants and derivatives have their own lifecycle

Current docs still show local shares as dependent descendants with their own special rules:
rights inherit downward, some changes cascade from source to derivative, some other changes require remove-and-re-share, and source removal does not yield clean automatic reattachment later.
That is useful evidence.

### 4) It admits that artifact rotation is a real epoch break

The key-flow docs still say a key change does not distribute automatically.
That is not an incidental technicality.
It is a governance boundary with continuity consequences.

## Why this is still a good reason not to clone them

### 1) In-place edit versus successor epoch is still not owned by one page

The operator still has to cross-read several current docs to answer one ordinary question:

- can I change this right live?
- if not, what exact artifact must be re-issued?
- which peers remain on the old epoch?
- which descendants inherit the downgrade automatically?
- what residue survives revoke?

That should not be a support-navigation exercise.

### 2) Artifact inventory and grant inventory are still too loosely coupled

Resilio is candid that keys, links, approvals, expiry, and use budgets matter.
But it is still too easy for the operator to know `somebody has access` without one stable page that also says:

- which specific live artifacts still exist
- which ones can still create fresh claim events
- whether a role edit updates the same grant or requires a replacement artifact
- whether old artifacts still define parallel continuity islands

### 3) Descendant blast radius still lives in special-case prose

Local-share docs currently reveal an important truth:
source-right changes, source disconnects, and source removal have descendant consequences.
But those consequences still arrive as article prose, not as a first-class blast-radius page in the product.

### 4) Revocation and cleanup are still too easy to over-compress

Current docs are honest that already-landed files remain.
But the operator still has to reconstruct what happens next for:

- direct members
- pending claims
- local derivatives
- old-key peers
- retained bytes on former recipients

A product should separate those answers explicitly.

## The tighter AnonSync conclusion

AnonSync should borrow the following from Resilio more boldly:

- visible live-right mutation where the class really supports it
- explicit expiry and use-budget controls on issued artifacts
- honest language that revocation stops future updates, not past replication
- candid admission that some changes create a new epoch rather than editing the old one

But AnonSync should refuse the exact page contract whenever one ordinary grant-lifecycle answer still depends on:

- class folklore
- derivative-share folklore
- key-versus-link folklore
- disconnect/reconnect how-tos
- later peer observation to infer which epoch survived

## The replacement pages this evaluation justifies

This pass therefore makes four page-shaped obligations concrete:

1. **Grant change** — am I editing this grant live, and what exact delta is being proposed?
2. **Issued access** — what live artifacts and grant epochs are still outstanding right now?
3. **Revocation scope** — what future updates stop, which descendants stay affected, and what bytes remain outside recall?
4. **Reissue plan** — when live edit is impossible, what exact successor artifact and continuity plan replaces it?

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still good evidence that mutable rights, security-bounded links, and derivative-share pragmatism are worth building, but it is also current evidence that ordinary grant-lifecycle truth still leaks across class fences, derivative caveats, and artifact-flow articles. AnonSync should copy the practicality and refuse the scattered lifecycle contract.
