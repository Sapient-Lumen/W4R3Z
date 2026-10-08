from pathlib import Path

root = Path('/mnt/data/work0387')
docs = root / 'docs'


def write(name: str, content: str):
    (docs / name).write_text(content.strip() + '\n', encoding='utf-8')


def prepend(path: Path, text: str):
    old = path.read_text(encoding='utf-8')
    path.write_text(text.strip() + '\n\n' + old, encoding='utf-8')

new_files = {
'1462-resilio-return-delta-convergence-cohort-settlement-and-straggler-truth-evaluation.md': '''
# Resilio return-delta convergence, cohort settlement, and straggler-truth evaluation

## Why this pass exists

The archive already knew how to:

- suspend a control truthfully
- bring activity back through typed return paths
- expose changed-but-working return states as explicit parity debt
- keep owner, expiry, rereview, and claim ceiling attached to each tolerated mismatch

What it still lacked was the next ordinary operator answer:

> once many changed returns are active at the same time, how do we settle them as a group without silently promoting drift, hiding stragglers, or overclaiming that the whole baseline is back?

That is the seam this pass locks.
A real operator does not just manage one tolerated delta.
They inherit a field of them.
The product needs a first-class answer for **return-delta convergence, cohort settlement, and straggler truth**.

Current official Resilio material is useful here because it already proves that large parts of this work happen today, but mostly as repeated per-folder or per-device maneuvers:

- `Folders are duplicating with an index (i) in their name`
- `How to manually set the location of the folders synced across linked devices?`
- `Disconnecting and Removing Folders`
- `Can I connect two pre-populated pre-existing folders?`
- `Folder not empty`
- `Can I move or rename a syncing folder?`
- `User Management`
- `Running Sync in configuration mode`

## Current official Resilio evidence that matters here

Current official docs still show all of the following:

- `Folders are duplicating with an index (i) in their name` still says that when linked devices are in Selective Sync or Synced mode, arriving folders are auto-created in the default storage location, and if a same-name folder exists Sync adds an index. The fix is a per-folder disconnect and reconnect to the right location. That is already convergence work, but handled one object at a time.
- The same article still says that choosing Disconnected mode is how operators force manual placement for future arrivals. So there is a coarse default lever, but not one settlement workspace for subjects already drifted.
- `How to manually set the location of the folders synced across linked devices?` still says custom placement requires switching the device to Disconnected mode, then using `Connect` for each arriving folder; on Android it still requires disabling Simple mode. That means cross-subject re-homing still routes through repeated local decisions rather than one cohort plan.
- `Disconnecting and Removing Folders` still says reconnect may propose a different default path, may create a new directory, and may append `(1)` if a same-name folder already exists. So convergence is not merely toggling a flag back on; it can be structural settlement.
- `Can I connect two pre-populated pre-existing folders?` still says linked-device workflows can require switching to Disconnected, then connecting a specific folder to an existing directory, with non-empty-folder confirmation. So merge-style reconciliation is still performed share by share.
- `Folder not empty` still says reconnecting or adding into an already existing directory can overwrite or delete already-present files. That means settlement waves need explicit safety fences; they are not just hygiene chores.
- `Can I move or rename a syncing folder?` still says renames are local-only and moving to another partition on Windows or Mac requires disconnect and reconnect. So some path/name debt can be retired only through structural re-entry, not through one global rename-normalize action.
- `User Management` still says disconnecting a peer suspends future updates while already-synchronized files remain. So some subjects can remain visually healthy while no longer belonging to the same future-update cohort.
- `Running Sync in configuration mode` still says configuration mode helps apply the same settings to a number of different machines. That is useful, but it is startup configuration and parameter distribution, not a first-class settlement campaign for already diverged live subjects.

So current Resilio still clearly admits serious convergence truths:

- many return-delta repairs are repeated local reconnect or placement operations
- default-mode changes can affect future arrivals without settling already drifted subjects
- some settlement steps are structural and risky rather than cosmetic
- subjects may still look healthy while not sharing the same path, mode, or future-update posture
- a broad defaulting tool can exist without answering how to settle a heterogeneous live field of debts

But those truths still do not become one operator-facing **convergence campaign / cohort settlement / straggler truth** object.

## What Resilio still gets right

### 1) It is candid that convergence often happens one subject at a time

Disconnect, reconnect, connect-to-existing-directory, and mode changes are openly described as discrete operations.
That honesty is worth borrowing.

### 2) It exposes that defaults help, but defaults are not retroactive truth

Default storage location, default synchronization mode, Android Simple mode, and config mode all show that broad levers matter.
That is useful.

### 3) It preserves real safety warnings during normalization work

`Folder not empty`, merge workflows, and `(1)` duplicate path behavior all admit that cleanup can be destructive or at least structurally meaningful.
That matters.

## Where current Resilio still fragments the operator answer

### A) There is no canonical cohort settlement object

A careful operator can manually track a list of folders and devices.
But the product still does not give one place to answer:

- which subjects belong in this settlement wave
- which ones route to exact restore versus successor promotion
- which ones are too risky and must reopen instead
- which ones are stragglers blocking the stronger sentence

### B) There is no durable truth about partial success

Current docs explain how to reconnect, repoint, merge, or change default mode.
What they do not provide is one durable answer to:

- how much of the affected cohort is actually settled
- whether the current stronger claim applies to all subjects or only a bounded subset
- whether a few drifted survivors are acceptable holdouts or a reason to keep the whole claim ceiling low

### C) There is no first-class aging model for stragglers

Current docs tell operators how to do the mechanics.
They do not tell them when unresolved survivors become the next real problem.
The product still lacks one object that can say:

- which subjects were intentionally deferred
- what keeps them deferred instead of reopened
- when the wave may honestly claim completion
- which stronger sentence remains blocked by uncovered or failed subjects

## Hard product decision unlocked by this pass

AnonSync should not let a collection of tolerated deltas dissolve into background noise.
It should promote any material multi-subject cleanup into a first-class **convergence campaign** that can separately express:

- target cohort
- intended end state per subject
- route per subject: exact restore, successor promotion, keep temporary, split out, reopen
- safety fences before destructive reconciliation steps
- settlement coverage and residual stragglers
- exact scope of any upgraded claim

That is the right next seam because it answers the operator question that always follows visible debt accumulation:

> we now have many changed-but-working states at once; how do we settle them without pretending the whole baseline is back just because most of them look close enough?

## Replacement line for AnonSync

Borrow from Resilio:

- candor that convergence often requires repeated reconnect and placement work
- explicit admission that defaults help future arrivals more than already drifted subjects
- honesty that normalization can be risky, merge-heavy, and only partially successful

Do not clone from Resilio:

- any workflow where multi-subject settlement lives only as repeated per-folder memory work
- any contract where partial success silently rounds up to cohort success
- any product shape where unresolved stragglers do not keep the stronger sentence blocked

AnonSync should instead ship explicit pages for:

- convergence campaign contract sheet
- convergence shaping review
- convergence proof and settlement class
- convergence timeline
- convergence lineage receipt
''',
'1463-convergence-campaign-contract-sheet-page-debt-cohort-target-end-state-and-safety-fences-interface-spec.md': '''
# Convergence campaign contract sheet page: debt cohort, target end state, and safety fences interface spec

## Purpose

After the archive learned how to represent each changed return as explicit parity debt, it still needed one ordinary page for the next operator question:

> which debts belong in this settlement effort, what end state do we want for each, and what safety fences stop us from turning cleanup into fresh damage?

## Core decision

AnonSync must expose one first-class **Convergence campaign contract sheet** whenever more than one active return-delta object is being settled under one operator goal.

## Fixed page order

1. **Campaign header**
2. **Target-claim card**
3. **Cohort membership card**
4. **Per-subject routing card**
5. **Safety fences card**
6. **Decision sentence**

### 1) Campaign header

Show:

- convergence campaign id
- linked baseline / profile / policy family
- linked case / control / return-delta ids in scope
- campaign owner
- created time
- next decision gate
- current campaign status
- highest safe claim for covered scope

Supported `current_campaign_status` values:

- `drafting`
- `awaiting-approval`
- `wave-active`
- `partially-settled`
- `blocked-by-stragglers`
- `settled-for-bounded-scope`
- `reopened`
- `retired`

Hard rule:

A settlement effort may not be represented only as a pile of independent tasks once it is being judged as one success story.

### 2) Target-claim card

This card states what stronger sentence the campaign is trying to earn back.
Required rows:

- intended post-campaign sentence
- current weaker still-safe sentence
- target scope
- target settlement class
- proof needed before claim upgrade
- blocking subject classes

Supported `target_settlement_class` values:

- `exact-baseline-restored`
- `approved-successor-baseline`
- `mixed-but-bounded`
- `narrowed-stable-subset`
- `debt-reduction-only`

Hard rule:

The page must say whether the goal is exact restoration or accepted successor settlement.
Those may not share one generic success label.

### 3) Cohort membership card

This card defines what is in scope.
Required rows:

- total candidate subjects
- selected subjects in campaign
- excluded subjects
- inclusion rule
- shared risk signature
- shared proof assumption if any

Supported `inclusion_rule` values:

- `same-baseline-family`
- `same-return-delta-class`
- `same-failed-rearm-shape`
- `same-path-drift-family`
- `same-mode-drift-family`
- `mixed-manual-selection`

Hard rule:

Every excluded subject must remain visible.
No silent scope trimming.

### 4) Per-subject routing card

This card states where each subject is headed.
Required columns:

- subject id
- current debt class
- chosen route
- owner
- blocking condition
- next proof or action

Supported `chosen_route` values:

- `exact-restore`
- `promote-successor`
- `keep-temporary-with-expiry`
- `split-out-and-narrow-claim`
- `reopen-linked-case`
- `drop-from-this-wave`

Hard rule:

Every subject gets one explicit route.
`will figure it out during cleanup` is not a valid route.

### 5) Safety fences card

This card publishes the dangerous edges of the wave.
Required rows:

- destructive action classes allowed
- destructive action classes forbidden
- folder-not-empty / merge risk present?
- path fork risk present?
- rights drift risk present?
- abort threshold

Supported `abort_threshold` values:

- `first-unexpected-overwrite-risk`
- `first-unapproved-path-fork`
- `first-unplanned-claim-downgrade`
- `more-than-n-stragglers`
- `operator-manual-stop-only`

Hard rule:

A settlement wave may not begin with ambiguous destructive boundaries.

### 6) Decision sentence

Format:

> `This campaign is settling [selected subjects] toward [target settlement class]. It is safe to say [current weaker still-safe sentence] for [target scope]. It is not yet safe to say [intended post-campaign sentence] until [blocking subject classes / missing proof] are cleared.`

## Required interactions

### A) `Shape cohort`

Builds or changes the selected subject set.

### B) `Assign route`

Applies one explicit route to each subject.

### C) `Arm safety fences`

Records campaign-level abort logic before execution.

### D) `Freeze claim`

Locks the current claim ceiling until enough settlement proof arrives.

## Explicit anti-goals

Do not:

- present a many-subject cleanup as generic maintenance
- allow hidden exclusions
- allow success language before routes are explicit
- allow average progress to erase uncovered subjects

## Why this page exists

Because once many tolerated deltas exist at the same time, the product needs one honest place that says what exactly this wave is trying to settle, who is in, who is out, and what must not be risked while doing it.
''',
'1464-convergence-shaping-review-page-restore-promote-split-and-reopen-routing-interface-spec.md': '''
# Convergence shaping review page: restore, promote, split, and reopen routing interface spec

## Purpose

The contract sheet defines the campaign.
The **Convergence shaping review** is where the operator proves that the cohort was shaped honestly and that each subject has the right route.

## Page promise

Before a settlement wave starts, this page must answer:

> which subjects really belong together, which should restore exactly, which should be promoted as successor state, which should be carved out, and which should reopen instead of being normalized?

## Fixed page order

1. **Cohort-shape summary**
2. **Route matrix**
3. **Proof-sharing review**
4. **Straggler policy card**
5. **Approval sentence**

### 1) Cohort-shape summary

Show:

- number of candidate subjects reviewed
- number accepted into active wave
- number split out
- number reopened immediately
- number held for later wave
- current campaign risk color

Supported `campaign_risk_color` values:

- `green-bounded`
- `yellow-heterogeneous`
- `orange-destructive-edges`
- `red-overcombined`

Hard rule:

A heterogeneous cohort is allowed, but only if the page makes the heterogeneity explicit.

### 2) Route matrix

Each subject row must show:

- subject id
- current delta class
- current strongest safe sentence
- proposed route
- why that route beats the alternatives
- blocker severity
- expected post-route sentence

Supported `blocker_severity` values:

- `none-known`
- `minor-operator-work`
- `merge-risk`
- `path-authority-gap`
- `rights-or-topology-gap`
- `reopen-now`

Hard rule:

The page must compare alternatives for each disputed subject.
Not every subject deserves the same destination.

### 3) Proof-sharing review

This card states where the campaign can legitimately reason in cohorts.
Required rows:

- fields safe to settle by shared proof
- fields requiring per-subject proof
- fields requiring live destructive check
- fields requiring manual signoff
- unsupported assumptions

Supported `shared_proof_basis` values:

- `same-device-policy-world`
- `same-return-class-same-path-family`
- `same-successor-policy-intent`
- `none-use-per-subject-proof`

Hard rule:

Shared proof may narrow work.
It may not hide exceptions.

### 4) Straggler policy card

Required rows:

- straggler class
- allowed count before claim freeze
- allowed count before campaign abort
- can claim upgrade proceed around them?
- if yes, for what bounded scope?
- who owns unresolved subjects after wave close?

Supported `straggler_class` values:

- `path-still-drifted`
- `mode-still-drifted`
- `merge-risk-unsettled`
- `rights-still-narrower`
- `subject-missing-proof`
- `subject-reopened`

Hard rule:

Stragglers may bound scope.
They may not vanish into aggregate progress.

### 5) Approval sentence

Format:

> `This wave may proceed for [accepted subjects] because each subject now has an explicit route and the remaining heterogeneity is bounded by [straggler policy / bounded scope]. It remains unsafe to speak about [broader sentence] until [specific stragglers / missing proof] are resolved.`

## Required interactions

### A) `Route disputed subject`

Forces explicit comparison of restore, promote, split, and reopen.

### B) `Split to later wave`

Removes a subject from the current settlement wave without erasing it.

### C) `Reopen instead of normalize`

Turns a deferred subject back into an active problem.

### D) `Bound claim to settled subset`

Lets the operator proceed without overclaiming across uncovered subjects.

## Explicit anti-goals

Do not:

- let one noisy cohort hide subject-level disagreement
- let `mostly similar` serve as routing logic by itself
- let unresolved subjects inherit success language from settled neighbors
- let campaign approval proceed without a straggler policy

## Why this page exists

Because once operators try to clean up a field of parity debts, the real work is deciding which subjects share a lane and which ones are trying to trick the team into one false green badge.
''',
'1465-convergence-proof-page-wave-progress-settlement-class-and-claim-upgrade-interface-spec.md': '''
# Convergence proof page: wave progress, settlement class, and claim upgrade interface spec

## Purpose

After the campaign is shaped, the product needs one durable page that proves what the wave actually accomplished.
This is the page that decides whether the archive earned a stronger sentence or only reduced debt.

## Page promise

This page must answer:

> what fraction of the intended cohort really settled, what class of settlement happened, what stragglers remain, and exactly what claim can be upgraded now without lying?

## Fixed page order

1. **Wave outcome header**
2. **Coverage proof card**
3. **Settlement class card**
4. **Claim-upgrade card**
5. **Residual straggler card**
6. **Outcome sentence**

### 1) Wave outcome header

Show:

- campaign id
- wave id
- start and end time
- subjects attempted
- subjects settled
- subjects deferred
- subjects reopened
- current wave outcome

Supported `current_wave_outcome` values:

- `fully-settled`
- `partially-settled`
- `bounded-success`
- `debt-reduced-only`
- `aborted`
- `reopened`

Hard rule:

A wave cannot use a green outcome when reopened subjects remain hidden inside `other`.

### 2) Coverage proof card

Required rows:

- attempted subject count
- successfully settled subject count
- excluded-by-design subject count
- failed or reopened subject count
- exact list of uncovered subjects
- evidence freshness for settlement proof

Hard rule:

Coverage must be enumerable.
Percentages alone are not enough.

### 3) Settlement class card

Required rows:

- dominant settlement class
- secondary settlement classes
- whether exact restoration occurred for all covered subjects
- whether successor promotion occurred for any covered subjects
- whether bounded-scope narrowing was used
- whether any subject remains on temporary debt after wave close

Supported `dominant_settlement_class` values:

- `exact-baseline-restored`
- `approved-successor-baseline`
- `mixed-settlement-bounded`
- `temporary-debt-reduced`
- `failed-and-reopened`

Hard rule:

`mixed settlement` is a valid class.
It may not be mislabeled as exact restoration.

### 4) Claim-upgrade card

Required rows:

- previous strongest safe sentence
- new strongest safe sentence
- scope of new sentence
- blocked broader sentence
- missing proof for broader sentence
- downgrade condition if drift reappears

Hard rule:

Claim upgrades must attach to the actually covered scope, not to campaign ambition.

### 5) Residual straggler card

Required rows:

- straggler ids
- residual debt classes
- owners
- expiry or next review
- whether they block family-wide success
- next required action

Hard rule:

A successful bounded wave must still publish who remained outside the winning sentence.

### 6) Outcome sentence

Format:

> `This wave achieved [dominant settlement class] for [scope of new sentence]. It is safe to say [new strongest safe sentence] for that scope. It is not safe to say [blocked broader sentence] because [residual stragglers / missing proof] remain.`

## Required interactions

### A) `Publish bounded win`

Allows a narrower stronger sentence for covered subjects only.

### B) `Carry forward stragglers`

Creates follow-on ownership without erasing residual debt.

### C) `Upgrade to family-wide settlement`

Allowed only when the broader scope is actually covered.

### D) `Mark debt-reduction-only`

Prevents overclaim when the wave improved conditions but did not settle enough to upgrade claims.

## Explicit anti-goals

Do not:

- let `most subjects fixed` imply family-wide success
- let exact and successor settlement share one success badge
- let reopened subjects disappear after a mostly good wave
- let claim scope exceed proof scope

## Why this page exists

Because cleanup work often genuinely helps without fully restoring baseline truth, and the product must be able to tell the difference without embarrassment.
''',
'1466-convergence-timeline-page-wave-entry-reconciliation-settlement-and-straggler-events-interface-spec.md': '''
# Convergence timeline page: wave entry, reconciliation, settlement, and straggler events interface spec

## Purpose

The archive already had subject timelines.
Once settlement becomes a campaign, it also needs one timeline that shows how the wave evolved, when its claim ceiling changed, and which stragglers kept the broader sentence blocked.

## Timeline promise

This page must answer:

> how did this settlement wave evolve over time, when did subjects enter or fall out, when did the claim narrow or upgrade, and what events kept full success blocked?

## Event families

### 1) Campaign-shape events

Supported values:

- `campaign-created`
- `cohort-expanded`
- `cohort-trimmed`
- `route-changed`
- `safety-fence-armed`

### 2) Subject-settlement events

Supported values:

- `subject-routed-to-restore`
- `subject-routed-to-successor`
- `subject-routed-to-reopen`
- `subject-restored-exactly`
- `subject-promoted-to-successor`
- `subject-kept-temporary`
- `subject-dropped-from-wave`

### 3) Risk and claim events

Supported values:

- `merge-risk-discovered`
- `overwrite-risk-blocked`
- `claim-frozen`
- `bounded-claim-published`
- `broader-claim-unblocked`
- `campaign-aborted`

### 4) Straggler events

Supported values:

- `straggler-created`
- `straggler-expiry-near`
- `straggler-reassigned`
- `straggler-reopened`
- `straggler-settled`

## Required timeline controls

The page must let operators filter by:

- subject
- route
- settlement class
- claim effect
- straggler state
- time window

## Required summary rail

Pinned above the timeline:

- current strongest safe sentence
- broader blocked sentence
- number of uncovered subjects
- next campaign gate
- whether the campaign is still safe to widen

## Explicit anti-goals

Do not:

- show only task completion events
- hide claim-freeze or claim-upgrade moments
- collapse subject settlement and cohort settlement into one timestamp
- let straggler creation disappear after a later bounded win

## Why this page exists

Because settlement campaigns are as much about preserving truthful claim evolution as they are about recording the mechanical fixes.
''',
'1467-convergence-lineage-receipt-page-cohort-settlement-coverage-and-blocked-stronger-sentences-interface-spec.md': '''
# Convergence lineage receipt page: cohort settlement, coverage, and blocked stronger sentences interface spec

## Purpose

After a settlement wave ends, the next operator still needs one durable receipt that says what really got settled, what scope the stronger sentence now covers, and which stragglers still keep the broader claim blocked.

## Receipt contract

This receipt is the handoff object for campaign truth.
It is not a worklog.
It is a statement of settled scope, residual debt, and remaining honesty limits.

## Fixed page order

1. **Receipt header**
2. **Covered-scope card**
3. **Settlement-class card**
4. **Residual-straggler card**
5. **Claim-ceiling card**
6. **Handoff sentence**

### 1) Receipt header

Show:

- campaign id
- wave id
- receipt time
- owner at close
- settlement outcome
- coverage summary

### 2) Covered-scope card

Required rows:

- included subjects
- settled subjects
- excluded subjects
- reopened subjects
- proof freshness horizon
- next mandatory rereview

### 3) Settlement-class card

Required rows:

- final settlement class
- exact restore count
- successor promotion count
- temporary debt carried forward count
- bounded subset description

### 4) Residual-straggler card

Required rows:

- straggler ids
- why each remains outside the stronger sentence
- owner
- expiry
- next action

### 5) Claim-ceiling card

Required rows:

- strongest safe sentence now
- exact scope of that sentence
- next blocked stronger sentence
- what would unlock it
- automatic downgrade trigger

Hard rule:

The receipt must state the broader blocked sentence even when the bounded scope outcome is good.

### 6) Handoff sentence

Format:

> `This receipt proves [final settlement class] for [exact scope of that sentence]. It remains unsafe to say [next blocked stronger sentence] because [straggler ids / missing proof] remain outside the settled scope.`

## Explicit anti-goals

Do not:

- turn a bounded win into a universal claim
- omit reopened or carried-forward subjects
- hide temporary debt behind a generic closed status
- issue a receipt with no rereview horizon when stragglers still exist

## Why this page exists

Because the archive should never again need a detective to determine whether a cleanup campaign really settled the cohort or merely improved the average.
'''
}

