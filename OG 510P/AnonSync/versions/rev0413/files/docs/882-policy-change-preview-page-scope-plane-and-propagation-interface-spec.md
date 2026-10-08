# Policy change preview page: scope, plane, and propagation interface spec

## Purpose

This page answers one ordinary question:

> if I change this policy now, which control plane am I editing, what cohort will feel it, and which subjects remain explicit exceptions?

The page exists because changing a share-local value, a standing default, and a config-owned rule are not the same action.

## Core decision

Any serious policy edit must pass through a first-class **Policy change preview** page before commit.
The preview owns:

- target field family
- target control plane
- blast radius
- exception handling
- supersession effect
- strongest safe sentence after commit

## Fixed page order

1. requested-change strip
2. target-plane card
3. propagation card
4. exception-preservation card
5. conflict / lock card
6. commit boundary card

### 1) Requested-change strip

Show:

- current effective value
- requested new value
- target subject or cohort
- current source plane
- strongest next-safe action

### 2) Target-plane card

One of the following must be selected explicitly:

- `subject-local override`
- `standing default edit`
- `future-arrivals default edit`
- `configuration-plane edit`
- `temporary reviewed exception`
- `blocked from this surface`

This card must explain why the chosen plane is the real one being edited.

### 3) Propagation card

Publish the exact blast radius:

- this subject only
- all currently inheriting subjects
- future arrivals only
- config-owned cohort on next activation
- explicit exceptions unaffected
- siblings requiring separate review

The operator must see examples of affected and unaffected subjects before commit.

### 4) Exception-preservation card

Show whether the change will:

- create a new exception
- clear an existing exception
- leave legacy exceptions in place
- force drift review because the cohort will still diverge afterward

### 5) Conflict / lock card

Publish blockers such as:

- config-owned lock
- narrower derivative ceiling
- reviewed danger barrier required
- stale receipt / freshness expiry
- blocked because current surface is read-only for this plane

### 6) Commit boundary card

End with one clear outcome:

- `change this subject`
- `change inheriting cohort`
- `change future default`
- `open config-plane workflow`
- `review drift first`
- `blocked`

## Rules

### Rule 1 — preview the plane, not just the value delta

`Turn relay off` or `Set Synced` is insufficient.
The operator must know which plane is actually being edited.

### Rule 2 — propagation must be concrete

The preview must name touched subjects, untouched exceptions, and future-only effects before commit.

### Rule 3 — locks must explain source-of-truth ownership

A config-owned or derivative-locked field cannot merely say `unavailable`.
It must say which stronger plane owns the truth.

## Acceptance criteria

A later operator can:

- tell which control plane is being changed
- tell which subjects change now and which do not
- tell whether the action creates or clears drift
- tell whether a different workflow is required because this surface is not the source of truth
