# Metadata-stream policy, xattr carriage, and bundle fidelity interface spec

## Purpose

The archive already had portability, warning-tier target, and alias-edge language.
What it still lacked was one explicit interface contract for metadata that is neither ordinary file content nor ignorable noise:

> when tags, resource forks, alternate streams, comments, or bundle-defining metadata matter, what page proves whether the product is preserving them natively, tunneling them indirectly, dropping them intentionally, or decomposing the object into a less faithful form?

Current official Resilio docs make this seam sharper than a generic `xattrs are hard` disclaimer would.
They still say Sync carries xattrs/alternate streams according to a hidden `StreamsList` whitelist, that this whitelist is editable, that xattrs cannot be ignored through `IgnoreList`, that cross-platform constraints may prevent native storage, and that in those cases Sync creates stub files under a hidden `.sync/Streams` service subfolder so a peer that cannot store the metadata can still propagate it.
Their troubleshooting docs also still say disabling xattr syncing can turn macOS bundles such as Pages, Keynote files, and apps into visible subdirectories.

That is useful capability.
It is not a clean public fidelity contract.

## Core decision

AnonSync should make **metadata carriage** first-class.

Every subject that may carry non-ordinary metadata must expose:

- which metadata channels are in scope
- whether each channel is preserved natively, tunneled indirectly, intentionally dropped, or blocked
- which targets can round-trip the metadata without loss
- whether disabling a channel would change object presentation, such as bundle-to-directory decomposition
- what evidence proves fidelity class per object family

If the operator still has to learn those truths from hidden whitelist files and service stubs, the interface is not explicit enough.

## Why this matters

Current Resilio docs still reveal seven truths AnonSync should not clone:

- metadata carriage can still be configured by editing a hidden whitelist file inside the subject
- metadata policy is distinct from ordinary ignore policy but not surfaced as its own contract
- some targets can act as metadata couriers without being able to store the metadata natively
- the courier mechanism still relies on hidden sidecar/stub service state
- a metadata-policy change can alter user-visible shape, not just hidden fidelity
- bundle-like objects may stop behaving as cohesive units when metadata carriage is disabled
- operators can still confuse `content synced` with `object faithfully preserved`

AnonSync should therefore keep one stronger rule:

> metadata fidelity must be stated in public as a channel contract, not inferred from hidden service behavior.

## Fixed review order

Every non-trivial metadata-channel action should render the same sections in the same order:

1. **Channel set and fidelity class now**
2. **Target/storage capability evidence**
3. **Object-shape consequences**
4. **Receipt and fidelity promise**

### 1) Channel set and fidelity class now

This section should show:

- each metadata channel in scope
- whether it is `native`, `tunneled`, `dropped`, or `blocked`
- the policy source for that choice
- the object families affected

The operator must be able to answer: **what metadata are we actually preserving, and how?**

### 2) Target/storage capability evidence

This section should show:

- whether the current target profile supports native storage for each channel
- size/namespace limits that could affect fidelity
- whether the member can only relay metadata rather than render or round-trip it locally
- whether metadata preservation depends on helper sidecars or carrier records

The operator must be able to answer: **is this target a true home for this metadata, or just a courier?**

### 3) Object-shape consequences

This section should show:

- whether disabling a channel would expose package contents as ordinary directories/files
- whether tags/comments/forks would become invisible but retained, irrecoverable, or rewritten
- which user-visible object families change semantics under the current policy
- whether a repair or migration path exists if fidelity is later upgraded

The operator must be able to answer: **what visible object behavior changes if this channel is off or tunneled?**

### 4) Receipt and fidelity promise

This section should show:

- the accepted metadata policy
- the per-channel fidelity class after apply
- which members accepted the same policy
- which members remain degraded couriers
- any object families now under a reduced-fidelity warning

The operator must be able to answer: **what fidelity did the system promise, and where is it weaker?**

## States

Use a small stable vocabulary:

- `native fidelity`
- `courier fidelity`
- `reduced fidelity`
- `blocked fidelity`
- `shape-changing policy`

## Main surface

The subject workspace should expose a **Metadata fidelity** card with:

- channels preserved natively
- channels tunneled or reduced
- any shape-changing warning
- a drill-in action: `Inspect metadata channels`

## Detailed surface

The detailed page should have five panes.

### Pane A — Channel ledger

Columns:

- channel
- current fidelity class
- policy source
- affected object families
- last validated target profile

### Pane B — Member capability map

Per member:

- native support yes/no
- courier-only yes/no
- reduced-fidelity reason
- last validation time

### Pane C — Shape consequences

Shows examples such as:

- `bundle preserved as cohesive object`
- `bundle decomposes to directory tree`
- `tags preserved but not locally rendered`
- `comment metadata dropped on this target`

### Pane D — Policy edits

Supports:

- enable channel
- disable channel
- require native support for selected members
- accept courier-only role with review

### Pane E — Receipts

Shows prior metadata-policy decisions and fidelity outcomes.

## CLI parity

Minimum commands:

- `anonsync metadata show <subject>`
- `anonsync metadata validate <subject> --member <id>`
- `anonsync metadata simulate <subject> --disable <channel>`
- `anonsync metadata apply <subject> --review <review-id>`

## Non-goals

This spec does **not** define:

- application-specific semantic understanding of every file bundle format
- rich document rendering
- archive/restore UX for metadata-only changes

It only defines how metadata-carriage truth becomes visible and reviewable.

## Acceptance criteria

A user can:

- inspect metadata-channel policy without editing hidden whitelist files
- tell which members are native preservers versus couriers versus reduced-fidelity holders
- see when a policy change would decompose bundles or otherwise alter visible object shape
- apply metadata-policy changes with the same truth in GUI and CLI
- prove afterward what fidelity class each member accepted
