from pathlib import Path
import shutil

root = Path('/mnt/data/rev0179_work/AnonSync-rev0179-2026.03.20.20.28-chronologyauthoritypages')
new_name = 'AnonSync-rev0180-2026.03.20.20.57-semantictradeoffguardpages'
new_root = root.parent / new_name
if new_root.exists():
    shutil.rmtree(new_root)
shutil.copytree(root, new_root)

docs = new_root / 'docs'

# Remove previous updater if present in copy then add new one later if desired.

readme = f'''# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `rev0180`
- Timestamp: `2026.03.20.20.57` (America/New_York)
- Codename: `semantictradeoffguardpages`

## What changed in this revision

This revision continues directly from `rev0179` and does seven concrete things:

1. Re-checks another cluster of current official Resilio Sync docs so the archive's non-clone stance now also covers read-only overwrite semantics, placeholder-delete guardrails, deferred hashing / initial-index readiness, and direct-fastpath transfer tradeoffs.
2. Adds one new **Resilio evaluation** document focused on hidden semantic tradeoffs that currently live in Folder Preferences, the RSLS article, the power-user preferences table, and the internal-tasks warning article.
3. Sharpens the main Resilio evaluation, source notes, and cross-cutting doctrine with a new answer: borrow Resilio's candor about destructive convenience and background work, refuse the page contracts that still make operators reconstruct those tradeoffs from scattered toggles and support prose.
4. Adds four new **interface page specs** for the strongest ordinary seams in this pass: read-only divergence policy, placeholder removal guard, hash readiness, and transfer method.
5. Extends the core interface/workbench language with explicit semantic-tradeoff obligations so GUI, local-web, CLI, mobile, and dense renderings all preserve the same answers about overwrite risk, placeholder fate, deferred readiness, and resume cost.
6. Refreshes product direction, architecture decisions, roadmap notes, status language, and source notes so the new tranche is integrated into the main archive rather than floating beside it.
7. Makes the archive's answer to `why not just clone Resilio here too?` tighter because each no-clone choice now points at a replacement page instead of spreading semantic tradeoffs across hidden settings, warning pages, and file-browser gestures.

## Current conclusion

We **still should not clone Resilio Sync wholesale**.

This pass makes the reason more precise in another ordinary but load-bearing part of the product:

> the parts worth copying from Resilio are still mostly **semantic candor** — explicit read-only overwrite behavior, explicit placeholder-deletion consequences, explicit acknowledgement that hashing/indexing readiness can delay visible progress, and explicit admission that some fast transfer paths sacrifice resume safety — while the parts worth changing are the **page contracts** around destructive convenience and hidden optimization tradeoffs.

That means AnonSync should become **more explicit than Resilio about whether a local change will be overwritten, whether a placeholder delete is local eviction or global destruction, whether bytes are ready for semantic operations yet, and what restart cost a faster transfer method accepts**.

## Recommended reading order

1. `docs/00-status.md`
2. `docs/10-resilio-sync-evaluation.md`
3. `docs/11-resilio-borrow-line-and-non-clone-scorecard.md`
4. `docs/12-resilio-interface-clone-veto-tests-and-page-obligations.md`
5. `docs/27-resilio-semantic-tradeoff-and-hidden-optimization-evaluation.md`
6. `docs/329-read-only-divergence-page-suspension-overwrite-and-added-file-fate-interface-spec.md`
7. `docs/330-placeholder-removal-page-local-evict-global-delete-and-guardrail-policy-interface-spec.md`
8. `docs/331-hash-readiness-page-deferred-indexing-placeholder-rename-and-preseed-gate-interface-spec.md`
9. `docs/332-transfer-method-page-piecewise-resume-direct-fastpath-and-interruption-cost-interface-spec.md`
10. `docs/38-operator-workbench-interface-spec.md`
11. `docs/30-interface-spec.md`
12. `docs/20-product-direction.md`
13. `docs/40-architecture-decisions.md`
14. `docs/50-roadmap.md`
15. `docs/sources.md`

## Archive map for this revision

- `docs/27-resilio-semantic-tradeoff-and-hidden-optimization-evaluation.md` — next-wave Resilio evaluation focused on overwrite semantics, placeholder deletion, deferred hashing/index readiness, and transfer-method tradeoffs
- `docs/329-read-only-divergence-page-suspension-overwrite-and-added-file-fate-interface-spec.md` — fixed page contract for read-only local divergence, overwrite posture, suspended files, and the fate of added files
- `docs/330-placeholder-removal-page-local-evict-global-delete-and-guardrail-policy-interface-spec.md` — fixed page contract for placeholder removal semantics, guardrails, and last-full-copy risk
- `docs/331-hash-readiness-page-deferred-indexing-placeholder-rename-and-preseed-gate-interface-spec.md` — fixed page contract for deferred readiness, placeholder-rename blind spots, and pre-seeded initial-index gates
- `docs/332-transfer-method-page-piecewise-resume-direct-fastpath-and-interruption-cost-interface-spec.md` — fixed page contract for piecewise versus direct transfer behavior, resume cost, and speed/resource tradeoffs

All previously-added documents remain in place; this revision adds the next page tranche and refreshes the cross-cutting doctrine around it.
'''
(new_root / 'README.md').write_text(readme)

