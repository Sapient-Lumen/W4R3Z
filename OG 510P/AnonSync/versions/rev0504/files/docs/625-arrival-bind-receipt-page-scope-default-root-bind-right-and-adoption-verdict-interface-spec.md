# Arrival bind receipt page — scope, default root, bind right, and adoption verdict interface spec

## Purpose

Produce durable proof for a reviewed arrival or reconnect bind decision.
The receipt should let a later operator answer, without reopening folklore:

- what seat default was in force
- what candidate path was suggested and why
- whether the operator exercised one-share manual bind right
- whether an existing directory was adopted, rejected, or left unresolved
- whether future defaults changed or remained untouched

## Inputs

- receipt identifier
- share identifier
- seat identifier
- reviewed scope
- seat default snapshot
- suggested path and suggestion source
- manual-bind-right verdict
- chosen action
- adoption verdict (`not-needed`, `adopted`, `rejected`, `compare-required`, `blocked`)
- duplicate-veto verdict
- resulting byte posture
- strongest safe sentence
- stronger forbidden sentence
- timestamp and actor

## Layout

### A. Receipt summary strip

Fields:

- share label
- seat label
- chosen action
- resulting path
- future-default impact sentence
- strongest safe sentence

Example:

- `Projects-2026 bound at /srv/projects/Projects-2026; seat default /srv/incoming unchanged.`
- `Photos-2026 left unbound after adoption review; duplicate-suffix creation vetoed.`

### B. Standing-default snapshot card

Show:

- reviewed scope
- visibility/materialization default in force at decision time
- default root/template in force at decision time
- whether those defaults changed as part of this review

### C. Bind-right card

Show:

- whether manual bind right was available
- whether the operator exercised it
- whether the bind consumed the seat suggestion or overrode it
- whether the current share remained the only object changed

### D. Candidate-path card

Show:

- suggested path
- suggestion source
- chosen path
- whether the chosen path matched the suggestion, overrode it, or restored a prior bind

### E. Adoption-verdict card

Show:

- whether an existing directory was inspected
- occupancy class
- lineage evidence grade
- final adoption verdict
- duplicate-veto verdict

### F. Resulting-state card

Show:

- resulting bind state
- resulting byte posture
- any remaining compare debt or follow-up requirement
- next honest action after receipt

### G. Claim-ceiling card

Show together:

- strongest approved sentence
- stronger forbidden sentence
- blocker basis at decision time

## Compact receipt row contract

A truthful compact receipt row should preserve this order:

1. share
2. chosen action
3. resulting path
4. defaults changed? yes/no
5. adoption verdict
6. next honest action

Example:

```text
Photos-2026    left unbound    none    defaults changed: no    compare-required / suffix veto    Re-open adoption review
```

## Success criteria

A good receipt lets a later operator answer:

1. what standing default was in force
2. whether one-share bind right was exercised
3. what path was suggested and which path won
4. whether an existing directory was adopted or rejected
5. whether future defaults changed or stayed untouched
