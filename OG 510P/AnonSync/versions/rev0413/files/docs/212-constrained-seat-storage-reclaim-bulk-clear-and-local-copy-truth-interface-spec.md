# Constrained-seat storage reclaim, bulk clear, and local-copy truth interface spec

## Purpose

The archive already had placeholder guardrails, storage budgets, and constrained-seat path consent.
What it still lacked was one explicit contract for a frequent follow-on action:

> clearing space on a constrained seat without lying about what disappears locally, what remains fetchable, and what merely leaves one UI surface.

Current official Resilio docs make this seam sharper than a generic `clear cache` option.
They still say iOS keeps files inside the app sandbox, splits storage into `App data` and `User data`, can remove all downloaded file-share receipts at once from the Storage menu, requires the `Downloads` folder for selective per-item deletion, and only allows clearing local copies from sync shares when Selective Sync is enabled.
Current Android share details also still say `Clear` turns all synced files on the device into placeholders and is available only when Selective Sync is on, while `Disconnect` preserves the folder in the system.

That is practical.
It is still not a good reclaim contract.
Local copy removal, placeholder reversion, receipt inbox cleanup, and subject departure are different actions and should not be inferred from whichever surface happened to expose the button.

## Core decision

AnonSync should treat local storage reclaim as a reviewed scope matrix.
Every reclaim action must explicitly declare:

- what byte class is being removed
- whether names remain visible afterward
- whether the bytes are still fetchable later
- whether the subject relationship itself changes

## Why this matters

Current Resilio docs still reveal four interface mistakes AnonSync should not clone:

- one surface can only bulk-clear a class of downloads while another does per-item cleanup
- reclaim ability can depend on subject posture such as Selective Sync being enabled
- `clear` and `disconnect` can sit near each other while changing very different things
- sandbox storage menus and subject-local menus can each tell only part of the byte-truth story

AnonSync should therefore keep one stronger rule:

> reclaim is not one button; it is a scoped local-byte decision with an explicit recovery floor.

## Fixed review order

Every reclaim action should render the same sections in the same order:

1. **Byte class targeted**
2. **Visibility after reclaim**
3. **Recovery floor**
4. **Reclaim receipt**

### 1) Byte class targeted

This section should show whether the action targets:

- receipt-inbox payloads
- materialized shared-file copies
- cached placeholders and metadata only
- whole local subject residency
- app/service data

The operator must be able to answer: **what class of local bytes am I deleting?**

### 2) Visibility after reclaim

This section should show:

- whether names remain visible as placeholders
- whether the subject stays mounted
- whether history rows remain
- whether the path still exists in the local filesystem or app sandbox

The operator must be able to answer: **what will still be visible after the cleanup?**

### 3) Recovery floor

This section should show:

- whether bytes can be fetched again from peers
- whether the local seat still has rights to re-materialize them
- whether the action needs Selective Sync or another posture precondition
- whether some cleanup is bulk-only or can be itemized

The operator must be able to answer: **what can I get back later, and under what conditions?**

### 4) Reclaim receipt

This section should show:

- byte classes removed
- placeholder or mount effect
- recovery prerequisites
- any remaining ledger or history records
- whether subject membership changed

The operator must be able to answer: **what local space action actually happened here?**

## Main surface

AnonSync should expose reclaim actions as explicit rows such as:

- `remove local receipt payloads`
- `evict materialized copies; keep placeholders`
- `leave subject mounted`
- `disconnect subject; keep filesystem copy`
- `purge app cache only`

The product must never let `clear` stand in for all of those.

## Object model implications

AnonSync should add or strengthen these objects:

- `local_reclaim_review`
- `byte_residency_class`
- `reclaim_scope_matrix`
- `reclaim_recovery_floor`
- `reclaim_receipt`

Suggested fields for `reclaim_scope_matrix`:

- `seat_id`
- `subject_id`
- `byte_classes[]`
- `placeholder_after`
- `path_persists`
- `history_persists`
- `rematerialization_allowed`
- `preconditions[]`

## Event language

Use explicit phrases such as:

- `receipt payloads removed; transfer ledger retained`
- `materialized files evicted; placeholders preserved`
- `subject disconnected; local path kept`
- `reclaim blocked because re-materialization posture is unavailable`

Avoid vague lines such as:

- `storage cleared`
- `downloads removed`
- `share cleaned up`

## CLI shape

Example commands:

```text
anonsync reclaim review --seat <seat> --subject <subject>
anonsync reclaim apply <review> --evict materialized
anonsync reclaim apply <review> --remove receipt-payloads
anonsync reclaim receipt <id>
```

The CLI must expose the same scope matrix as the local web UI.

## Failure and edge cases

### Reclaim requested on a non-placeholder posture

The product should explain the missing precondition and offer a reviewed posture change if appropriate, not just hide the action.

### Bulk-only cleanup surface

If a platform only supports bulk cleanup for a byte class, the review must say so plainly before apply.

### History row survives cleanup

That must be presented as a retained ledger fact, not as evidence that bytes still exist.

## The non-clone reason

This is another clean example of why AnonSync should not merely copy Resilio's surface.
Current official Resilio docs still split reclaim truth across storage menus, download folders, share details, and posture prerequisites.
AnonSync should instead expose one reclaim matrix where local byte class, placeholder effect, and recovery floor stay visible together.
