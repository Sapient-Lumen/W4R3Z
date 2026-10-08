#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / 'docs'

REV = 'rev0198'
TIMESTAMP = '2026.03.21.05.28'
CODENAME = 'servicespinesidecarpages'
NEW_DOCS = [
    '416-resilio-subject-spine-sidecars-and-hidden-authority-evaluation.md',
    '417-subject-spine-page-payload-vs-service-namespace-and-portability-boundary-interface-spec.md',
    '418-sidecar-policy-page-ignore-streams-locality-and-peer-agreement-interface-spec.md',
    '419-spine-integrity-page-id-authority-foreign-runtime-and-rebind-boundary-interface-spec.md',
    '420-managed-hidden-bytes-page-archive-inflight-stubs-and-safe-browse-interface-spec.md',
]

README_TEXT = f'''# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `{REV}`
- Timestamp: `{TIMESTAMP}` (America/New_York)
- Codename: `{CODENAME}`

## What changed in this revision

This revision continues directly from `rev0197` and does seven concrete things:

1. Re-checks another cluster of current official Resilio Sync docs so the archive's non-clone stance now also covers hidden subject spines, sidecar policy files, xattr whitelist sidecars, continuity-bearing ID state, unsupported instance cloning, and safe handling of managed hidden bytes.
2. Adds one new **Resilio evaluation** document focused on how current Resilio still spreads the ordinary answer to `what inside this folder is product-owned, portable, local-only, damaged, or safe to touch?` across `.sync` FAQ material, IgnoreList docs, xattr docs, service-file warnings, troubleshooting notes, move/rename limits, and the cloning warning.
3. Sharpens the main non-clone argument with a tighter claim: borrow Resilio's candor that sync subjects really do have hidden product-owned state, but refuse any contract where continuity-bearing sidecars, local-only policy text, in-flight partials, stream stubs, and repair rituals still have to be reconstructed from hidden filesystem artifacts and scattered articles.
4. Adds four new **interface page specs** for the strongest seams in this pass: subject spine, sidecar policy, spine integrity, and managed hidden bytes.
5. Extends the interface/workbench doctrine so every subject can expose `payload vs service namespace`, `subject-wide vs local-only sidecars`, `preserved vs recreated continuity`, and `safe browse vs unsafe manual mutation` without forcing operators into hidden-folder archaeology.
6. Refreshes product direction, scorecard, clone-veto tests, architecture decisions, roadmap notes, pattern language, and source notes so the new tranche is integrated into the archive rather than bolted on.
7. Makes the archive's answer to `why not just clone Resilio here too?` tighter because each no-clone choice now points at a replacement page instead of leaning on folklore about `.sync`, `IgnoreList`, `StreamsList`, `.!sync`, or `Service files missing`.

## Current conclusion

We **still should not clone Resilio Sync wholesale**.

This pass makes the reason more precise in another ordinary but load-bearing part of the product:

> the parts worth copying from Resilio are still mostly **operational candor** — explicit acknowledgement that a sync subject really does carry hidden service state, explicit distinction between IgnoreList and StreamsList, explicit admission that `.sync` loss suspends continuity, and explicit warning that naive cloning or duplicate runtimes can corrupt that state — while the parts worth changing are the **page contracts** around what exactly is product-owned inside the subject tree, which sidecars are local policy versus shared continuity, and what repair preserves continuity versus recreates it.

That means AnonSync should become **more explicit than Resilio about whether a byte family is payload, continuity spine, local policy sidecar, xattr carriage sidecar, archive history, or in-flight residue — before the operator edits, moves, purges, clones, or rebinds anything.**

## Recommended reading order

1. `docs/00-status.md`
2. `docs/10-resilio-sync-evaluation.md`
3. `docs/11-resilio-borrow-line-and-non-clone-scorecard.md`
4. `docs/12-resilio-interface-clone-veto-tests-and-page-obligations.md`
5. `docs/416-resilio-subject-spine-sidecars-and-hidden-authority-evaluation.md`
6. `docs/417-subject-spine-page-payload-vs-service-namespace-and-portability-boundary-interface-spec.md`
7. `docs/418-sidecar-policy-page-ignore-streams-locality-and-peer-agreement-interface-spec.md`
8. `docs/419-spine-integrity-page-id-authority-foreign-runtime-and-rebind-boundary-interface-spec.md`
9. `docs/420-managed-hidden-bytes-page-archive-inflight-stubs-and-safe-browse-interface-spec.md`
10. `docs/38-operator-workbench-interface-spec.md`
11. `docs/30-interface-spec.md`
12. `docs/20-product-direction.md`
13. `docs/40-architecture-decisions.md`
14. `docs/50-roadmap.md`
15. `docs/sources.md`

## Archive map for this revision

- `docs/416-resilio-subject-spine-sidecars-and-hidden-authority-evaluation.md`
- `docs/417-subject-spine-page-payload-vs-service-namespace-and-portability-boundary-interface-spec.md`
- `docs/418-sidecar-policy-page-ignore-streams-locality-and-peer-agreement-interface-spec.md`
- `docs/419-spine-integrity-page-id-authority-foreign-runtime-and-rebind-boundary-interface-spec.md`
- `docs/420-managed-hidden-bytes-page-archive-inflight-stubs-and-safe-browse-interface-spec.md`

The rest of the archive remains in place and is updated in-place where the new tranche changes doctrine.
'''

