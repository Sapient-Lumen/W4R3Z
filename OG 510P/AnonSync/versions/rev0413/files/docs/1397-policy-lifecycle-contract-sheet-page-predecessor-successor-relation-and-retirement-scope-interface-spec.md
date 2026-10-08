# Policy-lifecycle contract sheet page — predecessor, successor, relation, and retirement scope

## Purpose

This page answers the lifecycle question that profile binding and waivers still do not finish:

> we have a new policy candidate now — what exactly is replacing what, what relation class is this, what subjects are in scope, and what would retiring the predecessor actually mean?

## Core decision

Every serious policy promotion, replacement, split, merge, rollback, or sunset must render one first-class **Policy-lifecycle contract sheet** before the product allows `make current`, `replace default`, `deprecate old`, or `retire` language.
The page owns:

- predecessor identity
- successor identity
- relation class
- scope of replacement
- waiver carry-forward rule
- retirement consequence
- strongest safe lifecycle sentence

## Fixed page order

1. family strip
2. predecessor card
3. successor card
4. relation-class card
5. scope-and-coverage card
6. waiver-carry-forward card
7. retirement consequence card
8. lifecycle receipt

### 1) Family strip

Show:

- canonical policy family id
- focused predecessor id and revision
- focused successor id and revision
- lifecycle action: `publish`, `promote`, `deprecate`, `split`, `merge`, `rollback`, `sunset`, `unknown`
- status: `draft`, `proposed`, `active`, `blocked`, `retired`, `rolled-back`, `unknown`
- top question being answered: `what exactly is replacing what?`

### 2) Predecessor card

Show the old contract clearly:

- predecessor profile id
- predecessor revision
- supported worlds
- live bound subject count
- active waiver count
- retirement eligibility
- strongest safe sentence about the predecessor now

## Hard rule

The page may not let `old defaults` stand in for a canonical predecessor object.

### 3) Successor card

Show the proposed new contract:

- successor profile id
- successor revision
- supported worlds
- field coverage delta versus predecessor
- prerequisite delta
- expected subject reach
- activation posture

## Hard rule

The page may not call a successor `current` until its relation class and coverage delta are explicitly computed.

### 4) Relation-class card

Render exactly one top-line relation:

- `in-place-revision`
- `compatible-successor`
- `split-successor`
- `merged-successor`
- `world-specific-successor`
- `rollback-successor`
- `sunset-no-successor`
- `unknown`

For the chosen class show:

- what is preserved
- what is not preserved
- whether subject movement is automatic, optional, blocked, or impossible
- stronger sentence blocked

## Hard rule

`deprecated` may never stand in for a relation class.
`Deprecated` is a status, not the shape of replacement.

### 5) Scope-and-coverage card

List exactly what the lifecycle action covers:

- worlds included
- worlds excluded
- field families included
- field families dropped
- subject classes expected to move
- subject classes expected to remain
- orphan risk

## Hard rule

Anything not listed in scope stays outside the lifecycle action.
The page must not let a family-level promotion silently overclaim subject or world coverage.

### 6) Waiver-carry-forward card

For every active waiver class in scope, show one verdict:

- `carry-forward`
- `re-prove-on-successor`
- `resolved-by-successor`
- `split-by-field-or-world`
- `blocks-retirement`
- `unknown`

Also show:

- affected waiver ids
- owner count
- rereview debt after promotion
- strongest safe sentence about waiver migration

## Hard rule

Waivers never carry forward by implication.
The page must issue a verdict for every active waiver family in scope.

### 7) Retirement consequence card

Show what retiring the predecessor would do:

- subjects that would still remain bound
- grandfathered subjects
- blocked subjects
- subjects that would become orphaned
- receipt and audit preservation class
- rollback availability
- last safe retirement moment

## Hard rule

The product may not offer `retire predecessor` if any still-bound subject lacks an explicit destination posture.

### 8) Lifecycle receipt

Emit one compact receipt with:

- family id
- predecessor id
- successor id
- relation class
- subject coverage summary
- waiver migration summary
- retirement verdict
- rollback class
- strongest safe lifecycle sentence
- blocked stronger sentence

## Copy rules

- Never say `new default` without naming predecessor and successor.
- Never say `deprecated` when the truer sentence is `retired` or `still current but discouraged`.
- Never say `everything moved` unless every subject posture is resolved.
- Never say `same policy, just newer` when field coverage, world scope, or prerequisite burden changed.
- Never say `rollback available` unless the predecessor still has preserved receipts and an allowed rebind path.

## Example strongest-safe sentence patterns

- `This is a compatible-successor promotion: most predecessor-bound subjects can adopt the new revision, but active migration-gap waivers must be re-proven before predecessor retirement.`
- `This is a world-specific-successor only: desktop and service-subjects can move, while mobile-local lanes stay outside successor scope and remain on the deprecated predecessor.`
- `This is a sunset-no-successor action: the predecessor is being retired without a replacement, so currently bound subjects will become explicitly orphaned unless detached first.`
- `This is a rollback-successor: the newer profile remains historically recorded, but the predecessor revision becomes current again for the covered cohort.`

