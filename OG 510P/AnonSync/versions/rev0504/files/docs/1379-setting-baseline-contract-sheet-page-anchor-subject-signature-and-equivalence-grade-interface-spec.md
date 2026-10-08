# Setting-baseline contract sheet page — anchor, subject signature, and equivalence grade

## Purpose

This page answers the comparison question that locator and impact pages do not finish:

> what exact baseline am I comparing against, which subject is actually under review, and what grade of sameness is honestly proven here?

## Core decision

Every serious settings comparison must render one first-class **Setting-baseline contract sheet** before any batch realignment is offered.
The page owns:

- baseline anchor
- canonical subject identity
- normalized governance signature
- equality grade
- false-friend warning
- allowed realignment actions
- strongest safe comparison sentence

## Fixed page order

1. comparison strip
2. baseline anchor card
3. subject signature card
4. equality-grade card
5. divergence ledger
6. realignment action card
7. comparison receipt

### 1) Comparison strip

Show:

- canonical setting id
- focused subject id
- comparison baseline id
- current world id
- current visible value
- baseline target value
- comparison mode: `single-subject`, `side-by-side`, `batch-audit`, `pre-realignment`, `unknown`
- strongest question being answered: `do these actually match?`

### 2) Baseline anchor card

Show exactly what the baseline is anchored to:

- canonical setting object
- canonical subject class or explicit cohort
- world scope
- authority lane
- baseline revision id
- baseline author and time

## Hard rule

A baseline may not be anchored only to:

- display label
- menu route
- custom share name
- current folder title in one UI surface

If any of those are used for navigation, the page must also show the canonical anchor they resolve to.

### 3) Subject signature card

For the focused subject emit one normalized signature with the following fields:

- canonical subject id
- local display label
- disk/path anchor if relevant
- world id
- value state
- inheritance / override state
- authority lane
- activation rung
- witness confidence

### 4) Equality-grade card

Render exactly one top-line grade and all weaker grades beneath it.
Supported grades:

- `label match only`
- `visible value match`
- `effective value match now`
- `governance-signature match`
- `baseline-conformant`
- `unknown`

For each grade show:

- what is proven
- what is not proven
- which stronger grade remains blocked

## Hard rule

`visible value match` may never overclaim `governance-signature match`.

### 5) Divergence ledger

List every reason the subject is not fully baseline-conformant.
Allowed reasons include:

- `manual override diverges`
- `detached but value currently matches`
- `explicit none vs inherit`
- `parallel mobile-local lane`
- `startup-config world differs`
- `service-world fork differs`
- `subject label is only a local alias`
- `insufficient witness`

### 6) Realignment action card

Only offer actions compatible with the proven grade.
Possible actions:

- `leave as-is`
- `change explicit value`
- `restore inheritance`
- `preserve explicit override`
- `adopt baseline in current world only`
- `fork new baseline branch`
- `re-anchor subject identity`
- `collect more evidence`

For every offered action show:

- exact semantic change
- whether governance state changes or only visible value changes
- whether detached state is preserved or removed
- whether another world remains unchanged

### 7) Comparison receipt

Emit one compact receipt with:

- baseline id
- subject id
- equivalence grade
- divergence count
- safe realignment options
- strongest safe comparison sentence
- blocked stronger sentence

## Copy rules

- Never say `matches baseline` unless governance-signature match is proven.
- Never say `same setting` when only the display label matches.
- Never say `same as default` when the subject is merely detached-but-coincidentally-equal.
- Never use a custom share name as the only subject anchor.
- Never offer `align all` before publishing divergence reasons.

## Example strongest-safe sentence patterns

- `This share currently shows the same priority as the baseline, but it remains manually detached from future default changes.`
- `These two rows refer to the same canonical setting but different worlds, so only visible-value equality is proven.`
- `The local alias matches the baseline label, but canonical subject identity is not yet proven.`
- `This subject is fully baseline-conformant: value, inheritance state, authority lane, and world all match.`
