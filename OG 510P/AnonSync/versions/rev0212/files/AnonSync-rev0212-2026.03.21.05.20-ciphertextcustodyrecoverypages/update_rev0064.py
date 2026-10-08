from pathlib import Path
import shutil
import textwrap

src = Path('/mnt/data/work_rev0064')
dst = Path('/mnt/data/work_rev0064_next')
if dst.exists():
    shutil.rmtree(dst)
shutil.copytree(src, dst)

def rw(rel):
    return dst / rel

def replace(path, old, new):
    p = rw(path)
    text = p.read_text()
    if old not in text:
        raise SystemExit(f'Pattern not found in {path}: {old[:120]!r}')
    p.write_text(text.replace(old, new, 1))

def insert_after(path, anchor, addition):
    p = rw(path)
    text = p.read_text()
    if anchor not in text:
        raise SystemExit(f'Anchor not found in {path}: {anchor[:120]!r}')
    p.write_text(text.replace(anchor, anchor + addition, 1))

# New doc
new_doc = textwrap.dedent('''\
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
''')
rw('docs/77-capacity-fit-and-scale-admission-review-spec.md').write_text(new_doc)

# README
replace('README.md', '- Revision: `rev0063`', '- Revision: `rev0064`')
replace('README.md', '- Timestamp: `2026.03.17.16.12` (America/New_York)', '- Timestamp: `2026.03.17.16.41` (America/New_York)')
replace('README.md', '- Codename: `contentionproofquiesceledger`', '- Codename: `fitproofscaleharbor`')
replace('README.md', 'This revision continues directly from `rev0062` and does seven things:', 'This revision continues directly from `rev0063` and does seven things:')
replace('README.md',
'''1. Re-checks **Resilio Sync** again with extra emphasis on writer contention: locked-file status still cannot name the locking application, save-burst coordination still lives in a storage-folder `FileDelayConfig` JSON plus restart ritual, retry behavior is still tuned through power-user preferences, and SMB/NAS mixed-access caveats still live in a separate troubleshooting article.
2. Sharpens the **non-clone rationale** into a stricter rule: AnonSync should not let “locked”, “delayed”, “rescan-only”, and “mixed SMB access” blur together ordinary slowdown, local-writer coordination, notification weakness, and real overwrite / rollback / corruption risk.
3. Adds a dedicated **writer-contention, lock-pressure, and quiescence review interface spec** so the archive now says what a real pre-apply contention surface must literally show before an operator keeps waiting, delays propagation, freezes sync, or escalates to stronger review.
4. Extends the **interface and daemon/API contract** so non-trivial lock pressure, burst-save delay, mixed external-writer risk, and quiesce actions can expose one stable review model instead of scattered status badges, hidden JSON knobs, retry intervals, and SMB caveats.
5. Extends the **workbench/interface pattern language** with sharper contention-review verbs and fixed review sections for contested scope, writer reality, notification/filesystem posture, quiesce effects, admissible actions, and receipts.
6. Adds additional **canonical interface flows** for reviewed contention decisions and cross-surface parity instead of leaving lock pressure and quiesce meaning to memory.
7. Refreshes the **evaluation**, **ADRs**, **roadmap**, **open questions**, **status**, **sources**, and **reading order** so future revisions keep contention honesty tied to surface parity, explicit quiesce truth, and durable coordination receipts.''',
'''1. Re-checks **Resilio Sync** again with extra emphasis on host-fit and scale: memory still scales with the whole tracked tree, watcher exhaustion on Linux degrades updates to periodic rescans, heavy indexing and merge work still appears as a generic internal-tasks warning, and huge-folder guidance still leans on power-user toggles and re-add/reindex folklore.
2. Sharpens the **non-clone rationale** into a stricter rule: AnonSync should not let “large share”, “slow indexing”, “out of memory”, “watcher ceiling”, and “path problem” blur together as vague operational pain when the real question is whether this host can honestly carry the subject and in what local mode.
3. Adds a dedicated **capacity-fit, scale-admission, and indexing-honesty review interface spec** so the archive now says what a real pre-apply host-fit surface must literally show before an operator adopts, rebinds, narrows, stages, or rejects a subject on the current machine.
4. Extends the **interface and daemon/API contract** so non-trivial RAM pressure, watcher ceilings, indexing cost, headroom limits, and path blockers can expose one stable review model instead of scattered warnings, advanced preferences, and later support ritual.
5. Extends the **workbench/interface pattern language** with sharper fit-review verbs and fixed review sections for subject role, local capacity/index cost, freshness posture, path blockers, admissible modes, and receipts.
6. Adds additional **canonical interface flows** for reviewed host-fit decisions and cross-surface parity instead of leaving scale admission to warnings, retries, or re-add folklore.
7. Refreshes the **evaluation**, **ADRs**, **roadmap**, **open questions**, **status**, **sources**, and **reading order** so future revisions keep scale honesty tied to explicit admission contracts, not hidden indexing lore.''')
insert_after('README.md',
'- a fixed contention-review pane that renders contested scope, writer/lock reality, notification/filesystem posture, quiesce effects, admissible actions, and receipt promise in the same order across GUI, TUI, CLI, and API-backed automation\n',
'- a fixed capacity-fit review pane that renders subject role, local capacity/index cost, freshness posture, path blockers, admissible modes, and receipt promise in the same order across GUI, TUI, CLI, and API-backed automation\n')
insert_after('README.md',
'- contention handling that still depends on locked-file badges, hidden `FileDelayConfig` JSON, retry-interval power-user knobs, and separate SMB caveats instead of one reviewed coordination/quiescence contract\n',
'- host-fit handling that still depends on out-of-memory notes, watcher-ceiling warnings, generic internal-task slowdowns, huge-folder power-user toggles, and re-add/reindex folklore instead of one reviewed capacity-fit contract\n')
insert_after('README.md',
'- `docs/76-writer-contention-and-quiescence-review-spec.md` — fixed contention-review pane anatomy for contested scope, writer/lock reality, notification/filesystem posture, quiesce actions, and contention receipts\n',
'- `docs/77-capacity-fit-and-scale-admission-review-spec.md` — fixed capacity-fit pane anatomy for subject role, local capacity/index cost, freshness posture, path blockers, admissible modes, and fit receipts\n')
replace('README.md', 'then `75-overlap-containment-and-graph-topology-review-spec.md`, then `41-report-and-intervention-language.md`', 'then `75-overlap-containment-and-graph-topology-review-spec.md`, then `76-writer-contention-and-quiescence-review-spec.md`, then `77-capacity-fit-and-scale-admission-review-spec.md`, then `41-report-and-intervention-language.md`')