status = '''# Status

## Scope of this revision

This revision is an in-place continuation of `rev0179`, driven by the current request and the now-current archive state:

- continue researching rather than merely polishing
- test the `do not clone Resilio wholesale` conclusion against current official docs again
- keep making every non-clone choice earn itself with a specific borrow/adapt/reject reason
- keep writing ordinary page contracts where the archive still has interface-shape gaps rather than only object-model doctrine
- stay narrow: prefer high-leverage operator pages over broad product sprawl
- in this pass specifically, force a cleaner answer for destructive convenience, placeholder removal, deferred readiness, and fastpath transfer tradeoffs

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

The archive now contains:

- Revision: rev0180
- Timestamp: 2026.03.20.20.57 America/New_York
- Codename: semantictradeoffguardpages

- one new Resilio evaluation document:
  - `27-resilio-semantic-tradeoff-and-hidden-optimization-evaluation.md`
- four new interface page specs:
  - `329-read-only-divergence-page-suspension-overwrite-and-added-file-fate-interface-spec.md`
  - `330-placeholder-removal-page-local-evict-global-delete-and-guardrail-policy-interface-spec.md`
  - `331-hash-readiness-page-deferred-indexing-placeholder-rename-and-preseed-gate-interface-spec.md`
  - `332-transfer-method-page-piecewise-resume-direct-fastpath-and-interruption-cost-interface-spec.md`
- refreshed Resilio evaluation and doctrine notes that now extend the non-clone line into overwrite semantics, placeholder-delete guardrails, deferred hashing/index readiness, and transfer-method tradeoffs
- refreshed top-level docs, workbench notes, architecture decisions, roadmap notes, and source notes so the new page tranche is integrated into the archive rather than bolted on

## The new tighter answer in this revision

This pass intentionally leans on another ordinary question that still survives in current Resilio docs:

> when a read-only seat drifts locally, when a placeholder is deleted, when hashes are not ready yet, or when a faster transfer path skips resumable piece logic, where does the product itself own the answers to `what will be overwritten?`, `what will be deleted?`, `what is not semantically ready yet?`, and `what restart cost did I just accept?`

The answer in this revision is:

- **read-only divergence policy** is still too easy to infer from FAQ prose and folder preferences rather than one ordinary page
- **placeholder removal semantics** are still too easy to infer from file-browser gestures, WebUI wording, and hidden guard toggles rather than one fixed review page
- **hash readiness and deferred indexing** are still too easy to infer from power-user settings and an internal-tasks warning rather than one first-class readiness page
- **transfer-method tradeoffs** are still too easy to infer from power-user toggles and background-task descriptions rather than one explicit method/risks page

## Outcome

The archive's current posture stays the same, but the argument is stronger:

- borrow Resilio's candor about destructive convenience and hidden optimization costs
- refuse the exact interface contracts when one ordinary answer still requires cross-reading preferences, power-user tables, warning pages, and RSLS/how-to articles
- replace each refusal with one sharper public page contract
'''
(docs / '00-status.md').write_text(status)

