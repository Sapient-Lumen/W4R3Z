# Permission change preview page: live policy edit, artifact reset, and required reissue interface spec

## Purpose

This page answers one ordinary question:

> if I try to change this seat's authority, am I editing a live policy, minting a successor, forcing reconnection, or only lowering a derivative?

The page exists because permission change is not one universal verb.

## Core decision

Any action that changes a seat's authority must pass through a **Permission change preview** page before commit.
The preview owns:

- requested change
- mechanism class
- continuity effect
- downstream seat effect
- reauthentication / reacceptance burden
- strongest safe sentence after change

## Fixed page order

1. requested change strip
2. mechanism class card
3. continuity effect card
4. downstream impact card
5. operator burden card
6. commit boundary card

### 1) Requested change strip

Show:

- current grant class
- requested grant class
- target principal or seat family
- whether this is upgrade, downgrade, revoke, or transform
- strongest next-safe action

### 2) Mechanism class card

One of the following must be chosen explicitly:

- `live policy edit`
- `successor issuance required`
- `remove and reconnect required`
- `lower derivative only`
- `not possible`

This card must explain why.

### 3) Continuity effect card

Publish whether the requested change:

- preserves the same seat lineage
- narrows the existing seat
- creates a new successor while old continuity may persist elsewhere
- requires the subject to reconnect or reaccept
- produces an epoch boundary or policy fork

### 4) Downstream impact card

Show effects on:

- derivatives
- delegates
- linked own seats
- retained approvals or remembered trust
- existing receipts

A change that would silently auto-lower or invalidate downstream seats must say so before commit.

### 5) Operator burden card

Show any required new work:

- reissue invite
- reclaim stale artifact
- request fresh acceptance
- rotate related derivatives
- publish new receipt

### 6) Commit boundary card

The preview ends with one of these clear outcomes:

- `change now`
- `issue successor instead`
- `downgrade only`
- `review delegation first`
- `blocked`

## Rules

### Rule 1 — preview the mechanism, not just the target label

`Make Read Only` or `Make Writer` is not enough.
The operator must know whether the system is editing policy or replacing authority.

### Rule 2 — lineage impact must be explicit

A change that forks continuity or requires reacceptance cannot look like a minor toggle.

### Rule 3 — downstream effects must publish before commit

The page must show derivative lowering, delegate invalidation, or receipt supersession before the operator confirms.

## Acceptance criteria

A later operator can:

- tell how the change is actually implemented
- tell whether the prior seat survives, narrows, or is superseded
- tell which downstream seats and receipts are affected
- avoid mistaking artifact reissue for live policy mutation
