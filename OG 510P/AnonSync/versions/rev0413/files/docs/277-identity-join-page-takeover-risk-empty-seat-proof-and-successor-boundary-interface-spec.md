# Identity join page: takeover risk, empty-seat proof, and successor boundary interface spec

## Purpose

`204` established the compatibility-gate logic for cohort joins and takeover risk.
This document makes it concrete as one ordinary page.

The page exists to answer one ordinary operator question:

> am I safely joining this seat into an existing identity family, or am I actually replacing a non-empty local control plane with another one?

## Core decision

Every non-trivial identity-join attempt must render one first-class **Identity join** page.
That page is the semantic home of:

- seat emptiness versus non-empty local control-plane proof
- cohort / schema compatibility summary
- takeover or successor-import risk
- local-byte survival versus local-app continuity loss
- admissible join paths and receipts

The page must not let a generic `Link device` action stand in for those truths.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. current join verdict strip
2. local seat population card
3. remote family card
4. takeover and successor-boundary card
5. admissible join paths
6. receipts and preserved evidence
7. blocked / destructive paths drawer

### 1) Current join verdict strip

The strip shows:

- local seat name
- remote family or source seat
- one compatibility verdict
- one continuity verdict
- one next-honest-action button

Allowed compatibility verdicts:

- `safe join`
- `reviewed import required`
- `cohort migration required`
- `unsafe takeover blocked`

Allowed continuity verdicts:

- `empty seat may join cleanly`
- `local control plane present`
- `successor import required`
- `local continuity would be displaced`

### 2) Local seat population card

Show:

- whether the local seat is empty, partially configured, or populated
- local identity / authority epoch
- current subject count
- approval / trust material presence
- whether local bytes exist outside the local control plane
- strongest evidence supporting the emptiness claim

This card must make `fresh seat` and `already configured seat` visibly different.

### 3) Remote family card

Show:

- remote identity family name or source seat
- release / schema cohort summary
- remote subject count
- current capability or license family when relevant
- why this source is admissible or risky

The page should answer: `what kind of world am I joining?`

### 4) Takeover and successor-boundary card

This card is mandatory whenever the local seat is non-empty.
Show:

- whether the action is a relationship join, successor import, or takeover risk
- which local control-plane objects would be replaced, hidden, retired, or preserved
- whether local bytes are expected to remain on disk
- whether local app-visible subjects would disappear or need salvage
- whether the action is harsher on constrained platforms

The page must say plainly when local files may survive while local app continuity does not.

### 5) Admissible join paths

Render ordered action rows such as:

- `Join empty seat`
- `Preserve local world and stop`
- `Export local receipts, then import successor`
- `Upgrade cohort first, then retry`
- `Block until explicit migration review`

Each row shows:

- continuity class
- local-control-plane result
- local-byte result
- reversibility
- whether additional salvage is required first

### 6) Receipts and preserved evidence

Show recent join or import receipts with:

- actor
- local seat
- source family
- join class
- preserved evidence bundle refs
- continuity result
- remaining follow-up

### 7) Blocked / destructive paths drawer

If a risky destructive path exists, place it behind a clearly named drawer such as `Displacing local continuity`.
That drawer may contain:

- force successor import
- discard local control plane and join remote family
- sever current identity and rebuild later

The page must state exact blast radius before any such action becomes live.

## Narrow-width behavior

In narrow width the page may stack cards, but it may not hide:

- local emptiness verdict
- takeover versus safe-join verdict
- byte survival versus control-plane survival truth
- next admissible action

## Acceptance criteria

This spec is satisfied when:

- an operator can tell from one page whether the seat is truly empty enough for clean join
- safe join, successor import, and takeover are visibly different outcomes
- local-byte survival cannot masquerade as preserved local app continuity
- mixed-cohort or mixed-license joins open through explicit compatibility language rather than lore
- any committed join leaves a durable receipt naming the continuity class that actually occurred