# Status
replace('docs/00-status.md', 'This revision is an in-place continuation of `rev0062`', 'This revision is an in-place continuation of `rev0063`')
insert_after('docs/00-status.md',
'- make sure the archive has a better reason not to clone writer-contention handling that still hides coordination meaning behind locked-file badges, storage-folder delay JSON, retry-interval tuning, and separate SMB/NAS caveats\n',
'- make sure the archive has a better reason not to clone host-fit handling that still hides scale truth behind out-of-memory notes, watcher-ceiling warnings, generic internal-task slowdowns, huge-folder indexing toggles, and re-add/reindex folklore\n')
replace('docs/00-status.md',
'''- a deeper Resilio-derived warning that current writer-contention handling still depends on locked-file status badges, hidden `FileDelayConfig` JSON, retry-interval tuning, and separate SMB/NAS caveats
- a dedicated **writer-contention, lock-pressure, and quiescence review interface spec** that says what a real reviewed coordination surface must literally show before waiting, delaying, freezing, or escalating contested paths
- stronger CLI/API requirements so non-trivial lock pressure, burst-save delay, mixed external-writer risk, and quiesce actions can expose one stable review model instead of falling back to badges, retries, or hidden config files
- stronger workbench and pattern-language rules for reviewed contention so rich and textual surfaces keep the same contested-scope, writer-reality, notification-posture, quiesce-effect, action, and receipt truth
- additional canonical flows for rendering the same contention review in workbench and CLI without semantic drift
- roadmap, ADR, status, open-question, and source updates so future revisions keep contention honesty tied to surface parity and explicit quiesce proof''',
'''- a deeper Resilio-derived warning that current host-fit handling still depends on out-of-memory notes, watcher-ceiling warnings, generic internal-task slowdowns, huge-folder indexing toggles, and re-add/reindex folklore
- a dedicated **capacity-fit, scale-admission, and indexing-honesty review interface spec** that says what a real reviewed host-fit surface must literally show before adopting, rebinding, narrowing, staging, or rejecting a subject on the current machine
- stronger CLI/API requirements so non-trivial RAM pressure, watcher ceilings, indexing cost, headroom limits, and path blockers can expose one stable review model instead of falling back to warnings, advanced preferences, or later support ritual
- stronger workbench and pattern-language rules for reviewed host fit so rich and textual surfaces keep the same subject-role, local-capacity, freshness-posture, blocker, action, and receipt truth
- additional canonical flows for rendering the same capacity-fit review in workbench and CLI without semantic drift
- roadmap, ADR, status, open-question, and source updates so future revisions keep scale honesty tied to explicit admission contracts and fit receipts''')
replace('docs/00-status.md', '`rev0031` through `rev0061` progressively turned state roots, binding, file intent, activity, projection, settlement, rollback, fidelity, storage, offers, transfer truth, attention, control access, recovery, release posture, policy origin, diagnostics, temporary exceptions, personal constellations, exit/replacement, intake, joining, cutover, compromise, stale re-entry, destructive replay, conflict adjudication, same-host derivation, and live authority mutation into explicit public contracts.', '`rev0031` through `rev0063` progressively turned state roots, binding, file intent, activity, projection, settlement, rollback, fidelity, storage, offers, transfer truth, attention, control access, recovery, release posture, policy origin, diagnostics, temporary exceptions, personal constellations, exit/replacement, intake, joining, cutover, compromise, stale re-entry, destructive replay, conflict adjudication, same-host derivation, live authority mutation, topology review, writer contention, and now host-fit review into explicit public contracts.')
replace('docs/00-status.md',
'''`rev0063` applies the same discipline to writer contention and quiescence:

> a serious Linux-first workbench still is not specified tightly enough if the archive can define transfer budgets, filesystem fidelity, destructive replay, and activity phases in the abstract, yet still leave the actual “who is writing this file, what is currently delayed or frozen, how trustworthy are notifications on this mount, and when may bidirectional sync safely resume?” surface vague enough that GUI, WebUI, TUI, and CLI might drift back into different products.

That changes the archive in six specific ways:

- non-trivial lock pressure, burst-save delay, mixed SMB/NAS writer risk, and explicit quiesce actions are now specified as a fixed review pane rather than only a mix of status badges, hidden delay files, and troubleshooting lore
- contested scope, writer/lock reality, notification/filesystem posture, quiesce effects, admissible actions, and receipt promise now have a stable render order across channels
- transfer slowdown, activity override, and filesystem warning work can project one review model instead of falling back to generic `Retry`, `Resume syncing`, or `Increase delay` ritual
- the daemon/API model is now held to a clearer requirement that contention changes be previewable as coordination work rather than ambient background retries
- the Resilio comparison now lands a sharper non-clone argument: locked files, hidden delay config, retry tuning, and SMB caveats still hide too much meaning behind separate articles and hidden storage paths
- future interface work now has a narrower quality bar for reviewed contention parity on Linux-first deployments''',
'''`rev0064` applies the same discipline to host fit and scale admission:

> a serious Linux-first workbench still is not specified tightly enough if the archive can define intake, fidelity, storage pressure, and contention in the abstract, yet still leave the actual “can this machine honestly carry this subject, with what RAM/watcher/index cost, under what freshness guarantees, and with which narrower local role if not?” surface vague enough that GUI, WebUI, TUI, and CLI might drift back into different products.

That changes the archive in six specific ways:

- non-trivial RAM pressure, watcher ceilings, heavy initial indexing, path portability blockers, and low-headroom admissions are now specified as one fixed review pane rather than only a mix of warnings, advanced toggles, and later troubleshooting lore
- subject role, local capacity/index cost, freshness posture, path blockers, admissible modes, and receipt promise now have a stable render order across channels
- intake, topology, storage, and readiness work can project one host-fit review model instead of falling back to generic `Connect`, `Add folder`, `Retry indexing`, or `Re-add` ritual
- the daemon/API model is now held to a clearer requirement that fit changes be previewable as admission work rather than ambient background pain discovered later
- the Resilio comparison now lands a sharper non-clone argument: memory notes, watcher warnings, huge-folder toggles, and re-add folklore still hide too much host-fit meaning behind separate articles and advanced settings
- future interface work now has a narrower quality bar for reviewed capacity-fit parity on Linux-first deployments''')
insert_after('docs/00-status.md', '- when writer contention, burst-save delay, or mixed external-writer risk should always force full contention review instead of a safely compressed path\n', '- when RAM pressure, watcher ceilings, indexing cost, or path blockers should always force full capacity-fit review instead of a safely compressed path\n')

