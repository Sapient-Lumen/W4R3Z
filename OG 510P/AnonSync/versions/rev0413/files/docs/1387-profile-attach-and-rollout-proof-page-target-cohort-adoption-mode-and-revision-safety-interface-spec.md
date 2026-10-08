# Profile attach and rollout proof page — target cohort, adoption mode, and revision safety

## Purpose

This page answers the pre-commit mutation question for reusable policy:

> if I bind these subjects to this profile or roll them forward to a new profile revision, which subjects will change, what adoption mode will each one enter, and which worlds or fields remain excluded?

## Core decision

Every serious profile attachment or revision rollout must compile into one **Profile attach and rollout proof** before apply.
The page owns:

- target cohort
- excluded cohort
- adoption mode per subject
- field-level pin preservation
- world-scope blocking
- activation plan
- strongest safe rollout sentence

## Fixed page order

1. rollout strip
2. target-and-exclusion card
3. adoption-mode ledger
4. field-change preview
5. activation-and-verification card
6. rollout receipt

### 1) Rollout strip

Show:

- canonical profile id
- from revision id
- to revision id
- rollout mode: `first bind`, `revision bump`, `rejoin`, `branch from live`, `unknown`
- target cohort id
- world scope
- top question being answered: `what exactly will this rollout do?`

### 2) Target-and-exclusion card

Publish explicit counts for:

- will bind live
- will remain live with partial pins
- will be converted to frozen snapshots
- will be branched
- will remain unbound
- blocked by unsupported world
- blocked by missing evidence

## Hard rule

`apply profile` may never be offered without explicit exclusion counts.

### 3) Adoption-mode ledger

For every affected subject emit one adoption mode:

- `bind live`
- `bind live with field pins preserved`
- `capture frozen snapshot`
- `branch new profile lineage`
- `rejoin existing live profile`
- `leave unbound`
- `blocked`

For each mode show:

- whether current value changes now
- whether future revisions apply automatically
- whether current world is supported
- whether any stronger adoption mode is blocked

### 4) Field-change preview

For all fields in the profile coverage list show:

- fields that will change value now
- fields already matching and remaining live
- fields already matching but remaining pinned
- fields outside profile coverage
- fields blocked by unsupported world or missing witness

### 5) Activation-and-verification card

Show for the rollout:

- activation rung per affected field family
- whether restart, reconnect, or rebind is required
- verification witness required after apply
- rollback or rejoin path
- receipts to emit on success or partial block

### 6) Rollout receipt

Emit one compact receipt with:

- profile id
- from/to revision ids
- target cohort id
- adoption-mode counts
- changed-field count
- blocked-subject count
- strongest safe rollout sentence
- blocked stronger sentence

## Copy rules

- Never say `roll out to all` unless blocked and excluded subjects are still published.
- Never let `same current value` stand in for `will adopt next revision`.
- Never convert a pinned subject into live inheritance without explicit review.
- Never silently bind unsupported worlds because the values happen to be representable there.
- Never let `update profile` hide whether this is live rollout, snapshot capture, or branch creation.

## Example strongest-safe sentence patterns

- `This rollout will bind 42 subjects live to profile rev13, preserve field pins on 5 subjects, and leave 3 service-world subjects outside scope.`
- `No values change today for these 9 subjects, but attaching them live will cause future revisions to apply automatically.`
- `These 4 rows require an explicit rejoin because they are frozen snapshots, not detached live bindings.`
- `The rollout is blocked for the mobile-local lane because the profile does not govern that parallel world.`
