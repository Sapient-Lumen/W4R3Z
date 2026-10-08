from pathlib import Path
import shutil

root = Path('/mnt/data/rev0180_work/AnonSync-rev0180-2026.03.20.20.57-semantictradeoffguardpages')
new_name = 'AnonSync-rev0181-2026.03.20.21.14-footprintconfidencepages'
new_root = root.parent / new_name
if new_root.exists():
    shutil.rmtree(new_root)
shutil.copytree(root, new_root)

docs = new_root / 'docs'

# README
readme = f'''# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `rev0181`
- Timestamp: `2026.03.20.21.14` (America/New_York)
- Codename: `footprintconfidencepages`

## What changed in this revision

This revision continues directly from `rev0180` and does seven concrete things:

1. Re-checks another cluster of current official Resilio Sync docs so the archive's non-clone stance now also covers subject footprint, size/count accounting, completeness confidence, and hidden service residue.
2. Adds one new **Resilio evaluation** document focused on how current Resilio docs still split `how much data is really here?`, `what counts?`, `is this view complete yet?`, and `what hidden bytes remain?` across IgnoreList, `.sync` internals, RSLS placeholders, and change-detection/power-user articles.
3. Sharpens the main Resilio evaluation, source notes, and cross-cutting doctrine with a new answer: borrow Resilio's candor about exclusions, hidden service material, placeholder sparsity, and rescan confidence — refuse the page contracts that still make operators reconstruct those truths from scattered support prose.
4. Adds four new **interface page specs** for the strongest ordinary seams in this pass: subject footprint, size-metric truth, completeness confidence, and service residue / clearance review.
5. Extends the core interface/workbench language with explicit accounting-truth obligations so GUI, local-web, CLI, mobile, and dense renderings all preserve the same answers about counted bytes, resident bytes, provisional counts, and hidden managed residue.
6. Refreshes product direction, architecture decisions, roadmap notes, status language, and source notes so the new tranche is integrated into the main archive rather than floating beside it.
7. Makes the archive's answer to `why not just clone Resilio here too?` tighter because each no-clone choice now points at a replacement page instead of relying on hidden folders, optional columns, and FAQ caveats to explain byte truth.

## Current conclusion

We **still should not clone Resilio Sync wholesale**.

This pass makes the reason more precise in another ordinary but load-bearing part of the product:

> the parts worth copying from Resilio are still mostly **semantic candor** — explicit acknowledgement that ignored files are not counted, that placeholders are 0-byte stand-ins, that `.sync` and `.!sync` carry real service meaning, and that rescans / hashing can make visibility provisional — while the parts worth changing are the **page contracts** around footprint, completeness, and hidden residue.

That means AnonSync should become **more explicit than Resilio about which bytes count toward a subject metric, which bytes merely reside on the seat, when a list or size is provisional, and what hidden managed material still remains before or after cleanup**.

## Recommended reading order

1. `docs/00-status.md`
2. `docs/10-resilio-sync-evaluation.md`
3. `docs/11-resilio-borrow-line-and-non-clone-scorecard.md`
4. `docs/12-resilio-interface-clone-veto-tests-and-page-obligations.md`
5. `docs/28-resilio-accounting-footprint-and-completeness-evaluation.md`
6. `docs/333-subject-footprint-page-counted-resident-and-hidden-byte-families-interface-spec.md`
7. `docs/334-size-metric-page-visible-counts-exclusions-and-drift-explanation-interface-spec.md`
8. `docs/335-completeness-confidence-page-index-hash-source-and-surface-readiness-interface-spec.md`
9. `docs/336-service-residue-page-inflight-archive-streams-and-clearance-review-interface-spec.md`
10. `docs/38-operator-workbench-interface-spec.md`
11. `docs/30-interface-spec.md`
12. `docs/20-product-direction.md`
13. `docs/40-architecture-decisions.md`
14. `docs/50-roadmap.md`
15. `docs/sources.md`

## Archive map for this revision

- `docs/28-resilio-accounting-footprint-and-completeness-evaluation.md` — next-wave Resilio evaluation focused on counted size, resident footprint, placeholder sparsity, rescan confidence, and hidden managed residue
- `docs/333-subject-footprint-page-counted-resident-and-hidden-byte-families-interface-spec.md` — fixed page contract for truthful subject footprint, including counted live bytes, resident local bytes, placeholders, history, and hidden managed material
- `docs/334-size-metric-page-visible-counts-exclusions-and-drift-explanation-interface-spec.md` — fixed page contract for every size/count metric shown in lists, rows, and review panes, including exclusions and reasons for drift
- `docs/335-completeness-confidence-page-index-hash-source-and-surface-readiness-interface-spec.md` — fixed page contract for whether a listing or metric is complete, provisional, or degraded by deferred indexing / weak watchers / unavailable sources
- `docs/336-service-residue-page-inflight-archive-streams-and-clearance-review-interface-spec.md` — fixed page contract for hidden service bytes, in-flight temp material, archive residue, metadata stubs, and safe clearance review

All previously-added documents remain in place; this revision adds the next page tranche and refreshes the cross-cutting doctrine around it.
'''
(new_root / 'README.md').write_text(readme)