# Evaluation
insert_after('docs/10-resilio-sync-evaluation.md',
'### Requirement 58 — writer contention and quiescence must share one reviewed coordination contract\n\nIf the operator still has to combine locked-file badges, hidden delay JSON, retry-interval tuning, and SMB mixed-access caveats to answer “who is writing here, what is currently delayed or frozen, and when may safe propagation resume?”, the product has not actually exposed its contention contract.\n\nAnonSync should instead publish one public contention-review model with explicit contested scope, explicit writer and lock reality, explicit notification/filesystem posture, explicit quiesce and propagation effects, explicit admissible actions, and durable contention receipts that preserve the difference between harmless burst-save delay, guarded upload hold, full bidirectional freeze, and escalation because current freshness or mixed-access posture is not honest enough.\n',
textwrap.dedent('''\

### 16v) Capacity fit and scale admission still depend too much on warnings, advanced toggles, and re-add folklore

Resilio's current docs make one more seam unusually explicit.

`Out of memory` says Sync keeps the whole tree of files and folders in memory, needs roughly 1.5–2 KB of RAM per file/folder, and the practical way to reduce RAM is to remove the biggest folders from all peers and add them back so a new database is built.
`Agent run out of system notify watchers` says watcher exhaustion is common on Linux with many files and subdirectories, and once the limit is reached updates are learned only by manual or periodic rescans.
`Some internal tasks are taking time to complete` says hashing, scanning, merging, dedup, reading, and writing may simply be heavy because there are many files or because disk/network are busy.
`My files don't sync` adds more scattered fit clues: UTF-8 filename assumptions, path-length limits, out-of-space conditions, notification loss that may need restart or `touch`, filesystem errors, and a `devices cannot merge folder trees` condition that often ends in remove-and-re-add ritual.
`Power user preferences` piles on more scale-sensitive knobs: `prioritize_initial_indexing` for huge folders with millions of files, `parallel_indexing` that may drive heavy CPU and disk usage, `enable_file_system_notifications`, and free-space reserve settings.

That is not one trustworthy host-fit model.
It is a mixture of warnings, advanced preferences, degraded freshness hints, and re-add folklore.

The operator still has to reconstruct several separate truths from scattered docs:

- whether a host is comfortable, guarded, or simply not honest enough for the requested subject and mode
- whether the real pressure is RAM, watchers, indexing cost, free space, or path portability
- whether proceeding should mean full adoption, selective/materialized narrowing, metadata-only visibility, subtree narrowing, reclaim-first, or outright rejection on this host
- whether change detection will stay continuous or degrade to periodic rescans from the start
- whether the safest next step is host-fit review, topology/fidelity review, or support ritual instead of `Add folder` or `Connect`

AnonSync should not clone that shape.
A serious control surface should instead publish one capacity-fit and scale-admission review model with:

- one explicit review grammar for subject+intended role, local capacity+index cost, freshness+notification posture, portability+path blockers, admissible modes, and receipt promise
- explicit separation between comfortable scale, guarded host fit, degraded-freshness admission, reclaim-first posture, and blocked-on-this-host outcomes
- explicit host-fit truth before apply instead of after-the-fact out-of-memory, watcher, or re-add folklore
- explicit handoff into topology, fidelity, or storage review when scale pressure is only part of the real problem
- explicit receipts proving which host-fit facts were reviewed, what local mode was accepted, what degraded posture was knowingly tolerated, and what follow-up still remained

### Requirement 59 — capacity fit and scale admission must share one reviewed host-fit contract

If the operator still has to combine out-of-memory notes, watcher warnings, generic internal-task slowdowns, huge-folder indexing toggles, and re-add folklore to answer “can this machine honestly carry this subject and under what local mode?”, the product has not actually exposed its host-fit contract.

AnonSync should instead publish one public capacity-fit review model with explicit subject role, explicit local capacity/index cost, explicit freshness and notification posture, explicit portability/path blockers, explicit admissible modes, and durable fit receipts that preserve the difference between comfortable adoption, guarded narrowing, reclaim-first staging, and honest rejection on the current host.
'''))
replace('docs/10-resilio-sync-evaluation.md', 'and explicit contention/quiescence contracts that keep contested scope, writer reality, notification weakness, quiesce posture, and safe resume conditions visible instead of leaving lock pressure and mixed external-writer risk to badges, hidden delay files, retry knobs, and SMB troubleshooting lore.', 'and explicit contention/quiescence contracts that keep contested scope, writer reality, notification weakness, quiesce posture, and safe resume conditions visible instead of leaving lock pressure and mixed external-writer risk to badges, hidden delay files, retry knobs, and SMB troubleshooting lore, and explicit capacity-fit contracts that keep subject role, host resource posture, indexing cost, freshness guarantees, and admissible local modes visible instead of leaving large-subject admission to memory notes, watcher warnings, advanced toggles, and re-add folklore.')

