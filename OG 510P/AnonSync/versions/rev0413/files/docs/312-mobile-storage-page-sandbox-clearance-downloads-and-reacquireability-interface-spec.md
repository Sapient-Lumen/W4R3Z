# Mobile storage page: sandbox, clearance, downloads, and reacquireability interface spec

## Purpose

This page answers:

> where do this seat's bytes actually live, what counts against local storage, what exactly will be removed by each cleanup action, and can the cleared material be reacquired later?

The page exists because mobile storage is a custody boundary, not just a quota bar.

## Core decision

Every constrained or sandboxed seat must expose one first-class **Mobile storage** page.
That page owns:

- storage container or sandbox facts
- app data versus user data accounting
- share-local bytes versus one-off downloads versus outbound shared-link residue
- cleanup verbs and their scope
- reacquireability of cleared bytes

## Primary layout

The page always renders the same regions:

1. storage strip
2. accounting card
3. residency classes card
4. cleanup action matrix
5. reacquireability and history card
6. receipts

### 1) Storage strip

Show:

- device / seat name
- storage container verdict: `sandboxed`, `shared filesystem`, `mixed`, `unknown`
- pressure verdict
- one next honest action

### 2) Accounting card

Show at minimum:

- app/runtime data
- user data inside synced shares
- one-off downloads
- outbound shared-link residue if modeled separately
- free / pressured / exhausted local capacity verdict

### 3) Residency classes card

Group local bytes by class:

- synced-share bytes
- placeholders only
- downloads from one-off send/share flows
- outbound share residue / transfer records
- service/runtime data

Each class shows whether it is visible in the filesystem, in app-local storage only, or both.

### 4) Cleanup action matrix

For each cleanup verb show exactly what it removes:

- `clear local synced files`
- `remove from this device`
- `remove from all devices`
- `delete download only`
- `clear history only`
- `purge app/runtime cache`

The matrix must publish:

- which residency classes are affected
- whether placeholders remain
- whether transfer history remains
- whether remote peers are changed
- whether Selective Sync or another prerequisite is required

### 5) Reacquireability and history card

Show:

- whether cleared synced files are reacquirable later
- whether one-off downloads can be re-downloaded from history or require a live source again
- whether outbound-share records persist after local file removal
- what survives as a receipt after bytes are gone

### 6) Receipts

Show storage-clearing and reacquire receipts with before/after pressure deltas when known.

## Rules

### Rule 1 — local removal scope must be concrete

The page must say whether cleanup removes only local bytes, only UI history, both, or also remote copies.

### Rule 2 — reacquireability must stay adjacent to cleanup

Operators should not discover after clearing that the only full copy is gone or that history survived without bytes.

### Rule 3 — sandbox truth is public state

If the seat stores bytes inside an app sandbox or similarly constrained container, the page must say so explicitly.

## Honest outputs

This page may conclude:

- `local bytes clearable and safely reacquirable`
- `cleanup leaves history only`
- `cleanup removes local bytes but preserves remote continuity`
- `cleanup would strand the last local full copy`
- `storage pressure remains in app/runtime data`

It may not collapse all local cleanup into one generic `free up space` action.