status = '''# Status

## Scope of this revision

This revision is an in-place continuation of `rev0180`, driven by the current request and the now-current archive state:

- continue researching rather than merely polishing
- test the `do not clone Resilio wholesale` conclusion against current official docs again
- keep making every non-clone choice earn itself with a specific borrow/adapt/reject reason
- keep writing ordinary page contracts where the archive still has interface-shape gaps rather than only object-model doctrine
- stay narrow: prefer high-leverage operator pages over broad product sprawl
- in this pass specifically, force a cleaner answer for footprint truth, count/size accounting, completeness confidence, and hidden service residue

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

The archive now contains:

- Revision: rev0181
- Timestamp: 2026.03.20.21.14 America/New_York
- Codename: footprintconfidencepages

- one new Resilio evaluation document:
  - `28-resilio-accounting-footprint-and-completeness-evaluation.md`
- four new interface page specs:
  - `333-subject-footprint-page-counted-resident-and-hidden-byte-families-interface-spec.md`
  - `334-size-metric-page-visible-counts-exclusions-and-drift-explanation-interface-spec.md`
  - `335-completeness-confidence-page-index-hash-source-and-surface-readiness-interface-spec.md`
  - `336-service-residue-page-inflight-archive-streams-and-clearance-review-interface-spec.md`
- refreshed Resilio evaluation and doctrine notes that now extend the non-clone line into count semantics, resident footprint, provisional completeness, and hidden managed residue
- refreshed top-level docs, workbench notes, architecture decisions, roadmap notes, and source notes so the new page tranche is integrated into the archive rather than bolted on

## The new tighter answer in this revision

This pass intentionally leans on another ordinary question that still survives in current Resilio docs:

> when a subject looks small because most of it is placeholders, when IgnoreList excludes bytes from the `Size` column, when `.sync` or `.!sync` still occupies space, or when watchers / rescans mean indexing is provisional, where does the product itself own the answers to `how much data is really here?`, `what exactly is counted?`, `is this view complete yet?`, and `what hidden bytes remain?`

The answer in this revision is:

- **subject footprint** is still too easy to infer from several separate docs about placeholders, hidden folders, archive, and mobile storage rather than one ordinary page
- **size/count metrics** are still too easy to misread because excluded files, hidden service material, and resident placeholders do not obey one obvious rule
- **completeness confidence** is still too easy to infer from watcher/rescan/how-soon FAQs and power-user settings rather than one first-class readiness page
- **service residue and hidden managed bytes** are still too easy to discover only when something breaks or when cleanup leaves surprising leftovers

## Outcome

The archive's current posture stays the same, but the argument is stronger:

- borrow Resilio's candor about what is excluded, hidden, sparse, and provisional
- refuse the exact interface contracts when one ordinary answer still requires cross-reading IgnoreList, `.sync` internals, RSLS placeholder docs, and change-detection articles
- replace each refusal with one sharper public page contract
'''
(docs / '00-status.md').write_text(status)