# Interface spec
insert_after('docs/30-interface-spec.md',
'''### Contention receipt

A durable explanation record proving what coordination action was applied to a contested path and what propagation it intentionally held back.

Fields:

- `contention_receipt_id`
- `contention_case_ref`
- `action_kind` (`delay-profile-applied`, `upload-held`, `bidirectional-frozen`, `reader-guard-applied`, `escalated-review`, `released`, `cancelled`)
- `scope_ref`
- `effective_quiesce_posture`
- `propagation_expectation` (`local-writes-preserved`, `remote-writes-held`, `delete-propagation-held`, `rescan-required`, `review-pending`)
- `expires_at` nullable
- `decision_trace_ref` nullable
- `completed_at`
- `outcome` (`applied`, `released`, `cancelled`, `blocked`)
- `provenance_ref` nullable
''',
textwrap.dedent('''\

### Capacity-fit review case

A durable plan-bearing record for deciding whether a host can honestly carry a subject and under what local mode.
This exists so operators can inspect the difference between “add the folder” and “accept this subject on this machine with specific RAM, watcher, indexing, storage, and freshness consequences.”

Fields:

- `capacity_fit_case_id`
- `primary_subject_ref`
- `candidate_path` nullable
- `requested_local_role` (`full-materialize`, `selective-materialize`, `metadata-only`, `receive-only`, `preseeded-adopt`, `cache-derivative`, `blocked`)
- `estimated_entry_count` nullable
- `estimated_total_bytes` nullable
- `memory_posture` (`comfortable`, `guarded`, `high-risk`, `blocked`, `unknown`)
- `watcher_posture` (`continuous-available`, `near-limit`, `rescan-fallback`, `unsupported`, `unknown`)
- `index_cost_posture` (`ordinary`, `heavy-initial-index`, `heavy-preseed-verify`, `parallel-index-risk`, `unknown`)
- `storage_headroom_posture` (`comfortable`, `warning`, `guarded`, `blocked`, `unknown`)
- `freshness_posture` (`continuous`, `mixed`, `periodic-rescan`, `blocked`, `unknown`)
- `portability_blocker_posture` (`none-known`, `path-length-risk`, `encoding-risk`, `merge-tree-risk`, `filesystem-error-risk`, `topology-coupled`, `unknown`)
- `admission_posture` (`full-ok`, `selective-preferred`, `metadata-only-preferred`, `narrow-scope-required`, `reclaim-first`, `reject-on-this-host`)
- `status` (`draft`, `preflighted`, `planned`, `applied`, `deferred`, `rejected`, `expired`)
- `review_model` nullable
- `evidence_refs[]`
- `provenance_ref` nullable

### Capacity-fit receipt

A durable explanation record proving how a host-fit decision was made for a subject and what local mode or degradation was knowingly accepted.

Fields:

- `capacity_fit_receipt_id`
- `capacity_fit_case_ref`
- `action_kind` (`accepted-full`, `accepted-selective`, `accepted-metadata-only`, `accepted-narrowed-scope`, `deferred-for-reclaim`, `escalated-review`, `rejected-host`)
- `scope_ref`
- `effective_local_role`
- `effective_freshness_posture`
- `accepted_limits[]`
- `follow_up_refs[]`
- `completed_at`
- `outcome` (`applied`, `deferred`, `rejected`, `blocked`)
- `provenance_ref` nullable
'''))

