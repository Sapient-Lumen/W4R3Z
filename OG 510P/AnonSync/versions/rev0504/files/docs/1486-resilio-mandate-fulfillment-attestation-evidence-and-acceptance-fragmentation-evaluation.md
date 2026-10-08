# Resilio mandate fulfillment attestation, evidence, and acceptance fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- publish a bounded certification for reliance
- separate reliance from action authority
- issue a downstream mandate with scope, expiry, and cancel behavior

What it still lacked was the next ordinary operator answer:

> once someone had authority and says the action is done, what exactly came back, what evidence came with it, what part is still blocked, and who has accepted or disputed that completion claim?

That is the seam this pass locks.
A mandate is not complete just because it was issued.
A mandate is not complete just because the assignee says `done`.
A mandate is not complete just because some system status looks greener than before.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose many of the ingredients an operator would use when trying to decide whether a delegated sync action is really complete:

- `Comprehensive guide to syncing (Desktop-Desktop)` still says that once a remote device adds a shared folder an approval request is sent to the source side, and that synchronization starts only after approval or when approval was disabled.
- The same guide still says that if a device remains in `Pending approval` while the source device receives no approval request, the condition indicates a network-connectivity problem between the devices.
- The same guide still says the approver can inspect requester name, IP address, certificate fingerprint, and approval-request receipt date before approving.
- `Sync functionality in detail` still says approval-time permissions can be altered, approvals can be handled from any linked device, and synchronization progress is shown for individual files in selective-sync surfaces.
- `Sync Main View (Desktop)` still says the bell lights up for approval requests or other notifications, the History lane shows general syncing activity for the last 30 days, green check means files are synced with all connected peers, and the peer count distinguishes online peers from total peers.
- `User Management` still says permissions can be changed without disrupting synchronization and that disconnect revokes future updates while already synchronized files remain.
- The current `Resilio Sync change log` still records notifications being synchronized across devices, a `Last transferred` column, a searchable/sortable History tab, and fixes/improvements around the accuracy of files that need to be sent or received in the peer list.

## What current Resilio still gets right

### 1) It acknowledges that completion has several observable planes

Approval state, notification state, history state, peer-list state, transfer state, and permission state are all real.
That is worth borrowing.

### 2) It keeps some approval evidence close to the act of approval

Requester name, IP, fingerprint, and request date are all useful witnesses.
That is much better than a blind `accept` button.

### 3) It distinguishes some visibly different aftermaths

Approved and syncing, pending approval, disconnected-but-bytes-remain, and connected-with-green-check are not presented as identical.
That is good discipline.

## Where current Resilio still fragments the operator answer

### A) There is no canonical fulfillment object

Resilio gives the operator approval request surfaces, peer state, history, notifications, and folder permissions.
What it still does not give is one first-class object answering:

- what exact mandate or requested action this return is claiming to fulfill
- whether the assignee is reporting `attempted`, `partially complete`, `complete`, or `blocked`
- what evidence payload came back with that claim
- what remainder or residual obligation still survives
- who reviewed the return
- whether the return was accepted, partially accepted, disputed, or sent back for rework

### B) Observable sync state is weaker than accepted completion

Green check means synced with connected peers.
History means activity happened.
Peer-list counters mean some peers are online or offline.
Notifications mean something needs attention.
None of those are the same thing as:

- the delegated action was fully performed
- the requested scope was actually covered
- the requester has accepted the return
- the stronger completion sentence is now safe

### C) Approval flow is not the same as task completion flow

Resilio's approval surfaces are good at saying a remote device may join or sync.
They are weaker at saying a previously issued operational mandate is now finished and accepted.
Those are different workflows and should stay different.

### D) Dispute and partial-return truth are left to operator folklore

If a delegate returns with incomplete work, overclaims, ambiguous evidence, or a changed side effect that the requester does not accept, current Resilio gives raw symptoms and history fragments, but not one durable adjudication object.

## Hard product decision unlocked by this pass

AnonSync should not let `issued` or `activity observed` impersonate `fulfilled and accepted`.
It should promote any material return on delegated work into a first-class **fulfillment attestation** that separately expresses:

- source mandate
- claimed completion class
- evidence bundle and evidence freshness
- blocked or skipped remainder
- reviewer verdict
- acceptance class
- surviving obligations and stronger blocked sentence

## Replacement line for AnonSync

Borrow from Resilio:

- visible approval and notification surfaces
- requester-identity details at approval time
- history, peer state, and transfer observations as real witnesses
- honesty that `connected`, `pending approval`, `green check`, and `disconnected` are different operational states

Do not clone from Resilio:

- any workflow where the assignee's `done` note plus a green check implicitly counts as accepted completion
- any contract where approval state doubles as mandate-fulfillment state
- any product shape where partial completion, disputed evidence, or residual duties are left to chat threads and memory
- any interface where observed sync activity silently stands in for requester acceptance

AnonSync should instead ship explicit pages for:

- fulfillment attestation contract sheet
- execution return review
- completion acceptance proof
- fulfillment timeline
- fulfillment lineage receipt