STATUS_TEXT = f'''# Status

## Scope of this revision

This revision is an in-place continuation of `rev0197`, driven by the current request and the now-current archive state:

- continue researching rather than merely polishing
- evaluate Resilio Sync again rather than relying on a stale caricature
- make every `do not clone` decision point point to a better replacement page
- keep writing concrete interface contracts where the archive still has page-shape gaps
- stay narrow: prefer ordinary operator authority and lifecycle surfaces over broad product sprawl
- in this pass specifically, force a cleaner answer for hidden subject spine, local sidecars, continuity-bearing service state, and safe visibility of managed hidden bytes

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

The archive now contains:

- Revision: {REV}
- Timestamp: {TIMESTAMP} America/New_York
- Codename: {CODENAME}

- one new Resilio evaluation document:
  - `416-resilio-subject-spine-sidecars-and-hidden-authority-evaluation.md`
- four new interface page specs:
  - `417-subject-spine-page-payload-vs-service-namespace-and-portability-boundary-interface-spec.md`
  - `418-sidecar-policy-page-ignore-streams-locality-and-peer-agreement-interface-spec.md`
  - `419-spine-integrity-page-id-authority-foreign-runtime-and-rebind-boundary-interface-spec.md`
  - `420-managed-hidden-bytes-page-archive-inflight-stubs-and-safe-browse-interface-spec.md`
- refreshed doctrine notes that now extend the non-clone line into hidden service namespace truth, local-vs-shared sidecar policy, continuity-bearing ID authority, unsupported duplicate runtime ownership, and safe browse/edit contracts for managed hidden bytes
- refreshed top-level docs, workbench notes, architecture decisions, roadmap notes, pattern-language notes, and source notes so the new page tranche is integrated into the archive rather than bolted on

## The new tighter answer in this revision

This pass intentionally leans on another ordinary question that still survives in current Resilio docs:

> when an operator opens a syncing folder, what inside it is really payload, what is product-owned hidden state, which sidecars are local policy, which hidden artifacts are safe to inspect but unsafe to edit, and which repairs preserve continuity instead of recreating it?

The answer in this revision is:

- **hidden service-spine candor** is still useful and worth borrowing
- **IgnoreList / StreamsList candor** is still useful and worth borrowing
- **ID-file / duplicate-runtime corruption candor** is still useful and worth borrowing
- **stuck partial / stream-stub / archive visibility candor** is still useful and worth borrowing
- **ordinary hidden-state truth** is still too easy to reconstruct from FAQ pages, sidecar docs, troubleshooting notes, move/rename limits, and the cloning warning rather than one stable product-owned page
- **payload-vs-service boundary truth** is still too easy to hide behind raw filesystem visibility instead of one exact page
- **local-sidecar authority truth** is still too easy to infer from text files rather than one exact review surface
- **preserved-versus-recreated continuity truth** is still too easy to scatter across error and repair prose instead of one exact review page

## Outcome

The archive's current posture stays the same, but the argument is stronger:

- borrow Resilio's candor about hidden service state, sidecar policy files, xattr whitelist handling, and continuity damage
- refuse the exact interface contracts when one ordinary answer about `what is product-owned here?`, `what do these sidecars mean?`, `did continuity survive?`, or `is this hidden byte safe to touch?` still requires cross-reading hidden-folder docs, ignore docs, xattr docs, troubleshooting notes, move/rename caveats, and cloning warnings
- replace each refusal with one sharper public page contract

## Latest addendum — subject spine, sidecars, and hidden authority after rev0197

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **hidden subject-state truth**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer can depend on:

- whether a byte family lives in payload, `.sync`, `.sync/Archive`, `.sync/Streams`, or `.!sync`
- whether a sidecar is continuity-bearing or merely local policy text
- whether sidecars agree across peers or intentionally differ
- whether damage means true continuity loss, duplicate runtime ownership, or just a recoverable rebind

So the tighter non-clone line is:

> borrow Resilio's candor that sync subjects really do carry hidden service state, but refuse any product contract where `what is product-owned here`, `which sidecar controls this behavior`, `did continuity survive`, and `what is safe to touch` still require filesystem archaeology across FAQ, sidecar, troubleshooting, and repair pages.

That yields four more ordinary product-owned pages:

- **Subject spine**
- **Sidecar policy**
- **Spine integrity**
- **Managed hidden bytes**
'''