new_eval = '''# Resilio semantic tradeoffs and hidden optimization evaluation

## Why this pass matters

Current official Resilio Sync docs are unusually candid about several semantic tradeoffs that many products hide.
They still say all of the following:

- read-only peers suspend synchronization for files they changed locally unless `Overwrite any changed files` is enabled
- that overwrite option is potentially destructive, restores deleted files, re-downloads the old name after a rename, and leaves added files in place without syncing them
- the same overwrite option is disabled for read-only folders with Selective Sync ON
- placeholder deletion can mean `revert locally to placeholder` or `remove permanently from all peers`, depending on access class and action path
- a power-user preference can prevent placeholder deletion from propagating destruction by recreating placeholders on removal
- `lazy_indexing` can defer hashing until requested, which means a remote placeholder rename will not rename the source peer's file accordingly
- `prioritize_initial_indexing` can intentionally delay syncing on pre-seeded folders until peers finish rescanning
- `direct_torrent_enabled` speeds some small transfers by not breaking files into pieces, but interrupted transfers then restart from the beginning

These are not cosmetic support notes.
They describe one load-bearing truth family: **semantic tradeoff visibility**.

Resilio still has good product substance here.
It is honest that convenience can be destructive, that placeholder actions are not all the same, that some semantic operations need hashing/readiness before they behave well, and that some transfer fastpaths accept worse interruption behavior.

But that honesty is still spread across:

- the read-only / one-way sync FAQ
- Folder Preferences
- the RSLS / placeholder article
- the power-user preferences table
- the internal-tasks warning page

That is a concrete reason not to clone the page contract.

## What Resilio gets right

### 1) It admits read-only is not semantically trivial

Current docs still say a read-only peer can make local changes, that changed files can stop syncing for that peer, and that `Overwrite any changed files` can restore deleted content, re-download renamed content under the old name, and revert edited content.
That is useful honesty.

### 2) It admits placeholder removal is a meaning fork

Current docs still distinguish local revert-to-placeholder from remove-from-all-devices and explicitly warn that deleting a placeholder with read-write access can remove it permanently from all peers.
That is again useful honesty.

### 3) It admits readiness work changes visible behavior

Current docs still say background tasks include block checking, hashing, merge, scan, dedup copy, and read/write work, and that some power-user preferences intentionally defer hashing or hold back syncing on pre-seeded folders until rescans complete.
That is real operator truth.

### 4) It admits some speed paths worsen interruption recovery

Current docs still say `direct_torrent_enabled` can speed small-file transfer by avoiding pieces, but an interrupted transfer then restarts from the beginning.
That is the sort of tradeoff products often hide completely.

## Why we still should not clone it

The core problem is not lack of truth.
The core problem is **where the truth lives**.

Resilio still makes the operator reconstruct one ordinary answer from several separate article families:

- *if this read-only seat drifts locally, what exactly gets suspended, restored, or preserved?*
- *if I delete this placeholder here, is that a local eviction or global destruction?*
- *is this subject actually ready for rename/dedup/semantic operations yet, or is hashing still deferred?*
- *did I just opt into a faster transfer method that will restart from zero if interrupted?*

Those should not be support-article questions.
They should be ordinary product pages.

## The AnonSync borrow line

Borrow from current Resilio:

- explicit candor that read-only overwrite policy can be destructive
- explicit distinction between local placeholder eviction and all-devices delete
- explicit acknowledgement that hashing/readiness gates can delay semantic correctness and visible progress
- explicit acknowledgement that some fast transfer paths sacrifice resume behavior

Adapt into AnonSync:

- one first-class page for **read-only divergence policy**
- one first-class page for **placeholder removal semantics**
- one first-class page for **hash readiness**
- one first-class page for **transfer method**

Refuse to clone from Resilio:

- FAQ-only ownership of read-only overwrite truth
- file-browser-gesture-plus-power-user-toggle ownership of placeholder destruction guardrails
- warning-page-plus-advanced-setting ownership of deferred readiness
- toggle-only ownership of transfer fastpath versus resume sacrifice

## Resulting interface obligations for this revision

This revision therefore adds four replacement page contracts:

1. `329-read-only-divergence-page-suspension-overwrite-and-added-file-fate-interface-spec.md`
2. `330-placeholder-removal-page-local-evict-global-delete-and-guardrail-policy-interface-spec.md`
3. `331-hash-readiness-page-deferred-indexing-placeholder-rename-and-preseed-gate-interface-spec.md`
4. `332-transfer-method-page-piecewise-resume-direct-fastpath-and-interruption-cost-interface-spec.md`

These pages make one ordinary promise explicit:

> An operator should never have to stitch together semantic tradeoff truth from a FAQ, a folder preference, a hidden power-user toggle, a file-browser gesture, and a background-task warning before touching real bytes.
'''
(docs / '27-resilio-semantic-tradeoff-and-hidden-optimization-evaluation.md').write_text(new_eval)

