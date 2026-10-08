# Setting-impact contract sheet page — target cohort, detached overrides, and inherit vs explicit none

## Purpose

This page answers the second settings question that the locator page does not finish:

> if I change this setting from here, exactly which subjects will change, which subjects are protected exceptions, and is the visible value inherited or explicit?

## Core decision

Every meaningful settings mutation must render one first-class **Setting-impact contract sheet** before commit.
The page owns:

- intended mutation
- target cohort
- detached exceptions
- parallel untouched lanes
- inherit-vs-explicit-none state
- activation effect
- strongest safe impact sentence

## Fixed page order

1. setting / mutation strip
2. target cohort card
3. exception ledger
4. inheritance state card
5. world and parallel-lane card
6. activation / adoption card
7. commit receipt

### 1) Setting / mutation strip

Show:

- canonical setting id
- current surface
- current value for the focused subject
- proposed value
- mutation class: `change-default`, `create-override`, `edit-override`, `reattach-to-inheritance`, `explicit-none`, `world-config-edit`, `unknown`
- strongest question being answered: `who changes?`

### 2) Target cohort card

Show one explicit cohort summary:

- `will change now`: exact subjects reached by the mutation
- `will change after activation`: exact subjects waiting on rescan/restart/cutover
- `future joins inherit this`: subjects not yet present but governed by the changed default
- `outside cohort`: visible but not governed subjects

Render the cohort as a matrix with one row per subject class:

- current focused share
- inheriting desktop shares
- manually detached desktop shares
- mobile-local shares
- startup-owned config subjects
- service-world subjects
- successor / imported worlds

For each row show:

- count
- why included or excluded
- whether operator can inspect the member list
- whether batch preview is complete or sampled only

### 3) Exception ledger

This is mandatory whenever the target is not universal.
Show:

- detached overrides that will not change
- blocked subjects requiring reattach
- unknown-membership subjects
- route-incompatible subjects
- world-incompatible subjects

Every row needs a reason string such as:

- `manually detached from global default`
- `parallel mobile-local setting`
- `startup-owned in sync.conf`
- `different service world`
- `insufficient proof`

### 4) Inheritance state card

This card exists to kill the most dangerous ambiguity.
For the focused subject show exactly one of:

- `inherits current default`
- `explicit override = <value>`
- `explicit none/off`
- `detached but current value matches default by coincidence`
- `unknown`

## Hard rule

`Inherit` and `explicit none/off` must never share one visual state.
If both can display as `None`, the page must show a secondary state label and explanation.

### 5) World and parallel-lane card

Show whether the mutation reaches:

- only the current share
- all inheriting shares in the current world
- current device only
- startup-owned next boot world
- current service world only
- migrated successor world
- clean-install forked world

Also show which same-looking surfaces are merely parallel and unaffected.

### 6) Activation / adoption card

Show:

- activation rung for the included cohort
- whether excluded subjects remain excluded after activation
- whether a reattach event is required before later default shifts can reach detached subjects

### 7) Commit receipt

Emit one compact receipt with:

- canonical setting id
- mutation class
- included subject count
- excluded subject count
- detached exception count
- inherit-vs-explicit state verdict
- activation rung
- strongest safe impact sentence
- blocked stronger sentence

## Copy rules

- Never say `apply to all` unless the member list is explicit.
- Never say `global change` if detached exceptions exist.
- Never say `same visible value` means `same inheritance state`.
- Never say `None` means `inherit`.
- Never say `future shares` are covered unless the default lane is the actual owner.

## Example strongest-safe sentence patterns

- `This change will reach 24 inheriting shares in the current desktop world; 3 detached shares remain unchanged.`
- `This share is explicitly set to no prioritization; it is not inheriting the global default.`
- `This edit changes startup-owned config for the next boot world only.`
- `This default shift does not reach the service world until that world is explicitly migrated or edited.`