new_eval = '''# Resilio accounting, footprint, and completeness evaluation

## Why this pass matters

Current official Resilio Sync docs are again useful for AnonSync precisely because they are candid about several byte-accounting truths that many products blur.
They still say all of the following:

- IgnoreList entries are not indexed and are not counted in the `Size` column in the main view
- IgnoreList lives in hidden `.sync`, is case-sensitive, and if edited after the folder was already added, the structure has already been stored in the database and passed to peers until disconnect
- every synced folder gets a hidden `.sync` directory that is critical for syncing and also contains `Archive`, `IgnoreList`, `StreamsList`, and in-flight `.!sync` files
- placeholder `.rsls` files are 0-byte stand-ins that save space, can later materialize bytes on demand, and can leave a mesh with placeholders only if every full copy is removed
- change detection can rely on filesystem notifications, scheduled rescans, or manual rescans; the scheduled rescan is 600 seconds by default, and if the interval is set to zero Sync will not rescan even on restart
- the power-user table still exposes `free_space_warning_threashold`, `folder_rescan_interval`, `max_file_size_for_versioning`, `parallel_indexing`, `enable_file_system_notifications`, `lazy_indexing`, and other knobs that directly affect what is resident, counted, or confidently known
- desktop list views can show additional columns such as `size` and `date synced`, but the meaning of those columns still depends on the surrounding support prose rather than an integrated accounting page

That is a strong product to learn from.
It is also a concrete reason not to clone the page contracts.

## What Resilio gets right

### 1) It admits that counted size is not the same thing as bytes on disk

Current docs still say ignored files are not counted in the main `Size` column and placeholders are 0-byte stand-ins.
That is important honesty.
A product that hides those facts would be worse.

### 2) It admits that hidden service material is real

Current docs still say `.sync` is critical, houses share ID and service files, contains Archive / IgnoreList / StreamsList, and temporarily contains `.!sync` during transfer.
That again is useful candor.

### 3) It admits that visibility can be provisional

Current docs still say watcher quality varies by storage, rescans are periodic by default, zero disables rescans entirely, and indexing/hashing settings affect what Sync can know cheaply versus only after more work.
That is the right kind of honesty.

### 4) It admits that sparse visibility is not full custody

Current placeholder docs still say `.rsls` files are 0-byte representations, not actual file content, and warn that all peers can end up with placeholders only if every full copy is removed.
That is exactly the kind of semantic distinction the UI should surface.

## Why we still should not clone it

The core problem is not lack of truth.
The core problem is **where the truth lives**.

Resilio still makes the operator reconstruct one ordinary answer from several separate article families:

- *how much of this subject is really resident on this seat?*
- *which bytes are counted in the visible size metric, and which are excluded or merely hidden?*
- *is this list complete, or is it provisional because watchers, rescans, or hashing have not caught up yet?*
- *what service, history, temp, or metadata residue still remains even after I think I have cleared the subject?*

Those should not be FAQ-navigation questions.
They should be ordinary product pages.

## The AnonSync borrow line

Borrow from current Resilio:

- explicit candor that excluded bytes are not counted
- explicit candor that placeholders are sparse stand-ins rather than real content
- explicit candor that hidden managed folders/files are real parts of the product's behavior
- explicit candor that watcher health, rescans, and hashing make some views provisional

Adapt into AnonSync:

- one first-class page for **subject footprint**
- one first-class page for **size-metric truth**
- one first-class page for **completeness confidence**
- one first-class page for **service residue / clearance review**

## The replacement principle

AnonSync should never force the operator to infer byte truth from a single column.
Every surface that shows `size`, `present`, `available`, `cleared`, or `empty` should be able to answer four questions directly:

1. what bytes are counted here?
2. what bytes exist here but are not counted here?
3. what bytes are only names/placeholders and not present content?
4. how confident is the product that this answer is current?

That is the tighter reason not to clone current Resilio page contracts in this part of the product.
'''
(docs / '28-resilio-accounting-footprint-and-completeness-evaluation.md').write_text(new_eval)