spec329 = '''# Read-only divergence page: suspension, overwrite, and added-file fate interface spec

## Purpose

This page answers one ordinary question:

> when a read-only seat has drifted locally, what exactly is suspended, what would be overwritten, what would remain, and what destructive policy is currently in force?

The page exists because `read-only`, `local edits present`, `overwrite any changed files`, and `safe to keep local extras` are not the same truth.

## Core decision

Every seat must render one first-class **Read-only divergence** page whenever the seat has read-only authority but local divergence exists or may exist.
That page owns:

- local divergence detection
- file-class fate under current policy
- suspension scope
- overwrite posture
- selective-sync incompatibility
- safe next actions

The workbench must not force the operator to infer destructive fate from a tiny checkbox label or a stalled file row.

## Primary layout

The page always renders the same regions in the same order:

1. subject strip
2. divergence summary card
3. fate matrix card
4. policy and incompatibility card
5. safe-action card
6. receipts

### 1) Subject strip

Show:

- subject label
- local seat label
- current verdict: `clean-ro`, `ro-diverged`, `ro-suspended-files`, `ro-overwrite-armed`, `ro-ambiguous`
- one next honest action

### 2) Divergence summary card

This card publishes:

- whether local edits, renames, deletions, or additions have been detected
- which files are currently suspended from ordinary update intake
- whether divergence is file-scoped, folder-scoped, or mixed
- last trustworthy scan/hash time

The operator must be able to answer: **what changed here locally that matters?**

### 3) Fate matrix card

This card publishes one row per divergence class:

- edited file → `kept`, `suspended`, `will revert`, or `unknown`
- renamed file → `local renamed copy remains`, `old name reappears`, `unknown`
- deleted file → `restored`, `left absent`, or `unknown`
- added file → `left local only`, `deleted`, `synced onward`, or `unknown`

The operator must be able to answer: **if I enable overwrite or leave it off, what happens to each class of local change?**

### 4) Policy and incompatibility card

This card publishes:

- current overwrite posture: `off`, `on`, `forced`, `not-available`
- whether Selective Sync currently disables overwrite behavior
- whether the seat is a special custody class that forces overwrite-like behavior
- policy provenance: local setting, inherited default, immutable seat class, or unknown

The operator must be able to answer: **why is this policy available, unavailable, or forced here?**

### 5) Safe-action card

This card publishes:

- least-destructive next actions
- copy-out or preserve-local options before enabling overwrite
- exact effect of `resume intake`, `keep local extras`, `switch posture`, or `promote to writable` if such verbs exist
- post-action retest required for a clean state

The operator must be able to answer: **what is the smallest safe move if I want updates again without accidentally losing local work?**

### 6) Receipts

Receipts show:

- when read-only divergence was first observed
- policy changes acknowledged
- preserve-local exports performed
- overwrite actions applied
- suspension cleared

## Non-negotiable rules

### Rule 1 — read-only must not imply semantically inert

Read-only authority is about outward write rights, not about whether local drift exists.

### Rule 2 — destructive overwrite must publish exact class fate

The page must never say only `changes may be overwritten`.
It must publish edited/renamed/deleted/added outcomes separately.

### Rule 3 — incompatible postures must stay explicit

If Selective Sync or another seat class makes overwrite unavailable, the page must say so directly.

## Honest outputs

The page may conclude:

- `Three files are suspended because this read-only seat edited them locally; overwrite is currently OFF.`
- `Enabling overwrite will restore two deletions, revert one edited file, and keep four added files as local-only extras.`
- `Overwrite is unavailable here because this read-only seat is currently in selective materialization posture.`

It may not collapse those outcomes into one generic `sync conflict` badge.
'''
(docs / '329-read-only-divergence-page-suspension-overwrite-and-added-file-fate-interface-spec.md').write_text(spec329)

