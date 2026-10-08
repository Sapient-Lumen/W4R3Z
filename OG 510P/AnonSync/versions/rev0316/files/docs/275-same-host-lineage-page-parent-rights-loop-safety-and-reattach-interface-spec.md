# Same-host lineage page: parent rights, loop safety, and reattach interface spec

The archive already has same-machine derivation doctrine and collision/claim safety work.
What it still lacked was one ordinary page for the most common operator question in that family:

> for these same-host copies, who is the parent, what rights and bytes can flow down, is the topology safe, and if continuity broke, can the child be reattached honestly?

Current Resilio docs still document the workflow clearly enough to make the opportunity obvious, but they also still express too much of it as a caveat cluster.

## Page promise

The Same-host lineage page should make five answers adjacent:

1. lineage family now
2. rights ceiling now
3. topology safety now
4. source/child continuity now
5. strongest honest next action

The page exists so the operator no longer has to reconstruct same-host continuity from scattered preferences, exceptions, and disappearance/reconnect behavior.

## Fixed page order

Every same-host lineage page should render the same sections in the same order:

1. **Family snapshot**
2. **Rights and flow ceilings**
3. **Topology and loop safety**
4. **Source health, child dependence, and reattach status**
5. **Admissible actions**
6. **Receipt promise**

### 1) Family snapshot

This section should show:

- parent/source subject
- one or more child/derived subjects
- family role for each node (`source`, `derived`, `detached child`, `reattach candidate`)
- bound paths for each node
- whether the page is about one child or the whole family

The operator should be able to answer: **what lineage family am I looking at?**

### 2) Rights and flow ceilings

This section should show:

- source permission ceiling
- child permission ceiling
- whether owner-like rights can ever flow down
- whether remote peers talk directly to the child or only through the source
- any narrowed rights currently in force because the parent narrowed

The operator should be able to answer: **what may flow down this family, and what can never flow down?**

### 3) Topology and loop safety

This section should show:

- whether current paths are safe
- whether any ancestor/descendant overlap exists
- whether any candidate new path would form a loop or unsafe nesting relation
- whether the requested action is blocked for topology reasons

The operator should be able to answer: **is this family topologically honest?**

### 4) Source health, child dependence, and reattach status

This section should show:

- source state (`healthy`, `offline`, `removed`, `placeholder-limited`, `reconnected`, `missing`)
- whether child can currently fetch through the source
- whether child continuity is intact, degraded, detached, or reattachable
- whether child disappeared only because parent was removed/disconnected
- whether reattach is possible now, guarded, or impossible without recreate

The operator should be able to answer: **is the child healthy now, and if not, is there an honest reattach path?**

### 5) Admissible actions

Example actions:

- `Add derived child`
- `Narrow rights`
- `Move child safely`
- `Detach intentionally`
- `Reattach child to restored source`
- `Recreate as new family`
- `Reject unsafe nested path`

The page must not force the operator into manual remove/re-add ritual when the product can honestly say `reattach`.

The operator should be able to answer: **what real move is available without lying about continuity?**

### 6) Receipt promise

A lineage receipt should preserve:

- family members in scope
- rights ceiling reviewed
- topology verdict
- source/child continuity verdict
- chosen repair or abstention
- whether continuity survived or a new family was created

The operator should be able to answer: **what later evidence will prove whether continuity was preserved, reattached, or deliberately severed?**

## Compact family row contract

A trustworthy compact family row should preserve the following order:

1. family subject
2. source → child relation
3. current continuity phrase
4. strongest blocker or risk
5. next honest action

Example:

```text
PrimaryPhotos → CacheMirror   detached child after source reconnect   safe to reattach   blocker: source path changed, child still unbound   Review
```

## What this page must never imply

The page must never imply that:

- same-host child equals independent peer family
- source removal and child continuity are unrelated
- child placeholder visibility proves source bytes exist now
- re-creation is the same fact as reattach
- a grayed-out permission option is an adequate explanation of rights ceiling

## Result

This page is how AnonSync borrows Resilio's real same-host workflow without cloning the weaker habit of making continuity and repair depend on remembered caveats.