spec333 = '''# Subject footprint page: counted, resident, and hidden byte families interface spec

## Purpose

The archive already had availability, fetchability, history, metadata-fidelity, exclusion policy, and storage/cleanup work.
What it still lacked was one ordinary page that answers the everyday operator question:

> how much of this subject is really here on this seat, and what byte families are part of that answer?

Current Resilio docs make this seam concrete instead of hypothetical.
They still say ignored files are not counted in the main `Size` column, placeholders are 0-byte stand-ins, `.sync` contains service material including `Archive`, `IgnoreList`, `StreamsList`, and temporary `.!sync` files, and some byte families are intentionally sparse or hidden.
That is good raw honesty.
It is still not a good page contract.

## Core decision

AnonSync should represent subject footprint as a **stack of byte families**, not a single vague `size` number.

Every subject-footprint page must separate at least these families:

1. **counted live bytes** — bytes that belong to the subject's main, policy-counted content on this seat
2. **resident but not counted bytes** — bytes present locally but excluded from the current metric contract
3. **sparse names only** — placeholders, detached names, or other entries that do not currently carry the full payload
4. **managed hidden bytes** — service state, temp transfer residue, metadata sidecars, history stores, or other product-owned bytes
5. **off-seat only bytes** — content known to exist elsewhere but not materially present here

## Why this matters

A subject can look `small` for several entirely different reasons:

- it is mostly placeholders
- excluded files exist but are outside the visible metric
- service/history bytes exist but the list row does not count them
- the seat only knows names or structure, not payloads
- indexing/readiness is still provisional

A single `size` field cannot honestly carry that load.

## Fixed review order

Every subject-footprint page should render sections in this order:

1. **Metric contract**
2. **Resident byte families**
3. **Sparse or off-seat families**
4. **Hidden managed material**
5. **Confidence and last verification**
6. **Action consequences**

## 1) Metric contract

At the top, say explicitly:

- the primary metric label (`counted live bytes`, `resident bytes`, `managed bytes`, etc.)
- whether the headline number includes hidden managed material
- whether excluded bytes are included
- whether placeholder names are included as entries, bytes, or neither
- whether the answer is point-in-time or continuously maintained

The operator should never have to guess what the headline number means.

## 2) Resident byte families

Render a breakdown such as:

- `fully materialized subject bytes`
- `locally cached subtrees`
- `history/rollback bytes`
- `metadata sidecar or fidelity bytes`
- `temp/in-flight bytes`

Each row must say:

- current size
- count of items
- whether counted in headline
- whether safe to reclaim independently
- what would need to remain elsewhere before reclaim is allowed

## 3) Sparse or off-seat families

Render a second block for:

- placeholders / sparse names
- disconnected but remembered items
- remote-only members known by structure only
- partial knowledge derived from prior indexing but not current local payload

Each row must make clear whether the seat currently has:

- names only
- names + metadata only
- some payload
- no local material at all

## 4) Hidden managed material

This section must surface:

- service roots or annexes bound to the subject
- rollback/history stores
- metadata preservation stores
- temporary/in-flight residue
- policy/config material specific to the subject

The page must make these bytes visible **without requiring raw filesystem inspection**.

## 5) Confidence and last verification

Show:

- last local scan / verification time
- whether the answer depends on watchers, scheduled rescans, or manual verification
- whether some byte families are estimated, exact, or stale
- whether source availability is required to complete the answer

A footprint page must admit uncertainty instead of silently flattening it.

## 6) Action consequences

The page should offer a compact action matrix:

- `evict materialized bytes`
- `clear managed temp bytes`
- `compact history bytes`
- `reverify footprint now`
- `open hidden-material review`

Each action must say what family changes and what family does not.

## Receipt

A footprint receipt should prove:

- subject ID
- headline metric contract
- byte-family breakdown
- confidence level
- last verification time
- any destructive or reclaim actions taken afterward

## What must never happen automatically

The product must never:

- call placeholders `present bytes`
- let ignored/excluded bytes silently impersonate deletion
- hide managed history/temp/service residue behind an empty-looking subject row
- display one headline number without a metric contract
- imply completeness when watchers/rescans make the answer provisional

## Resulting product doctrine

A subject is not `small` merely because the visible counted metric is small.
A subject is only `small` when the page can prove which byte families are absent, sparse, excluded, or hidden.
'''
(docs / '333-subject-footprint-page-counted-resident-and-hidden-byte-families-interface-spec.md').write_text(spec333)