spec330 = '''# Placeholder removal page: local evict, global delete, and guardrail policy interface spec

## Purpose

This page answers one ordinary question:

> when I remove this placeholder or partially present file, am I evicting bytes locally, destroying the object everywhere, or invoking a guardrail that converts destruction back into local-only eviction?

The page exists because `Delete`, `Remove from this device`, `Remove from all devices`, and `recreate placeholders on removal` are not the same action.

## Core decision

Every seat must render one first-class **Placeholder removal** page whenever a materialization-reducing or removal action targets a placeholder-capable subject.
That page owns:

- action class
- propagation scope
- last-full-copy risk
- guardrail policy in force
- surface asymmetry
- safe alternatives

The workbench must not force the operator to learn these differences from file-browser context menus or hidden advanced toggles.

## Primary layout

The page always renders the same regions in the same order:

1. subject strip
2. current presence card
3. action semantics card
4. guardrail card
5. last-copy risk card
6. receipts

### 1) Subject strip

Show:

- object label
- current seat label
- current verdict: `local-evict`, `global-delete`, `guarded-evict`, `blocked-delete`, `ambiguous-removal`
- one next honest action

### 2) Current presence card

This card publishes:

- whether the target is placeholder-only, partially materialized, or fully materialized locally
- whether the seat has read-only or read-write destructive authority
- known full-copy witnesses on other seats
- whether subfolder semantics widen the action to descendants

The operator must be able to answer: **what is actually here right now, and who else still has the bytes?**

### 3) Action semantics card

This card publishes:

- candidate action verbs and exact propagation class
- local result after action: removed, reverted to placeholder, unchanged, or blocked
- remote result after action: no change, object deleted, descendants deleted, or unknown
- special-case meaning on surfaces with no shell integration

The operator must be able to answer: **what exactly happens if I press this verb on this surface?**

### 4) Guardrail card

This card publishes:

- whether a removal guardrail is active
- whether destructive delete is being remapped into placeholder recreation / local-only eviction
- scope and provenance of the guardrail: seat default, subject policy, emergency mode, or unknown
- any surfaces where the guardrail is unavailable or bypassed

The operator must be able to answer: **is a safety rail protecting me from accidental all-peer destruction here?**

### 5) Last-copy risk card

This card publishes:

- whether at least one trustworthy other full copy exists
- whether all known seats may already be placeholders only
- risk class: `safe-evict`, `at-risk`, `no-other-full-copy-proven`, `unknown`
- safer alternatives such as hold, fetch elsewhere, or verify another witness first

The operator must be able to answer: **am I about to turn the last real bytes into zero-byte promises?**

### 6) Receipts

Receipts show:

- action previews acknowledged
- delete/evict conversions performed
- last-copy proof checks performed
- actual propagation result observed

## Non-negotiable rules

### Rule 1 — local eviction and global destruction must never share one unlabeled affordance

The page must keep them separate even if the current surface historically conflated them.

### Rule 2 — safety rails must be visible

If a hidden setting or seat policy remaps deletion into placeholder recreation, the page must say so plainly.

### Rule 3 — last-copy uncertainty must block casual language

The UI must not say `remove from this device` casually when no other trustworthy full copy is proven.

## Honest outputs

The page may conclude:

- `This action will evict local bytes only and leave a placeholder because a delete guardrail is active.`
- `Deleting this placeholder with current authority would remove the object from all peers.`
- `No other full-copy witness is currently proven; local eviction is blocked until another seat is verified.`

It may not collapse those outcomes into a single `remove` button label.
'''
(docs / '330-placeholder-removal-page-local-evict-global-delete-and-guardrail-policy-interface-spec.md').write_text(spec330)

spec331 = '''# Hash readiness page: deferred indexing, placeholder rename, and preseed gate interface spec

## Purpose

This page answers one ordinary question:

> is this subject semantically ready for rename, dedup, and ordinary sync reasoning yet, or are hashing/indexing gates still withholding stronger guarantees?

The page exists because `visible in the tree`, `scanned`, `hashed`, `ready for placeholder-driven rename`, and `allowed to start syncing from a pre-seeded population` are not the same truth.

## Core decision

Every seat must render one first-class **Hash readiness** page whenever readiness is materially affected by deferred hashing, pre-seeded indexing, or related semantic gates.
That page owns:

- scan versus hash state
- deferred-index policy
- semantic consequences of incomplete readiness
- placeholder-rename capability
- pre-seeded holdback posture
- safe release and retest actions

The workbench must not force the operator to infer semantic readiness from vague `internal tasks` warnings or slow-but-healthy progress rows.

## Primary layout

The page always renders the same regions in the same order:

1. subject strip
2. readiness ladder card
3. semantic consequence card
4. preseed gate card
5. release and retest card
6. receipts

### 1) Subject strip

Show:

- subject label
- current seat label
- current verdict: `tree-visible-only`, `scanned-not-hashed`, `partially-hashed`, `semantically-ready`, `preseed-held`, `ambiguous-readiness`
- one next honest action

### 2) Readiness ladder card

This card publishes:

- observation phase reached: discovered, scanned, hashed, merge-stable, transfer-ready
- whether hashing is eager, deferred, or remote-demand-triggered
- current counts or proportions where available
- last progress witness and stall/slow distinction

The operator must be able to answer: **how far along the semantic-readiness ladder is this subject really?**

### 3) Semantic consequence card

This card publishes:

- which behaviors are safe now and which are not yet trustworthy
- whether remote placeholder rename can currently replay correctly to this seat or from this seat
- whether dedup/local-block copy can already rely on local evidence
- whether background warnings are merely load-related or indicate a harder stall

The operator must be able to answer: **what meaning is still degraded because hashing/indexing is not done?**

### 4) Preseed gate card

This card publishes:

- whether the subject is a pre-seeded intake currently held until rescans complete
- which peers still need to finish rescanning
- whether the gate is a performance policy, correctness policy, or unknown mix
- exact effect on upload/download start and semantic operations

The operator must be able to answer: **why is this pre-populated subject waiting even though bytes already exist locally?**

### 5) Release and retest card

This card publishes:

- least-destructive actions to wait, nudge, or widen resources
- whether changing readiness policy sacrifices semantic guarantees
- minimum retest that proves placeholder rename or dedup readiness is now available
- any actions that are intentionally blocked until stronger readiness exists

The operator must be able to answer: **what can I safely do next, and what would be premature?**

### 6) Receipts

Receipts show:

- readiness-policy changes
- preseed hold acknowledgments
- retests performed
- semantic capability becoming available

## Non-negotiable rules

### Rule 1 — tree visibility must not impersonate semantic readiness

Seeing names is not the same as being ready for rename/dedup/transfer claims.

### Rule 2 — deferred hashing must publish behavior loss, not just performance intent

If a setting improves indexing behavior while losing placeholder-rename correctness or delaying proof, that must be explicit.

### Rule 3 — slow healthy work must stay distinct from a hard stall

A background-task warning should route here, where the product can say whether work is intermittent-but-progressing or blocked.

## Honest outputs

The page may conclude:

- `Names are visible and scanned, but hashes are still deferred; placeholder-driven rename is not yet trustworthy.`
- `This pre-seeded subject is intentionally held until two peers finish rescanning.`
- `Background work is heavy but healthy; hashing and merge are still advancing.`

It may not collapse those outcomes into a vague `please wait` spinner.
'''
(docs / '331-hash-readiness-page-deferred-indexing-placeholder-rename-and-preseed-gate-interface-spec.md').write_text(spec331)

