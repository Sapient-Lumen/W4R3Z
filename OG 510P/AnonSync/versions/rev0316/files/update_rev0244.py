from pathlib import Path

root = Path('/mnt/data/workrev/AnonSync-rev0243-2026.03.21.23.33-actionfloorvanishingcontrol')
docs = root / 'docs'

new_docs = {
'646-resilio-non-authority-local-edit-contract-destructive-auto-heal-and-encrypted-hardwire-evaluation.md': '''# Resilio non-authority local-edit contract, destructive auto-heal, and encrypted hardwire evaluation

## Why this pass exists

The archive already had strong doctrine for authority, local material, severance, and recovery.
What it still lacked was one direct current Resilio evaluation for another ordinary seam:

> when this seat is not the authority for a shared subject, what exactly happens if local edits occur here — do updates freeze, do remote bytes overwrite the edit, do some local additions survive unsynced, and is that contract even available in the same way across modes and peer types?

Current official Resilio docs still show a useful, living product, but they also still show that one everyday answer still leaks across several different article families at once:

- `User Management`
- `Is one-way synchronization possible?`
- `Folder Preferences`
- `Folder Types and Management`
- `Encrypted folders`
- `Sync interface on Android` / `Sync Interface on iOS devices`
- `How to create a Read Only folder while syncing across linked devices?`

## Current official Resilio evidence that matters here

Current official docs still show an active v3 line through `3.1.2.1076`.
They also still say all of the following:

- `User Management` still says Read Only peers cannot propagate their edits and that further synchronization of files changed by a Read Only peer is suspended for that peer unless `Overwrite any changed files` is used.
- `Is one-way synchronization possible?` still spells out per-change-class behavior: with overwrite enabled, renamed files remain while the old name is re-downloaded, deleted files are restored, edited files revert to the most recent version from a RW peer, and added files are not synced back.
- `Folder Preferences` still says `Overwrite any changed files` is potentially destructive, includes locally added files, and is disabled for Read-only folders with Selective Sync ON.
- `Folder Types and Management` still says Read Only folders may allow local changes depending on local settings, but that such changes can stop the user from receiving later updates to those files.
- `Encrypted folders` still says encrypted backup peers are always Read Only, always have overwrite enabled, and do not allow Selective Sync.
- `Sync interface on Android` and `Sync Interface on iOS devices` still expose overwrite as a per-share control on mobile surfaces rather than a deeper contract page.
- `User Management`, `Is one-way synchronization possible?`, and `How to create a Read Only folder while syncing across linked devices?` still make clear that linked devices under one identity act as Owners, that Advanced folders do not offer Read Only across linked devices, and that creating a Read Only copy on one of your own devices still routes through a Standard-folder/manual-key/disconnect workflow.

So current Resilio still contains a real but scattered answer to `what kind of local edit freedom do I actually have here, and what happens to future updates if I use it?`

## What Resilio still gets right

### 1) It is candid that non-authority local edits are not one simple thing

The docs do not pretend that `Read Only` automatically means `immutable local copy`.
They admit suspension, overwrite, and special encrypted behavior.
That honesty matters.

### 2) It still publishes concrete per-change-class effects

Rename, delete, edit, and add do not all behave the same way.
Resilio's docs still say so explicitly.
That is valuable operator candor.

### 3) It still admits that some postures hardwire the policy

Encrypted peers forcing overwrite and forbidding Selective Sync is real product truth.
The docs do not hide it.

## Why this is still a good reason not to clone them

### 1) One `Read Only` badge still hides several incompatible local-edit contracts

Current docs still require the operator to reconstruct whether this share means:

- local edits freeze future updates for changed paths
- local edits are destructively auto-healed
- local additions remain as unsynced residue
- Selective Sync forbids the overwrite option
- encrypted posture forces overwrite and forbids Selective Sync

AnonSync should not inherit a single badge that carries all of that.

### 2) Destructive auto-heal still looks like an ordinary preference

Current docs are candid that `Overwrite any changed files` is destructive.
But the contract still arrives as a checkbox in per-folder preferences and mobile share details, not as a first-class review of what local edits will lose.
A serious sync product should not let destructive reversion masquerade as routine tuning.

### 3) Non-authority posture and identity posture are still mixed awkwardly

Current docs still say linked devices act as Owners, and that creating a Read Only copy on one of your own devices routes through Standard-folder/manual-key/disconnect ritual.
That means the product still lacks one clean operator-owned sentence for `this device is intentionally non-authoritative for this subject`.

### 4) Future-update continuity is still path-local but not surfaced that way

Some paths freeze, some revert, some survive local-only, and some policies cannot be toggled in some modes.
Current Resilio still makes the operator stitch that truth together from permission docs, one-way-sync docs, preferences, and encrypted-backup docs.

## The tighter AnonSync conclusion

AnonSync should borrow the following from Resilio more boldly:

- candid admission that non-authority local edit behavior is a real policy surface
- explicit per-change-class outcomes rather than one vague `read only` sentence
- explicit publication of hardwired posture limits such as encrypted/opaque backup roles

But AnonSync should refuse the exact page contract whenever one ordinary answer still depends on:

- permission folklore
- hidden per-path suspension
- destructive auto-heal disguised as a preference toggle
- identity-level owner semantics being worked around by manual Read Only detours

## The replacement pages this evaluation justifies

This pass therefore makes four page-shaped obligations concrete:

1. **Non-authority edit posture** — what local changes are allowed here, and what is their fate?
2. **Non-authority local-change review** — before a local edit or policy change, what freezes, reverts, survives locally, or must be diverted elsewhere?
3. **Affected-path continuity** — after divergence or auto-heal, which paths still receive updates, which are frozen, and why?
4. **Non-authority edit receipt** — what policy was in force, what local changes occurred or were reviewed, and what is the strongest honest sentence now?

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still good evidence that non-authority local edits need explicit policy, but it is also current evidence that one `Read Only` story can still require archaeology across permission pages, one-way-sync details, destructive preference text, encrypted exceptions, and linked-device workarounds. AnonSync should copy the candor and refuse the overloaded read-only contract.
''',
'647-non-authority-edit-posture-page-rights-local-change-fate-and-continuity-mode-interface-spec.md': '''# Non-authority edit posture page — rights, local-change fate, and continuity mode interface spec

## Purpose

This page answers one ordinary question:

> this seat is not authoritative for this subject, so can I edit locally at all, what happens if I do, and do future updates keep flowing or stop per path?

The page exists because `read only`, `observer`, `backup`, and `mirror` are not enough.
The operator needs one direct statement of local-edit fate.

## Core decision

Every non-authority subject must render one first-class **Non-authority edit posture** page.
The page owns:

- authority grade on this seat
- whether local edits are blocked, tolerated, auto-healed, or allowed only outside the managed lane
- change-class fate for add / edit / rename / delete
- future-update continuity rule
- hardwired posture limits

## Primary layout

The page always renders the same regions in the same order:

1. posture strip
2. authority and lane card
3. local-change fate matrix
4. continuity mode card
5. hardwired limits card
6. receipts

### 1) Posture strip

Show:

- subject label
- seat label
- authority grade: `owner`, `writer`, `non-authority`, `opaque-backup`, `unknown`
- local-edit mode: `blocked`, `freeze-on-change`, `auto-heal`, `divert-locally`, `mixed`
- one honest next action

### 2) Authority and lane card

This card publishes:

- whether this seat may publish changes upstream
- whether this seat may only receive
- whether local edits are within the managed lane or must be redirected elsewhere
- whether this posture was chosen intentionally, inherited, or hardwired

The operator must be able to answer: **am I not allowed to write upstream, or am I not even allowed to change the local managed copy?**

### 3) Local-change fate matrix

Render one row for each change class:

- add local file
- edit existing file
- rename existing file
- delete existing file
- mutate metadata only

Columns:

- `local edit permitted?`
- `upstream propagation?`
- `future remote updates continue?`
- `auto-heal / revert risk?`
- `local-only residue possible?`
- `receipt language`

The product must not compress these rows into one generic `read only` sentence.

### 4) Continuity mode card

This card publishes:

- whether future updates stop per changed path, whole subject, or not at all
- whether auto-heal replaces local edits with remote state
- whether some local additions remain outside sync while other path classes revert
- what must happen to restore full continuity for frozen paths

The operator must be able to answer: **if I touch this here, what later updates do I stop getting?**

### 5) Hardwired limits card

This card publishes:

- posture-imposed limits such as `overwrite forced`, `selective materialization unavailable`, or `path-local freeze only`
- whether the current surface can change these limits
- whether the limit belongs to identity design, peer type, encryption posture, or current surface only

### 6) Receipts

Receipts show:

- authority grade
- local-edit mode
- continuity mode
- hardwired limits acknowledged
- strongest safe sentence after review

## Public object

### `non_authority_edit_posture`

Fields:

- `non_authority_edit_posture_id`
- `subject_ref`
- `seat_ref`
- `authority_grade`
- `local_edit_mode`
- `change_class_rules[]`
- `continuity_mode`
- `hardwired_limits[]`
- `policy_origin`
- `generated_at`

## Non-negotiable rules

### Rule 1 — permission and local-edit fate must stay separate

`Cannot publish upstream` is not the same truth as `cannot safely edit local managed bytes`.

### Rule 2 — per-change-class outcomes must stay visible

Add, edit, rename, delete, and metadata-only mutations may differ.
The page must publish those differences directly.

### Rule 3 — forced policy must look forced

If the posture hardwires overwrite, disables selective materialization, or forbids a safer alternative, the page must say so explicitly.

## Honest outputs

The page may conclude:

- `This seat is non-authoritative. Editing an existing managed file freezes future updates for that path until continuity is repaired.`
- `This seat is non-authoritative with auto-heal enabled. Local edits may be reverted by upstream state and should be treated as disposable unless preserved elsewhere first.`
- `This posture forces auto-heal and does not offer selective materialization on this seat.`

It may not collapse those outcomes into one `read only` badge.
''',
'648-non-authority-local-change-review-page-suspend-auto-heal-or-preserve-elsewhere-interface-spec.md': '''# Non-authority local-change review page — suspend, auto-heal, or preserve elsewhere interface spec

## Purpose

This page answers one ordinary question:

> I am about to make a local change on a non-authority copy, or enable a policy that will police such changes, so what exactly will freeze, revert, survive locally, or need to be preserved elsewhere first?

The page exists because the danger is not the local edit alone.
The danger is hidden future-update loss or silent destructive reversion.

## Core decision

Before either of these commits, the product must open one first-class **Non-authority local-change review** page:

- a local edit that touches managed bytes on a non-authority seat
- a policy mutation that changes local-edit fate for such bytes

The page owns:

- intended local action
- current posture and continuity rule
- predicted path-class outcome
- preserve / divert options
- post-commit claim ceiling

## Fixed review order

1. intended action strip
2. current posture card
3. predicted-outcome matrix
4. preserve-or-divert card
5. commit review
6. receipt

### 1) Intended action strip

Show:

- subject and seat
- intended local action
- relevant path set
- current local-edit mode
- top-level risk class: `safe`, `guarded`, `destructive`, `blocked`

### 2) Current posture card

This card publishes:

- authority grade
- current continuity mode
- whether auto-heal is disabled, optional, or forced
- whether selective materialization or other posture constraints narrow options

### 3) Predicted-outcome matrix

Rows should cover the affected path classes.
Columns should include:

- intended change class
- upstream propagation
- future update continuity
- auto-heal / revert behavior
- local residue fate
- proof lost if committed

The operator must be able to answer: **what exactly happens to these paths if I continue?**

### 4) Preserve-or-divert card

Offer typed alternatives such as:

- preserve copy outside managed lane
- convert to explicit fork / branch / exported work area
- keep change but accept frozen continuity
- enable auto-heal and treat local edits as disposable
- cancel and edit on an authority-bearing seat instead

This card must state which alternative is the least destructive.

### 5) Commit review

This section publishes:

- actual commit being approved
- strongest safe sentence afterward
- stronger unsupported sentence
- required repair if continuity will freeze

### 6) Receipt

The receipt preserves:

- intended action
- posture in force
- predicted path-class outcome
- preserve/divert option shown
- actual committed choice
- claim ceiling

## Public object

### `non_authority_local_change_review`

Fields:

- `non_authority_local_change_review_id`
- `subject_ref`
- `seat_ref`
- `intended_action`
- `affected_paths[]`
- `authority_grade`
- `continuity_mode`
- `auto_heal_mode`
- `predicted_outcomes[]`
- `preserve_or_divert_options[]`
- `committed_choice`
- `claim_ceiling`
- `generated_at`

## Review rules

### Rule 1 — destructive auto-heal must be reviewed as destruction

If enabling or relying on auto-heal can overwrite local edits, the page must present that as destructive, not routine synchronization hygiene.

### Rule 2 — frozen continuity must be reviewed as future loss, not just current success

A local save that looks successful now may still suspend future remote updates for that path.
The page must publish that future cost.

### Rule 3 — preserve elsewhere must be first-class

When the safest route is to move work outside the managed lane or to a writable seat, the page must show that route before commit.

## Honest outputs

The page may conclude:

- `Continuing here will keep the local rename, but future remote continuity for the managed path will stop until repaired.`
- `With auto-heal enabled, this edited file is expected to revert to upstream state. Preserve a copy elsewhere first if the local version matters.`
- `This posture cannot offer the safer selective materialization route on this seat.`

It may not flatten those outcomes into `changes may be lost`.
''',
'649-affected-path-continuity-page-suspended-updates-auto-heal-basis-and-path-class-verdict-interface-spec.md': '''# Affected-path continuity page — suspended updates, auto-heal basis, and path-class verdict interface spec

## Purpose

This page answers one ordinary question after the fact:

> which exact paths are still receiving updates, which are frozen or being auto-healed, and why?

The page exists because divergence under non-authority posture is often path-local.
Operators should not have to infer the affected set from missed updates or surprise reversions.

## Core decision

Whenever a non-authority local edit or policy change creates mixed continuity outcomes, the product must render one first-class **Affected-path continuity** page.

The page owns:

- affected path inventory
- continuity verdict per path class
- auto-heal basis
- repair routes
- strongest safe sentence for the subject as a whole

## Fixed page order

1. continuity summary strip
2. path verdict table
3. auto-heal and freeze basis card
4. repair routes card
5. subject-level claim ceiling
6. receipts

### 1) Continuity summary strip

Show:

- subject and seat
- counts for `continuing`, `frozen`, `auto-heal`, `local-only`, `unknown`
- whether the issue is path-local or subject-wide
- one honest next action

### 2) Path verdict table

Each row should show:

- path or path-group label
- triggering local change class
- current verdict (`continuing`, `frozen`, `auto-heal`, `local-only residue`, `blocked`, `unknown`)
- upstream status
- future remote update fate
- data-loss risk
- repair action

Rows may be grouped by pattern if the proof is exact enough, but grouping must never hide a stronger risk class.

### 3) Auto-heal and freeze basis card

This card publishes:

- the rule or posture that caused each verdict
- whether overwrite was optional, enabled by policy, or forced by posture
- whether selective materialization or peer type removed safer alternatives
- whether the verdict is proven or inferred

### 4) Repair routes card

For each affected class, show the least-strong repair route such as:

- preserve local version and reopen on writable seat
- discard local edits and resume upstream continuity
- export local-only additions into explicit unmanaged area
- rebind / reset / rescan after proof-preserving action

### 5) Subject-level claim ceiling

This section must state:

- the strongest safe sentence for the subject overall
- any stronger sentence still unsupported
- whether the subject may still be described as `mirroring`, `protected backup`, `fully current`, or only a narrower statement

### 6) Receipts

Receipts preserve:

- affected set
- verdict classes
- policy basis
- repair route chosen or deferred
- subject-level claim ceiling

## Public object

### `affected_path_continuity`

Fields:

- `affected_path_continuity_id`
- `subject_ref`
- `seat_ref`
- `path_verdicts[]`
- `path_local_or_subject_wide`
- `policy_basis[]`
- `repair_routes[]`
- `subject_claim_ceiling`
- `generated_at`

## Non-negotiable rules

### Rule 1 — path-local freeze must not masquerade as whole-subject health

A subject may still have many healthy paths while some paths are frozen or auto-healed.
The page must show that mixed truth directly.

### Rule 2 — auto-heal must name its basis

If a path reverted, the page must state whether that came from explicit policy, forced posture, or another narrower rule.

### Rule 3 — local-only residue must stay visible

Unsynced additions or preserved local forks must not disappear just because they are outside future upstream continuity.

## Honest outputs

The page may conclude:

- `12 paths continue normally, 3 paths are frozen after local edits, and 2 local additions remain outside upstream continuity.`
- `This seat is currently auto-healing edited managed files because the active posture forces overwrite.`
- `The subject is still receiving upstream changes, but not all managed paths are continuity-clean.`

It may not flatten those outcomes into `share is out of sync`.
''',
'650-non-authority-edit-receipt-page-local-change-verdict-continuity-status-and-claim-ceiling-interface-spec.md': '''# Non-authority edit receipt page — local-change verdict, continuity status, and claim ceiling interface spec

## Purpose

This page answers one ordinary question later:

> what non-authority local-edit policy was in force, what local change or review happened, and what is the strongest honest sentence now?

The page exists because later operators should not have to reconstruct a frozen path, reverted file, or preserved local-only copy from logs and memory.

## Core decision

Every meaningful non-authority edit event must emit one durable **Non-authority edit receipt**.
That includes:

- reviewed local edits on non-authority seats
- policy changes that alter local-edit fate
- auto-heal events that revert local managed bytes
- continuity-freeze outcomes for affected paths

## Fixed page order

1. event summary
2. posture in force
3. affected paths and outcomes
4. continuity status
5. claim ceiling
6. reopening conditions

### 1) Event summary

Show:

- subject
- seat
- event type
- time
- operator intent in plain language

### 2) Posture in force

Show:

- authority grade
- local-edit mode
- whether auto-heal was disabled, enabled, or forced
- whether hardwired limits removed safer alternatives

### 3) Affected paths and outcomes

Show:

- changed / reviewed path set
- per-path or grouped verdicts
- whether edits were preserved, reverted, frozen, or left as local-only residue
- whether upstream state continued or stopped per path

### 4) Continuity status

Show:

- whether subject-wide continuity remained intact
- whether only some paths froze
- whether later repair is required
- whether repair was completed, deferred, or declined

### 5) Claim ceiling

Show:

- strongest safe sentence now
- stronger unsupported sentences
- what evidence would be needed to regain them

### 6) Reopening conditions

Show:

- what would restore full continuity for affected paths
- whether moving work to a writable seat or unmanaged lane is required
- whether current posture can ever provide a safer route later

## Public object

### `non_authority_edit_receipt`

Fields:

- `non_authority_edit_receipt_id`
- `subject_ref`
- `seat_ref`
- `event_type`
- `operator_intent`
- `authority_grade`
- `local_edit_mode`
- `auto_heal_mode`
- `affected_path_outcomes[]`
- `continuity_status`
- `repair_status`
- `claim_ceiling`
- `reopen_conditions[]`
- `issued_at`

## Honest outputs

The receipt may conclude:

- `Local edits on this non-authority seat were reviewed. Two managed paths froze for future upstream continuity; one added file remained local-only.`
- `This seat auto-healed the edited managed copy under forced posture. Strongest safe sentence: upstream state remains authoritative here; local changes were not retained in the managed lane.`
- `Safer alternative unavailable: this posture did not offer selective materialization or writable-seat substitution on-device.`

It may not reduce the event to `read-only sync completed` or `changes overwritten`.
'''
}

