# Resilio reliance-to-action authority, delegation, and recall fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- certify bounded estate scope
- publish an audience-safe reliance packet
- keep freshness, exclusions, supersession, and recall visible for that packet

What it still lacked was the next ordinary operator answer:

> now that someone received a packet, who is merely informed, who is allowed to decide, who is allowed to execute, who may re-delegate, and what happens to work already in motion when the packet is superseded or recalled?

That is the seam this pass locks.
A reliance packet is **not** a work order.
It becomes operational only when it is translated into an explicit **action mandate**.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose many real action-authority ingredients, but as separate sharing and approval surfaces rather than one canonical downstream-action contract:

- `Sync functionality in detail` still says folder permissions determine what a user can do with a shared folder, with three classes: Read Only, Read & Write, and Owner. It also still says permissions can be changed before, during, or after sharing, access can be revoked, and a requester’s approval can be altered at approval time. So action authority is real and mutable.
- The same functionality article still says that when devices are linked under one private identity, all linked devices act as Owners, and a folder can be shared and approval requests handled from any linked device. So action authority can expand through identity topology, not just one local button.
- `User Management` still says only users with Owner permission can invite new users, Owners also have full Read & Write permission, and peers with different identities may receive different permissions. It also still says a disconnect revokes future updates for that peer while already synchronized files remain. So the product already distinguishes between knowing, changing, sharing onward, and receiving future effects.
- `Sync Share Dialog (Desktop)` still says Advanced folders can be shared only by peers who have Owner access, whereas Standard folders have no Owner level and all peers can share the folder onward, with Read Only peers limited to sharing only a Read Only key. It also still keeps approval requirement, link expiry, and use-count limit in the share dialog. So the practical downstream authority contract changes with folder type, link mode, and security options.
- `Comprehensive guide to syncing (Desktop-Desktop)` still says manual sharing requires choosing the access mechanism (key, link, or QR), choosing the permission set for the remote device, and approving the connection if approval is required. It also still says the approver can inspect the requester’s name, IP address, fingerprint, and approval request receipt date before approving. So action enablement is already a small workflow with identity witness, not just permission labels.

## What current Resilio still gets right

### 1) It is candid that action authority is not one flat thing

Read Only, Read & Write, and Owner are genuinely different.
Approval, invitation, revoke, and onward-sharing rights differ.
That is worth borrowing.

### 2) It preserves some expiry and security truth

Link expiry, link-use limits, and approval rules all acknowledge that an authority grant can be temporary, conditional, or routed through a checkpoint.
That is useful.

### 3) It keeps folder-type and identity topology visible

Advanced versus Standard folders, linked-family ownership, and per-peer permission changes all show that the same apparent sharing action can mean different authority.
That is important.

## Where current Resilio still fragments the operator answer

### A) There is no canonical action-mandate object

Resilio gives the operator permission labels, share dialogs, approval checkpoints, requester fingerprints, and revoke/disconnect actions.
What it still does not give is one operator-facing object answering:

- whether this recipient is merely informed or actually authorized to act
- what exact action is authorized, required, or forbidden
- whether the authority may be re-delegated
- which world / scope / asset set the authority applies to
- when the mandate expires
- what supersedes or cancels work already queued or underway

### B) Reliance and authority still blur too easily

A recipient can receive a link, a packet, a status update, or a permission change.
Current Resilio exposes these ingredients, but still leaves the operator to infer whether the recipient may merely observe, approve, execute, or invite others.
That is too much ambiguity for serious downstream operations.

### C) Recall and execution cancellation are not one durable lane

Resilio can revoke access, disconnect a peer, expire a link, or require approval again.
Those are real controls.
But it still does not provide one durable product answer to:

- which already-issued instruction is still live
- which newer instruction supersedes it
- whether a recipient acknowledged the new one
- whether in-flight action must stop, continue, or complete under a weakened ceiling

## Hard product decision unlocked by this pass

AnonSync should not let `received the packet` impersonate `may act on the packet`.
It should promote any material downstream instruction into a first-class **action mandate** that separately expresses:

- recipient or actor class
- authority class
- allowed action set
- required action set
- forbidden action set
- re-delegation rights
- expiry and cancellation rule
- stronger blocked sentence the recipient must not infer

## Replacement line for AnonSync

Borrow from Resilio:

- candor that permissions, invitation rights, approval steps, and revoke flows are different things
- honesty that folder type, identity topology, and share mechanism affect what a recipient can do
- practical use of expiry, use-count limits, and requester fingerprint review before approval

Do not clone from Resilio:

- any workflow where a reliance packet quietly becomes an action order without an explicit authority object
- any contract where `can read status`, `can approve`, `can execute`, and `can re-share` are inferred from context instead of stated directly
- any product shape where superseding or canceling in-flight downstream action depends on thread folklore or human memory

AnonSync should instead ship explicit pages for:

- action mandate contract sheet
- mandate shaping review
- action authority proof
- mandate timeline
- mandate lineage receipt