for name, content in new_files.items():
    write(name, content)

prepend(root / 'README.md', '''
## Revision addendum — return-delta convergence, cohort settlement, and straggler truth after rev0386

This pass locks the next seam after return-delta debt and baseline rebind: **how to settle many changed-but-working states as a group without silently promoting drift or hiding the subjects that still block the stronger sentence**.
The archive already knew how to make one tolerated mismatch explicit.
What it still lacked was one explicit answer to:

> once many return deltas exist at once, how do we shape a settlement wave, route each subject honestly, publish stragglers, and upgrade claims only for the scope actually proved?

This revision adds that answer.
It contributes:

- one new **Resilio evaluation** focused on why current convergence truth still fragments across per-folder disconnect/reconnect, default-mode placement, manual path choice, existing-directory merge, folder-not-empty risk, local-only rename/move constraints, peer-right drift, and config-mode parameter distribution instead of one durable convergence campaign object
- five new **interface specs** for convergence campaign contract sheet, convergence shaping review, convergence proof, convergence timeline, and convergence lineage receipt
- a tighter non-clone line based on current official Resilio evidence that multi-subject settlement today is real work but still lives mostly as repeated per-share memory and one-off routing rather than one operator-facing settlement truth
- five hard product decisions:
  - **many tolerated deltas become a first-class convergence campaign once they are being judged as one success story**
  - **every subject in the campaign must route explicitly to exact restore, successor promotion, temporary keep, split-out, or reopen**
  - **partial success may upgrade claims only for the scope actually settled**
  - **stragglers remain first-class objects and cannot be averaged away**
  - **cohort success is a proof-and-scope statement, not a vibes statement**

New docs in this tranche:

- `1462-resilio-return-delta-convergence-cohort-settlement-and-straggler-truth-evaluation.md`
- `1463-convergence-campaign-contract-sheet-page-debt-cohort-target-end-state-and-safety-fences-interface-spec.md`
- `1464-convergence-shaping-review-page-restore-promote-split-and-reopen-routing-interface-spec.md`
- `1465-convergence-proof-page-wave-progress-settlement-class-and-claim-upgrade-interface-spec.md`
- `1466-convergence-timeline-page-wave-entry-reconciliation-settlement-and-straggler-events-interface-spec.md`
- `1467-convergence-lineage-receipt-page-cohort-settlement-coverage-and-blocked-stronger-sentences-interface-spec.md`

### Why this pass matters

The previous tranche answered `when one changed active state is debt, successor, or reopen-worthy`.
This tranche answers the next harder question:

> `when there are many such states, how do we settle them together without lying about coverage, hiding stragglers, or silently rounding a bounded win up to family-wide success?`

Current official Resilio material is useful here because it already proves that convergence is real, but still fragmented:

- duplicate `(1)` folders are still fixed through per-folder disconnect/reconnect and manual repointing
- Disconnected mode and Android Simple mode still govern whether custom placement is possible for future arrivals
- existing-directory connection still routes through folder-specific merge and non-empty-folder confirmation
- reconnect can still create new paths and structural forks
- move/rename rules can still stay local or require disconnect/reconnect
- peer disconnect can still leave bytes present while future-update rights diverge
- configuration mode can still apply settings across multiple machines without becoming a settlement campaign for already drifted live subjects

That candor is worth borrowing.
The contract shape is not.
AnonSync should not clone a world where the operator still has to reconstruct cohort settlement truth out of repeated folder mechanics and memory.
''')