spec334 = '''# Size metric page: visible counts, exclusions, and drift explanation interface spec

## Purpose

The archive already had list rows, policy precedence, exclusion rules, and availability language.
What it still lacked was one precise interface contract for a deceptively ordinary surface:

> when the product shows `size`, `items`, `bytes present`, or `storage used`, what exactly is that metric counting, and why might it differ from what the operator sees on disk or on another seat?

Current Resilio docs make this seam load-bearing.
They still say ignored files are not counted in the `Size` column, placeholders are 0-byte files, folder views can expose optional columns like `size` and `date synced`, and hidden `.sync` / Archive / StreamsList / `.!sync` material can coexist with user files.
That is a usable product.
It is still too easy to misread.

## Core decision

AnonSync should give every visible size/count metric its own inspectable **metric card**.
A metric card answers four questions:

1. **scope** — which object does this metric talk about?
2. **membership** — which entries qualify?
3. **count rule** — which bytes/counts are included or excluded?
4. **freshness** — how current is the computation?

## Fixed review order

Every metric page or popover should render sections in this order:

1. **Metric identity**
2. **Inclusions**
3. **Exclusions**
4. **Known drift causes**
5. **Seat variance**
6. **Repair / reverify actions**

## 1) Metric identity

State clearly:

- metric name
- unit (`bytes`, `entries`, `materialized bytes`, `subject bytes`, etc.)
- surface where it appears
- whether it is a per-seat, per-subject, or cross-seat metric

No row or column should display a number whose type cannot be named.

## 2) Inclusions

List the included families explicitly, for example:

- fully materialized payload bytes
- directories as entries but not as bytes
- fetched metadata that is part of the current contract
- history bytes only if the metric says it is a `resident footprint` metric rather than `live subject size`

## 3) Exclusions

List the excluded families explicitly, for example:

- ignored/excluded paths
- placeholder names without payload bytes
- hidden managed material
- temp or in-flight bytes
- off-seat content known only by announcement or structure

Every exclusion row should say whether the excluded family still exists locally, exists remotely only, or is outside the subject entirely.

## 4) Known drift causes

This section must explain why the visible metric may disagree with the operator's expectations:

- policy changes applied after indexing
- provisional scans or deferred hashing
- weak watchers / delayed rescans
- sparse files or placeholders
- hidden service/history/temp material
- peer-wise differences in excluded sets or materialized subsets

The point is not to apologize for drift.
The point is to name it.

## 5) Seat variance

A metric page should state whether another seat may legitimately show a different value because of:

- different materialization level
- different exclusion policy
- different history retention
- different temporary/in-flight state
- different storage class or metadata capability

A different number should not automatically look like corruption.

## 6) Repair / reverify actions

Good actions include:

- `recompute metric now`
- `show byte-family breakdown`
- `show excluded families`
- `show hidden managed bytes`
- `compare with another seat`

These actions should explain rather than overwrite.

## Compact row behavior

In list views, the number itself can stay compact.
But every compact metric must have an inspectable explanation surface with:

- metric label
- freshness state
- top exclusions
- link to footprint page

## Receipt

A metric receipt should prove:

- metric name and scope
- exact inclusion / exclusion contract
- timestamp of computation
- confidence state
- top drift causes that were active at the time

## What must never happen automatically

The product must never:

- let `size` silently switch meaning between surfaces
- call placeholder-only entries `present bytes`
- silently hide excluded bytes while implying absence
- let hidden service/history bytes distort a `live subject` metric without explanation
- show stale numbers as if freshly computed

## Resulting product doctrine

A metric is a contract, not a decoration.
If the product cannot say what a number counts, it should not show the number as authoritative.
'''
(docs / '334-size-metric-page-visible-counts-exclusions-and-drift-explanation-interface-spec.md').write_text(spec334)

