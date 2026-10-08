# Local-mutability contract sheet page — write grant, lock barrier, and host lane

## Purpose

This page answers one ordinary question:

> can this runtime actually mutate bytes here now, by what authority, through what lane, and what barrier is presently stronger than the write request?

The page exists because `visible path`, `share connected`, `folder present`, `readable`, `writeable`, and `safe to mutate` are not interchangeable.

## Core decision

Every serious write or hydration action must render one first-class **Local-mutability contract sheet**.
The page owns:

- subject path
- runtime / actor
- write grant class
- host write lane
- lock barrier class
- filesystem health class
- current mutability ceiling
- strongest safe sentence now

## Fixed page order

1. mutability strip
2. barrier stack
3. host-lane card
4. retry / escalation card
5. proof card
6. receipts

### 1) Mutability strip

Show:

- subject path
- requested verb: `write-bytes`, `rename`, `delete`, `hydrate`, `restore`, `create-child`, `update-mtime`, `unknown`
- active actor / principal
- write grant class: `full-local-grant`, `provider-api-grant`, `nas-service-account-grant`, `service-principal-grant`, `read-only-grant`, `unknown`
- current mutability class: `writeable-now`, `blocked-by-lock`, `blocked-by-grant`, `blocked-by-principal`, `blocked-by-host-lane`, `blocked-by-filesystem-health`, `blocked-by-mount-loss`, `unknown`
- one honest next action

### 2) Barrier stack

List all blockers from strongest current winner to weaker or merely historical blockers.
For each barrier show:

- barrier class
- evidence basis
- retryability: `auto-recheck`, `needs-human-fix`, `needs-restart`, `needs-world-shift`, `unknown`
- whether the current surface can resolve it

The operator must be able to answer: **what is the strongest blocker right now, and what weaker blockers are merely nearby?**

### 3) Host-lane card

Publish:

- host write lane: `direct-local-fs`, `provider-api`, `smb-through-server`, `sync-direct-plus-smb-observers`, `nas-internal-user`, `service-profile-world`, `unknown`
- lane safety class: `ordinary`, `fragile`, `unsafe-mixed-authority`, `unknown`
- whether the lane can safely coexist with third-party mutation paths
- what stronger sentence is blocked

The operator must be able to answer: **is the path just writable, or writable through a lane the product considers safe?**

### 4) Retry / escalation card

Show:

- next retry rung: `automatic-lock-recheck`, `rescan`, `app-restart`, `service-restart`, `grant-repick`, `principal-switch`, `remount-or-fs-repair`, `manual-readd`, `unknown`
- whether the product expects automatic recovery
- whether a world change will invalidate old folder continuity

### 5) Proof card

Show:

- best evidence that bytes can mutate here now
- best evidence that they cannot
- weakest missing proof still preventing a stronger sentence

### 6) Receipts

Always link:

- latest local-mutability receipt
- latest governance-plane receipt if authorship / principal changed
- latest action-surface receipt if the current surface cannot resolve the barrier

## Copy rules

- Never collapse `path visible` into `path writable`.
- Never collapse `provider granted root` into `every sub-action is allowed`.
- Never collapse `not locked now` into `safe host lane`.
- Never collapse `service has access` into `same world as prior interactive runtime`.
- Never collapse `will retry later` into `writeable now`.
