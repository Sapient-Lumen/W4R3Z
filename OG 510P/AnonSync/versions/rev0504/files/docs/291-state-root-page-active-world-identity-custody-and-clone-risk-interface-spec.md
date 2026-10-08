# State-root page — active world, identity custody, and clone risk interface spec

## Purpose

The archive already has state-root objects, service-profile language, and service-promotion doctrine.
What it still lacked was one explicit ordinary page for the practical question:

> which exact local world is active here, where does it live, which identity and inventory belong to it, and is there any sign that this world is being copied, shadowed, or accidentally replaced?

This page exists so `storage folder` stops being support lore and becomes ordinary product state.

## Core rule

A state root is not just a path.
It is a lived local world with:

- one stable world identity
- one current runtime principal/profile
- one inventory and identity custody story
- one clone/snapshot risk classification

If the operator still has to infer all of that from filesystem paths and missing-share surprises, the product is not explicit enough.

## Fixed review order

Every serious state-root page should render the same sections in the same order:

1. **Active world now**
2. **Location and runtime principal**
3. **Identity and inventory custody**
4. **Clone / shadow / snapshot risk**
5. **Next safe actions and receipts**

### 1) Active world now

This section should answer:

- active state-root/world ID
- whether the world is `attached`, `maintenance`, `detached`, `shadowed`, or `unknown`
- last verified time
- whether the current empty/non-empty inventory is expected

The operator must be able to answer: **which exact world am I currently operating in?**

### 2) Location and runtime principal

This section should show:

- filesystem path
- whether the path is explicit, implicit-default, imported, or discovered
- current user/service principal
- current runtime profile (`workstation`, `background-service`, `local-web`, etc.)
- whether this principal naturally points at a different default storage location than another seat/profile on the same host

The operator must be able to answer: **where does this world live, and why this path instead of another one?**

### 3) Identity and inventory custody

This section should show:

- identity fingerprint / label
- share / subject counts
- approval/trust or contact inventory counts where relevant
- whether the world contains continuity-critical receipts or only disposable caches
- whether the current inventory looks cleanly expected, unexpectedly empty, unexpectedly partial, or foreign

The operator must be able to answer: **what exactly belongs to this world, and does the current inventory match expectation?**

### 4) Clone / shadow / snapshot risk

This section should show:

- whether the current world shows signs of concurrent copy, stale restore, host migration without review, or service-user shadowing
- whether the same world ID was recently observed at another path or host
- whether a backup/snapshot restore may have created chronology ambiguity
- whether the current empty world is more likely a wrong-root branch than real data loss

The operator must be able to answer: **am I safely attached to one world, or am I looking at clone-risk or shadow-state?**

### 5) Next safe actions and receipts

This section should show only honest next actions, such as:

- `Inspect alternate state roots`
- `Review attach existing root`
- `Stay on current world`
- `Export snapshot before any switch`
- `Escalate clone-risk incident`

The operator must be able to answer: **what safe move preserves continuity from here?**

## States

Use a small stable vocabulary:

- `active verified world`
- `active but unexpectedly empty`
- `shadow world suspected`
- `clone-risk suspected`
- `snapshot-restore ambiguity`
- `foreign world`
- `maintenance attach only`

## Main surface

A compact **State root** card should show:

- world ID
- path
- runtime principal
- identity fingerprint summary
- clone/shadow verdict
- primary action: `Inspect state root`

## Detailed surface

The detailed page should provide five panes.

### Pane A — World strip

Shows:

- world ID
- current attach status
- last verified time
- strongest verdict

### Pane B — Location and principal

Columns:

- path
- source (`explicit`, `implicit`, `imported`, `discovered`)
- runtime principal
- runtime profile
- default-path divergence risk

### Pane C — Identity and inventory

Rows may include:

- identity fingerprint
- share count
- contact/trust count
- audit/receipt count
- continuity-critical material presence

### Pane D — Risk findings

Rows may include:

- service-user switched to different storage root
- same world seen elsewhere recently
- stale snapshot restore suspected
- host migration not yet reviewed
- empty world may be wrong-root branch

### Pane E — Receipts

Shows:

- verification receipts
- prior attach/switch receipts
- state snapshot exports
- clone-risk acknowledgments

## CLI parity

Minimum commands:

- `anonsync state-root show`
- `anonsync state-root verify`
- `anonsync state-root list-known`
- `anonsync state-root receipt <receipt-id>`

## Acceptance criteria

A user can:

- tell which local world is active
- see why that path and principal were chosen
- see whether the current inventory is expected or suspicious
- detect clone/shadow/snapshot ambiguity before mutating anything significant
- move from state-root inspection into attach/export/escalation flows without guesswork