DOC_TEXTS = {
    '416-resilio-subject-spine-sidecars-and-hidden-authority-evaluation.md': '''# Resilio subject-spine, sidecars, and hidden-authority evaluation

## What current official docs still make clear

Another current Resilio pass again strengthens the main archive conclusion rather than weakening it.

Current official docs still show real product substance:

- a live v3 line with `3.1.2.1076`
- explicit admission that every synced folder gets a hidden `.sync` directory and that this directory is critical for syncing
- explicit admission that `.sync` contains several different managed families at once: folder identity, IgnoreList, StreamsList, Archive, and in-flight `.!sync` names
- explicit admission that IgnoreList is a UTF-8 text sidecar, that ignored files are not indexed and not counted in the visible size column, that matching is case-sensitive, and that peers may differ even if that later causes operator confusion
- explicit admission in troubleshooting guidance that ignore disagreement can itself explain sync divergence and that peers effectively need to agree on what should be skipped
- explicit admission that StreamsList is a separate whitelist sidecar for xattrs / alternate streams, that xattrs cannot be ignored through IgnoreList, and that when a filesystem cannot store xattrs properly Sync creates stub material in `.sync/Streams`
- explicit admission that `Service files missing` suspends synchronization for the subject and can come from deleting/corrupting `.sync` or from two Sync instances touching the same subject on one machine or external drive
- explicit admission that one documented repair path is effectively `export what matters, delete .sync, remove/re-add the share`, which recreates a fresh subject instance rather than magically proving preserved continuity
- explicit admission that moving the subject itself is platform-constrained and can break continuity if done across the wrong boundary
- explicit admission that cloning an entire Sync instance by disk copy / Time Machine / cloner is unsupported and can produce multiple strange, non-converging instances

That is not fake candor.
It is very useful operator truth.

## What still should not be cloned

The ordinary operator answer is still fragmented.
Current docs still require cross-reading at least seven places to answer four basic questions:

1. **What inside this folder is really payload, and what is product-owned hidden state?**
2. **Which hidden sidecars are local policy, which are continuity-bearing, and which affect only metadata carriage?**
3. **If hidden state is damaged or duplicated, did continuity survive or am I really creating a new subject epoch?**
4. **Which hidden byte families are safe to inspect, safe to clear, unsafe to edit, or only safe to touch through reviewed product actions?**

Resilio still has strong ideas here.
It still does **not** earn direct interface cloning.

The reason is the same clone-veto rule now applied to another seam:

> one ordinary operator question should have one stable page answer.

Current Resilio still spreads the ordinary hidden-state answer across FAQ prose, IgnoreList docs, xattr docs, service-file warnings, troubleshooting notes, move/rename caveats, and cloning warnings.
So the product idea stays strong while the page contract still fails.

## Why this matters for AnonSync

AnonSync should borrow four important habits directly:

- **say openly that a sync subject has product-owned state as well as payload bytes**
- **say openly that sidecars can differ in meaning: continuity, local policy, metadata carriage, history, or in-flight residue**
- **say openly when damage forces a recreated subject epoch rather than preserved continuity**
- **say openly which hidden byte families are safe to browse but not safe to mutate by hand**

But AnonSync should refuse four weaker habits:

- learning the subject's managed namespace primarily by looking inside hidden folders
- treating local sidecar text as the main semantic home of exclusion or xattr policy
- burying preserved-versus-recreated continuity behind repair folklore
- requiring raw filesystem spelunking to understand archive, stream stubs, or stuck partials

## Replacement pages added for this seam

This revision therefore adds four narrower replacement pages:

- `417` — Subject spine
- `418` — Sidecar policy
- `419` — Spine integrity
- `420` — Managed hidden bytes

These pages keep the Resilio candor and reject the hidden-folder reconstruction path.

## Sharper non-clone line after this pass

The archive now has one tighter sentence for this seam:

> borrow Resilio's candor that sync subjects really do carry hidden service state, local policy sidecars, xattr-carriage sidecars, and continuity-bearing identifiers; refuse any interface contract where `what is product-owned here`, `what sidecar controls this`, `did continuity survive`, and `what hidden bytes are safe to touch` still depends on filesystem archaeology across FAQs, troubleshooting articles, and repair notes.
''',
    '417-subject-spine-page-payload-vs-service-namespace-and-portability-boundary-interface-spec.md': '''# Subject spine page — payload vs service namespace and portability boundary interface spec

## Purpose

The archive already had service-material, residue, path continuity, and history language.
What it still lacked was one ordinary page for the simpler question:

> when I look at this subject as a folder/tree, which bytes are payload, which bytes are managed service namespace, which parts must move with the subject for continuity, and which location changes create a new epoch instead of preserving the old one?

Current official Resilio docs make this seam concrete.
They still say every subject gets a hidden `.sync` directory, that the directory carries multiple managed families, that moving the subject is only supported across certain boundaries, and that losing or separating the managed directory breaks continuity.
That is useful truth.
It should not remain scattered.

## Core decision

AnonSync must expose one first-class **Subject spine** page for every subject.

The page exists to answer five things in one place:

1. where payload namespace ends and managed namespace begins
2. which managed families are continuity-bearing, local policy, history, or transient residue
3. which managed families travel with the subject during supported moves
4. which move / rename / rehome actions preserve the same subject epoch
5. which tempting filesystem edits are observations only and which are dangerous mutations

## Fixed page order

1. **Current boundary verdict**
2. **Namespace map**
3. **Managed family roles**
4. **Portability and move boundary**
5. **Safe observation vs mutation rules**

### 1) Current boundary verdict

Show:

- `subject_spine_page_id`
- subject scope
- current `spine_verdict` (`healthy-and-explicit`, `healthy-but-hidden`, `mixed-local-policy`, `damaged`, `foreign-owned`, `unknown`)
- strongest honest summary
- last materially spine-shaping event time

The operator must be able to answer:

> what kind of subject namespace am I looking at right now?

### 2) Namespace map

Show rows for the major namespace families:

- payload bytes
- continuity spine
- local policy sidecars
- metadata-carriage sidecars
- history / rollback bytes
- transient in-flight bytes

Each row must show:

- location class
- visibility class (`normal`, `managed-hidden`, `hidden-but-browsable`, `diagnostic-only`)
- whether the family should move with the subject
- whether manual deletion is ever safe

### 3) Managed family roles

Show a card for each family with:

- family name
- why it exists
- whether it is subject-wide or seat-local
- whether it is continuity-bearing
- whether recreation preserves continuity or only recreates capability

This section must make `continuity spine` visibly different from `local sidecar policy`.

### 4) Portability and move boundary

Show:

- currently supported rename/move classes
- supported within-same-root or within-same-parent moves
- unsupported cross-boundary moves that force detach/rebind
- whether current storage class changes the rule
- strongest continuity witness after a move

The page must answer:

> if I move or rename this thing, do I still have the same subject afterward?

### 5) Safe observation vs mutation rules

Actions may include:

- `Browse managed namespace`
- `Open sidecar policy page`
- `Open spine integrity page`
- `Review rehome plan`
- `Export history before rebind`
- `Do not edit by hand`

Each action must preview the continuity delta and its non-effects.

## Public object

### Subject spine page

Fields:

- `subject_spine_page_id`
- `subject_ref`
- `spine_verdict`
- `namespace_family_rows[]`
- `move_boundary_rows[]`
- `continuity_bearing_components[]`
- `safe_observation_actions[]`
- `dangerous_manual_mutations[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. subject
2. spine verdict
3. dominant managed family risk
4. move-preservation verdict
5. next least-widening action

Example:

```text
Project Alpha     healthy-but-hidden     continuity spine present     rename local / rehome reviewed only     Open subject spine
```

## Non-goals

This page does **not** replace residue cleanup, exclusion editing, or history restore pages.
It proves only the current **subject spine boundary** and how continuity travels with it.
''',
    '418-sidecar-policy-page-ignore-streams-locality-and-peer-agreement-interface-spec.md': '''# Sidecar policy page — ignore, streams, locality, and peer-agreement interface spec

## Purpose

The archive already had exclusion, metadata-stream, and policy-lineage work.
What it still lacked was one ordinary page for the simpler question:

> which hidden sidecar files currently shape what this subject indexes, counts, or preserves for metadata carriage, and are those sidecars local-only, aligned across peers, or drifting dangerously?

Current official Resilio docs make this seam concrete.
They still say IgnoreList lives in hidden `.sync`, that ignored files are not indexed or counted, that matching is case-sensitive, that peers may differ, that troubleshooting later treats ignore disagreement as a real cause of divergence, that StreamsList separately whitelists xattrs, and that xattrs cannot be ignored through IgnoreList.
That is useful truth.
It should not remain scattered.

## Core decision

AnonSync must expose one first-class **Sidecar policy** page for every subject that supports hidden policy sidecars or carriage sidecars.

The page exists to answer five things in one place:

1. which sidecar families are active now
2. whether each sidecar is seat-local, subject-wide, imported, or temporary
3. what indexing, accounting, and fidelity consequences follow from the current entries
4. whether peer agreement is aligned, intentionally divergent, or risky
5. what reviewed edit would change the effective policy without forcing filesystem spelunking

## Fixed page order

1. **Current sidecar verdict**
2. **Active sidecar families**
3. **Rule locality and agreement**
4. **Accounting and fidelity effects**
5. **Reviewed mutation draft**

### 1) Current sidecar verdict

Show:

- `sidecar_policy_page_id`
- subject scope
- current `sidecar_verdict` (`baseline-only`, `custom-local`, `custom-shared`, `intentional-divergence`, `unsafe-drift`, `unknown`)
- strongest honest summary
- last materially sidecar-shaping event time

The operator must be able to answer:

> which hidden sidecars currently matter here?

### 2) Active sidecar families

Show rows such as:

- ignore / exclusion sidecar
- metadata carriage whitelist sidecar
- imported subject policy sidecar
- retired sidecar pending cleanup

Each row must show:

- source of truth
- dominant scope
- current entry count
- whether defaults were modified
- whether direct filesystem editing is disabled / discouraged / imported-only

### 3) Rule locality and agreement

Show:

- seat-local vs subject-wide classification
- peer-agreement state (`aligned`, `tolerated-divergence`, `unsafe-drift`, `unknown`)
- path / case / platform sensitivity warnings
- whether a rule affects future discovery only or also current accounting views

The page must answer:

> are peers actually agreeing on what counts and what carries metadata?

### 4) Accounting and fidelity effects

Show:

- excluded candidate count and bytes
- counted-size delta
- metadata-carriage delta
- xattr / alternate-stream portability warnings
- whether unsupported xattr storage is being carried through managed stubs instead

This section must make `not indexed`, `not counted`, and `metadata not carried` visibly different.

### 5) Reviewed mutation draft

Actions may include:

- `Edit ignore rules`
- `Edit metadata carriage whitelist`
- `Adopt shared baseline`
- `Preserve deliberate local divergence`
- `Open managed hidden bytes page`
- `Export sidecar receipt`

Each action must preview the policy delta, accounting delta, and non-effects.

## Public object

### Sidecar policy page

Fields:

- `sidecar_policy_page_id`
- `subject_ref`
- `sidecar_verdict`
- `sidecar_family_rows[]`
- `agreement_state`
- `accounting_delta`
- `metadata_carriage_delta`
- `unsupported_storage_fallback_rows[]`
- `draft_mutation_rows[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. subject
2. sidecar verdict
3. agreement state
4. dominant consequence
5. next least-widening action

Example:

```text
Project Alpha     intentional-divergence     ignore aligned / streams local     counted bytes differ, payload bytes unchanged     Open sidecar policy
```

## Non-goals

This page does **not** prove subject continuity, cleanup safety, or history restore results.
It proves only the live **sidecar policy** and the consequences of changing it.
''',
    '419-spine-integrity-page-id-authority-foreign-runtime-and-rebind-boundary-interface-spec.md': '''# Spine integrity page — ID authority, foreign runtime, and rebind boundary interface spec

## Purpose

The archive already had repair ladders, seat-lineage work, and service-material integrity language.
What it still lacked was one ordinary page for the narrower question:

> is the continuity-bearing hidden spine for this subject actually healthy, or am I looking at missing identity, duplicate runtime ownership, foreign-managed state, or a repair that recreates a new epoch?

Current official Resilio docs make this seam concrete.
They still say deleting or corrupting `.sync` / the ID file suspends synchronization, that two Sync instances touching the same folder can corrupt internal state, that one repair path is remove/re-add after checking Archive and deleting `.sync`, and that cloning a Sync instance by raw copy is unsupported.
That is useful truth.
It should not remain scattered.

## Core decision

AnonSync must expose one first-class **Spine integrity** page for every degraded or repair-reviewed subject.

The page exists to answer five things in one place:

1. whether continuity-bearing hidden state is healthy, damaged, foreign, duplicated, or recreated
2. which component currently acts as the authoritative spine witness
3. whether the likely cause is loss, corruption, duplicate runtime, foreign ownership, or unsupported copy
4. which repair paths preserve the current epoch and which create a successor epoch
5. what evidence or history must be exported before any destructive repair

## Fixed page order

1. **Integrity verdict**
2. **Authoritative spine witnesses**
3. **Likely damage or conflict origin**
4. **Preserve vs recreate repair ladder**
5. **Evidence and receipts**

### 1) Integrity verdict

Show:

- `spine_integrity_page_id`
- subject scope
- current `integrity_verdict` (`healthy`, `missing-id`, `corrupted-spine`, `duplicate-runtime`, `foreign-owned`, `recreated`, `unknown`)
- strongest honest summary
- last materially integrity-shaping event time

The operator must be able to answer:

> does this subject still have the same continuity spine or not?

### 2) Authoritative spine witnesses

Show rows for components such as:

- subject identity witness
- preserved history witness
- current runtime owner witness
- imported or recreated spine witness

Each row must show:

- witness strength
- whether it proves preserved continuity or only recreated capability
- whether another seat corroborates it
- whether the witness is stale, conflicting, or absent

### 3) Likely damage or conflict origin

Show candidate causes such as:

- accidental deletion or movement of continuity spine
- duplicate runtimes touching one subject
- external-drive reuse across runtimes
- unsupported disk or machine clone
- abrupt interruption / corruption
- operator-accepted clean rebind

Each row shows confidence, evidence used, and whether it threatens payload bytes, continuity, or both.

### 4) Preserve vs recreate repair ladder

Actions may include:

- `Reattach preserved spine`
- `Quarantine foreign runtime ownership`
- `Export history before rebind`
- `Create reviewed successor epoch`
- `Force clean rebind`
- `Abort destructive repair`

Each action must preview continuity result, archive/history risk, and reversibility.

### 5) Evidence and receipts

Show:

- recent integrity receipts
- exported history / archive witnesses
- repair drafts awaiting approval
- whether a successor-epoch receipt would be issued

## Public object

### Spine integrity page

Fields:

- `spine_integrity_page_id`
- `subject_ref`
- `integrity_verdict`
- `authoritative_witness_rows[]`
- `candidate_origin_rows[]`
- `preserve_vs_recreate_actions[]`
- `history_export_requirements[]`
- `successor_epoch_preview`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. subject
2. integrity verdict
3. dominant origin hypothesis
4. preserve/recreate boundary
5. next least-widening action

Example:

```text
Project Alpha     duplicate-runtime     shared external path conflict     preserve possible if foreign owner quarantined     Open spine integrity
```

## Non-goals

This page does **not** replace sidecar editing, ordinary browse, or residue cleanup.
It proves only the current **continuity-spine integrity** and the repair boundary around it.
''',
    '420-managed-hidden-bytes-page-archive-inflight-stubs-and-safe-browse-interface-spec.md': '''# Managed hidden bytes page — archive, inflight, stubs, and safe browse interface spec

## Purpose

The archive already had service residue and cleanup language.
What it still lacked was one ordinary page for the simpler question:

> right now, while this subject is alive, which hidden managed bytes exist under it, what do they mean, and which of them are safe to browse, safe to export, or unsafe to edit by hand?

Current official Resilio docs make this seam concrete.
They still say Archive may need to be opened through the hidden filesystem path, that `.!sync` names represent in-flight data, that stream stubs may appear when xattrs cannot be stored natively, and that deleting the wrong hidden material can suspend sync entirely.
That is useful truth.
It should not remain scattered.

## Core decision

AnonSync must expose one first-class **Managed hidden bytes** page for every subject with hidden managed families.

The page exists to answer five things in one place:

1. which hidden managed byte families are present now
2. whether each family represents live work, history, metadata fallback, policy sidecars, or continuity spine
3. which families are browse-safe, export-safe, compact-safe, or mutation-forbidden
4. which families are currently overdue / stuck / expected / empty
5. what reviewed action is the least-widening way to inspect, export, compact, or repair them

## Fixed page order

1. **Current hidden-bytes verdict**
2. **Managed family inventory**
3. **Live meaning now**
4. **Safe browse / edit / delete contract**
5. **Reviewed actions**

### 1) Current hidden-bytes verdict

Show:

- `managed_hidden_bytes_page_id`
- subject scope
- current `hidden_bytes_verdict` (`none-present`, `expected-families-present`, `history-heavy`, `inflight-active`, `fallback-stubs-present`, `stuck-or-overdue`, `unknown`)
- strongest honest summary
- last materially hidden-bytes-shaping event time

The operator must be able to answer:

> what hidden managed bytes are under this subject right now?

### 2) Managed family inventory

Show rows such as:

- continuity spine
- history / archive bytes
- in-flight temp bytes
- metadata fallback stubs
- sidecar policy files
- diagnostic spill attached to the subject

Each row must show:

- item count
- byte count
- current state (`empty`, `active`, `retained`, `stuck`, `degraded`, `unknown`)
- default visibility class

### 3) Live meaning now

For each family show:

- what it means while the subject is healthy
- what it means when overdue or stuck
- strongest next proof that it will clear or settle
- whether another page owns the next decision

This section must make `archive retained`, `in-flight active`, and `fallback stubs present` visibly different.

### 4) Safe browse / edit / delete contract

Show one contract row per family:

- browse-safe?
- export-safe?
- compact-safe?
- direct manual delete safe?
- managed-action-only?

The page must make `safe to inspect` visibly different from `safe to mutate`.

### 5) Reviewed actions

Actions may include:

- `Open archive review`
- `Inspect inflight residue`
- `Inspect metadata fallback stubs`
- `Export hidden-bytes receipt`
- `Compact retained history`
- `Open spine integrity page`
- `Do not delete by hand`

Each action must preview state delta and non-effects.

## Public object

### Managed hidden bytes page

Fields:

- `managed_hidden_bytes_page_id`
- `subject_ref`
- `hidden_bytes_verdict`
- `managed_family_rows[]`
- `safe_contract_rows[]`
- `next_proof_rows[]`
- `reviewed_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. subject
2. hidden-bytes verdict
3. dominant managed family
4. dominant safety rule
5. next least-widening action

Example:

```text
Project Alpha     inflight-active     .!sync + archive present     browse safe, manual delete blocked     Open managed hidden bytes
```

## Non-goals

This page does **not** replace subject-spine continuity review or sidecar mutation review.
It proves only the current **managed hidden bytes** and their safe-handling contract.
'''
}

