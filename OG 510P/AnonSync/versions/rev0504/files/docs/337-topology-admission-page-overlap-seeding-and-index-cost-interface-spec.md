# Topology admission page: overlap, seeding, and index cost interface spec

The archive already has overlap-containment doctrine, same-host derivation doctrine, and pre-existing-material review.
What it still lacked was one ordinary page for the most common operator question before a new bind lands:

> what topology am I about to create, who will actually seed whom, and what extra index/load cost am I buying if I let parent and child coexist?

Current Resilio docs still make this seam obvious enough to justify a replacement page.
They say nested shares are possible, but only with specific permission levels and with Selective Sync disabled on both sides; they say peers holding only the parent do not seed peers holding only the child; and they say the shared child can be rescanned twice and still piggyback onward through the parent.
That is exactly the kind of truth a product should own on one page.

## Page promise

The Topology admission page should make five answers adjacent:

1. candidate relation now
2. propagation and seeding route now
3. indexing/load side effect now
4. strongest honest admission verdict now
5. strongest honest next action

The page exists so the operator no longer has to reconstruct graph shape from path strings and caveat prose.

## Fixed page order

Every topology admission page should render the same sections in the same order:

1. **Candidate snapshot**
2. **Relation and overlap proof**
3. **Propagation and seeding truth**
4. **Index/load and mode constraints**
5. **Admissible actions**
6. **Receipt promise**

### 1) Candidate snapshot

This section should show:

- candidate target path or subject
- incumbent parent, child, sibling, or duplicate bind nearby
- whether this is `new disjoint share`, `child share`, `same-host edge`, `safe rebind`, or `conflicting duplicate`
- whether the page is evaluating one proposed edge or a larger overlap family

The operator should be able to answer: **what topology proposal am I looking at?**

### 2) Relation and overlap proof

This section should show:

- path containment proof (`disjoint`, `child-of`, `parent-of`, `same-root duplicate`, `ambiguous provider path`)
- identity proof if existing `.sync`/subject ID evidence already binds the path elsewhere
- whether the proposal is harmless reuse, warning-tier overlap, or illegal duplicate bind
- whether any existing provider abstraction hides the real containment boundary

The operator should be able to answer: **why does the product believe this relation is what it says it is?**

### 3) Propagation and seeding truth

This section should show:

- who seeds the candidate directly
- whether propagation will piggyback through a parent share rather than direct child-to-child seeding
- whether the proposed topology creates a self-only edge, a parent-mediated edge, or ordinary peer participation
- whether a peer subset will see the same bytes twice under different graph subjects

The operator should be able to answer: **how will bytes actually move if I accept this?**

### 4) Index/load and mode constraints

This section should show:

- whether indexing/rescan will duplicate work for any subtree
- whether Selective Sync, disconnected posture, or placeholder-heavy state blocks honest admission
- whether the proposal narrows performance, increases rescan cost, or creates misleading completeness expectations
- whether the most relevant cost is CPU, watcher budget, delayed propagation, or operator confusion

The operator should be able to answer: **what extra cost or constraint comes with this topology?**

### 5) Admissible actions

Example actions:

- `Accept as disjoint share`
- `Accept child share with stated extra cost`
- `Convert to local edge instead`
- `Reuse existing bind`
- `Reject duplicate bind`
- `Flatten by keeping only parent` or `Flatten by keeping only child`

The primary action should be the safest truthful action, not the shortest label.

### 6) Receipt promise

A topology-admission receipt should preserve:

- candidate relation reviewed
- overlap/identity proof used
- seeding and propagation verdict
- index/load side effects acknowledged
- chosen action or rejection
- whether any later follow-up was required

The operator should be able to answer: **what later evidence will prove what topology was admitted and why?**

## Compact admission row contract

A trustworthy compact admission row should preserve the following order:

1. candidate subject
2. relation phrase
3. seeding phrase
4. strongest blocker or cost
5. next honest action

Example:

```text
B under A   child share, parent still propagates onward   direct seeding only from source peer   extra cost: subtree indexed twice, selective sync not admissible   Review
```

## What this page must never imply

The page must never imply that:

- a child share is just another disjoint share
- path containment alone explains seeding behavior
- duplicate bind and safe rebind are the same fact
- parent visibility proves child-only peers can seed each other directly
- `Add` or `Connect` is an adequate explanation of graph creation

## Result

This page is how AnonSync borrows Resilio's topology candor without cloning the weaker habit of hiding one graph answer across nested-share FAQs, duplicate-bind warnings, and separate pre-populated-folder articles.