# API spec
insert_after('docs/31-daemon-api-spec.md',
'## Topology-review resources\n',
textwrap.dedent('''\
## Capacity-fit / scale-admission resources

These resources keep RAM pressure, watcher ceilings, indexing cost, storage headroom, and path blockers visible as one host-fit model.
They answer what subject and local role are being considered, whether this host can honestly sustain them, and whether the safe next step is full adoption, selective or metadata-only narrowing, reclaim-first staging, or rejection on the current host.

```text
GET    /v1/capacity-fit-cases
POST   /v1/capacity-fit-cases
GET    /v1/capacity-fit-cases/{capacity_fit_case_id}
POST   /v1/capacity-fit-cases/{capacity_fit_case_id}/apply
POST   /v1/capacity-fit-cases/{capacity_fit_case_id}/defer
GET    /v1/capacity-fit-receipts/{capacity_fit_receipt_id}
```

`POST /v1/capacity-fit-cases` should accept one or more share/mount/claim refs plus an explicit target path and intended local role such as `full-materialize`, `selective-materialize`, `metadata-only`, `preseeded-adopt`, or `narrow-scope`.
The resulting case or referenced plan should always include:

- subject and intended-local-role summary
- local capacity and index-cost findings
- freshness and notification-posture findings
- portability and path-blocker findings
- admissible modes / mitigations and any escalation path into topology, fidelity, or storage review
- a stable `review_model` grouping so clients can render the same sections in the same order without inventing their own semantics

The `review_model` should at minimum group facts into:

- `subject_and_intended_local_role`
- `local_capacity_and_index_cost`
- `freshness_and_notification_posture`
- `portability_and_path_blockers`
- `admissible_modes_and_mitigations`
- `receipt_promise`

Intake, storage, fidelity, and topology endpoints may still exist for narrower domain actions, but when the operator-visible outcome is deciding whether this host can honestly carry a subject and under what local mode, those endpoints should reference or emit the same capacity-fit-case / capacity-fit-receipt model.

'''))