for name, content in new_docs.items():
    (docs / name).write_text(content)

prepend_map = {
    '00-status.md': '''## Latest addendum — non-authority local edits, destructive auto-heal, and path-local continuity after rev0243

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **non-authority edit posture / non-authority local-change review / affected-path continuity / non-authority edit receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `what happens if I edit locally on a non-authority copy?` can still depend on:

- whether this seat is merely forbidden to publish upstream or whether local edits also freeze future updates for touched paths
- whether `Overwrite any changed files` is off, optional, enabled, or forced by posture
- whether Selective Sync disables the overwrite option on a Read Only share
- whether encrypted/backup posture forces overwrite and forbids Selective Sync entirely
- whether local additions remain as unsynced residue while edits, deletes, or renames behave differently
- whether linked-device ownership semantics force a manual Read Only detour instead of one native seat-level non-authority posture

So the tighter non-clone line is:

> borrow Resilio's candor that non-authority local edits are a real policy surface, but refuse any product contract where one `Read Only` badge still has to cover frozen paths, destructive auto-heal, local-only residue, mode-specific option disappearance, and encrypted hardwiring.

That yields four more ordinary product-owned pages:

- **Non-authority edit posture**
- **Non-authority local-change review**
- **Affected-path continuity**
- **Non-authority edit receipt**


''',
    '10-resilio-sync-evaluation.md': '''## Revision addendum — non-authority local edits, destructive auto-heal, and path-local continuity after rev0243

Another current official Resilio pass still exposes one more page-shaped reason not to clone Resilio wholesale.

Current docs are still candid that `Read Only` is not one simple thing.
They still say all of the following:

- current `User Management` docs still say Read Only peers cannot propagate their edits and that further synchronization of changed files is suspended for that peer unless `Overwrite any changed files` is used
- current `Is one-way synchronization possible?` docs still spell out concrete per-change-class behavior, including rename staying local while the old name is re-downloaded, deleted files being restored, edited files reverting to upstream state, and added files not being synced back
- current `Folder Preferences` docs still say `Overwrite any changed files` is potentially destructive and is disabled for Read-only folders with Selective Sync ON
- current `Folder Types and Management` docs still say local changes on a Read Only folder may cause the peer to stop receiving updates to those files depending on local settings
- current `Encrypted folders` docs still say encrypted peers are Read Only, always have overwrite enabled, and do not offer Selective Sync
- current `User Management`, `Is one-way synchronization possible?`, and `How to create a Read Only folder while syncing across linked devices?` docs still show that linked devices act as Owners, Advanced folders do not offer Read Only across linked devices, and a manual Standard-folder / Read-Only-key / disconnect detour is still required to get a Read Only copy on one of your own devices
- the active v3 line still appears through `3.1.2.1076`

That is useful candor.
The non-clone problem is workflow ownership.
Current Resilio still lets one ordinary answer about `what happens if I edit locally on this non-authority copy?` leak across permission docs, one-way-sync behavior docs, destructive preference text, encrypted-backup docs, and linked-device workaround docs.

The archive now owes four more first-class pages:

- **Non-authority edit posture**
- **Non-authority local-change review**
- **Affected-path continuity**
- **Non-authority edit receipt**

These pages are required whenever a non-authority local copy could otherwise be flattened into one reassuring badge such as `Read Only`, `backup`, or `mirror` without publishing per-change-class fate, future-update continuity, forced-policy limits, and safe post-event language.


''',
    '11-resilio-borrow-line-and-non-clone-scorecard.md': '''## Revision addendum — scorecard after rev0243: borrow non-authority candor, reject overloaded `Read Only` meaning

Another current Resilio pass improves the scorecard in one more narrow place.

### Borrow

Keep borrowing these traits:

- admitting that non-authority local edit behavior is a real product policy surface
- publishing different outcomes for add, edit, rename, and delete rather than one vague permission sentence
- admitting that encrypted/opaque backup roles can hardwire stricter policy than ordinary peers
- admitting that future-update continuity may change after local edits on a non-authority peer

### Refuse to clone

Do not clone these traits:

- one `Read Only` badge standing in for frozen-path behavior, destructive auto-heal, local-only residue, and hardwired encrypted exceptions at once
- destructive overwrite presented as an ordinary checkbox or share-detail preference instead of a first-class review
- Selective Sync silently removing the overwrite option without a posture-owned explanation page
- linked devices acting as Owners by default while Read Only on your own device requires a manual Standard-folder / key / disconnect detour

### Replacement obligation

AnonSync should own four direct replacement pages:

- **Non-authority edit posture**
- **Non-authority local-change review**
- **Affected-path continuity**
- **Non-authority edit receipt**


''',
    '12-resilio-interface-clone-veto-tests-and-page-obligations.md': '''## Revision addendum — clone-veto after rev0243: never let one non-authority badge hide freeze, auto-heal, and local-only residue

Another current Resilio pass sharpens four more veto tests.

### Veto test 1 — permission badge outruns local-change fate

If the product can say `read only`, `observer`, or `backup` without publishing what add, edit, rename, and delete each do locally, it fails.

### Veto test 2 — destructive auto-heal disguised as routine preference

If a policy that can overwrite local managed bytes is presented as ordinary tuning rather than destructive review, it fails.

### Veto test 3 — continuity freeze hidden at path level

If local edits can stop future remote updates for touched paths and the product cannot show the affected set directly, it fails.

### Veto test 4 — forced posture limits hidden

If encrypted/opaque posture, selective-materialization limits, or identity-level ownership rules remove safer alternatives without a first-class explanation and receipt, it fails.

### New page obligations from this pass

The archive now owes four more ordinary pages:

- **Non-authority edit posture**
- **Non-authority local-change review**
- **Affected-path continuity**
- **Non-authority edit receipt**


''',
    '50-roadmap.md': '''## Revision addendum — next interface tranche after rev0243

The next high-value interface tranche after this pass should now explicitly prioritize:

1. non-authority local-edit work so permission badges stop hiding frozen-path versus auto-heal versus local-only-residue outcomes
2. destructive auto-heal review so overwrite policy changes are treated as review-grade, not preference-grade
3. affected-path continuity work so path-local freeze and resume evidence stay visible after local edits
4. durable receipts so later operators can prove what local-edit policy was in force, what changed, and what continuity sentence still remains honest


''',
    '64-critical-open-questions.md': '''## 0f) How much local edit freedom should non-authority copies allow before convenience becomes hidden divergence folklore?

The archive now requires explicit non-authority local-edit posture, typed review, and path-level continuity evidence.
What remains unresolved is the convenience budget:

- when the safest default should be `block local managed edits` versus `allow but freeze touched paths`
- whether any ordinary desktop/mobile posture should still permit destructive auto-heal by default or always force explicit review first
- how strongly the product should steer users toward unmanaged scratch lanes or writable seats instead of tolerating local-only residue in managed trees
- how much mixed path-level continuity can accumulate before the product should escalate from quiet evidence to mandatory repair review

This matters because too little freedom recreates brittle mirror-only behavior, while too much freedom recreates exactly the overloaded `Read Only` folklore the archive is trying to escape.


''',
    'sources.md': '''## Revision addendum — non-authority local edits, destructive auto-heal, and path-local continuity after rev0243

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about Read Only permission behavior, one-way synchronization details, destructive overwrite policy, encrypted-peer constraints, mobile share-detail controls, linked-device ownership semantics, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that non-authority local edits can freeze continuity, auto-heal destructively, or leave local-only residue rather than one simple `read only` story?

> where do those same current docs still show that the ordinary operator answer about `what happens if I edit locally on this non-authority copy?` still depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `User Management` article, which still says Read Only peers cannot propagate local edits and that further synchronization of changed files is suspended unless `Overwrite any changed files` is used.
- Resilio's current `Is one-way synchronization possible?` article, which still spells out per-change-class behavior for rename, delete, edit, and add when overwrite policy is in play.
- Resilio's current `Folder Preferences` article, which still says overwrite is potentially destructive and is disabled for Read-only folders with Selective Sync ON.
- Resilio's current `Folder Types and Management` article, which still says local changes on Read Only folders can stop future updates depending on local settings.
- Resilio's current `Encrypted folders` article, which still says encrypted peers are Read Only, always have overwrite enabled, and do not offer Selective Sync.
- Resilio's current `Sync interface on Android` and `Sync Interface on iOS devices` articles, which still expose overwrite behavior as a per-share control on mobile surfaces.
- Resilio's current `How to create a Read Only folder while syncing across linked devices?` article together with `User Management` and `Is one-way synchronization possible?`, which still show that linked devices act as Owners, Advanced folders do not offer Read Only across linked devices, and a manual Standard-folder / Read-Only-key / disconnect route is still required for that outcome.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0244

- User Management
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- Is one-way synchronization possible?
  https://help.resilio.com/hc/en-us/articles/204754279-Is-one-way-synchronization-possible

- Folder Preferences
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- Folder Types and Management
  https://help.resilio.com/hc/en-us/articles/204762459-Folder-Types-and-Management

- Encrypted folders
  https://help.resilio.com/hc/en-us/articles/207370466-Encrypted-folders

- Sync interface on Android
  https://help.resilio.com/hc/en-us/articles/213500383-Sync-interface-on-Android

- Sync Interface on iOS devices
  https://help.resilio.com/hc/en-us/articles/212016726-Sync-Interface-on-iOS-devices

- How to create a Read Only folder while syncing across linked devices?
  https://help.resilio.com/hc/en-us/articles/206216565-How-to-create-a-Read-Only-folder-while-syncing-across-linked-devices

- Resilio Sync 3.0 change log
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log


'''
}

for fname, prefix in prepend_map.items():
    path = docs / fname
    path.write_text(prefix + path.read_text())