prepend(docs / '00-status.md', '''
## Revision addendum — status shift toward return-delta convergence and cohort settlement after rev0386

The next seam after explicit parity debt is now explicit:

- the archive can already say when one changed active state is tolerated debt, successor candidate, or reopen-worthy
- it still needed to own the harder multi-subject truth where many such states are being judged together and therefore need one campaign, one claim ceiling, and one honest story about stragglers

This pass turns that gap into a first-class product object: **the convergence campaign**.

What is newly true in the archive:

- many tolerated deltas can now be shaped as one settlement effort without hiding subject-level routing
- every subject in a settlement wave now gets an explicit route: exact restore, promote successor, keep temporary, split out, or reopen
- partial success can now publish a bounded stronger sentence without overclaiming across uncovered subjects
- stragglers now remain visible as blockers, not statistical noise
- campaign handoff now preserves settled scope, carried-forward debt, and the next blocked stronger sentence

New docs in this tranche:

- `1462-resilio-return-delta-convergence-cohort-settlement-and-straggler-truth-evaluation.md`
- `1463-convergence-campaign-contract-sheet-page-debt-cohort-target-end-state-and-safety-fences-interface-spec.md`
- `1464-convergence-shaping-review-page-restore-promote-split-and-reopen-routing-interface-spec.md`
- `1465-convergence-proof-page-wave-progress-settlement-class-and-claim-upgrade-interface-spec.md`
- `1466-convergence-timeline-page-wave-entry-reconciliation-settlement-and-straggler-events-interface-spec.md`
- `1467-convergence-lineage-receipt-page-cohort-settlement-coverage-and-blocked-stronger-sentences-interface-spec.md`

### Why this pass matters

The archive now has a cleaner answer to another very common operator failure mode:

> a team cleaned up most of a messy field of changed-but-working states, then gradually started talking as if the whole baseline was back even though a few drifted survivors, reopen-worthy subjects, or successor-only exceptions were still doing all the real blocking work.

That ambiguity is now explicitly disallowed.
''')

