# Byte-action review — local evict vs global delete and last-copy proof interface spec

## Purpose

The archive already has fetchability, availability, and observer posture language.
What it still lacked was one explicit page for the dangerous seam where several superficially similar gestures diverge sharply:

> am I only removing local bytes, reverting to placeholder/names-only state, disconnecting local presence, or actually deleting the object for everyone?

This page exists so convenience gestures do not blur local dematerialization and global destruction.

## Core rule

Any action that changes byte residency or object existence must first classify itself into one of four families:

1. `keep object, keep local bytes`
2. `keep object, remove local bytes`
3. `keep object, remove local presence`
4. `remove object everywhere`

The product may use shorter labels in dense surfaces.
It may not let those families collapse into one overloaded `remove` or shell gesture.

## Fixed review order

Every serious byte-action review should render the same sections in the same order:

1. **Requested action family**
2. **Current byte and witness truth**
3. **Resulting visibility/presence after apply**
4. **Blocked and safer alternatives**
5. **Receipt and recovery promise**

### 1) Requested action family

This section should answer:

- exact path or subtree under review
- whether the operator requested local evict, revert to placeholder, disconnect local presence, or delete everywhere
- whether the scope is single object or mixed subtree

The operator must be able to answer: **what family of action am I actually about to perform?**

### 2) Current byte and witness truth

This section should show:

- current local byte posture
- current visibility posture after apply would differ how
- who still witnesses full bytes
- whether this seat is the last confirmed full-copy witness
- whether history/Archive remains a recovery path

The operator must be able to answer: **what bytes survive elsewhere if I proceed?**

### 3) Resulting visibility/presence after apply

This section should show the predicted after-state:

- `full visible`
- `placeholder visible`
- `names only`
- `locally absent but still shared`
- `removed everywhere`

The operator must be able to answer: **what will remain visible here, and what will still exist elsewhere?**

### 4) Blocked and safer alternatives

This section should list:

- blocked action because of last-copy risk
- downgrade to safer local-only alternative
- `pin elsewhere first`
- `create witness first`
- `restore path before delete`

The operator must be able to answer: **what is the safest honest action if the requested one is too dangerous?**

### 5) Receipt and recovery promise

This section should show:

- which action family was actually applied
- witness truth at apply time
- whether recoverability remained `fetchable`, `history-backed`, `uncertain`, or `none promised`
- any required follow-up such as `create witness within 24h`

## States

Use a small stable vocabulary:

- `local-preserving`
- `local-evict`
- `presence-drop`
- `global-destroy`
- `blocked-last-copy`
- `history-guarded`

## Main surface

A compact **Byte action** card should show:

- action family requested
- current witness summary
- resulting after-state summary
- primary action or block reason

## Detailed surface

The detailed page should provide five panes.

### Pane A — Requested action strip

Shows:

- requested verb family
- path count
- danger class
- whether review is mandatory

### Pane B — Witness matrix

Columns:

- path
- local bytes now
- remote witnesses
- history backing
- last-copy risk

### Pane C — After-state preview

Columns:

- path
- local visibility after apply
- local bytes after apply
- remote existence after apply
- recovery class after apply

### Pane D — Alternatives

Rows may include:

- `Evict locally instead`
- `Disconnect locally instead`
- `Create witness on seat X`
- `Restore candidate first`
- `Retire stale announcement instead`

### Pane E — Receipts

Shows:

- byte-action receipts
- witness snapshots
- follow-up obligations

## CLI parity

Minimum commands:

- `anonsync byte-action review <subject> <path>`
- `anonsync byte-action simulate <subject> <path> --action <family>`
- `anonsync byte-action apply <review-id>`
- `anonsync byte-action receipt <receipt-id>`

## Acceptance criteria

A user can:

- tell the difference between local byte eviction and global object deletion
- see last-copy risk before destructive apply
- preview resulting visibility and recovery posture after apply
- choose a safer alternative without leaving the review page
- prove later exactly which byte-action family was committed
