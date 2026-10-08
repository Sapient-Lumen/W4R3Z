# Capacity-fit, scale-admission, and indexing-honesty review spec

The archive already has intake review, topology review, filesystem fidelity, settlement readiness, storage budgets, and writer-contention review.
This document answers the narrower practical question those layers still leave open:

> what must a real operator surface literally show before a device adopts, rebinds, or materially carries a large subject whose local truth may be limited by RAM, watchers, indexing cost, path portability, or storage headroom?

This is the admission companion to `66-claim-and-adoption-intake-interface-spec.md`, the scale companion to `47-settlement-barrier-and-readiness-spec.md`, the local-resource companion to `51-space-pressure-reclaim-and-retention-budget-spec.md`, and the preflight companion to `76-writer-contention-and-quiescence-review-spec.md` when degraded notifications are not just a live-writer problem but a host-fit problem from the start.

## Why this needs its own spec

Resilio's current docs make the seam unusually clear.
`Out of memory` says Sync keeps the whole tree of files and folders in memory, needs roughly 1.5–2 KB of RAM per file/folder, and the practical way to reduce RAM is to remove the biggest folders from all peers and add them back so a new database is built.
`Agent run out of system notify watchers` says watcher exhaustion is common on Linux with many files and subdirectories, and once the limit is reached updates are learned only by manual or periodic rescans.
`Some internal tasks are taking time to complete` says hashing, scanning, merging, dedup, reading, and writing may simply become heavy because there are many files or because disk/network are busy.
`My files don't sync` adds more scattered fit clues: UTF-8 filename assumptions, path-length limits, out-of-space conditions, notification loss that may need restart or `touch`, filesystem errors, and a `devices cannot merge folder trees` condition that is often answered with remove-and-re-add folklore.
`Power user preferences` piles on more scale-sensitive knobs: `prioritize_initial_indexing` for huge folders with millions of files, `parallel_indexing` that may drive heavy CPU and disk usage, `enable_file_system_notifications`, and free-space reserve settings.

Those features and warnings are individually useful.
Together, they still scatter one important operator truth:

- can this host honestly carry this share or mount at the requested mode
- will freshness stay continuous or degrade to rescans from the start
- is the first safe action full adoption, selective visibility, metadata-only visibility, narrower scope, reclaim-first, or outright rejection on this host
- are the real blockers RAM, watchers, disk headroom, path portability, or topology/path mistakes
- what will initial indexing and pre-seeded verification cost before the product starts promising ordinary sync behavior

AnonSync should not clone that shape.
A serious control surface should instead publish one capacity-fit and scale-admission review model so “can this machine honestly host this subject?” becomes explicit product truth rather than troubleshooting folklore.

## Core rule

A non-trivial capacity or scale situation should always compile to a reviewed fit surface.
That includes at least:

- any adoption, claim, bind, or rebind where estimated entry count, bytes, or index cost are large enough that host fit is no longer obvious
- any host where RAM, watcher budget, disk headroom, or scan posture may force degraded freshness or a narrower local mode
- any path where path-length, encoding, filesystem-error, or merge-tree problems are known or strongly suspected before safe steady-state can be promised
- any case where the safest answer may be selective/materialized differently, metadata-only, subtree-narrowed, reclaim-first, or rejected on this host rather than `Add folder` or `Connect`
- any Linux/WebUI/headless path where the product would otherwise hide host-fit truth behind warnings, advanced toggles, or later support ritual

A channel may compress the review when risk is truly low.
It may not replace the meaning with vague `Add anyway`, `Connect`, `Retry indexing`, or `Re-add folder` prose.

## Entry points that must converge

The product may offer several ergonomic entry points:

- workbench warning `Review host fit`
- claim/adoption page `Review capacity before apply`
- topology/rebind page `Review scale on target host`
- CLI `fit review --share ... --path ... --plan`
- CLI `fit show <capacity_fit_case_id> --view review`
- CLI `claim prepare ... --emit-fit-review` when the real issue is not authority but host honesty

But these must all converge on the same public capacity-fit model.
The operator should never have to wonder whether one surface is merely showing a scary warning while another is actually explaining memory, watcher, indexing, storage, and portability consequences.

## Fixed review order

Every non-trivial capacity-fit review should render the same sections in the same order:

1. **Subject and intended local role**
2. **Local capacity and index cost**
3. **Freshness and notification posture**
4. **Portability and path blockers**
5. **Admissible modes and mitigations**
6. **Receipt promise**

### 1) Subject and intended local role

This section should show:

- which share, subtree, mount, or incoming claim is being reviewed
- whether the request is full materialization, selective materialization, metadata-only visibility, receive-only/pre-seeded adoption, or another narrower local role
- estimated entry count and byte scale when available
- whether the trigger came from intake, rebind, low-space policy, watcher pressure, or operator review

The operator must be able to answer: **what exactly am I trying to carry here, and in what local role?**

### 2) Local capacity and index cost

This section should show:

- memory posture for the requested subject on this host
- watcher posture and whether continuous notifications remain plausible
- initial-indexing / verification posture, including whether hashing, merge, or pre-seeded verification will be heavy
- storage-headroom posture for materialized bytes, temp files, archive/history, and service-state needs
- whether the current host is comfortable, guarded, high-risk, or blocked for this subject/mode