prepend(docs / '10-resilio-sync-evaluation.md', '''
## Revision addendum — return-delta convergence and cohort settlement after rev0386

The next non-clone seam is now explicit: **current Resilio admits many repeated convergence mechanics, but still lacks one operator-facing cohort-settlement contract**.
Current official material remains useful and candid:

- `Folders are duplicating with an index (i) in their name` still says duplicate-path cleanup is performed by disconnecting and reconnecting the affected folder to the intended location, while default mode still auto-places new folders into the default storage folder unless the device is switched to Disconnected mode
- `How to manually set the location of the folders synced across linked devices?` still says manual placement requires Disconnected mode and repeated `Connect` actions, and Android still requires Simple mode to be disabled
- `Disconnecting and Removing Folders` still says reconnect may propose a different path and may create a new `(1)` directory
- `Can I connect two pre-populated pre-existing folders?` still says merging an existing directory is a folder-specific connect workflow with non-empty-folder confirmation
- `Folder not empty` still warns that reconnecting or adding into an existing non-empty directory can overwrite or delete already-present files
- `Can I move or rename a syncing folder?` still says renaming remains local-only and moving across partitions can require disconnect/reconnect
- `User Management` still says peer disconnect leaves already-synchronized bytes in place while future updates are suspended
- `Running Sync in configuration mode` still says configuration mode helps apply the same settings on a number of different machines

That is enough to justify a sharper product stance:

- **borrow Resilio's candor that convergence often means repeated local reconnect and placement work**
- **borrow the honesty that broad defaults help future state more than they settle already-diverged live subjects**
- **do not clone a world where the operator still has to infer cohort truth, coverage, stragglers, and claim ceiling from many repeated per-folder operations**

The replacement line for AnonSync is now stronger:

- model **convergence campaigns** directly
- require an explicit route for every subject in the wave
- treat partial success as a bounded proof statement, not as generalized family-wide success
- keep stragglers as first-class blockers with owners and follow-on paths
- preserve exactly which stronger sentence is safe for covered scope and which broader sentence is still blocked
''')

