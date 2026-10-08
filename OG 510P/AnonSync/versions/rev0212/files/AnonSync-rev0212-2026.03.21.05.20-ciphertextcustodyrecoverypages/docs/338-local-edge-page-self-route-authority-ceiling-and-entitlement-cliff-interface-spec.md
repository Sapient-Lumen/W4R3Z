# Local edge page: self route, authority ceiling, and entitlement cliff interface spec

The archive already has local-derivation doctrine and same-host lineage review.
What it still lacked was one ordinary page for the simplest same-host question:

> if I create or inspect a same-host edge, is this a real independent participant, or only a self-routed dependent edge whose rights, bytes, and lifetime all hang off the source and the current entitlement?

Current Resilio docs still make the seam unusually clear.
They say local sharing is desktop-only, entitlement-bound, self-only, supports USB and network paths, forbids loops into parent/child paths, cannot exceed the source permission ceiling, does not use tracker/relay/LAN discovery, disappears when the source disappears, and must be manually reconnected when the source later returns.
That deserves one stable page.

## Page promise

The Local edge page should make five answers adjacent:

1. edge family now
2. actual route now
3. rights ceiling now
4. lifecycle and entitlement dependence now
5. strongest honest next action

The page exists so the operator no longer has to mistake a same-host convenience for an independent peer relationship.

## Fixed page order

Every local edge page should render the same sections in the same order:

1. **Edge snapshot**
2. **Route and participant truth**
3. **Rights ceiling and inheritance**
4. **Lifecycle, source dependence, and entitlement**
5. **Admissible actions**
6. **Receipt promise**

### 1) Edge snapshot

This section should show:

- source subject
- local target subject
- host and seat identity
- target media class (`local-native`, `USB`, `network-reviewed`, `other provider`)
- whether the edge is healthy, detached, downgraded, or entitlement-blocked

The operator should be able to answer: **what same-host edge am I looking at?**

### 2) Route and participant truth

This section should show:

- whether bytes travel only through self from the source
- whether any remote peers ever talk directly to the local target
- whether helper/discovery systems are irrelevant for this edge
- whether source placeholders or missing bytes cap what the local target can materialize

The operator should be able to answer: **who actually carries bytes to this target?**

### 3) Rights ceiling and inheritance

This section should show:

- source permission level
- local-target permission ceiling
- whether `Owner`-class rights are impossible here
- whether rights changes must be done by recreate/re-share rather than in-place mutation
- whether source downgrades already cascaded to the target

The operator should be able to answer: **what can this target do, and what can it never do?**

### 4) Lifecycle, source dependence, and entitlement

This section should show:

- whether source removal/disconnect also removes the local edge
- whether source return allows reattach or requires recreate
- whether entitlement loss freezes or disables the edge
- whether the target remains visible only as history/receipt or remains an active bind
- whether media class or provider weakness changes the continuity grade

The operator should be able to answer: **what happens to this edge if the source or entitlement changes?**

### 5) Admissible actions

Example actions:

- `Create local edge`
- `Narrow to read-only edge`
- `Move target to safer media`
- `Reattach after source return`
- `Recreate with new rights`
- `Reject as loop risk`
- `Pause because entitlement is insufficient`

The page must not reduce these choices to a vague `sync locally` verb.

### 6) Receipt promise

A local-edge receipt should preserve:

- source and target in scope
- route truth reviewed
- rights ceiling reviewed
- lifecycle/entitlement dependence reviewed
- chosen action or abstention
- whether continuity survived or a new edge was created

The operator should be able to answer: **what later evidence will prove how this same-host edge actually worked?**

## Compact edge row contract

A trustworthy compact edge row should preserve the following order:

1. source → target
2. route phrase
3. continuity phrase
4. strongest blocker or cliff
5. next honest action

Example:

```text
Projects → USBMirror   self-routed only   detached after source removal, manual reattach required   cliff: entitlement expired, edge inactive   Review
```

## What this page must never imply

The page must never imply that:

- same-host edge equals independent peer
- a writable source implies owner-level writable target
- remote peers seed the local target directly
- entitlement loss is a cosmetic badge rather than a continuity change
- source placeholders prove target durability

## Result

This page is how AnonSync borrows Resilio's same-host practicality without cloning the weaker habit of burying route truth, rights ceilings, entitlement cliffs, and reattach behavior in one long tips article.