The operator must be able to answer: **can this machine honestly absorb the indexing and local-state cost of this subject?**

### 3) Freshness and notification posture

This section should show:

- whether change detection is expected to be continuous, mixed, periodic-rescan only, or already blocked
- whether degraded freshness comes from watcher ceilings, disabled notifications, network-reviewed mounts, or another known cause
- whether readiness/settlement claims will later be weakened by this host-fit posture
- whether initial adoption can still be honest or should narrow to a mode that does not imply full freshness

The operator must be able to answer: **if I proceed, how trustworthy will change detection and convergence actually be?**

### 4) Portability and path blockers

This section should show:

- path-length, encoding, tree-merge, filesystem-error, or portability blockers that already threaten safe admission
- whether the current path is merely risky, needs narrowing/rebinding, or should be blocked outright
- whether the blocker is local-host-specific, mount-specific, or share-topology-specific
- whether stronger filesystem-fidelity or topology review is the honest next step instead of ordinary admission

The operator must be able to answer: **is there a hard blocker or semantic downgrade hiding inside the path itself?**

### 5) Admissible modes and mitigations

This section should show:

- proceed with full local role
- narrow to selective / metadata-only / receive-only posture
- narrow to a smaller subtree or different target path
- reclaim or resize first
- stage indexing with an explicit guarded mode
- reject this host for now and keep the subject unclaimed or visibility-only

The operator must be able to answer: **what safe host-fit actions are actually available here?**

### 6) Receipt promise

This section should show:

- which capacity-fit receipt will exist after apply, defer, or rejection
- what it will later prove about the reviewed scale, host posture, chosen local mode, and any degraded-freshness conditions accepted
- whether the receipt remains provisional because estimates were weak or the host stayed on guarded posture
- what later audit survives after indexing finishes, headroom changes, or the operator picks a different host

The operator must be able to answer: **what later evidence will prove how this host-fit decision was made and what limits were knowingly accepted?**

## Action hierarchy inside capacity-fit review

The primary action should be the safest meaningful next step.
Examples:

- a huge incoming dataset on a comfortable workstation → `Adopt with selective materialization`, not `Connect anyway`
- a path set that will exceed watcher comfort on Linux → `Adopt metadata-only and monitor fit`, not `Retry if sync feels slow`
- a host near RAM and free-space ceilings → `Reclaim and re-run fit review`, not `Add folder`
- a path with portability blockers and merge-tree ambiguity → `Escalate to topology / fidelity review`, not `Re-add and hope`

Convenience labels such as `Connect`, `Add folder`, `Retry indexing`, or `Re-add` should be visually separate and usually not primary.

## What the surface must never imply

The capacity-fit surface must never imply that these are the same thing:

- large but comfortable versus large and host-blocking
- selective/materialized narrowing versus full adoption with weaker hidden guarantees
- continuous notifications versus periodic-rescan-only freshness
- storage pressure versus RAM pressure versus watcher pressure versus portability blockers
- honest guarded admission versus troubleshooting folklore that says “just re-add the folder”

## Cross-links to other review models

Capacity-fit review should often hand off to nearby review families, but it should not dissolve into them.

- **Intake / claim review** answers whether a subject should be accepted and with what authority.
  Capacity-fit review answers whether this host can honestly carry the accepted subject and in which local role.
- **Topology review** answers whether the path/graph relationship is safe.
  Capacity-fit review answers whether the chosen host and mode can sustain the graph once admitted.
- **Filesystem fidelity review** answers what semantic downgrade a mount/path implies.
  Capacity-fit review answers whether the host can afford continuous truthful operation on that mount/path.
- **Storage-budget review** answers which bytes can be reclaimed or retained over time.
  Capacity-fit review answers whether the initial/local role is honest before long-term budget work even begins.
- **Writer-contention review** answers what to do when active coordination with another writer exists.
  Capacity-fit review answers whether degraded notifications or rescans are structural host-fit limits from the start.

## CLI projection expectation

A textual projection should be able to render the fixed review order directly, for example through `anonsync fit show <capacity_fit_case_id> --view review`.
That output should be good enough that a headless operator does not need a richer workbench merely to learn whether the system is comfortable, guarded, or blocked by RAM, watcher ceilings, index cost, path portability, or storage headroom.

## Linux/WebUI parity rule

A Linux-first product has to assume that WebUI, TUI, CLI, and headless automation are not edge cases.
So the reviewed fit grammar must survive across those channels.
It is not acceptable for one richer surface to show memory/watcher/index/headroom truth while Linux/WebUI falls back to `slow indexing`, `out of memory`, `touch files`, or `increase watchers` folklore.

## Why this is worth the trouble

AnonSync only justifies its extra complexity if the safer model also becomes easier to read.
A fixed capacity-fit grammar is how the archive avoids rebuilding a system where out-of-memory notes, watcher warnings, indexing toggles, path-limit troubleshooting, and re-add folklore are all individually documented, yet the full meaning of “can this host honestly carry this subject, with what freshness guarantees, and under what narrower mode if not?” still depends on which warning, preference, or support article the operator happened to notice first.