prepend(docs / '11-resilio-borrow-line-and-non-clone-scorecard.md', '''
## Revision addendum — non-clone line hardens around convergence campaigns after rev0386

Another current Resilio pass makes the next non-clone obligation clearer:

- **AnonSync should model return-delta settlement as a first-class convergence campaign instead of letting multi-subject cleanup live as repeated per-folder memory work.**

Resilio still deserves credit for exposing the ingredients:

- duplicate-path cleanup still routes through disconnect/reconnect and manual repointing
- Disconnected mode and Android Simple mode still govern custom placement behavior
- existing-directory connection is still a folder-specific merge decision
- reconnect can still create new paths and `(1)` folders
- move/rename constraints can still force structural re-entry instead of in-place normalization
- peer disconnect can still keep old bytes visible while future-update rights narrow
- config mode can still distribute the same settings across multiple machines

But that is exactly why the product should not clone the contract shape.
The current operator still has to reconstruct from multiple pages whether a settlement effort has:

- actually covered the intended cohort
- routed each subject to restore versus promote versus reopen correctly
- earned a stronger sentence for all subjects or only a bounded subset
- hidden stragglers that still block the broader claim

So the borrow line sharpens again:

### Keep

- candid distinction between future-default shaping and present-state cleanup
- explicit admission that reconnect, repoint, and merge are real settlement mechanics
- explicit warnings where normalization can overwrite, fork path, or preserve rights drift

### Do not clone

- any workflow where multi-subject settlement is only repeated folder surgery
- any `mostly fixed` story that silently rounds up to cohort success
- any product that lets uncovered subjects vanish into aggregate progress

### Replace with

- convergence campaign contract sheets
- convergence shaping reviews
- convergence proofs with settlement class and bounded claim upgrades
- convergence timelines with straggler events
- convergence lineage receipts with exact covered scope and blocked broader sentence
''')

