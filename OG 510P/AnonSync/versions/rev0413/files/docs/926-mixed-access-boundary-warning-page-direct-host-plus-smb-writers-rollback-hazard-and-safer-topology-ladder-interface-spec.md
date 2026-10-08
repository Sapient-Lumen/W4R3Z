# Mixed access boundary warning page: direct host plus SMB writers, rollback hazard, and safer topology ladder interface spec

## Purpose

This warning appears when the product detects or the operator declares a topology where the same bytes may be touched through more than one semantic write lane, especially `direct-on-host` plus `SMB/UNC mediated` access.

The page exists to answer:

> am I merely making access easier, or am I creating a topology where writes can be lost, rolled back, or corrupted because different paths do not share one coherent contract?

## Trigger conditions

Open this warning when any of the following are true:

- Sync touches a path directly on the host while other users/apps touch the same data through SMB/Samba
- the operator declares both service-direct and share-mediated writes as active
- lock/contention evidence plus topology evidence suggests mixed writers
- the product cannot guarantee one authoritative write lane

## Fixed page order

1. boundary warning header
2. hazardous topology card
3. loser / rollback risk card
4. safer topology ladder
5. approval footer

### 1) Boundary warning header

Show:

- affected subject
- hazardous topology class
- current claim ceiling
- stronger rejected sentence

Example safe sentence:

- `This setup mixes direct host access with SMB-mediated writers; changes may be rolled back or files may be damaged, so the product cannot honestly claim one safe shared write lane.`

### 2) Hazardous topology card

Show the active lanes side by side:

- runtime direct lane
- SMB / Samba lane
- service / automation lane
- user interactive lane

For each lane show:

- who uses it
- whether it sees the same namespace
- whether it participates in the same lock / notification contract
- whether it is being blocked, degraded, or retired

### 3) Loser / rollback risk card

Show risk families explicitly:

- silent overwrite / rollback
- file corruption / damage
- delayed change discovery
- stranded lock residue
- false confidence from path alias sameness

Each risk row shows:

- current confidence
- affected scope
- why the product refuses the stronger claim

### 4) Safer topology ladder

Offer ordered alternatives such as:

- `Choose direct host as the only writer`
- `Choose SMB / UNC as the only writer`
- `Split into read-only observer lane plus one writer lane`
- `Move Sync to a different host / substrate`
- `Stop and export before continuing`

Each rung shows:

- preserved behavior
- lost convenience
- effect on notification / lock truth
- receipt or follow-up page emitted

### 5) Approval footer

Possible outcomes:

- `Block topology`
- `Continue only after lane retirement`
- `Continue as degraded observer topology`
- `Emit mixed-access warning receipt`

## Rules

### Rule 1 — mixed-writer hazard is not a tooltip

This boundary must interrupt setup or migration with a full-page review.

### Rule 2 — same path string does not mean same semantic lane

If two access paths look similar but participate in different lock or notification systems, the page must say so.

### Rule 3 — safer alternatives must be concrete

Do not leave the operator with `be careful`; provide explicit topology ladders.

### Rule 4 — claim ceiling is mandatory

The page must keep the strongest honest sentence visible and reject any stronger claim of safe shared writing.

## Acceptance criteria

A later operator can:

- tell why the topology is hazardous
- tell which lanes are colliding
- tell what kinds of data loss or rollback risk exist
- tell which safer topology choices exist
- tell whether the product blocked or accepted the configuration under a weaker claim