spec332 = '''# Transfer method page: piecewise resume, direct fastpath, and interruption cost interface spec

## Purpose

This page answers one ordinary question:

> what transfer method is this subject using right now, why did that method win, and what interruption, resume, CPU, memory, or delta-sacrifice costs come with it?

The page exists because `fast`, `direct`, `piecewise`, `dedup`, and `resumable` are not the same truth.

## Core decision

Every seat must render one first-class **Transfer method** page whenever method choice materially affects recovery, cost, or correctness expectations.
That page owns:

- winning method
- why it won
- interruption cost
- resource tradeoffs
- fallbacks and better alternatives
- receipts

The workbench must not force the operator to infer method consequences from a hidden toggle or a transfer that mysteriously restarted from zero.

## Primary layout

The page always renders the same regions in the same order:

1. subject strip
2. winning-method card
3. interruption and resume card
4. cost-profile card
5. better-method counterfactual card
6. receipts

### 1) Subject strip

Show:

- subject label
- peer pair or cohort
- current verdict: `piecewise-resumable`, `direct-fastpath`, `local-dedup`, `mixed-method`, `ambiguous-method`
- one next honest action

### 2) Winning-method card

This card publishes:

- current method in force
- method provenance: default, subject policy, adaptive threshold, emergency fallback, or unknown
- file-size / workload condition that selected it
- whether delta/piece logic is active, bypassed, or unavailable

The operator must be able to answer: **what transfer strategy is actually happening now, and why?**

### 3) Interruption and resume card

This card publishes:

- resume posture after interruption: piece-resume, whole-file restart, local-copy restart, or unknown
- last interruption witness if any
- expected loss if interrupted now
- whether restart-from-zero is an accepted cost of the current fastpath

The operator must be able to answer: **if this stops halfway, what starts over and what survives?**

### 4) Cost-profile card

This card publishes:

- likely bandwidth, CPU, memory, and disk effects of the current method
- whether the method favors lower latency, fewer requests, lower disk work, or better resume behavior
- whether local dedup/block-copy is participating instead of re-download
- any explicit thresholds or limits that matter

The operator must be able to answer: **what resource tradeoff did the product just make for me?**

### 5) Better-method counterfactual card

This card publishes:

- a better alternative method if one plausibly exists
- what policy or condition would need to change to use it
- what would be gained and lost by switching
- whether the current method is merely faster, merely cheaper, or semantically safer

The operator must be able to answer: **is there a different method that would better match my priority right now?**

### 6) Receipts

Receipts show:

- method changes acknowledged
- interruptions observed
- restarts from zero
- successful resumptions
- policy changes that altered method choice

## Non-negotiable rules

### Rule 1 — speed claims must publish recovery cost

A faster method is incomplete information unless the page also says what happens on interruption.

### Rule 2 — method choice must be public state

The product must not make the operator guess whether a file is using piecewise transfer, direct fastpath, or local-copy reuse.

### Rule 3 — cost profile must name the dominant sacrifice

When the current method favors speed, it must say whether the sacrifice is resume behavior, extra CPU, extra memory, extra disk work, or something else.

## Honest outputs

The page may conclude:

- `Current method is direct fastpath; interruption would restart the whole file from the beginning.`
- `Current method is piecewise resumable; slower request overhead is accepted to preserve partial progress.`
- `This subject is currently satisfying bytes through local block copy, not network transfer.`

It may not collapse those outcomes into a bare `transferring` label.
'''
(docs / '332-transfer-method-page-piecewise-resume-direct-fastpath-and-interruption-cost-interface-spec.md').write_text(spec332)