APPENDS = {
    'docs/10-resilio-sync-evaluation.md': '''\n\n## Further non-clone evidence after rev0197 — hidden subject spine and sidecar authority\n\nAnother current Resilio pass now tightens the argument in a different ordinary place:\n\n- current docs still openly admit that a subject carries hidden product-owned state inside `.sync`\n- current docs still split hidden families across identity, Archive, IgnoreList, StreamsList, and in-flight `.!sync` names\n- current docs still make exclusion semantics depend on a hidden text sidecar and xattr carriage depend on a separate hidden whitelist sidecar\n- current docs still let duplicate runtimes or unsupported instance cloning corrupt or confuse that hidden state\n- current docs still make one repair path effectively `check Archive, delete .sync, remove/re-add`, which is continuity-recreation folklore rather than one product-owned continuity page\n\nSo one more strong no-clone reason is now clear:\n\n> Resilio is still worth borrowing for its candor that sync subjects really do have hidden product-owned state, but not for the way ordinary answers about `what is payload`, `what is hidden product state`, `which sidecar is local policy`, `did continuity survive`, and `what hidden bytes are safe to touch` still live across FAQ pages, hidden text files, warning articles, troubleshooting notes, move/rename caveats, and cloning warnings.\n\nAnonSync should therefore expose one visible subject-spine contract, one sidecar-policy page, one spine-integrity page, and one managed-hidden-bytes page instead of relying on hidden folders as the interface.\n''',
    'docs/11-resilio-borrow-line-and-non-clone-scorecard.md': '''\n\n## Addendum after rev0197 — hidden subject state, sidecars, and continuity spine\n\nAnother current Resilio pass now clarifies one more borrow/adapt/reject line.\n\n### Borrow directly\n\nAnonSync should copy these instincts with little embarrassment:\n\n- admit that a sync subject has product-owned state in addition to payload bytes\n- admit that history, metadata fallback, and in-flight residue are real managed families\n- admit that continuity-bearing identifiers are ordinary operator concerns\n\n### Adapt instead of clone\n\nAnonSync should preserve the use case but change the contract for:\n\n- exclusion and xattr policy sidecars\n- hidden managed-byte browsing\n- subject move / rehome continuity explanation\n\n### Do not clone\n\nAnonSync should reject these exact clone lines:\n\n1. hidden `.sync` contents acting as the primary public explanation surface for subject state\n2. local text sidecars acting as the main semantic home of exclusion and metadata carriage truth\n3. `delete .sync and re-add` functioning as the ordinary continuity explanation instead of one explicit preserve-vs-recreate review\n4. raw filesystem spelunking being required to understand Archive, `.!sync`, or stream stubs\n\nThe scorecard implication is simple: keep the candor, reject the hidden-folder-first page contract.\n''',
    'docs/12-resilio-interface-clone-veto-tests-and-page-obligations.md': '''\n\n## Further page obligations after rev0197\n\nA further current Resilio pass now shows four more ordinary questions that also deserve one stable product-owned page:\n\n1. **Inside this subject, what is payload, what is managed service namespace, and which move/rehome actions preserve the same subject epoch?**\n2. **Which hidden sidecars currently shape indexing, counted size, and metadata carriage, and are they aligned across peers or drifting locally?**\n3. **Is the continuity-bearing hidden spine for this subject healthy, foreign-owned, duplicated, missing, or already recreated?**\n4. **Which hidden managed bytes currently exist here, what do they mean, and which are safe to browse versus unsafe to edit by hand?**\n\nThose become four more replacement pages:\n\n- **Subject spine**\n- **Sidecar policy**\n- **Spine integrity**\n- **Managed hidden bytes**\n\nThese are not support annexes.\nThey are ordinary pages because the operator questions they answer are ordinary.\n''',
    'docs/20-product-direction.md': '''\n\n## Revision addendum — hidden subject spine and sidecar truth after rev0197\n\nProduct direction should now explicitly require that AnonSync never treat hidden service namespace as mere implementation detail.\n\nThe product should instead make three distinctions public everywhere:\n\n- **payload bytes vs managed service bytes**\n- **continuity-bearing spine vs seat-local sidecar policy**\n- **safe observation vs safe mutation**\n\nThat means every ordinary subject surface should be able to answer:\n\n- what managed families exist under this subject\n- which ones are identity/continuity-bearing\n- which ones are local policy or metadata-carriage sidecars\n- whether a move, repair, or cleanup preserves the current subject epoch or creates a successor epoch\n\nA privacy-respecting sync product that hides these distinctions behind a hidden folder is still under-explaining itself.\n''',
    'docs/30-interface-spec.md': '''\n\n## Revision addendum — subject-spine and sidecar-authority page families after rev0197\n\nThe interface corpus now needs one more ordinary page family because hidden subject state is not implementation trivia.\n\nAdd four stable page contracts:\n\n- **Subject spine** for payload vs service-namespace and move/rehome continuity truth\n- **Sidecar policy** for Ignore / Streams class policy, locality, agreement, and accounting/fidelity effects\n- **Spine integrity** for continuity-bearing ID authority, duplicate-runtime conflict, and preserve-vs-recreate repair review\n- **Managed hidden bytes** for Archive / inflight / fallback-stub families and safe browse vs unsafe manual mutation\n\nThese pages close another clone-veto seam: the user should never need a hidden-folder browser tab just to understand the product's own state.\n''',
    'docs/38-operator-workbench-interface-spec.md': '''\n\n## Revision addendum — workbench obligations for hidden subject-state truth after rev0197\n\nThe workbench must now support four more ordinary reviews:\n\n- a **subject spine** review that shows payload namespace and managed namespace adjacent\n- a **sidecar policy** review that keeps local-vs-shared policy and peer-agreement visible during edits\n- a **spine integrity** review that keeps preserved continuity and recreated continuity visibly separate\n- a **managed hidden bytes** review that supports safe inspection and export without implying manual deletion is safe\n\nThis is another case where the workbench must replace filesystem archaeology with product-owned proof.\n''',
    'docs/39-interface-pattern-language.md': '''\n\n## Revision addendum — pattern rules for hidden service namespace after rev0197\n\n### Pattern 9 — hidden product bytes need visible family names\n\nIf the product owns hidden bytes under the subject tree, the interface must name those families directly.\n`Managed hidden bytes present` is better than requiring the operator to infer meaning from a raw folder name.\n\n### Pattern 10 — sidecars must declare locality, not just syntax\n\nA sidecar row should always say whether it is seat-local, subject-wide, imported, or temporary.\nSyntax without locality is not enough for trustworthy review.\n\n### Pattern 11 — preserved continuity and recreated continuity must never share the same badge\n\nA repair that preserves the current subject epoch and a repair that recreates a successor epoch may both end in `working`, but they are not the same truth and must render differently.\n''',
    'docs/40-architecture-decisions.md': '''\n\n## ADR addendum after rev0197 — hidden subject spine and sidecar policy deserve public pages\n\nThe architecture should now treat hidden subject namespace as first-class model state, not incidental filesystem litter.\n\nThat implies:\n\n- subject objects should enumerate payload, continuity spine, sidecar policy, history, and transient hidden-byte families explicitly\n- sidecar-policy objects should encode locality and peer-agreement rather than only storing raw pattern text\n- repair plans must distinguish preserved continuity from recreated successor epochs\n- browse surfaces should expose safe observation contracts for managed hidden bytes without endorsing raw manual mutation\n''',
    'docs/50-roadmap.md': '''\n\n## Revision addendum — hidden-subject-state tranche after rev0197\n\nNear-term Phase 0 follow-through should now explicitly prioritize:\n\n- subject-spine object coverage so payload namespace and managed namespace are visible without hidden-folder archaeology\n- sidecar-policy coverage so ignore / metadata-carriage rules have locality, agreement, and consequence receipts\n- spine-integrity repair review so duplicate-runtime, missing-spine, and recreated-epoch outcomes are explicit before apply\n- managed-hidden-bytes coverage so Archive, inflight residue, and fallback stubs are inspectable through product pages rather than raw filesystem spelunking\n\nPhase 0 should count this tranche as complete only when operators can tell:\n\n- which hidden byte families are product-owned here\n- which sidecars are local policy versus continuity-bearing state\n- whether continuity was preserved or recreated during repair\n- which hidden bytes are safe to inspect, export, compact, or never edit by hand\n''',
    'docs/sources.md': '''\n\n## Revision addendum — hidden subject spine, sidecar policy, and continuity-bearing service state\n\nThis revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about the `.sync` folder, IgnoreList, StreamsList, service-file loss, move/rename limits, troubleshooting for stuck partials and ignore disagreement, and the unsupported cloning warning.\nThe new questions were:\n\n> where do current official docs most clearly show that Resilio is actually fairly candid that a sync subject has hidden product-owned state, local text sidecars, xattr-carriage sidecars, and continuity-bearing identifiers?\n\n> where do those same current docs still show that the ordinary operator answer about `what is product-owned here?`, `which sidecar controls this behavior?`, `did continuity survive?`, and `what hidden bytes are safe to touch?` still depends on hopping across several FAQs, sidecar docs, warning pages, troubleshooting notes, and caveat articles instead of one stable product-owned page?\n\nThe most load-bearing source set for this pass was:\n\n- Resilio's current v3 changelog, which still shows the product line is active enough that these seams are current design evidence rather than abandoned-history trivia.\n- Resilio's current `.sync` FAQ, which still says every subject gets a hidden service folder containing ID, IgnoreList, StreamsList, Archive, and in-flight `.!sync` names.\n- Resilio's current `Service files missing` warning, which still says `.sync` loss suspends sync and that duplicate runtimes touching the same subject can corrupt the internal files.\n- Resilio's current IgnoreList doc and `My files don't sync` troubleshooting doc, which still show that ignore policy is a hidden text sidecar, that excluded files are not indexed or counted, and that peer disagreement over ignore behavior can itself explain divergence.\n- Resilio's current xattr / StreamsList doc, which still says metadata carriage uses a separate whitelist sidecar and can fall back to stub files in `.sync/Streams`.\n- Resilio's current move/rename FAQ and `Cloning Sync` warning, which still show that continuity-preserving moves are limited and naive instance cloning is unsupported.\n\n## Additional Resilio official sources emphasized in rev0198\n\n- Resilio Sync 3.0 change log  \n  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log\n\n- What is '.sync' folder, and StreamsList, IgnoreList and Archive inside?  \n  https://help.resilio.com/hc/en-us/articles/206217185-What-is-sync-folder-and-StreamsList-IgnoreList-and-Archive-inside\n\n- Ignoring files in Sync (Ignore List)  \n  https://help.resilio.com/hc/en-us/articles/205458165-Ignoring-files-in-Sync-Ignore-List\n\n- Alt Streams and Xattrs in Sync  \n  https://help.resilio.com/hc/en-us/articles/204754729-Alt-Streams-and-Xattrs-in-Sync\n\n- Service files missing / Cannot identify destination folder  \n  https://help.resilio.com/hc/en-us/articles/205450225-Service-files-missing-Cannot-identify-destination-folder\n\n- My files don't sync  \n  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync\n\n- Can I move or rename a syncing folder?  \n  https://help.resilio.com/hc/en-us/articles/205450655-Can-I-move-or-rename-a-syncing-folder\n\n- Cloning Sync  \n  https://help.resilio.com/hc/en-us/articles/360018421940-Cloning-Sync\n'''
}


def append_if_missing(path: Path, block: str):
    text = path.read_text()
    if block.strip() in text:
        return
    text = text.rstrip() + "\n" + block
    path.write_text(text)


def main():
    (ROOT / 'README.md').write_text(README_TEXT)
    (DOCS / '00-status.md').write_text(STATUS_TEXT)

    for name, body in DOC_TEXTS.items():
        (DOCS / name).write_text(body)

    for rel, block in APPENDS.items():
        append_if_missing(ROOT / rel, block)

    missing = [name for name in NEW_DOCS if not (DOCS / name).exists()]
    if missing:
        raise SystemExit(f"Missing expected rev0198 docs: {missing}")
    print('rev0198 archive updated and structurally complete.')


if __name__ == '__main__':
    main()
