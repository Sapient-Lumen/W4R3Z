# Fetchability page: last-full-copy risk and eviction review interface spec

The archive already has fetchability doctrine, storage-pressure review, and history/restore work.
What it still lacked was one ordinary page for the operator question current products still make too reconstructive:

> before I evict, clear, or trust this placeholder-visible path, who still definitely has the bytes, what recovery routes still exist, and would this action remove the last easy way back?

Current Resilio docs make this seam concrete by combining placeholder workflows, Archive/versioning, manual restore, timestamp gotchas, and cross-surface history lookup.

## Page promise

The Fetchability page should make five answers adjacent:

1. current visibility and residency
2. strongest full-copy witness now
3. current restore/fetch routes now
4. requested downgrade or eviction risk now
5. strongest honest next action

This page exists so `available on demand` never gets to stand in for `durably recoverable later`.

## Fixed page order

Every fetchability page should render the same sections in the same order:

1. **Requested action and scope**
2. **Current visibility and local residency**
3. **Full-copy witness stack**
4. **Restore and fetch routes**
5. **Admissible actions**
6. **Receipt promise**

### 1) Requested action and scope

This section should show:

- subject/path/subtree in scope
- requested action (`inspect`, `fetch`, `evict`, `clear`, `remove from this device`, `pin`, `retire stale announcement`, or similar)
- whether the operator is changing one path, subtree, whole share, or standing policy

The operator should be able to answer: **what exact byte-risk question am I asking?**

### 2) Current visibility and local residency

This section should show:

- whether the subject is full-local, partial-local, placeholder-visible, names-only, or announcement-only
- whether the current device is pinned, ordinary, already absent, or eviction-pending
- whether Archive currently holds relevant prior material on this seat
- whether the current visible path came from live namespace, stale announcement, or restored candidate

The operator should be able to answer: **what is visible here, and how much of it is truly local?**

### 3) Full-copy witness stack

This section should rank witness quality, for example:

- `local full copy`
- `multi-peer confirmed full copy`
- `single remote confirmed full copy`
- `offline/stale remote witness`
- `Archive-only candidate`
- `announcement without confirmed bytes`
- `none known`

The page should show timestamps or freshness classes for witness quality.

The operator should be able to answer: **who still definitely has the bytes, and how strong is that proof?**

### 4) Restore and fetch routes

This section should distinguish:

- fetchable now from live peer
- fetchable when source returns
- restorable from local Archive only
- restorable through other reviewed route
- guarded by timestamp/continuity caveat
- no honest recovery route proven

If Archive is involved, the page should say whether restore is:

- manual only
- local only
- desktop-only or hidden-path only
- blocked from direct live-share restoration on this seat

The operator should be able to answer: **what real path back exists if I downgrade now?**

### 5) Admissible actions

Example actions:

- `Proceed with eviction`
- `Proceed, but pin first`
- `Preserve last full copy here`
- `Verify remote witness before evicting`
- `Open Archive candidate browser`
- `Escalate ghost-risk`
- `Block downgrade`

The page must not quietly treat `remove from this device` as harmless when it would erase the last well-evidenced full copy.

The operator should be able to answer: **what honest move remains safe from here?**

### 6) Receipt promise

A fetchability receipt should preserve:

- requested action and scope
- visibility/residency state reviewed
- witness quality reviewed
- restore routes considered
- resulting risk verdict (`safe`, `guarded`, `last-copy`, `ghost-risk`, `blocked`)
- chosen action or abstention

The operator should be able to answer: **what later evidence will prove why I trusted this eviction, fetch, or preservation decision?**

## Compact card contract

A trustworthy compact fetchability card should preserve this order:

1. path or subtree
2. current visibility/residency phrase
3. strongest witness phrase
4. risk verdict
5. next honest action

Example:

```text
/Projects/Video/master.mov   placeholder-visible only   witness: single remote full copy, stale   risk: guarded last-easy-recovery route   Review
```

## What this page must never imply

The page must never imply that:

- placeholder-visible equals fetchable-now
- Archive-present equals live-share-restorable in the same way everywhere
- offline witness equals confirmed current full copy
- `clear synced files` is only a space action rather than sometimes a recovery-risk action
- restore candidate browsing is the same thing as successful current reintroduction

## Result

This page is how AnonSync keeps Resilio's useful selective-materialization and Archive instincts while refusing the weaker contract where true recovery meaning only emerges after the operator pieces together placeholders, hidden Archive folders, and timestamp caveats by hand.
