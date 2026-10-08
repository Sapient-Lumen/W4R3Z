# Membership presence, offline aging, and hidden-device truth interface spec

## Purpose

The archive already has retirement records, successor replacement, approval memory, and empty-state attribution.
What it still lacked was one concrete interface contract for the question:

> when a member is absent, hidden, stale, or unexpectedly back online, what surface tells the operator whether this is live presence, remembered absence, cosmetic hiding, safe retirement, or a still-trusted device that simply has not been seen lately?

Current Resilio docs expose this seam clearly.
The peers view still reports `X of Y` where `Y` includes offline peers, an offline peer is disconnected from a folder after 7 days by default but that timer is configurable, and clearing an offline linked device does not unlink it — it only hides it, after which it will reappear if it comes back online.
Those are honest facts.
They still leave too much operational meaning spread across peer counts, aging rules, and list-hiding behavior.

## Core decision

Presence and membership must be represented by one first-class **membership ledger**.
The ledger must keep live reachability, trust state, aging, and cosmetic visibility distinct.

The operator should never have to infer `this thing is really gone` from the fact that it is merely hidden from one list.

## Membership classes

The interface must distinguish at least:

1. **Live present** — currently reachable and trusted
2. **Offline remembered** — still trusted, currently absent
3. **Aged-disconnected** — absent long enough to have been detached from active participation
4. **Hidden from view** — cosmetically suppressed but still trusted and able to reappear
5. **Retired / ignored** — intentionally kept out of future ordinary workflows
6. **Revoked** — no longer trusted even if it reappears
7. **Replaced by successor** — continuity moved elsewhere by review

## The fixed review order

Every membership/presence surface should render sections in this order:

1. **Current live-presence answer**
2. **Trust and membership state**
3. **Offline age and expected return behavior**
4. **Safe operator actions**
5. **Dependent effects**
6. **Receipt promise**

## 1) Current live-presence answer

Show:

- member label and stable handle
- last-seen and last-acted time
- current reachability class
- whether the member is counted in live quorum, remembered inventory, both, or neither
- whether the member is visible, hidden, retired, or revoked in the current view

The operator should immediately be able to answer:

> is this member alive right now, merely remembered, or hidden for cosmetic reasons only?

## 2) Trust and membership state

This section should state plainly:

- whether the member remains trusted
- whether it may still approve, write, or serve bytes when it returns
- whether it belongs to the current personal constellation, a shared subject, or only historical receipts
- whether its presence is ordinary, degraded, frozen, retired, or revoked

Reachability is not trust, and trust is not visibility.
The page must keep those answers separate.

## 3) Offline age and expected return behavior

Show:

- current offline age
- the policy or threshold that changes how absence is treated
- whether the member will rejoin automatically if it comes online
- whether it would appear again in ordinary views or only in historical inventory
- whether the current absence is harmless, aging toward review, or already past a safety threshold

A configurable aging threshold should not remain power-user folklore.
It should be part of the presence answer.

## 4) Safe operator actions

Primary actions should be explicit:

- `Hide from current views`
- `Keep remembered and trusted`
- `Mark for retirement`
- `Revoke trust`
- `Replace with successor`
- `Open compromise response`

The interface must not pretend those actions are all variants of `remove from list`.

## 5) Dependent effects

Show fallout on:

- approval memory
- future-arrival posture that references the member
- subjects for which this member is currently a known witness or writer
- successor or replacement plans
- diagnostics and evidence bundles that still reference the member

A member is not just an avatar in a list.
It is part of continuity, trust, and recovery state.

## 6) Receipt promise

The resulting receipt must prove:

- prior membership class and new one
- whether the action was cosmetic, trust-changing, or continuity-changing
- whether the member may reappear automatically
- whether any approval, witnessing, or successor relationship changed

A later reader should be able to answer:

> did we hide a cluttering offline laptop, retire an old member, revoke trust, or replace it with a successor?

## What must never happen automatically

The product must never automatically:

- equate hidden with retired
- equate offline with safe
- bury the aging threshold outside the membership answer
- let a previously hidden member reappear without preserving the earlier hide receipt
- let an operator think a cosmetic hide severed trust or vice versa

## Why this is worth the trouble

Presence is one of the places where sync products quietly mix liveness, trust, and inventory into one vague list.
AnonSync can do better by making membership state legible enough that a returning device is a classified event, not a surprise contradiction of what the operator thought `hidden` meant.