# Update other docs by appending concise addenda.
append_map = {
    docs / '10-resilio-sync-evaluation.md': '''\n\n## Semantic tradeoffs and hidden optimization truth after rev0180\n\nAnother current no-clone seam is now concrete.\nResilio's official docs are fairly candid that:\n\n- read-only overwrite can be destructive and has class-specific outcomes for edits, renames, deletions, and added files\n- placeholder deletion can mean local eviction or global destruction depending on access and verb\n- hidden settings can remap placeholder deletion into safety-biased placeholder recreation\n- deferred hashing and initial-index policies change when subjects are semantically ready for rename, dedup, and ordinary sync behavior\n- some fast transfer paths accept whole-file restart on interruption\n\nThat is useful product honesty.\nIt is also a good reason not to clone the page contract, because one ordinary answer still requires stitching together a FAQ, Folder Preferences, the RSLS article, the power-user table, and the internal-tasks warning page.\n\nThe right AnonSync response is therefore:\n\n- borrow the candor\n- refuse the toggle-and-article ownership model\n- replace it with four ordinary pages: **Read-only divergence**, **Placeholder removal**, **Hash readiness**, and **Transfer method**\n''',
    docs / '20-product-direction.md': '''\n\n## Revision addendum — semantic-tradeoff and hidden-optimization pages after rev0180\n\nThe product direction now owes four more explicit ordinary surfaces:\n\n- **Read-only divergence** so suspension, overwrite posture, and added-file fate stop living in FAQ folklore\n- **Placeholder removal** so local eviction, global delete, and delete-guard remapping remain visibly distinct\n- **Hash readiness** so scanned, hashed, semantically ready, and preseed-held remain separate truths\n- **Transfer method** so speed/resume/resource tradeoffs are inspectable instead of hidden behind adaptive behavior or advanced toggles\n\nNear-term direction should keep four doctrine choices explicit:\n\n1. **read-only does not mean semantically quiet** — local drift, suspension, and destructive overwrite risk must stay public\n2. **removal intent and destruction scope are separate truths** — placeholder eviction must never masquerade as object destruction or vice versa\n3. **visibility is not readiness** — seeing names or progress is not the same as having enough hash/index evidence for semantic operations\n4. **speed is not free** — fastpath transfer choices must publish their interruption and recovery cost\n''',
    docs / '30-interface-spec.md': '''\n\n## Revision addendum — semantic-tradeoff page families after rev0180\n\nThe interface corpus now explicitly requires four additional ordinary pages whenever convenience or optimization changes semantic behavior:\n\n1. **Read-only divergence** — local drift classes, suspension scope, overwrite posture, and preserve-local actions\n2. **Placeholder removal** — local evict versus global delete, guardrail policy, and last-full-copy risk\n3. **Hash readiness** — scan/hash ladder, semantic capability loss, preseed holdbacks, and release proof\n4. **Transfer method** — winning method, interruption cost, resource profile, and better-method counterfactual\n\nThese are required because destructive convenience and hidden optimization are not advanced-user trivia; they are ordinary operator truths.\n''',
    docs / '38-operator-workbench-interface-spec.md': '''\n\n## Revision addendum — workbench support for semantic-tradeoff pages after rev0180\n\nThe workbench now owes four more ordinary page families whenever convenience or optimization changes semantic behavior:\n\n- one fixed **Read-only divergence** page so suspended files, overwrite posture, and added-file fate can be opened directly from any drifted read-only seat\n- one fixed **Placeholder removal** page so remove/evict/delete gestures route through one explicit propagation and last-copy review\n- one fixed **Hash readiness** page so background work, deferred hashing, and preseed holdbacks can be inspected without leaving the workbench\n- one fixed **Transfer method** page so speed/resume/resource tradeoffs are visible from live transfer lanes instead of hidden behind progress bars\n\nThese are ordinary workbench obligations for any honest sync product.\n''',
    docs / '40-architecture-decisions.md': '''\n\n## ADR-097 — Semantic tradeoffs from convenience or optimization need first-class pages\n\n**Decision:** Model read-only overwrite behavior, placeholder-removal scope, hash/index readiness, and transfer-method recovery cost as first-class product objects with receipts.\n\n**Why:** Current Resilio docs still spread these truths across the read-only FAQ, Folder Preferences, the RSLS article, the power-user table, and the internal-tasks warning page. That is candid support knowledge. It is not one durable operator contract.\n\n**Consequences:**\n\n- read-only drift can publish exact class fate before any destructive overwrite is armed\n- placeholder removal can separate local eviction, global delete, and guardrail remap explicitly\n- readiness can separate scanned names from semantically trustworthy operations like placeholder rename or preseed release\n- fast transfer can publish interruption and restart cost alongside speed claims\n''',
    docs / '50-roadmap.md': '''\n\n## Revision addendum — semantic-tradeoff tranche after rev0180\n\nThis revision adds another narrow but high-leverage requirement set:\n\n- operators can tell what local drift on a read-only seat will be suspended, restored, preserved, or overwritten before policy changes are applied\n- operators can tell whether removing a placeholder is local eviction, global destruction, or a safety-biased remap\n- operators can tell whether a subject is merely visible, actually hashed, semantically ready, or intentionally held while preseed rescans complete\n- operators can tell what transfer method is in force and what restart cost an interruption would impose\n''',
}
for path, text in append_map.items():
    path.write_text(path.read_text() + text)