prepend(docs / '12-resilio-interface-clone-veto-tests-and-page-obligations.md', '''
## Revision addendum — interface clone veto tests extend to convergence campaigns after rev0386

The page-family veto line is now stricter.
After this pass, any interface that treats a many-subject cleanup effort as generic maintenance or that reports aggregate progress without subject-level settlement truth should be treated as a clone smell.

New veto tests:

1. **If the page says the campaign succeeded but does not say which exact subjects are covered by that sentence, fail it.**
2. **If subjects can route to restore, successor, split-out, or reopen but the page hides those route differences, fail it.**
3. **If stragglers can still block the broader claim and the page averages them away, fail it.**
4. **If a bounded win can be mistaken for family-wide success, fail it.**
5. **If the page cannot say what stronger sentence is safe for covered scope and what broader sentence is still blocked, fail it.**

New page obligations:

- every many-subject settlement effort must have a **convergence campaign contract sheet**
- every campaign must expose a **convergence shaping review** with explicit per-subject routes
- every settlement wave must publish a **convergence proof** with settlement class and exact claim scope
- every campaign timeline must preserve straggler creation, settlement, and claim-freeze / claim-upgrade events
- every campaign receipt must preserve the broader blocked sentence, not only the bounded win
''')

prepend(docs / '20-product-direction.md', '''
## Revision addendum — product direction shift toward convergence campaigns and bounded settlement truth after rev0386

The archive now has enough structure that the next product obligation becomes explicit:

- a changed active state can be represented honestly as parity debt
- the next obligation is to settle many such debts together without turning a bounded cleanup wave into a false family-wide victory

This matters because the product is now deliberately choosing not to let `we fixed most of them` impersonate `the baseline is back`.

The direction hardens around five decisions:

1. **many-subject cleanup is a first-class product object once it carries one success story**
2. **every subject in a campaign needs an explicit route, not inherited optimism**
3. **bounded wins are legitimate product truths and should stay bounded**
4. **stragglers are product truth, not noise**
5. **claim scope must equal proof scope even when progress is impressive**

This gives the archive a cleaner long-range direction:

- controls can be suspended truthfully
- changed returns can become explicit parity debt
- many parity debts can be gathered into convergence campaigns
- campaigns can publish bounded wins without lying about uncovered subjects
- broader baseline claims return only when the actual cohort is settled, not when the narrative gets tired
''')

