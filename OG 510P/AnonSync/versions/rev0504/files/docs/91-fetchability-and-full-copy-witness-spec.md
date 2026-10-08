# Fetchability and full-copy-witness spec

The archive already has projection, file intent, storage budgets, observer posture, and transfer explanations.
This document answers the narrower practical question those abstractions still left open:

> what must a real operator surface literally show before an operator evicts, pins, clears, or trusts placeholder-visible content, so AnonSync does not drift back into `available on demand`, placeholder, or ghost-file folklore?

This is the materialization-truth companion to `44-file-intent-deviation-and-restore-spec.md`, the namespace companion to `46-namespace-projection-and-placeholder-spec.md`, the storage-safety companion to `51-space-pressure-reclaim-and-retention-budget-spec.md`, and the observer-posture companion to `89-observer-readonly-local-write-and-serve-rights-spec.md`.

## Why this needs its own spec

Resilio's docs are strong enough to make the problem unusually clear.
`Selective Sync` says enabling it means the device receives placeholder information rather than full bytes, and that linked-device Selective Sync can leave new files presented as `.rsl` placeholders.
`What Is an RSLS File?` then says reverting a file to placeholder preserves copies on other peers — but warns that if you and all other peers do this, you can end up with placeholders only and no actual file.
`Sync Interface on iOS devices` adds `Clear synced files`, which turns all synced files on that device into placeholders.
Finally, the ghost-file warning article says a peer may announce new or updated files, others may merge the tree later, and by then the source may already have reverted to placeholder or removed the bytes, leaving a stale announcement that no peer can now satisfy.

The lesson is not that selective materialization is bad.
The lesson is that a useful product can still hide too many materially different truths behind one casual `available on demand` story.

AnonSync should therefore make these differences explicit before apply:

- visible name plus confirmed durable full-copy witness elsewhere
- visible name backed only by this local full copy
- visible name backed only by an offline/uncertain source
- visible name announced in the tree even though no peer now has the bytes
- eviction, clear, or placeholder conversion that would silently create a placeholder-only universe

## Core rule

Placeholder visibility, namespace visibility, and durable retrievability are separate public facts.
A path should compile to a reviewed fetchability surface whenever any of these are true:

- the requested action would remove the last known full-copy witness
- remote full-copy witnesses are offline, stale, or unconfirmed enough that future fetch is only guarded
- the subject is visible in namespace but current byte backing is only announcement-level or `ghost`-risk
- a bulk `clear synced files` or subtree eviction would materially weaken the easiest recovery path
- local serve/reseed value still matters even though ordinary local materialization is being reduced

A channel may compress the review when risk is truly low.
It may not replace the meaning with `available on demand`, `placeholder only`, `clear synced files`, or `remove from this device` success language.

## Entry points that must converge

The product may offer several ergonomic entry points:

- workbench file card `Open fetchability`
- storage page `Review last-full-copy risk`
- observer page `Inspect byte backing`
- CLI `anonsync file availability ...`
- CLI `anonsync file evict ... --plan`
- API-backed automation that prepares, shows, and applies fetchability reviews explicitly

But these must all converge on the same public fetchability model.
The operator should never have to wonder whether one surface is merely showing placeholder state while another silently knows there are no real bytes left anywhere.

## Fixed review order

Every non-trivial fetchability review should render the same sections in the same order:

1. **Requested materialization intent**
2. **Visibility and local-residency reality**
3. **Source backing and full-copy witnesses**
4. **Fetchability, ghost risk, and admissible actions**
5. **Collateral effects on eviction, pinning, and serve value**
6. **Receipt promise**

### 1) Requested materialization intent

This section should show:

- triggering share, mount, or path
- requested action (`inspect`, `fetch`, `evict`, `clear`, `pin`, `unpin`, `retire stale announcement`, or similar)
- requested scope (one file, subtree, mount, or whole share)
- whether the operator is changing local residency only or also changing a broader policy/default

The operator must be able to answer: **what exact byte-presence question am I asking, and what action am I about to take?**

### 2) Visibility and local-residency reality

This section should show:

- whether the subject is full-bytes-visible, placeholder-visible, names-only, or announcement-only
- whether bytes are currently local on this device
- whether the current local state is pinned, ordinary, evictable, or already absent
- whether the currently visible name came from ordinary share visibility, local projection, or stale remote announcement

The operator must be able to answer: **what is visible here right now, and how much of it is actually local?**

### 3) Source backing and full-copy witnesses

This section should show:

- whether the current device holds a full copy
- which other peers recently confirmed a full copy
- whether those witnesses are online now, recently seen, stale, or absent
- whether the strongest honest summary is `local-only`, `remote-confirmed`, `multi-source-confirmed`, `offline-only`, `announcement-only`, or `none-known`

The operator must be able to answer: **who, if anyone, still definitely has the bytes?**

### 4) Fetchability, ghost risk, and admissible actions

This section should show:

- fetchability posture (`fetchable-now`, `fetchable-when-source-returns`, `local-last-copy`, `ghost-risk`, `not-fetchable`)
- whether the product is relying on fresh witness evidence, stale witness evidence, or tree-announcement residue only
- whether the requested action may proceed directly, must preserve/pin first, or should block and escalate
- whether stale announcement should be preserved, re-witnessed, retired, or explicitly left visible with a guarded warning

The operator must be able to answer: **can I still get these bytes later, and what honest actions are available from here?**

### 5) Collateral effects on eviction, pinning, and serve value

This section should show:

- whether evicting or clearing would remove the last known full copy
- whether pinning would materially improve recovery or serve posture
- whether local bytes still matter for reseed or other peers even if this mount is not authoritative
- whether a bulk action changes ordinary local convenience only or materially weakens the easiest recovery path

The operator must be able to answer: **what operational value do these bytes still have if I keep or remove them?**

### 6) Receipt promise

This section should show:

- which fetchability receipt will exist after apply
- what it will later prove about visibility, local residency, full-copy witnesses, fetchability posture, and chosen action
- whether witness quality was strict or guarded
- what later audit survives after the placeholder badge or warning row is gone

The operator must be able to answer: **what later evidence will prove why I trusted, pinned, evicted, or retired this visible path?**

## What the surface must never imply

The fetchability surface must never imply that these are the same thing:

- visible name vs durable retrievable bytes
- placeholder-visible vs remotely backed by a confirmed full copy
- offline witness hope vs current fetchability
- local clear/evict convenience vs removing the last known full copy
- stale announcement vs delayed but still honest download availability

If the product compresses those differences, it has recreated the ritual it is trying to replace.

## CLI projection expectation

A textual projection should be able to render the fixed review order directly, for example through `anonsync file availability <share> <path> --view review` or `anonsync file evict <share> <path> --plan`.
That output should be good enough that a headless operator does not need a richer workbench merely to learn whether a placeholder-visible path is safely backed elsewhere, safely fetchable only when an offline source returns, or no longer honestly retrievable.

## Why this is worth the trouble

AnonSync only justifies its extra complexity if the safer model also becomes easier to read.
A fixed fetchability grammar is how the archive avoids rebuilding a system where placeholders, clear-synced-files actions, offline warnings, ghost-file warnings, and support guidance are individually documented, yet the full meaning of `can I still get the bytes later if I do this now?` still depends on which help article the operator happened to remember first.
