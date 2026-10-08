# Policy-profile contract sheet page — profile signature, field coverage, and binding class

## Purpose

This page answers the reusable-policy question that baseline comparison alone does not finish:

> what policy profile exists here, what exact fields does it govern, which subjects can bind to it, and what binding class is the focused subject in right now?

## Core decision

Every serious reusable defaults bundle must render one first-class **Policy-profile contract sheet** before bulk attachment, revision rollout, or conformance claims are offered.
The page owns:

- profile signature
- field coverage
- supported subject classes
- supported world scope
- current revision
- focused-subject binding class
- strongest safe profile sentence

## Fixed page order

1. profile strip
2. profile signature card
3. field-coverage card
4. supported-subject-and-world card
5. focused-subject binding card
6. revision-safety card
7. profile receipt

### 1) Profile strip

Show:

- canonical profile id
- profile title
- current profile revision id
- profile status: `draft`, `active`, `retired`, `superseded`, `unknown`
- focused subject id
- focused world id
- focused binding class
- top question being answered: `what profile governs this subject?`

### 2) Profile signature card

Emit one normalized signature with:

- canonical profile id
- canonical setting-family ids covered
- revision id
- author and issuance time
- allowed mutation surfaces
- allowed activation rungs
- witness confidence

## Hard rule

A profile may not be identified only by:

- a UI section title
- a remembered settings cluster
- a screenshot of current values
- `the defaults we usually use`

If the operator started from any of those, the page must resolve them to one canonical profile id first.

### 3) Field-coverage card

List every field the profile explicitly governs.
For each field show:

- canonical field id
- target value state
- whether inheritance is part of the field contract
- activation rung
- unsupported surfaces/worlds
- stronger sentence blocked if witness is incomplete

## Hard rule

Anything not listed in field coverage is **outside the profile**.
The page must never imply that a profile governs nearby settings by vibe, menu adjacency, or prior operator memory.

### 4) Supported-subject-and-world card

Show where the profile is allowed to bind:

- supported subject classes
- supported world classes
- excluded subject classes
- excluded world classes
- known parallel lanes
- required prerequisites for attachment

Examples of world classes include:

- interactive desktop world
- service world
- config-authored world
- mobile-local share lane
- linked-family arrival lane

### 5) Focused-subject binding card

For the focused subject render exactly one binding class:

- `live-inherit`
- `field-pin`
- `frozen-snapshot`
- `branched-profile`
- `unbound`
- `unknown`

For the chosen class show:

- what is proven
- which fields are still live to profile revisions
- which fields are pinned away
- whether current value coincidence is misleading
- what stronger class remains blocked

## Hard rule

`same visible values as profile` may never overclaim `live-inherit`.

### 6) Revision-safety card

Show what a future profile revision would do to this focused subject:

- `auto-adopts next revision`
- `adopts only unpinned fields`
- `never changes until explicit rebind`
- `belongs to another branch`
- `outside supported world`
- `unknown`

### 7) Profile receipt

Emit one compact receipt with:

- profile id
- profile revision id
- focused subject id
- field coverage count
- focused binding class
- next-revision adoption posture
- strongest safe profile sentence
- blocked stronger sentence

## Copy rules

- Never say `on profile` unless a binding class stronger than `unbound` is proven.
- Never say `inherits this profile` when the subject is only value-equal.
- Never say `same defaults` unless the field-coverage contract actually matches.
- Never say `profile governs this world` unless world scope is explicitly listed.
- Never let `all the usual settings` stand in for the coverage list.

## Example strongest-safe sentence patterns

- `This subject currently matches the profile's visible values, but it is a frozen snapshot and will not adopt later profile revisions.`
- `This subject is live-bound to profile rev12 for covered fields, while two explicitly pinned fields remain outside live inheritance.`
- `The profile governs desktop interactive worlds only; this service world remains outside supported scope.`
- `No canonical policy profile has yet been proven for this subject, even though several nearby defaults currently coincide.`
