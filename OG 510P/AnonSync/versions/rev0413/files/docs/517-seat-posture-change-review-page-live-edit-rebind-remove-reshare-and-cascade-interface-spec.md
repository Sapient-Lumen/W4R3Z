# Seat posture change review page — live edit, rebind, remove-reshare, cascade, and blocked-class interface spec

## Purpose

The archive already has pages for effective seat posture, grant mutation, and derived rights.
What it still lacked was one page for the moment an operator asks:

> make this seat broader, narrower, or different — what kind of change is that actually?

This page exists so the operator does not have to infer mechanism class from folder family, linked-device folklore, or local-share caveats.

## Core decision

Every requested posture delta for a seat/subject pair must be classified before commitment into exactly one **mechanism class**:

- `live_edit`
- `rebind_same_seat`
- `remove_and_reshare_descendant`
- `cascade_from_source_change`
- `blocked_by_class`
- `blocked_by_policy`
- `unknown`

The product must not offer one generic `change permissions` action and only explain the real class later.

## Fixed page order

1. **Seat and subject in scope**
2. **Requested posture delta**
3. **Mechanism class**
4. **Why this class won**
5. **Consequences before commit**
6. **Next actions and receipt promise**

### 1) Seat and subject in scope

Show:

- seat identity
- subject identity
- current effective posture
- strongest subject-family label
- linked-family relation if relevant
- descendant count at risk

The operator should be able to answer: **which exact seat/subject pair am I changing?**

### 2) Requested posture delta

Render the change as before/after vectors, not one vague sentence.

Required rows:

- observe
- materialize bytes
- write local names
- write local content
- propagate local mutations
- delegate / share onward
- recover plaintext

For each row show:

- current verdict
- requested verdict
- delta class (`broaden`, `narrow`, `lateral`, `no_change`)

### 3) Mechanism class

Render one mechanism card with:

- mechanism class
- same-subject or successor-subject verdict
- same-path or rebind-required verdict
- auto-cascade or manual-followup verdict
- reversibility hint

Example:

```text
Mechanism class: rebind_same_seat
Why: linked-owner default cannot narrow in place
Result: same seat, separate Standard subject with RO artifact
Manual work: disconnect current linked instance, bind new subject, verify target
```

### 4) Why this class won

The page must name the strongest basis in explicit language, such as:

- `Advanced folder supports live mutation`
- `Standard folder requires new key`
- `linked devices act as Owners by default`
- `read-only linked seat requires Standard-folder rebind`
- `local share permission cannot change via user management`
- `source-right narrowing cascades automatically`
- `local share cannot receive Owner`
- `encrypted-key-only peer cannot be shared locally`

This section must also list rejected mechanism classes and why they lost.

### 5) Consequences before commit

Show four consequence groups:

- **posture result** — effective rights expected after commit
- **byte/path result** — same path, new path, disconnect, placeholder risk, or residue
- **descendant result** — auto-lower, removal, no effect, or manual rebind needed
- **manual work** — steps the product can or cannot perform automatically

Primary actions may include:

- `Apply live change`
- `Open rebind plan`
- `Open local descendant reshare plan`
- `Review cascade graph`
- `Keep current posture`

### 6) Next actions and receipt promise

The page must promise one durable change receipt that preserves:

- requested delta
- mechanism class
- strongest basis
- expected manual work
- cascade scope

## Public object

### `seat_posture_change_draft`

Required fields:

- `seat_posture_change_draft_id`
- `seat_ref`
- `subject_ref`
- `current_effective_posture`
- `requested_posture`
- `delta_vector[]`
- `mechanism_class`
- `same_subject_verdict`
- `path_continuity_verdict`
- `cascade_scope_summary`
- `manual_work_items[]`
- `generated_at`

## Main surface

A compact **Seat posture change** card should show:

- current → requested posture
- mechanism class chip
- strongest basis chip
- followup burden chip

Example:

```text
Laptop-Aster · finances
owner effective → receive-only requested   rebind required   basis: linked-owner default   2 follow-ups
```

## Detailed surface

The detailed page should keep four panes.

### Pane A — Delta vector

Columns:

- capability axis
- current
- requested
- delta class

### Pane B — Mechanism verdict

Columns:

- mechanism candidate
- verdict
- why

### Pane C — Consequences

Columns:

- consequence family
- predicted result
- confidence

### Pane D — Follow-up work

Columns:

- work item
- auto/manual
- blocking or optional

## CLI parity

Minimum commands:

- `anonsync seat-posture change-review <seat> --subject <subject> --to <posture>`
- `anonsync seat-posture explain-change <draft-id>`
- `anonsync seat-posture apply-change <draft-id>`

## Acceptance criteria

A user can:

- see whether the request is a live edit, rebind, descendant recreation, cascade-only effect, or blocked request
- see why the chosen mechanism class won
- see what manual work remains before accepting the change
- export one durable draft/receipt pair for later review