spec335 = '''# Completeness confidence page: index, hash, source, and surface readiness interface spec

## Purpose

The archive already had readiness, transfer lanes, warning tiers, and hash-readiness work.
What it still lacked was one explicit page for this ordinary question:

> is the product's current view of this subject complete, or is it provisional because detection, hashing, scanning, or source availability is still lagging?

Current Resilio docs make this seam concrete.
They still say watcher quality depends on the storage, scheduled rescans run every 600 seconds by default, rescans can be disabled entirely by setting the interval to zero, only mtime/size are checked cheaply before rehashing, and some advanced settings defer or prioritize indexing work.
That is real operator truth.
It still lives mostly in FAQs and power-user tables.

## Core decision

AnonSync should expose a first-class **completeness confidence** object for every subject and every substantial subtree.
The object answers four questions:

1. have names been enumerated?
2. have payload bytes been verified / hashed as needed?
3. are required sources reachable for the missing parts?
4. how current is the surface relative to the local filesystem and the known mesh?

## Fixed review order

Every completeness-confidence page should render sections in this order:

1. **Scope of claim**
2. **Enumeration state**
3. **Verification state**
4. **Source reachability dependence**
5. **Freshness / watcher quality**
6. **Actions to raise confidence**

## 1) Scope of claim

State clearly whether the confidence applies to:

- the full subject
- this subtree only
- this list view only
- this metric only
- this seat only

A product must not overclaim completeness for the whole subject when only the current pane has been checked.

## 2) Enumeration state

Show whether the product currently has:

- no listing yet
- structural listing only
- full local enumeration
- announced remote structure but incomplete local confirmation

This section should say when names or directories are known before payload verification.

## 3) Verification state

Show whether the product has:

- verified payload hashes
- only mtime/size-based suspicion of change
- deferred hashing still pending
- pre-seeded bytes awaiting comparison
- placeholder-only entries not yet materialized

This is the page that should answer whether rename, dedup, conflict, and replay semantics are fully ready to trust yet.

## 4) Source reachability dependence

Say plainly whether higher confidence depends on:

- another peer coming online
- a full-copy witness existing somewhere
- a manual rescan or manual fetch
- waiting for background indexing to finish

Confidence is partly a local question and partly a reachability question.

## 5) Freshness / watcher quality

Show:

- whether filesystem notifications are healthy, degraded, or unavailable
- scheduled rescan cadence
- manual reverify option
- last verified time
- whether the surface may lag due to sleep, throttling, or disabled rescans

This section should make `current enough for browsing` distinct from `current enough for destructive decisions`.

## 6) Actions to raise confidence

Good actions include:

- `rescan now`
- `finish indexing now`
- `verify hashes for this subtree`
- `fetch missing members from source`
- `show confidence blockers`

Each action should say what kind of confidence it improves.

## Confidence classes

Use a small fixed set such as:

- **complete** — enumeration and needed verification are current for this claim scope
- **usable but provisional** — likely correct for browsing, not yet strong enough for destructive decisions without review
- **degraded** — known watcher/rescan/source blockers exist
- **unknown** — the product cannot currently justify a claim

## Receipt

A completeness receipt should prove:

- claim scope
- confidence class
- blockers
- verification state
- source dependencies
- last verified time

## What must never happen automatically

The product must never:

- present a provisional surface as authoritative without a confidence label
- hide watcher/rescan disablement when the operator is about to trust completeness
- imply payload verification from structure alone
- imply local completeness when remote-only members are still required for the claim
- make destructive decisions on a degraded confidence surface without a review step

## Resulting product doctrine

Completeness is not binary.
The interface must say whether it knows the names, the bytes, both, or neither — and how current that knowledge is.
'''
(docs / '335-completeness-confidence-page-index-hash-source-and-surface-readiness-interface-spec.md').write_text(spec335)

spec336 = '''# Service residue page: inflight, archive, streams, and clearance review interface spec

## Purpose

The archive already had hidden service state, history access, repair ladders, and storage-cleanup work.
What it still lacked was one ordinary page for a cleanup and repair question that operators hit constantly:

> after I clear, disconnect, move, or think I have emptied this subject, what hidden managed bytes still remain here, and which of them are safe to remove?

Current Resilio docs make this seam concrete instead of speculative.
They still say `.sync` is critical, Archive holds prior versions, `StreamsList` governs metadata behavior, `.!sync` files represent in-flight data, temp and service material can remain inside hidden folders, and deleting the wrong hidden material can turn into `Service files missing`.
That is strong evidence that the product needs a first-class residue page.

## Core decision

AnonSync should expose a **service residue page** for each subject and seat.
This page is not a raw-file browser.
It is a managed explanation of which hidden/product-owned byte families exist and what their current removal rules are.

## Fixed review order

Every service-residue page should render sections in this order:

1. **Residue families present**
2. **Purpose of each family**
3. **Current safety status**
4. **Clearance consequences**
5. **Required witnesses / exports before removal**
6. **Repair path if already damaged**

## 1) Residue families present

Render rows such as:

- subject service state
- in-flight temp bytes
- rollback/history bytes
- metadata preservation sidecars or stubs
- exclusion/config material
- diagnostic or profiler spill specific to this subject

Each row should show:

- current size
- item count
- location class
- whether it is counted in main footprint metrics

## 2) Purpose of each family

For each row, say what it is for:

- continuity / identity
- in-progress transfer
- rollback / restore
- metadata portability
- policy state
- diagnostics only

Operators should not have to decode hidden filenames to understand purpose.

## 3) Current safety status

Each residue family must declare one of these statuses:

- **required for continuity now**
- **required only until transfer settles**
- **required if rollback is still desired**
- **safe to compact**
- **safe to delete after receipt/export**
- **unsafe to delete manually; use managed action**

## 4) Clearance consequences

For each action, say exactly what changes:

- `clear temp only`
- `compact history`
- `detach subject and remove managed state`
- `remove local payload but keep history`
- `purge all managed state`

The page must make `cleanup` distinct from `damage`.

## 5) Required witnesses / exports before removal

Before destructive cleanup, the page should show:

- whether another full copy exists
- whether rollback receipts are still needed elsewhere
- whether metadata portability evidence has been exported
- whether diagnostic bundles should be captured first

No clearance surface should assume the operator remembers these dependencies.

## 6) Repair path if already damaged

If managed residue is missing or corrupted, show a short repair ladder:

- what capability is degraded
- what data remains safe
- whether rebind / reconnect / re-adopt is required
- which receipts or witnesses can preserve continuity

This section turns hidden-state failure into a product-owned explanation rather than a filesystem scavenger hunt.

## Compact row behavior

From any subject row, the operator should be able to inspect:

- `managed residue present`
- `history bytes retained`
- `temp bytes present`
- `cleanup unsafe until receipt/export`

without opening hidden folders.

## Receipt

A residue receipt should prove:

- subject ID
- byte-family list and sizes
- safety status for each family
- cleanup actions taken
- any continuity break or rollback loss accepted

## What must never happen automatically

The product must never:

- hide critical managed residue while implying the subject is fully gone
- allow ordinary cleanup wording to delete continuity-critical material silently
- require manual deletion of hidden folders as the primary UX
- collapse temp, history, policy, and metadata residue into one generic `misc` bucket
- leave a subject appearing `empty` when managed bytes are the only thing that remain

## Resulting product doctrine

`Empty`, `cleared`, `disconnected`, and `purged` are different states.
A service-residue page exists so the operator can see which one is actually true.
'''
(docs / '336-service-residue-page-inflight-archive-streams-and-clearance-review-interface-spec.md').write_text(spec336)

