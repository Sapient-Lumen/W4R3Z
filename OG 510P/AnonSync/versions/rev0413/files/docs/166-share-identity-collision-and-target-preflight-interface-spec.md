# Share-identity collision and target-preflight interface spec

## Purpose

The archive already has compare-before-bind and reconnect/repair doctrine.
What it still lacked was one explicit answer to the `already added`, `same path`, and `same share identity` seam:

> when an operator points a claim, reconnect, or import at some local directory, how does the product distinguish **path collision**, **same-subject reuse**, **artifact replay**, **stale residue**, and **illegal duplicate bind** before anything mutates?

Current Resilio troubleshooting keeps this seam concrete.
A folder may already be tracked at the same path, or the same share identity may already be bound somewhere else on the device.
That is real operational truth.
AnonSync should expose it as first-class preflight, not an error after the fact.

## Core decision

Every bind-like action must pass through a fixed **target preflight**.
The preflight classifies collision type before any path is created, reused, rebound, or rejected.

The operator should never receive one generic `already added` verdict when the real possibilities are materially different.

## Collision classes

The preflight must classify at least these cases:

### 1) Empty safe target

No existing binding, no conflicting material, no identity markers, no custody ambiguity.
This may proceed with ordinary bind review.

### 2) Same path already bound to another subject

The chosen directory is already under active custody for a different subject.
This is not a merge prompt.
It is a collision.

### 3) Same subject already bound elsewhere on this seat

The incoming subject or artifact refers to a subject already known locally at another path.
This may indicate:

- reconnect to existing bind
- alternate-path attempt for same subject
- stale duplicate invite
- accidental duplicate bind attempt

### 4) Same subject markers already present in this target

The target contains strong lineage evidence for the same subject.
This may be a reconnect, rebind, or recovery case rather than a new bind.

### 5) Non-empty target with unrelated bytes

The target is not empty and current bytes do not yet prove same-lineage reuse.
This requires compare review.

### 6) Stale residue only

The target contains old lineage or state residue from a prior subject that is no longer live here.
This may be reclaimable, but only with explicit cleanup or re-adoption review.

### 7) Illegal recursive or ancestor/descendant target

The chosen target would create a loop, shadow, or parent/child overlap with an existing bound subject or derivative.
This must fail before bind.

## The fixed preflight order

Every target preflight should render sections in the same order:

1. **What you are trying to bind**
2. **What this path already means locally**
3. **Strongest collision class**
4. **Evidence that supports the classification**
5. **Safe next actions**
6. **What must not happen automatically**

## 1) What you are trying to bind

Show:

- subject label and stable handle
- artifact or claim identity
- acting seat
- whether this is new bind, reconnect, rebind, adopt, import, or repair

This prevents later confusion where the operator no longer knows whether the preflight is about a new share or a known subject returning.

## 2) What this path already means locally

Show:

- whether the exact path is already under custody
- whether ancestor or descendant paths are already under custody
- whether lineage markers for some subject are present
- whether the path is empty, lightly occupied, or non-empty
- whether any existing material appears to belong to the same subject, another subject, or an unknown one

This section should answer `what is already true here before we do anything?`

## 3) Strongest collision class

The preflight must choose one primary class and may show secondary findings.
Examples:

- `safe empty target`
- `same-subject rebind candidate`
- `same-subject duplicate bind risk`
- `different-subject custody collision`
- `stale residue requires cleanup or reclaim`
- `recursive topology not allowed`

The operator should not have to interpret several raw flags and guess which one matters most.

## 4) Evidence that supports the classification

Evidence may include:

- active local binding records
- lineage markers or service-state proofs
- prior bind receipts
- artifact/claim identity already seen on this seat
- directory occupancy summary
- ancestor/descendant overlap detection

The important thing is that the product shows *why* it believes this is a duplicate, reuse, or collision.

## 5) Safe next actions

Good actions include:

- `Open existing binding`
- `Compare and rebind`
- `Review duplicate-claim history`
- `Choose another target`
- `Inspect stale residue`
- `Clean residue and retry`
- `Abort`

Poor actions include:

- `Try anyway`
- `Connect again`
- `Create (1)`

when those labels would merely push the collision downstream.

## 6) What must not happen automatically

The preflight should explicitly forbid:

- creating a sibling duplicate path merely because the preferred path is busy
- silently treating same-subject duplicate attempts as harmless
- silently merging unrelated bytes into a tracked subject
- erasing residue before the operator has seen what it means
- turning a same-machine derivative into a recursive topology

## Duplicate artifact handling

If the same offer or claim artifact has already been processed on this seat, the preflight should say so.
Possible outcomes:

- already consumed and bound here
- already rejected here
- already drafted but not yet applied
- refers to same subject as another active bind

Artifact replay is not the same as safe reconnect, and the surface should say which one it is.

## Table rules

Dense views may show chips such as:

- `safe`
- `same-subject`
- `other-subject collision`
- `stale residue`
- `recursive overlap`

Expanding the row should reveal the actual evidence and next actions.
Compactness may hide detail, not classification.

## CLI rules

CLI should support:

```text
anonsync target preflight --subject shr_docs --path ~/Docs --explain
```

The output should state:

- strongest collision class
- active local subject if any
- whether same-subject reuse is plausible
- whether bind is blocked, compare-required, or safe
- the next safe verb

## Result

A good target-preflight contract prevents five failures:

- one generic `already added` error standing in for several materially different cases
- duplicate bind attempts becoming silent sibling directories
- stale local residue being mistaken for live same-subject continuity
- recursive same-machine topologies being caught only after data movement begins
- operators losing track of whether they are reconnecting a known subject or accidentally replaying a consumed artifact

If path selection can still collapse same-subject reuse, other-subject collision, and artifact replay into one vague refusal or one duplicate folder, AnonSync has not yet made bind preflight honest enough.