# Flows
append_flows = textwrap.dedent('''\

## Flow 111 — review host fit before adopting a huge subject on a watcher-limited Linux machine

Problem: a Linux operator is about to adopt a very large pre-seeded project tree onto a machine with limited RAM, nearly exhausted watcher budget, and modest free space. The product must explain host-fit truth directly instead of asking the operator to infer it from warnings, slow indexing, and later rescans.

Goal:

- prove that scale, RAM, watcher, indexing, headroom, and path blockers can render as one reviewed capacity-fit case
- make the safe next action read like admission policy rather than troubleshooting lore

Workbench expectations:

- clicking `Review host fit` from claim/adoption, path rebind, or a warning opens one capacity-fit review page
- the page renders sections in this order:
  1. subject and intended local role
  2. local capacity and index cost
  3. freshness and notification posture
  4. portability and path blockers
  5. admissible modes and mitigations
  6. receipt promise
- the primary action inherits the reviewed intent, for example `Adopt metadata-only on this host` or `Defer and reclaim before full materialization`, instead of generic `Connect` or `Add folder`

CLI expectations:

```text
$ anonsync fit show fit_01J... --view review
Capacity-fit review
-------------------
1. Subject and intended local role
   Subject: incoming share research-archive
   Requested local role: full-materialize
   Estimated scale: 9.8M entries / 2.4 TiB

2. Local capacity and index cost
   Memory posture: guarded
   Watcher posture: rescan-fallback likely on this host
   Index cost: heavy-preseed-verify
   Storage headroom: warning

3. Freshness and notification posture
   Expected freshness: periodic-rescan if fully adopted here
   Settlement honesty: guarded, not continuous

4. Portability and path blockers
   Path blocker posture: none-known
   Additional blocker: candidate path sits on network-reviewed mount

5. Admissible modes and mitigations
   - Adopt metadata-only on this host
   - Narrow to subtree and rerun fit review
   - Reclaim space and keep selective materialization
   - Escalate to filesystem fidelity review

6. Receipt promise
   Receipt will prove reviewed scale, accepted local role, degraded freshness posture, and any required follow-up.
```

Expected operator answers from CLI alone:

- whether the machine is comfortable, guarded, or blocked for the requested subject
- whether degraded freshness is structural from watcher limits rather than temporary contention
- whether a narrower local mode is the honest answer
- whether another review family should take over because the real blocker is portability or topology

## Flow 112 — render the same capacity-fit review in CLI and workbench without semantic drift

Problem: a GUI operator narrows a large share to metadata-only on a low-resource laptop; later a headless operator checks the same case over SSH. Both surfaces must show the same scale, host posture, freshness, and receipt truth.

Goal:

- prove that rich and textual surfaces render the same reviewed host-fit case
- make subject role, local capacity, freshness posture, path blockers, and admissible modes read like one product

Cross-surface success criteria:

- both surfaces answer the same question: **can this machine honestly carry this subject, under what local mode, and with what freshness guarantees if accepted?**
- neither surface falls back to generic `Add folder`, `Connect`, `Retry indexing`, or `Re-add` language when the real decision is a reviewed host-fit choice
''')
rw('docs/32-interface-flows.md').write_text(rw('docs/32-interface-flows.md').read_text() + append_flows)