# Append addenda to key docs
add_10 = '''

## Revision addendum — footprint truth, metric contract, completeness confidence, and hidden residue

This revision pushes the Resilio evaluation further in another quiet but load-bearing place.
Current official docs are still candid that ignored files are not counted in the main `Size` column, placeholders are 0-byte stand-ins, `.sync` / Archive / StreamsList / `.!sync` are real managed byte families, and watcher / rescan / hashing policy can make a view provisional rather than final.
That is all worth borrowing.
What is still not worth cloning is the page contract that leaves the ordinary operator answer spread across IgnoreList, `.sync` internals, RSLS placeholder docs, folder-view columns, and change-detection/power-user articles.

The AnonSync replacement in this revision is four fixed pages:

- `333` for truthful **subject footprint**
- `334` for **metric contract** and drift explanation
- `335` for **completeness confidence**
- `336` for **service residue / clearance review`

The tighter doctrinal answer is:

> a sync product should never make `size`, `present`, `empty`, or `cleared` look self-explanatory when placeholders, exclusions, hidden service bytes, and provisional indexing are all real states.
'''
with open(docs / '10-resilio-sync-evaluation.md', 'a') as f:
    f.write(add_10)

add_20 = '''

## Revision addendum — doctrine 75: counted bytes, resident bytes, and hidden bytes are separate truths

A product that shows one number and one `present/empty` badge for a subject is lying by compression whenever the following can all be true at once:

- some names are only placeholders
- some bytes are excluded from the visible metric
- some managed/history/temp bytes remain on the seat
- some structure is known before payload verification is complete

From this revision onward, AnonSync doctrine requires that **metric contract**, **resident footprint**, **completeness confidence**, and **service residue** are separate inspectable truths.
A subject row may stay compact, but the answer must exist.
'''
with open(docs / '20-product-direction.md', 'a') as f:
    f.write(add_20)

add_30 = '''

## Revision addendum — accounting truth surfaces

Any interface surface that displays a size, count, `present`, `available`, `empty`, or `cleared` label must link to:

- a **metric contract** explanation if the surface shows a number
- a **footprint** explanation if residency matters
- a **completeness confidence** explanation if the answer may be provisional
- a **service residue** explanation if hidden managed bytes still exist

Compact UI is acceptable.
Implicit semantics are not.
'''
with open(docs / '30-interface-spec.md', 'a') as f:
    f.write(add_30)

