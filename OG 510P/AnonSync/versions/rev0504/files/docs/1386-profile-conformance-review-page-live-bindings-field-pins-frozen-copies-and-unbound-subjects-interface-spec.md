# Profile conformance review page — live bindings, field pins, frozen copies, and unbound subjects

## Purpose

This page answers the cohort question that one-subject profile inspection does not finish:

> across all candidate subjects, who is truly live on this profile, who only looks similar, who is partially pinned away, and who is outside the profile entirely?

## Core decision

Every serious profile audit must render one first-class **Profile conformance review**.
The page owns:

- profile-wide cohort counts
- conformance grades
- false-friend matches
- pin/freeze/branch reasons
- safe next actions

## Fixed page order

1. conformance summary strip
2. grade ledger
3. cohort buckets
4. false-friend review
5. safe action tray
6. conformance receipt

### 1) Conformance summary strip

Show:

- canonical profile id
- active revision id
- reviewed cohort id
- reviewed world scope
- total candidate subjects
- total proven live-bound subjects
- total partial/pinned subjects
- total frozen or branched subjects
- total unbound subjects
- total unknown subjects

### 2) Grade ledger

Every reviewed subject must receive exactly one top-line conformance grade:

- `full live conformance`
- `partial live conformance`
- `snapshot conformance`
- `branched conformance`
- `value-only coincidence`
- `unbound`
- `unknown`

For each grade the page must define:

- what is proven
- what is not proven
- whether next profile revision will apply
- blocked stronger sentence

## Hard rule

`value-only coincidence` may never be rendered in the same visual style as `full live conformance`.

### 3) Cohort buckets

Group the reviewed subjects into explicit buckets:

- fully live-bound
- live-bound with pinned fields
- frozen snapshots
- branched descendants
- unsupported-world subjects
- unbound but similar
- unknown or insufficient-witness subjects

For each bucket show:

- count
- representative fields causing placement
- next safe action

### 4) False-friend review

Catch at least the following misleading similarities:

- same displayed values but pinned fields
- same values from another branch revision
- same values in an unsupported world
- same values in a frozen snapshot
- same values from manual coincidence after detach
- same label but different profile id

### 5) Safe action tray

Only actions compatible with the proven grade may be offered:

- `leave live-bound`
- `pin selected fields`
- `unpin and rejoin`
- `capture snapshot`
- `branch new profile`
- `bind from unbound state`
- `exclude from profile`
- `collect more evidence`

For each action show:

- whether value changes
- whether revision adoption changes
- whether world support changes
- whether future drift remains expected

### 6) Conformance receipt

Emit one compact receipt with:

- profile id
- profile revision id
- cohort id
- subject counts by grade
- false-friend count
- offered safe actions
- strongest safe cohort sentence
- blocked stronger sentence

## Copy rules

- Never say `all subjects conform` unless no weaker bucket remains.
- Never say `same profile` when only `same visible values` is proven.
- Never hide pinned fields inside the `conformant` bucket.
- Never let frozen snapshots masquerade as live-bound subjects.
- Never allow unsupported-world rows to count as profile members.

## Example strongest-safe sentence patterns

- `Forty-eight subjects are fully live-bound to this profile revision; six more currently match values but remain outside live adoption because of field pins.`
- `Three subjects look conformant at today's values, but they are frozen snapshots and will not adopt revision rev13.`
- `This service-world cohort is similar to the profile but remains outside supported binding scope.`
- `Conformance is unknown for nine subjects because the product has not yet proven their active world or field-pin posture.`