# Workbench
insert_after('docs/38-operator-workbench-interface-spec.md',
'''Those three lines may all start from “some files are locked”, but the product should never force operators to assume they are the same action.
''',
textwrap.dedent('''\

## Capacity-fit and scale-admission surface

A capacity-fit surface exists so non-trivial RAM pressure, watcher ceilings, indexing cost, storage headroom, and path blockers compile to one reviewed host-fit decision instead of a mix of generic warnings, advanced toggles, and re-add folklore.

A capacity-fit page should show one fixed review grammar in this order:

1. subject and intended local role
2. local capacity and index cost
3. freshness and notification posture
4. portability and path blockers
5. admissible modes and mitigations
6. receipt promise

Inside those sections the page should still answer at least:

- what exact share, subtree, mount, or incoming claim is being reviewed and what local role is being asked of this host
- estimated entry count and byte scale when available
- whether RAM, watcher budget, indexing/verification cost, and storage headroom are comfortable, guarded, or blocked
- whether freshness is expected to stay continuous, become mixed, degrade to periodic-rescan only, or already be blocked
- whether path-length, encoding, merge-tree, filesystem, or mount-tier blockers are part of the host-fit story
- whether the safest next action is full adoption, selective/materialized narrowing, metadata-only visibility, reclaim-first staging, subtree narrowing, or escalation into topology / fidelity review
- what receipt will later prove the reviewed scale, accepted local mode, degraded posture, and any remaining follow-up

The page should make one difference visually unavoidable:

- **Accept this host-fit decision**
- **Narrow the local mode and keep scale honest**
- **Escalate because this path or host is not honest enough yet**

Those three lines may all start from “large share” or “slow indexing”, but the product should never force operators to assume they are the same action.
'''))
replace('docs/38-operator-workbench-interface-spec.md', '19. Every non-trivial writer-contention case must keep contested-scope/writer-reality/notification-posture/quiesce-effects/receipt truth visible in a fixed order across GUI, WebUI, TUI, and CLI-backed surfaces.', '19. Every non-trivial writer-contention case must keep contested-scope/writer-reality/notification-posture/quiesce-effects/receipt truth visible in a fixed order across GUI, WebUI, TUI, and CLI-backed surfaces.\n20. Every non-trivial capacity-fit case must keep subject-role/local-capacity/freshness-posture/path-blocker/admissible-mode/receipt truth visible in a fixed order across GUI, WebUI, TUI, and CLI-backed surfaces.')

# Pattern language
insert_after('docs/39-interface-pattern-language.md',
'''## Pattern 22g — contention and quiescence review need a fixed grammar

Every non-trivial contention review should render the same sections in the same order:

1. trigger and contested scope
2. writer and lock reality
3. notification and filesystem posture
4. quiesce and propagation effects
5. admissible actions
6. receipt promise

This matters because a product can define good transfer, activity, and fidelity objects on paper and still regress in practice if one client offers a rich coordination sheet while another falls back to a locked-files badge, a retry timer, or `increase delay` folklore.
''',
textwrap.dedent('''\

## Pattern 22h — capacity-fit and scale-admission review need a fixed grammar

Every non-trivial capacity-fit review should render the same sections in the same order:

1. subject and intended local role
2. local capacity and index cost
3. freshness and notification posture
4. portability and path blockers
5. admissible modes and mitigations
6. receipt promise

This matters because a product can define good intake, storage, and fidelity objects on paper and still regress in practice if one client offers a rich host-fit sheet while another falls back to `slow indexing`, `out of memory`, `increase watchers`, or `re-add the folder` folklore.
'''))
replace('docs/39-interface-pattern-language.md', 'A reviewed contention case should not end with a generic `Retry`, `Resume syncing`, or `Increase delay` button if the real action is `Hold uploads and preserve local writes`, `Freeze bidirectional propagation`, or `Escalate to filesystem-fidelity review`.', 'A reviewed contention case should not end with a generic `Retry`, `Resume syncing`, or `Increase delay` button if the real action is `Hold uploads and preserve local writes`, `Freeze bidirectional propagation`, or `Escalate to filesystem-fidelity review`.\nA reviewed capacity-fit case should not end with a generic `Add folder`, `Connect`, `Retry indexing`, or `Re-add` button if the real action is `Adopt metadata-only on this host`, `Defer and reclaim before full materialization`, or `Escalate to topology/fidelity review`.')