prepend(docs / 'sources.md', '''
## rev0387 source set — return-delta convergence, cohort settlement, and straggler truth

The most load-bearing source set for this pass was:

- Resilio's current `Folders are duplicating with an index (i) in their name.` article, which still says duplicate-path cleanup routes through per-folder disconnect/reconnect and that devices in Selective Sync or Synced mode auto-place arriving folders into the default storage folder unless the device is switched to Disconnected mode.
- Resilio's current `How to manually set the location of the folders synced across linked devices?` article, which still says manual placement requires Disconnected mode plus repeated `Connect`, and that Android still requires disabling Simple mode.
- Resilio's current `Disconnecting and Removing Folders` article, which still says reconnect may propose a different default path and may create a new directory with `(1)` appended.
- Resilio's current `Can I connect two pre-populated pre-existing folders?` article, which still says existing-directory reconciliation is a folder-specific connect workflow and still calls out the need to confirm when the target is not empty.
- Resilio's current `Folder not empty` article, which still warns that files already present in the receiving folder may be deleted or overwritten.
- Resilio's current `Can I move or rename a syncing folder?` article, which still says renaming is local-only and that moving across partitions can require disconnect/reconnect.
- Resilio's current `User Management` article, which still says peer disconnect suspends future updates while already-synchronized files remain.
- Resilio's current `Running Sync in configuration mode` article, which still says configuration mode is helpful when applying the same settings on a number of different machines.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that convergence often requires repeated structural per-folder work and that defaults help future arrivals more than already drifted live subjects
- but current Resilio still answers `how much of this cohort is really settled, which subjects remain outside the stronger sentence, and when is a bounded win all we honestly have?` too diffusely
- AnonSync should therefore prefer explicit convergence campaign sheets, shaping reviews, settlement proofs, convergence timelines, and durable campaign receipts over overloaded `cleanup complete` or `mostly fixed` language

Primary sources:

- Folders are duplicating with an index (i) in their name.  
  https://help.resilio.com/hc/en-us/articles/204753869-Folders-are-duplicating-with-an-index-i-in-their-name

- How to manually set the location of the folders synced across linked devices?  
  https://help.resilio.com/hc/en-us/articles/206216615-How-to-manually-set-the-location-of-the-folders-synced-across-linked-devices

- Disconnecting and Removing Folders  
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- Can I connect two pre-populated pre-existing folders?  
  https://help.resilio.com/hc/en-us/articles/205506569-Can-I-connect-two-pre-populated-pre-existing-folders

- Folder not empty  
  https://help.resilio.com/hc/en-us/articles/204753689-Folder-not-empty

- Can I move or rename a syncing folder?  
  https://help.resilio.com/hc/en-us/articles/205450655-Can-I-move-or-rename-a-syncing-folder

- User Management  
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode
''')

(root / 'apply_rev0387.py').write_text((root / 'apply_rev0387.py').read_text(encoding='utf-8'), encoding='utf-8')
