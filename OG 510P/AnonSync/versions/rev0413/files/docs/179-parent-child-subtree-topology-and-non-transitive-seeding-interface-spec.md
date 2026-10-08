# Parent-child subtree topology and non-transitive seeding interface spec

## Purpose

The archive already had overlap containment, local derivation, and graph-aware flows.
What it still lacked was one dedicated interface contract for the deceptively simple request:

> can I share a child subtree separately without pretending it is just another ordinary subject?

Current Resilio docs sharpen this seam.
They still say nested sharing is possible only with limitations: parent and child must both have Read & Write or Owner permissions, both become separate sync folders, the child gets indexed and rescanned twice, parent peers do not seed data to peers that only have the child, and both parent and child must have Selective Sync disabled.
That is candid and useful.
It also proves nested subtree sharing is a graph decision, not an ordinary share action.

## Core decision

Creating or accepting a child subject inside a parent subject must always open a first-class **topology review**.
The product should never flatten `share this subfolder too` into a generic publish flow.

The review must classify at least these truths:

1. **Graph shape**
2. **Indexing and rescan cost**
3. **Propagation boundaries**
4. **Materialization constraints**
5. **Dependent fallout on parent and child**

## Why this matters

Current Resilio docs still reveal four truths AnonSync should not clone:

- child subtree sharing is a separate sync subject, not a lightweight alias
- the shared machine can pay duplicate indexing/rescan cost
- parent-only peers are not equivalent seeders for child-only peers
- changes arriving through the child can still propagate onward via the parent graph

That is not a corner-case implementation detail.
It is core topology truth that deserves one visible page.

## The topology review page

Every nested-subtree decision should render sections in this order:

1. **Graph preview**
2. **Propagation matrix**
3. **Cost and custody**
4. **Admissibility rules**
5. **Receipt promise**

### 1) Graph preview

Show:

- parent subject
- candidate child subject path
- members of parent and child
- which member is shared between them
- whether the child already exists as its own subject
- whether the proposal would create overlap, loop risk, or duplicate bind

The operator should be able to answer:

> what exact graph am I creating if I accept this child subtree as a separate subject?

### 2) Propagation matrix

Show explicitly:

- who can seed parent bytes
- who can seed child bytes
- whether parent-only peers can satisfy child-only demand
- whether child-originated mutations will later propagate into parent peers through shared members
- which flows are direct, transitive, or impossible

This is the heart of the review.
The page must make non-transitive seeding and onward propagation legible in one place.

### 3) Cost and custody

Show:

- duplicate indexing/rescan burden on shared members
- local storage duplication or lineage reuse
- custody concentration on the shared bridge member
- whether the bridge member becomes a required transit point for some flows

Operators should not discover after the fact that one NAS or laptop silently became the topology hinge.

### 4) Admissibility rules

The review must classify the proposal as:

- `ordinary child derivation`
- `bridge-required subtree`
- `overlap-risk child`
- `illegal loop or ancestor/descendant bind`
- `blocked due to materialization/posture conflict`

It should also show any constraints such as:

- selective materialization or observer-only posture not admissible for this graph
- source-right ceiling for the child
- requirement that the shared bridge member stay healthy for some paths to converge

### 5) Receipt promise

The resulting receipt must prove:

- graph shape accepted
- bridge members
- non-transitive seeding boundaries acknowledged
- indexing/cost warning accepted
- admissibility constraints applied
- whether the child is independent, transit-bound, or blocked

## What must never happen automatically

The product must never automatically:

- flatten nested subtree sharing into a generic `share subfolder` action
- imply parent peers can seed child-only peers when they cannot
- hide duplicate indexing/rescan cost on the shared bridge member
- allow ancestor/descendant loops or ambiguous overlap through convenience defaults

## Why this is worth the trouble

Nested subtree sharing is useful, but it is not ordinary.
AnonSync can keep it powerful without copying the caveat-driven model by making topology, propagation, cost, and admissibility visible before apply.
