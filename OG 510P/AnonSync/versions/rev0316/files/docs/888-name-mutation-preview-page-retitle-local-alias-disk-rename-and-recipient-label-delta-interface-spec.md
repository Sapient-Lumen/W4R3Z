# Name mutation preview page: retitle, local alias, disk rename, and recipient-label delta interface spec

## Purpose

This page exists to answer one ordinary question before commit:

> if I change this name now, which exact plane changes, which audiences notice, which older artifacts stay untouched, and what residue may remain afterward?

## Core decision

Every non-trivial naming action must compile into one explicit **Name mutation preview**.
The preview is required for:

- canonical subject retitle
- local alias edit
- disk path rename here
- recipient-label template change
- stale-alias reset
- mixed requests that touch more than one plane

## Fixed page order

1. current plane snapshot
2. requested mutation table
3. audience and propagation delta
4. stale-artifact and residue consequences
5. admissible actions

### 1) Current plane snapshot

Show the before-state for:

- canonical title
- local alias here
- disk basename here
- current recipient-label template
- recent issued artifact labels when relevant

### 2) Requested mutation table

One row per touched plane with columns:

- plane
- before
- after
- changed? yes/no
- actor scope
- required reissue? yes/no

### 3) Audience and propagation delta

Explicitly publish:

- who sees the new label immediately
- who keeps seeing the old label
- whether older artifacts remain unchanged
- whether existing peers are unaffected
- whether a later connect/import could still surface old residue

### 4) Stale-artifact and residue consequences

If older issued artifacts or disconnected aliases will remain, show them here.
At minimum publish:

- surviving old label
- where it will still appear
- whether it is valid, stale-but-visible, or invalid residue
- cleanup/reset or reissue option

### 5) Admissible actions

Only honest action verbs are allowed, such as:

- `Apply canonical retitle only`
- `Apply local alias only`
- `Rename disk path here`
- `Update future recipient labels only`
- `Reissue selected artifacts`
- `Reset stale alias only`
- `Split into two separate reviews`

## Rules

### Rule 1 — generic rename buttons are forbidden here

The preview must force the plane choice into the open.

### Rule 2 — unchanged audiences stay visible

A preview that says who changes but not who definitely stays on the old label is incomplete.

### Rule 3 — reset is explicit local cleanup

A stale-alias reset must not overclaim canonical subject mutation.

### Rule 4 — reissue is separate from rename

Changing future recipient-label defaults is not the same action as changing already-issued artifacts.

## Example strongest-safe sentence

- `This will change the local alias on this seat and the default label for future invites; it will not rename the disk folder here, and older issued links keep their old labels until reissued.`

## Acceptance criteria

A careful operator can answer:

- what exact plane is changing
- who sees the new label now
- who keeps seeing the old one
- whether already-issued artifacts are untouched
- whether any stale residue will remain after apply
