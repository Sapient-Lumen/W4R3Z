# Nested-share topology review page: parent-child rights, shadow propagation, and seed-gap interface spec

## Purpose

This page answers one ordinary question:

> if I admit this child inside the parent, how do bytes and authority actually move through the overlap?

The page exists because `shared below a shared folder`, `visible through parent`, `seeds the child`, and `can publish outward through the parent lane` are not the same truth.

## Core decision

Every material nested-overlap mutation must compile into one first-class **Nested-share topology review**.

The review owns:

- topology sketch
- rights floor
- seed gap
- shadow propagation consequence
- index/rescan cost
- apply verdict

## Fixed page order

1. requested overlap topology
2. rights floor card
3. seed-gap matrix
4. shadow propagation card
5. cost card
6. apply verdict

### 1) Requested overlap topology

Show:

- parent subject
- child subject
- origin seat
- other parent peers
- other child peers
- strongest safe pre-apply sentence
- stronger rejected sentence

### 2) Rights floor card

Show:

- parent permission requirement
- child permission requirement
- weakest permission observed
- overlap verdict (`eligible`, `blocked by permission floor`, `unknown`)

### 3) Seed-gap matrix

Minimum rows:

- parent owner/RW peer → parent peer
- child owner/RW peer → child peer
- parent-only peer → child-only peer
- child-only peer → parent-only peer (through parent overlap)

Columns:

- direct seed authority
- indirect arrival possibility
- prerequisite present
- notes

### 4) Shadow propagation card

Possible explicit outcomes:

- `child changes stay inside child cohort`
- `child changes also surface to parent peers through the parent subject`
- `parent peers can observe bytes but do not become child seeders`
- `overlap truth unknown`

The operator must be able to answer:

> who can actually seed this child subject, and who merely receives the consequence of overlap?

### 5) Cost card

Show:

- child subtree indexed once or twice
- child subtree rescanned once or twice
- heavy-load warning for the origin seat
- evidence source

### 6) Apply verdict

Possible outcomes:

- `apply nested overlap`
- `apply with heavy-load and seed-gap warning`
- `block; permission floor not met`
- `cancel and reopen overlap contract sheet`

## Rules

### Rule 1 — seed authority and shadow delivery may not collapse

The page must keep `Peer2 eventually gets B through A` separate from `Peer2 is a seeder for B as a child subject`.

### Rule 2 — overlap cost is first-class

An operator must not learn only after slowdown that a child subtree is being indexed and rescanned twice.

### Rule 3 — rights floor must be explicit

If both parent and child require RW/Owner, the page must say so plainly instead of surfacing only a later failure.
