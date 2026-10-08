# Resilio dispatch claim, custody, and abandonment fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- threshold one case honestly
- prioritize several live decisions in one portfolio
- preserve attention budget, preemption, and starvation truth
- say which candidate decision should go now

What it still lacked was the next ordinary operator answer:

> after dispatch picks the winner, who has actually taken custody of that work, under what commitment window, and when does a silently aging assignment fall back into unowned risk?

That is the seam this pass locks.
A product that can rank work but cannot tell whether it has actually been claimed still leaves too much truth in hallway expectation, vague notification, and remembered intent.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose several real **people / authority / notification** ingredients, but mostly as sharing and access surfaces rather than one operator-facing work-custody contract:

- `Sync Main View (Desktop)` still gives a notification bell for approval requests or other notifications, plus a share list, peer list access, and status surfaces.
- `Comprehensive guide to syncing (Desktop-Desktop)` still says a remote add triggers an approval request, that synchronization starts after approval unless approval was disabled, and that the requester details include name, IP address, fingerprint, and request receipt date.
- `User Management` still separates Read Only, Read & Write, and Owner permissions, allows on-the-fly permission changes for Advanced folders, and says all linked devices under one identity act as Owners.
- `Sync functionality in detail` still says permissions can be changed before, during, or after sharing; connection requests can be approved from any linked device; and previously approved identities may not require approval next time unless the share requires approval every time.

## What current Resilio still gets right

### 1) It does expose real identity and approval witnesses

Requester details, approval events, permissions, and owner rights are all real and useful.
That identity candor is worth borrowing.

### 2) It distinguishes several authority levels

Read Only, Read & Write, and Owner are not the same.
That separation matters.

### 3) It allows practical approval from more than one linked device

That convenience is real.
Distributed approval authority is often operationally helpful.

## Where current Resilio still fragments the operator answer

### A) Notification is still weaker than accepted custody

A bell, an approval request, or a visible peer event may tell you that something wants attention.
But it still does not say that a specific operator has taken responsibility for it.

### B) Access authority is not the same as work ownership

Resilio tells you who may read, write, share, revoke, or approve.
It still does not tell you who has actually claimed one dispatched task, what commitment window they accepted, or when silence becomes abandonment.

### C) Linked-device authority can widen who *may* act without clarifying who *did* take custody

If any linked device can approve a connection and all linked devices act as Owners under one identity, authority becomes more convenient but also more diffuse.
That is useful for access management, but it is not yet a work-custody contract.

### D) Previously approved identity is not the same as current work acceptance

Retaining trust or approval relationships is operationally helpful.
But a person or device being generally trusted is still weaker than explicit acceptance of this specific dispatched work item now.

### E) There is still no first-class abandonment or reclaim story

Current Resilio docs explain approvals, permissions, and revocation.
They still do not compile one explicit answer to: what happens when the selected work sits unclaimed, ages out, gets re-delegated, or needs to return visibly to the portfolio?

## What AnonSync should borrow

- visible notification and approval surfaces
- requester identity details before acceptance
- explicit authority levels
- practical approval convenience where authority really is shared

## What AnonSync should not clone

AnonSync should not clone a world where the operator must infer work ownership from notifications, generic authority, or the existence of a prior trust relationship.
It should not leave the following questions scattered across notification state, permissions, and memory:

- who has actually claimed the dispatched work?
- was it merely announced, or explicitly accepted?
- what commitment window was accepted?
- when does silence become expiry or abandonment?
- who may re-delegate the work, and under what bounded authority?
- when does the work fall back into the unowned portfolio visibly?

## Product requirement extracted from this evaluation

AnonSync should own one stable page family for **work claim and execution custody**.
That family should make it ordinary to publish:

- dispatched item
- requested assignee
- claim state
- commitment window
- re-delegation boundary
- expiry and reclaim rules
- abandonment guard
- durable custody receipt

## Bottom line

Current Resilio still deserves credit for exposing useful identity, approval, and permission surfaces.
But it still does not own one operator-facing answer to:

> after dispatch chooses the work, who actually has custody of it now, what commitment was accepted, and when does that work fall back into visible risk if nobody truly takes it?

That is why this seam belongs on the non-clone side.