add_38 = '''

## Revision addendum — workbench accountability for byte truth

The operator workbench should now support four quick pivots from any subject row or subtree pane:

1. `why this size?`
2. `what is actually resident here?`
3. `how complete/current is this answer?`
4. `what managed residue still remains?`

This keeps the workbench from turning hidden folders, support lore, or shell inspection into the real explanation layer.
'''
with open(docs / '38-operator-workbench-interface-spec.md', 'a') as f:
    f.write(add_38)

add_40 = '''

## Revision addendum — ADR: list metrics are contracts, not ornaments

**Decision:** Any displayed size/count metric must have a named contract, and any subject cleanup claim must disclose hidden managed residue.

**Why:** Current Resilio docs are candid that ignored files are not counted, placeholders are 0-byte stand-ins, `.sync` and `.!sync` are real managed byte families, and rescans/hashing can make views provisional. Those truths are valuable; the scattered explanation path is not. AnonSync therefore treats metric meaning and cleanup residue as first-class design objects rather than support notes.
'''
with open(docs / '40-architecture-decisions.md', 'a') as f:
    f.write(add_40)

add_50 = '''

## Revision addendum — next tranche after semantic-tradeoff pages

This revision lands the accounting-confidence tranche that the corpus still lacked:

1. subject footprint so `present bytes`, sparse names, hidden managed bytes, and remote-only knowledge stop collapsing into one vague `size`
2. metric-contract work so every list number says what it includes and excludes
3. completeness-confidence work so provisional enumeration / hashing / source dependence stops impersonating certainty
4. service-residue work so cleanup surfaces stop relying on hidden folders and break/fix lore as the real explanation layer
'''
with open(docs / '50-roadmap.md', 'a') as f:
    f.write(add_50)

add_sources = '''

## Revision addendum — accounting truth, subject footprint, completeness confidence, and hidden residue

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about byte accounting, hidden service state, sparse placeholders, and provisional completeness.
The new questions were:

> where do current official docs most clearly show that Resilio is actually candid about ignored bytes not counting, placeholders being 0-byte stand-ins, hidden `.sync` / Archive / StreamsList / `.!sync` material being real, and rescans / hashing making some answers provisional?

> where do those same docs still show that the ordinary operator answer to `how much is really here?`, `what counts?`, `is this view complete yet?`, and `what hidden bytes remain?` still depends on hopping across IgnoreList, `.sync` internals, RSLS placeholders, folder-view columns, and change-detection / power-user articles rather than one stable page family?

The most load-bearing source set for this pass was:

- Resilio's current IgnoreList article, which still says ignored files are not indexed and not counted in the `Size` column, that rules are case-sensitive, and that post-add IgnoreList edits still leave structural knowledge in the database and passed to peers until disconnect.
- Resilio's current `.sync` article, which still says `.sync` is critical and houses Archive, IgnoreList, StreamsList, and in-flight `.!sync` files.
- Resilio's current RSLS placeholder article, which still says placeholders are 0-byte stand-ins, warns that all peers can end up with placeholders only if every full copy is removed, and distinguishes local revert-to-placeholder from global delete.
- Resilio's current change-detection and power-user articles, which still say watcher quality varies by storage, rescans default to 600 seconds, rescans can be disabled entirely, and advanced settings like `lazy_indexing`, `parallel_indexing`, `folder_rescan_interval`, `max_file_size_for_versioning`, and `free_space_warning_threashold` affect what the product knows and reports.
- Resilio's current folder-view article, which still shows `size` and related columns as optional surface-level numbers without one integrated accounting-contract page.

## Additional Resilio official sources emphasized in rev0181

- Ignoring files in Sync (Ignore List)
  https://help.resilio.com/hc/en-us/articles/205458165-Ignoring-files-in-Sync-Ignore-List

- What is '.sync' folder, and StreamsList, IgnoreList and Archive inside?
  https://help.resilio.com/hc/en-us/articles/206217185-What-is-sync-folder-and-StreamsList-IgnoreList-and-Archive-inside

- What Is an RSLS File?
  https://help.resilio.com/hc/en-us/articles/206115384-What-Is-an-RSLS-File

- How soon does synchronization start?
  https://help.resilio.com/hc/en-us/articles/204754319-How-soon-does-synchronization-start

- Power user preferences
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Folder Types and Management
  https://help.resilio.com/hc/en-us/articles/204762459-Folder-Types-and-Management
'''
with open(docs / 'sources.md', 'a') as f:
    f.write(add_sources)

# Create new update script for provenance
(new_root / 'update_rev0181.py').write_text(Path(__file__).read_text())