# Prepend a new section to sources, keeping existing content intact.
sources_path = docs / 'sources.md'
old_sources = sources_path.read_text()
new_sources_head = '''## Revision addendum — semantic tradeoffs, destructive convenience, and hidden optimization truth\n\nThis revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about read-only overwrite behavior, placeholder removal, deferred hashing / preseed readiness, and transfer-method tradeoffs.\nThe new questions were:\n\n> where do current official docs most clearly show that Resilio is actually fairly candid about destructive convenience and hidden optimization costs?\n\n> where do those same current docs still show that the ordinary operator answer about `what will be overwritten?`, `what will be deleted?`, `what is not semantically ready yet?`, and `what interruption cost did I just accept?` still depends on hopping across FAQs, preferences, power-user tables, RSLS/how-to pages, and warning articles rather than one stable page?\n\nThe most load-bearing source set for this pass was:\n\n- Resilio's current read-only / one-way sync, user-management, and folder-preferences docs, which still say local changes on read-only seats can suspend synchronization, that `Overwrite any changed files` can be destructive, and that the precise fate of renamed, deleted, edited, and added files differs by class.\n- Resilio's current RSLS / Selective Sync docs, which still distinguish local revert-to-placeholder from remove-from-all-devices and still warn that placeholder-only meshes can leave no actual bytes anywhere.\n- Resilio's current power-user preferences and internal-tasks docs, which still expose `lazy_indexing`, `prioritize_initial_indexing`, `direct_torrent_enabled`, and `recreate_placeholders_on_removal`, and still explain that hash/check/merge/copy work materially changes visible behavior without necessarily meaning the product is stuck.\n\n## Additional Resilio official sources emphasized in rev0180\n\n- Power user preferences  \n  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences\n\n- Folder Preferences  \n  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences\n\n- Is one-way synchronization possible?  \n  https://help.resilio.com/hc/en-us/articles/204754279-Is-one-way-synchronization-possible\n\n- What Is an RSLS File?  \n  https://help.resilio.com/hc/en-us/articles/206115384-What-Is-an-RSLS-File\n\n- Selective Sync  \n  https://help.resilio.com/hc/en-us/articles/205458095-Selective-Sync\n\n- Some internal tasks are taking time to complete  \n  https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete\n\n- My files don't sync  \n  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync\n\n'''
sources_path.write_text(new_sources_head + old_sources)

# update main resilio scorecard note and status maybe minimal by appending to borrow-line scorecard
scorecard = docs / '11-resilio-borrow-line-and-non-clone-scorecard.md'
scorecard.write_text(scorecard.read_text() + '''\n\n## Additional current borrow/adapt boundary after rev0180\n\nCurrent official docs also support one more now-clear line:\n\n- **Borrow** the candor that destructive convenience and optimization have semantic cost.\n- **Adapt** read-only overwrite, placeholder-evict safety rails, deferred readiness, and transfer-method choice into first-class pages.\n- **Do not clone** a product contract where those meanings still live in a FAQ, Folder Preferences, RSLS instructions, power-user toggles, and warning prose.\n''')

# add update script itself from the generated file contents? already this file in original tree copied. keep as update_rev0180.py in new_root and maybe delete old copy's content irrelevant? This file is this script.