# ADRs
insert_after('docs/40-architecture-decisions.md',
'''## ADR-076 — Writer contention needs one reviewed coordination contract, not badges and hidden delay lore

**Decision:** Non-trivial lock pressure, burst-save delay, mixed external-writer risk, and explicit quiesce actions should compile to one reviewed contention model rather than living as separate status badges, hidden delay files, retry knobs, and SMB caveats.

**Why:** Current Resilio docs still spread coordination meaning across `Locked files`, storage-folder `FileDelayConfig`, `recheck_locked_files_interval`, and SMB warning pages about notification loss, broken locks, and mixed access outside Samba. AnonSync should keep contested scope, writer reality, filesystem posture, quiesce effect, and safe resume conditions visible in one place.

**Consequences:**
- contention work gains a stable review grammar and durable contention receipts
- workbench and CLI both need explicit contested-scope, writer-reality, notification-posture, and quiesce-effect sections
- delay profiles, upload holds, bidirectional freezes, and reader-only guards remain visibly distinct public actions
- degraded notification or mixed-access evidence can escalate visibly into fidelity, topology, or destructive-replay review instead of hiding behind retries
''',
textwrap.dedent('''\

## ADR-077 — Host fit and scale admission need one reviewed contract, not warnings and re-add folklore

**Decision:** Non-trivial RAM pressure, watcher ceilings, indexing cost, storage headroom, and path blockers should compile to one reviewed capacity-fit model rather than living as separate warnings, advanced toggles, and re-add/reindex ritual.

**Why:** Current Resilio docs still spread host-fit meaning across `Out of memory`, watcher-exhaustion warnings, generic internal-task slowdown notes, huge-folder indexing preferences, free-space reserve knobs, and troubleshooting advice that can end in restart, `touch`, or remove-and-re-add. AnonSync should keep subject role, host resource posture, freshness guarantees, path blockers, and admissible local modes visible in one place.

**Consequences:**
- host-fit work gains a stable review grammar and durable fit receipts
- workbench and CLI both need explicit subject-role, local-capacity/index-cost, freshness-posture, and path-blocker sections
- full adoption, selective/materialized narrowing, metadata-only visibility, reclaim-first staging, and reject-on-this-host outcomes remain visibly distinct public actions
- intake, topology, fidelity, and storage surfaces can escalate into host-fit review instead of hiding scale pain behind generic add/connect flows
'''))

# Roadmap
insert_after('docs/50-roadmap.md', '- review-model projection for writer contention and quiescence so rich and textual clients render the same contested-scope/writer-reality/notification-posture/quiesce-effect sections\n', '- review-model projection for capacity fit and scale admission so rich and textual clients render the same subject-role/local-capacity/freshness-posture/path-blocker sections\n')
insert_after('docs/50-roadmap.md', '- operators can preview the same topology-review truth in workbench and CLI without semantic drift\n', '- operators can preview the same capacity-fit truth in workbench and CLI without semantic drift\n- operators can tell before adopting or rebinding a large subject whether the current host is comfortable, guarded, or blocked by RAM, watcher ceilings, indexing cost, storage headroom, or path blockers\n')

# Open questions
rw('docs/64-critical-open-questions.md').write_text(rw('docs/64-critical-open-questions.md').read_text() + textwrap.dedent('''\


## 46) How much low-risk host-fit automation is safe before scale honesty becomes either noisy or too magical?

The archive is now clearer that non-trivial RAM pressure, watcher ceilings, indexing cost, storage headroom, and path blockers should use first-class reviewed capacity-fit cases and receipts, but one policy seam remains open:

- when an obviously comfortable host and modest share may use a safely compressed review versus always opening the full capacity-fit sheet
- whether degraded-freshness outcomes such as metadata-only or periodic-rescan admission should always force stronger acknowledgement when the original request was full materialization
- how much automatic narrowing is acceptable before the product starts hiding meaningful local-role change behind reassuring `Connect` or `Add` language
- when repeated fit failures on one host should divert into topology, storage, or device-placement guidance instead of keeping the operator inside a host-local warning loop

This matters because weak defaults recreate out-of-memory, watcher, and re-add folklore, while overly strict defaults could make harmless moderate-size admissions feel ceremonial instead of trustworthy.
'''))

# Sources
rw('docs/sources.md').write_text(rw('docs/sources.md').read_text() + textwrap.dedent('''\

- Out of memory
  https://help.resilio.com/hc/en-us/articles/209724663-Out-of-memory

- Agent run out of system notify watchers. Updated files will be uploaded only after periodic folder rescan
  https://help.resilio.com/hc/en-us/articles/360015593120-Agent-run-out-of-system-notify-watchers-Updated-files-will-be-uploaded-only-after-periodic-folder-rescan

- Some internal tasks are taking time to complete
  https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete

- My files don't sync
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- Power user preferences
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences
'''))

