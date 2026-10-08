from pathlib import Path

root = Path('/mnt/data/work0386')
docs = root / 'docs'

def write(name: str, content: str):
    (docs / name).write_text(content, encoding='utf-8')

def prepend(path: Path, text: str):
    old = path.read_text(encoding='utf-8')
    path.write_text(text.rstrip() + '\n\n' + old, encoding='utf-8')

new_files = {
'1456-resilio-return-delta-debt-baseline-rebind-and-reopen-fragmentation-evaluation.md': '''# Resilio return-delta debt, baseline rebind, and reopen fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- suspend a control truthfully
- bring activity back through typed return paths
- distinguish motion restored from protection restored
- preserve structural delta while requalification is still pending

What it still lacked was the next ordinary operator answer:

> once a changed return is accepted and the system is working again, is that change a temporary debt, a deliberate successor state, or a reason to reopen because we never truly got back to the intended protected state?

That is the seam this pass locks.
A real operator cannot afford a vague `still syncing` verdict.
The product needs a first-class answer for **accepted return delta, parity debt, baseline rebind, and honest reopen**.

Current official Resilio material is useful here because it already proves that a changed but working state can persist after return:

- `Disconnecting and Removing Folders`
- `Folders are duplicating with an index (i) in their name`
- `How to manually set the location of the folders synced across linked devices?`
- `Folder Types and Management`
- `Synchronization Modes`
- `Can I connect two pre-populated pre-existing folders?`
- `Folder not empty`
- `Can I move or rename a syncing folder?`
- `User Management`

## Current official Resilio evidence that matters here

Current official docs still show all of the following:

- `Disconnecting and Removing Folders` still says reconnect may propose a default path different from the original path, may create a new directory, and may append `(1)` if a same-name folder already exists. So a changed path can become the active working state even when the operator wanted the original home back.
- The same article still says disconnect removes placeholder files if Selective Sync was enabled. So some returns re-enter with less local witness state than before even when activity later resumes.
- `Folders are duplicating with an index (i) in their name` still says devices in Selective Sync or Synced mode place arriving folders into the default storage location, and that choosing Disconnected mode is the way to force explicit manual placement later. That means a changed path is not an exotic edge case; it is a normal byproduct of default-mode behavior.
- `How to manually set the location of the folders synced across linked devices?` still says disabling Simple mode on Android causes new linked-device folders to arrive in Disconnected mode so the operator can choose a custom path at each connect. That is useful, but it also confirms that path authority and return authority do not live in one obvious place.
- `Folder Types and Management` still says disconnected folders have no folder path associated locally, while Selective Sync preserves a visible tree through placeholders and Full Sync keeps all bytes. So a working post-return state may differ materially in what kind of local residency and witness it actually provides.
- `Synchronization Modes` still distinguishes Disconnected, Selective Sync, and Synced as three different data-movement postures. A return that lands in a different posture can still look healthy while preserving different local guarantees.
- `Can I connect two pre-populated pre-existing folders?` still says same-hash files will not be re-synced, same-name different-hash files resolve by latest timestamp, and other files are merged into the folder tree. So one operator path to a working state is explicitly a merge-successor state, not a restoration of exact prior parity.
- `Folder not empty` still warns that if you add or reconnect into an already existing non-empty directory, files that were already present there might be deleted or overwritten. That is a huge clue that some working returns have durable survivor debt rather than clean parity.
- `Can I move or rename a syncing folder?` still says renaming a folder affects only the device where it is renamed, and other devices are not updated with the new name. It also still says that moving to a new partition on Windows or Mac requires disconnect and reconnect. So a path/name successor can remain active without becoming a globally aligned baseline.
- `User Management` still says disconnecting a peer suspends future updates while already-synchronized files remain in the folder. So a working content tree may persist after rights changed underneath.

So current Resilio still clearly admits serious post-return truths:

- an active working state may still have a different path than the old intended home
- a working state may preserve different local residency or placeholder posture than before
- a merge-based return can remain active after timestamp winner rules changed the tree
- local rename and move semantics can drift name/path parity without ending sync activity
- permission/future-update posture can differ while old bytes remain visible

But those truths still do not become one operator-facing **return-delta debt / baseline rebind / honest reopen** object.

## What Resilio still gets right

### 1) It is candid that working does not always mean same-place or same-shape

Path forks, `(1)` suffixes, disconnected mode, placeholder posture, and merge rules are openly documented.
That honesty is worth borrowing.

### 2) It exposes path authority and mode authority as real constraints

Default storage behavior, Disconnected mode, and Android Simple mode make clear that re-entry can be correct or drifted depending on where authority lives.
That matters.

### 3) It preserves some survivor warnings

`Folder not empty`, placeholder removal, and peer-disconnect behavior all admit that visible bytes may survive even when the underlying contract changed.
That is useful.

## Where current Resilio still fragments the operator answer

### A) There is no canonical answer to `is this changed return still a temporary debt or the new intended baseline?`

A careful operator can infer it.
But the product still does not answer in one place:

- whether the new path is temporary or adopted
- whether placeholder/full-byte posture is an accepted successor or a debt
- whether merge results were merely tolerated or formally blessed
- whether rights/topology deltas are temporary or intentional
- when the changed return must be fixed, promoted, or reopened

### B) `Still syncing` is allowed to masquerade as parity

Current docs explain how to reconnect, connect to an existing directory, disable Simple mode, or change synchronization mode.
What they do not provide is one durable verdict about whether the resulting active state is:

- exact restoration
- temporary accepted delta
- permanent successor state
- unresolved debt requiring later exact restore
- or grounds to reopen the associated case/control/rollout

### C) There is no first-class aging model for accepted return debt

Current docs tell operators how to reach a working state.
They do not tell them when a changed working state expires as a tolerable compromise.
The product still lacks one object that can say:

- owner of the accepted delta
- expiry date for the tolerated mismatch
- proof needed to promote the successor state to the new baseline
- triggers that worsen the debt and reopen the case

## Hard product decision unlocked by this pass

AnonSync should not let a changed-but-working return silently become the new normal.
It should promote every material post-return mismatch into a first-class object that can separately express:

- accepted delta class
- whether the delta is exact-restoration debt or intentional successor candidate
- owner and expiry
- next required proof or reconciliation step
- whether the stronger old sentence is still blocked
- whether the next honest move is exact restore, successor promotion, or reopen

That is the right next seam because it answers the operator question that always follows a messy but successful return:

> we are working again, but is this merely a tolerated changed state, when does that tolerance expire, and what must happen before calling it the new baseline instead of drift?

## Replacement line for AnonSync

Borrow from Resilio:

- candor that path, mode, and merge results can produce a working but changed state
- explicit admission that rights, placeholders, and default paths can diverge from the old state
- honesty that some warnings imply durable survivor debt

Do not clone from Resilio:

- any contract where `still syncing` silently rounds up to `same protected state`
- any workflow where changed path/mode/topology becomes the new baseline without explicit promotion
- any product shape where the operator must remember expiry, owner, and reopen triggers out of band

AnonSync should instead ship explicit pages for:

- return-delta contract sheet
- delta-aging review
- parity-debt proof and baseline rebind
- return-delta timeline
- return-delta lineage receipt
''',
'1457-return-delta-contract-sheet-page-accepted-successor-delta-expiry-and-owner-interface-spec.md': '''# Return-delta contract sheet page: accepted successor delta, expiry, and owner interface spec

## Purpose

After the archive learned how to bring protection back truthfully, it still needed one ordinary page for the next operator question:

> this return is active, but what exactly is still different from the old protected state, who owns that difference, and when does the tolerance expire?

## Core decision

AnonSync must expose one first-class **Return-delta contract sheet** whenever activity or protection comes back in a changed-but-accepted state.

## Fixed page order

1. **Return-delta header**
2. **Accepted-delta card**
3. **Parity-debt card**
4. **Expiry and owner card**
5. **Promotion-or-restore card**
6. **Decision sentence**

### 1) Return-delta header

Show:

- return-delta id
- linked return id
- linked suspension id
- linked control / case / rollout id
- current delta status
- owner
- created time
- next rereview time
- current strongest safe sentence

Supported `current_delta_status` values:

- `newly-accepted`
- `temporary-accepted`
- `temporary-accepted-expiring-soon`
- `candidate-successor-baseline`
- `awaiting-exact-restore`
- `promoted-to-new-baseline`
- `reopened`
- `retired-after-exact-restore`

Hard rule:

A changed return may not disappear into normal state merely because the system is active again.

### 2) Accepted-delta card

This card states exactly what changed.
Required rows:

- previous intended protected state
- current active state
- accepted delta class
- exact difference summary
- why the difference is currently tolerated
- whether the delta is temporary or successor-candidate

Supported `accepted_delta_class` values:

- `path-successor`
- `mode-successor`
- `placeholder-successor`
- `merge-successor`
- `permission-successor`
- `topology-successor`
- `name-plane-successor`
- `multi-delta`

Hard rule:

The page must describe the difference in operator language, not only as machine diff fields.

### 3) Parity-debt card

This card records what claim remains blocked because of the delta.
Required rows:

- blocked stronger sentence
- weaker still-safe sentence
- missing proof to remove debt
- hidden survivor risk
- reversibility class
- consequence if left unresolved

Supported `reversibility_class` values:

- `easy-reverse`
- `planned-maintenance-reverse`
- `requires-merge-reconciliation`
- `requires-rights-or-policy-change`
- `cannot-return-exactly`

Hard rule:

`working` is not allowed to erase the blocked stronger sentence.

### 4) Expiry and owner card

This card makes tolerated drift concrete.
Required rows:

- owner
- expiry type
- expiry time
- rereview cadence
- automatic downgrade on miss?
- reopen trigger class

Supported `expiry_type` values:

- `fixed-time-expiry`
- `next-maintenance-window`
- `next-proof-window`
- `until-exact-restore-completes`
- `until-successor-promotion-decision`

Supported `reopen_trigger_class` values:

- `same-delta-persists-past-expiry`
- `delta-worsens`
- `same-cause-recurrence`
- `scope-expands`
- `owner-missing`
- `required-proof-missed`

Hard rule:

A tolerated delta without owner and expiry is not an accepted state; it is unmanaged drift.

### 5) Promotion-or-restore card

This card states the next honest branch.
Required rows:

- planned next branch
- preconditions
- proof required
- who decides
- what stronger sentence could return if branch succeeds
- what happens if branch fails

Supported `planned_next_branch` values:

- `exact-restore`
- `keep-temporary-and-rereview`
- `promote-successor-baseline`
- `split-state-and-narrow-claim`
- `reopen-linked-case`

Hard rule:

The branch must be explicit even if the answer is `keep temporary and rereview`.

### 6) Decision sentence

Format:

> `This subject is active in a [accepted_delta_class] return state owned by [owner] until [expiry_time]. It is safe to say [weaker still-safe sentence], but not safe to say [blocked stronger sentence] until [missing proof / branch].`

## Required interactions

### A) `Accept temporarily`

Creates a return-delta object with owner, expiry, and blocked stronger sentence.

### B) `Promote as successor candidate`

Does not promote immediately.
It only marks the delta as eligible for baseline decision.

### C) `Schedule exact restore`

Attaches maintenance window or proof window.

### D) `Reopen now`

Moves the state from tolerated delta to active problem.

## Explicit anti-goals

Do not:

- collapse `temporary accepted` and `promoted baseline`
- hide accepted delta inside generic healthy status
- allow missing owner or missing expiry
- allow `same visible folder name` to stand in for parity

## Why this page exists

Because a changed return is often operationally acceptable for a while, but that does not make it the new intended state.
The product must remember the difference so operators do not normalize drift by accident.
''',
'1458-delta-aging-review-page-restore-exact-promote-successor-or-reopen-interface-spec.md': '''# Delta-aging review page: restore exact, promote successor, or reopen interface spec

## Purpose

After the archive learned how to register accepted return debt, it still needed one review page that answers the harder question:

> now that this changed return has aged for a while, should we restore exact parity, deliberately adopt the successor state, narrow the claim, or reopen because the debt is no longer honest?

## Core decision

AnonSync must expose one first-class **Delta-aging review** page whenever a tolerated return delta reaches its rereview point, worsens, or becomes a candidate for permanent adoption.

## Fixed page order

1. **Review header**
2. **State comparison panel**
3. **Aging pressure panel**
4. **Decision ladder**
5. **Outcome proof preview**
6. **Review sentence**

### 1) Review header

Show:

- review id
- linked return-delta id
- owner
- age since acceptance
- expiry posture
- review trigger
- current safe sentence

Supported `review_trigger` values:

- `scheduled-rereview`
- `expiry-reached`
- `delta-worsened`
- `proof-arrived`
- `same-cause-near-miss`
- `same-cause-recurrence`
- `operator-requested`

### 2) State comparison panel

Compare four columns:

- pre-bypass intended state
- current active state
- exact-restore target
- candidate successor baseline

Hard rule:

The page must make visible whether the proposed successor is identical to the current active state or still requires additional cleanup before promotion.

### 3) Aging pressure panel

Required rows:

- operational benefit of keeping current state
- surprise cost of current mismatch
- hidden survivor risk
- proof depth available
- reversibility remaining
- claim damage if left unresolved

Supported `surprise_cost` values:

- `small-and-local`
- `operator-visible`
- `user-visible`
- `cross-subject-confusing`
- `compliance-or-policy-sensitive`

Supported `proof_depth_available` values:

- `weak-observation-only`
- `moderate-usage-history`
- `strong-targeted-proof`
- `strong-repeated-proof`

### 4) Decision ladder

Present exactly five mutually exclusive outcomes:

1. `restore-exact-now`
2. `keep-temporary-with-shorter-expiry`
3. `promote-current-state-to-successor-baseline`
4. `split-state-and-narrow-the-protected-claim`
5. `reopen-linked-case-or-control`

Hard rules:

- `promote current state` must require proof that the mismatch is intentional, understood, and not a hidden leftover.
- `keep temporary` must shorten or reaffirm expiry explicitly.
- `split state` is only valid when the operator can describe the narrower truth precisely.

### 5) Outcome proof preview

For each outcome show:

- proof required
- blocked sentence removed if outcome succeeds
- blocked sentence that still remains even after success
- rollback / undo class
- who must sign off

### 6) Review sentence

Format:

> `After [age since acceptance], the current [accepted_delta_class] state is reviewed as [decision]. The safe sentence remains [current safe sentence] until [proof / exact restore / promotion] completes.`

## Required interactions

### A) `Reaffirm temporary`

Requires new expiry and explicit reason why exact restore is still postponed.

### B) `Promote successor baseline`

Requires successor description, proof basis, and explicit retirement of the old baseline sentence.

### C) `Narrow claim`

Requires new weaker stable sentence and explicit does-not-mean statement.

### D) `Reopen`

Requires trigger and linked case/control/rollout target.

## Anti-goals

Do not:

- let time alone promote a successor
- let frequent use stand in for proof that the changed state is intentional and safe
- hide claim narrowing inside a healthy badge
- allow exact-restore and successor-promotion language to blur together

## Why this page exists

Because changed-but-working states age.
Some deserve exact restoration.
Some deserve deliberate successor promotion.
Some deserve reopen.
The product must own that choice instead of leaving it to memory and habit.
''',
'1459-parity-debt-proof-page-temporary-accepted-delta-baseline-rebind-and-claim-ceiling-interface-spec.md': '''# Parity-debt proof page: temporary accepted delta, baseline rebind, and claim ceiling interface spec

## Purpose

After the archive learned how to review aging return debt, it still needed one proof page that records the winning branch honestly.

## Core decision

AnonSync must expose one first-class **Parity-debt proof** page whenever a return delta is reaffirmed, exactly restored, promoted to a successor baseline, or reopened.

## Fixed page order

1. **Proof header**
2. **Winning branch card**
3. **Proof basis card**
4. **Baseline rebind card**
5. **Claim ceiling card**
6. **Proof sentence**

### 1) Proof header

Show:

- proof id
- linked return-delta id
- linked aging review id
- winning branch
- proof time
- approver
- resulting status

### 2) Winning branch card

Required rows:

- previous delta status
- chosen branch
- resulting state
- immediate follow-up obligation
- expiration / retirement behavior

Supported `winning_branch` values:

- `temporary-reaffirmed`
- `exact-restore-completed`
- `successor-baseline-promoted`
- `claim-narrowed-stable`
- `reopened`

### 3) Proof basis card

Required rows:

- observed evidence
- targeted proof steps performed
- unresolved caveats
- why the branch is honest now
- what evidence would overturn it later

Supported `proof_basis_class` values:

- `configuration-and-observation`
- `targeted-reconciliation-proof`
- `merge-audit-proof`
- `rights-and-topology-proof`
- `insufficient-proof-reopen`

Hard rule:

The page must record why this branch is honest, not merely what button was pressed.

### 4) Baseline rebind card

This card explains whether the old baseline survives.
Required rows:

- old baseline sentence
- new baseline sentence if any
- baseline relation
- effective-from time
- subjects affected
- whether old baseline is retired or remains for other subjects

Supported `baseline_relation` values:

- `old-baseline-restored`
- `old-baseline-kept-delta-still-open`
- `successor-baseline-created`
- `baseline-split`
- `baseline-abandoned-reopen`

Hard rule:

A successor baseline must be created explicitly.
A changed active state may not silently inherit baseline authority.

### 5) Claim ceiling card

Required rows:

- strongest safe sentence now
- stronger blocked sentence still not safe
- next proof if stronger sentence should return later
- downgrade trigger

### 6) Proof sentence

Format:

> `This proof records [winning_branch]. The subject is now honest to describe as [strongest safe sentence now]. It is not honest to describe as [stronger blocked sentence still not safe] until [next proof / none if restored].`

## Required interactions

### A) `Retire debt`

Available only for exact restore or successor baseline promotion.

### B) `Keep debt open`

Available only for temporary reaffirmation.
Requires expiry.

### C) `Create successor baseline`

Requires baseline relation and affected-subject scope.

### D) `Send to reopen`

Links proof directly to the reopened object.

## Anti-goals

Do not:

- let proof pages read like success theater
- let `promoted baseline` happen without explicit old/new baseline relation
- let temporary reaffirmation masquerade as closure

## Why this page exists

Because once a changed return matures, the product must say exactly whether the old parity returned, a successor baseline was deliberately adopted, or the debt proved too dishonest to keep.
''',
'1460-return-delta-timeline-page-accepted-drift-expiry-promotion-and-reopen-events-interface-spec.md': '''# Return-delta timeline page: accepted drift, expiry, promotion, and reopen events interface spec

## Purpose

After the archive learned how to prove the fate of return debt, it still needed one timeline page that preserves how a changed return aged over time.

## Core decision

AnonSync must expose one first-class **Return-delta timeline** page for every non-trivial accepted delta.

## Event classes

The timeline must preserve at least these event types:

- `delta-accepted`
- `owner-assigned`
- `expiry-set`
- `proof-window-missed`
- `delta-worsened`
- `same-cause-near-miss`
- `same-cause-recurrence`
- `temporary-reaffirmed`
- `exact-restore-started`
- `exact-restore-completed`
- `successor-promotion-started`
- `successor-baseline-created`
- `claim-narrowed`
- `reopened`
- `debt-retired`

## Fixed page order

1. **Timeline header**
2. **Debt aging ribbon**
3. **Event ledger**
4. **Sentence-change rail**
5. **Next trigger card**

### 1) Timeline header

Show:

- return-delta id
- age
- current delta status
- current owner
- next expiry / rereview

### 2) Debt aging ribbon

A horizontal band showing:

- accepted
- stable temporary
- expiring
- overdue
- promoted
- restored
- reopened

Hard rule:

The ribbon must not show `healthy` without showing whether debt still exists.

### 3) Event ledger

Each event row must show:

- timestamp
- event type
- actor
- before sentence
- after sentence
- debt size change (`smaller`, `same`, `larger`, `retired`)
- notes

### 4) Sentence-change rail

This rail shows how the strongest safe sentence changed over time.
It must make visible:

- initial blocked stronger sentence
- weaker sentence during temporary acceptance
- sentence after reaffirmation or promotion
- sentence after exact restore or reopen

### 5) Next trigger card

Required rows:

- next forced review
- next automatic downgrade
- next proof expected
- next event that would retire debt
- next event that would reopen immediately

## Required interactions

### A) `Jump to proof`

From any event that changed claim ceiling.

### B) `Compare before and after`

For exact restore, promotion, and reopen events.

### C) `Escalate now`

Available when overdue or worsened.

## Anti-goals

Do not:

- reduce the timeline to operational uptime
- omit missed proof windows
- hide sentence downgrades because bytes kept flowing

## Why this page exists

Because accepted drift is not static.
The operator needs to see whether the gap is shrinking honestly, being normalized dangerously, or getting worse until reopen is unavoidable.
''',
'1461-return-delta-lineage-receipt-page-parity-debt-owner-expiry-and-blocked-stronger-sentences-interface-spec.md': '''# Return-delta lineage receipt page: parity debt, owner, expiry, and blocked stronger sentences interface spec

## Purpose

After the archive learned how to register, review, and prove accepted return debt, it still needed one durable handoff page for the next operator.

## Core decision

AnonSync must expose one first-class **Return-delta lineage receipt** whenever a changed return remains active, is reaffirmed, is promoted, or is retired.

## Fixed page order

1. **Receipt header**
2. **Current debt summary**
3. **Owner and expiry summary**
4. **Baseline relation summary**
5. **Safe language summary**
6. **Next action summary**

### 1) Receipt header

Show:

- receipt id
- return-delta id
- linked return id
- emitted time
- emitted because

Supported `emitted_because` values:

- `delta-created`
- `temporary-reaffirmed`
- `promotion-decided`
- `exact-restore-finished`
- `reopened`
- `handoff-requested`

### 2) Current debt summary

Required rows:

- current delta status
- accepted delta class
- one-line difference summary
- debt active?
- current age

### 3) Owner and expiry summary

Required rows:

- owner
- expiry type
- expiry time
- overdue?
- next rereview

### 4) Baseline relation summary

Required rows:

- old baseline relation
- new baseline relation if any
- exact restore still planned?
- successor promotion already approved?

### 5) Safe language summary

Required rows:

- strongest safe sentence now
- blocked stronger sentence
- unsafe overclaim to avoid
- next proof that could improve the sentence

### 6) Next action summary

Required rows:

- next required action
- next allowed action
- next forbidden silent normalization
- immediate reopen trigger

## Receipt sentence

Format:

> `This receipt says the subject is currently in [current delta status] under a [accepted delta class] difference owned by [owner] until [expiry time]. Safe language stops at [strongest safe sentence now]. Do not silently normalize this into [blocked stronger sentence].`

## Anti-goals

Do not:

- omit owner or expiry
- omit whether debt is still active
- state that the baseline changed unless promotion was explicit
- hide the next forbidden overclaim

## Why this page exists

Because the next operator needs a compact answer to the hardest post-return truth:

> are we still carrying accepted parity debt, who owns it, when does it expire, and what stronger sentence is still unsafe to say?
'''
}

for name, content in new_files.items():
    write(name, content)

prepend(root / 'README.md', '''## Revision addendum — return-delta debt, baseline rebind, and honest successor adoption after rev0385

This pass locks the next seam after control re-arm and return-to-protection: **what to do when the system comes back in a changed-but-working state that is operationally acceptable for a while but not yet the same protected state as before**.
The archive already knew how to suspend controls, bring them back, and keep motion restoration separate from trust restoration.
What it still lacked was one explicit answer to:

> when a changed return keeps working, is that state temporary debt, a deliberate successor baseline, or an unresolved mismatch that must reopen later?

This revision adds that answer.
It contributes:

- one new **Resilio evaluation** focused on why current post-return truth still fragments across reconnect path changes, duplicate `(1)` folders, mode/default-location behavior, existing-directory merges, folder-not-empty risks, local-only renames, move/reconnect boundaries, and peer-rights drift instead of one durable return-delta contract
- five new **interface specs** for return-delta contract sheet, delta-aging review, parity-debt proof, return-delta timeline, and return-delta lineage receipt
- a tighter non-clone line based on current official Resilio evidence that a state can be visibly active and still differ materially from the old intended home, mode, witness, or rights posture
- five hard product decisions:
  - **a changed-but-working return becomes explicit parity debt unless it is deliberately promoted**
  - **temporary accepted delta and successor baseline are separate truths**
  - **every tolerated mismatch requires owner, expiry, and rereview cadence**
  - **time and usage alone may not silently promote a changed state to the new baseline**
  - **`still syncing` is weaker than `same protected state` and must stay weaker until proof or promotion says otherwise**

New docs in this tranche:

- `1456-resilio-return-delta-debt-baseline-rebind-and-reopen-fragmentation-evaluation.md`
- `1457-return-delta-contract-sheet-page-accepted-successor-delta-expiry-and-owner-interface-spec.md`
- `1458-delta-aging-review-page-restore-exact-promote-successor-or-reopen-interface-spec.md`
- `1459-parity-debt-proof-page-temporary-accepted-delta-baseline-rebind-and-claim-ceiling-interface-spec.md`
- `1460-return-delta-timeline-page-accepted-drift-expiry-promotion-and-reopen-events-interface-spec.md`
- `1461-return-delta-lineage-receipt-page-parity-debt-owner-expiry-and-blocked-stronger-sentences-interface-spec.md`

### Why this pass matters

The previous tranche answered `did we actually bring protection back, and what structural delta still remains?`
This tranche answers the next harder question:

> `if we keep operating in that changed state, when does it become a debt with an owner and expiry, when can it honestly become the new baseline, and when must it reopen instead of being normalized?`

Current official Resilio material is useful here because it already proves that changed-but-working returns are real:

- reconnect may propose a different default path, create a new directory, and append `(1)` when a same-name folder already exists
- Selective Sync or Synced default-mode behavior can auto-place arriving folders into the default storage location until the operator switches the device into Disconnected mode for manual placement
- disabling Android Simple mode changes whether custom path choice is available at connect time
- disconnected folders have no local path while Selective Sync and Full Sync preserve different local witness shapes
- existing-directory connect merges trees and resolves same-name different-hash files by latest timestamp
- reconnecting to or adding into a non-empty folder can overwrite or delete already-present files
- renaming a syncing folder is local-only while moving across partitions can require disconnect/reconnect
- peer disconnect can leave bytes in place while future updates remain suspended

That candor is worth borrowing.
The contract shape is not.
AnonSync should not clone a world where the operator still has to infer, from scattered KB pages, whether a changed return is temporary debt, an intentional successor, or a problem that should reopen.''')

prepend(docs / '00-status.md', '''## Revision addendum — status shift toward return-delta debt, baseline rebind, and honest successor adoption after rev0385

The next seam after return-to-protection is now explicit:

- the archive can already tell whether activity came back and whether the same protected state returned
- it still needed to own the harder middle where the current state is active and acceptable, but not yet exact parity with the old baseline

This pass turns that middle into a first-class product object: **accepted return-delta debt**.

What is newly true in the archive:

- changed-but-working returns now remain visible as debt until exact restore, successor promotion, or reopen
- tolerated deltas now require explicit owner, expiry, rereview cadence, and blocked stronger sentence
- a successor baseline now requires deliberate promotion rather than silent normalization through time or frequent use
- exact restore, successor promotion, claim narrowing, and reopen now form one decision ladder instead of out-of-band operator folklore
- handoff now preserves the next forbidden overclaim: `still syncing` may not silently round up to `same protected state`

New docs in this tranche:

- `1456-resilio-return-delta-debt-baseline-rebind-and-reopen-fragmentation-evaluation.md`
- `1457-return-delta-contract-sheet-page-accepted-successor-delta-expiry-and-owner-interface-spec.md`
- `1458-delta-aging-review-page-restore-exact-promote-successor-or-reopen-interface-spec.md`
- `1459-parity-debt-proof-page-temporary-accepted-delta-baseline-rebind-and-claim-ceiling-interface-spec.md`
- `1460-return-delta-timeline-page-accepted-drift-expiry-promotion-and-reopen-events-interface-spec.md`
- `1461-return-delta-lineage-receipt-page-parity-debt-owner-expiry-and-blocked-stronger-sentences-interface-spec.md`

### Why this pass matters

The archive now has a cleaner answer to a very common operator failure mode:

> a system came back in a changed state, kept working, and everyone gradually started treating that changed state as the intended baseline without ever deciding whether it was debt, successor, or latent failure.

That ambiguity is now explicitly disallowed.''')

prepend(docs / '10-resilio-sync-evaluation.md', '''## Revision addendum — return-delta debt and baseline rebind after rev0385

The next non-clone seam is now explicit: **current Resilio admits many changed-but-working return states, but still lacks one operator-facing return-delta debt contract**.
Current official material remains useful and candid:

- `Disconnecting and Removing Folders` still says reconnect may propose a different default path, create a new directory, and append `(1)` when a same-name folder already exists
- the same article still says disconnect removes placeholders if Selective Sync was enabled
- `Folders are duplicating with an index (i) in their name` still says default-mode behavior can auto-place arriving folders into the default storage folder until the operator switches to Disconnected mode for manual placement
- `How to manually set the location of the folders synced across linked devices?` still says Android Simple mode must be disabled to choose a custom path at connect time
- `Folder Types and Management` still says disconnected folders have no local path while Selective Sync and Full Sync preserve different local witness shapes
- `Synchronization Modes` still distinguishes disconnected, selective, and full-sync data-movement postures
- `Can I connect two pre-populated pre-existing folders?` still says existing-directory connect merges trees and resolves same-name different-hash files by latest timestamp
- `Folder not empty` still warns that adding or reconnecting into a non-empty directory can overwrite or delete already-present files
- `Can I move or rename a syncing folder?` still says renaming is local-only and moving across partitions can require disconnect/reconnect
- `User Management` still says peer disconnect leaves already-synchronized bytes in place while future updates are suspended

That is enough to justify a sharper product stance:

- **borrow Resilio's candor that a working return may still differ in path, mode, witness, merge history, or rights**
- **borrow the honesty that some changed returns are ordinary, not exotic**
- **do not clone a world where the operator still has to infer whether a changed state is temporary debt, intended successor, or latent reopen from scattered KB pages**

The replacement line for AnonSync is now stronger:

- model **return-delta debt** directly
- require owner, expiry, rereview cadence, and blocked stronger sentence for every tolerated mismatch
- keep exact restore, successor promotion, claim narrowing, and reopen in one decision ladder
- forbid silent promotion of changed activity into baseline truth
- preserve the difference between `still syncing`, `acceptable temporary delta`, and `deliberately promoted successor baseline`''')

prepend(docs / '11-resilio-borrow-line-and-non-clone-scorecard.md', '''## Revision addendum — non-clone line hardens around accepted return-delta debt after rev0385

Another current Resilio pass makes the next non-clone obligation clearer:

- **AnonSync should model changed-but-working returns as first-class parity debt instead of letting active sync quietly become the new baseline.**

Resilio still deserves credit for exposing the ingredients:

- reconnect can land on a different path and create a `(1)` directory
- default mode and default storage location can create changed path outcomes routinely
- Android Simple mode and Disconnected mode change who controls path choice
- disconnected, selective, and full-sync states preserve different local witness shapes
- existing-directory connect is explicitly a merge workflow, not exact restoration
- reconnecting to a non-empty folder can overwrite or delete already-present files
- rename and move semantics can remain local or require reconnect
- peer disconnect preserves bytes while future updates remain suspended

But that is exactly why the product should not clone the contract shape.
The current operator still has to reconstruct from multiple pages whether a changed active state is:

- temporary tolerated drift
- acceptable but weaker successor state
- a new intended baseline
- or a problem that should reopen instead of being normalized

So the borrow line sharpens again:

### Keep

- candid distinction between exact return and changed active state
- explicit admission that path, mode, witness, merge, and rights deltas can survive a successful return
- explicit warnings where pre-existing contents or default-placement behavior can change outcomes

### Do not clone

- any `syncing again` story that silently rounds up to baseline parity
- any workflow where changed path/mode/topology becomes the new normal without explicit promotion
- any product that leaves expiry, owner, and reopen triggers to memory instead of product truth

### Replace with

- return-delta contract sheets
- delta-aging reviews
- parity-debt proofs
- return-delta timelines
- return-delta lineage receipts''')

prepend(docs / '12-resilio-interface-clone-veto-tests-and-page-obligations.md', '''## Revision addendum — interface clone veto tests extend to accepted return-delta debt after rev0385

The page-family veto line is now stricter.
After this pass, any interface that treats a changed-but-working return as normal state without explicit debt, promotion, or reopen semantics should be treated as a clone smell.

New veto tests:

1. **If the page says the subject is active again but does not say whether exact parity returned, fail it.**
2. **If path/mode/merge/rights deltas can persist but the page hides owner or expiry, fail it.**
3. **If time or repeated use can silently turn a tolerated mismatch into the new baseline, fail it.**
4. **If successor promotion and exact restoration share the same success language, fail it.**
5. **If the page cannot say when the changed state must reopen rather than be normalized, fail it.**

New page obligations:

- every changed return must have a **return-delta contract sheet** when the mismatch is tolerated
- every tolerated mismatch must publish owner, expiry, rereview cadence, and blocked stronger sentence
- every aging review must compare exact restore, temporary keep, successor promotion, claim narrowing, and reopen
- every proof page must state the baseline relation explicitly
- every receipt must preserve the next forbidden silent normalization
''')

prepend(docs / '20-product-direction.md', '''## Revision addendum — product direction shift toward return-delta debt, baseline rebind, and honest successor adoption after rev0385

The archive now has enough structure that the next product obligation becomes explicit:

- a system can return from bypass in a changed-but-working state
- the next obligation is to decide whether that changed state is temporary debt, a deliberate successor baseline, or a reason to reopen

This matters because the product is now deliberately choosing not to let `working again` impersonate `same intended baseline`.

The direction hardens around five decisions:

1. **exact restoration and stable successor adoption are separate product truths**
2. **every tolerated post-return mismatch is parity debt until explicitly retired or promoted**
3. **owner, expiry, and rereview are mandatory for tolerated drift**
4. **baseline rebind is compare-first and proof-first, never silent**
5. **claim ceilings must stay visible while parity debt remains active**

This gives the archive a cleaner long-range direction:

- controls can be suspended truthfully
- controls can be returned through typed re-arm paths
- changed returns become visible debt instead of hidden normalcy
- debt can age into exact restore, successor promotion, narrower stable claim, or reopen
- baseline truth changes only through explicit proof-backed rebind''')

prepend(docs / 'sources.md', '''## rev0386 source set — return-delta debt, baseline rebind, and honest successor adoption

The most load-bearing source set for this pass was:

- Resilio's current `Disconnecting and Removing Folders` article, which still says reconnect may propose a different default path, create a new directory, append `(1)` when a same-name folder already exists, and remove placeholders on disconnect when Selective Sync was enabled.
- Resilio's current `Folders are duplicating with an index (i) in their name` article, which still says default-mode behavior can auto-place arriving folders into the default storage folder and that switching to Disconnected mode is how the operator regains explicit placement control.
- Resilio's current `How to manually set the location of the folders synced across linked devices?` article, which still says Android Simple mode must be disabled to choose a custom path at connect time.
- Resilio's current `Folder Types and Management` article, which still says disconnected folders have no local path while Selective Sync and Full Sync preserve different local witness shapes.
- Resilio's current `Synchronization Modes` article, which still distinguishes disconnected, selective, and full-sync postures.
- Resilio's current `Can I connect two pre-populated pre-existing folders?` article, which still says existing-directory connect merges trees, skips same-hash files, and resolves same-name different-hash files by latest timestamp.
- Resilio's current `Folder not empty` article, which still warns that adding or reconnecting into a non-empty directory can overwrite or delete already-present files.
- Resilio's current `Can I move or rename a syncing folder?` article, which still says renaming is local-only and moving across partitions can require disconnect/reconnect.
- Resilio's current `User Management` article, which still says peer disconnect leaves already-synchronized bytes in place while future updates remain suspended.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that a changed active state can be operationally real
- but current Resilio still answers `is this temporary debt, the new baseline, or a reopen-worthy mismatch?` too diffusely
- AnonSync should therefore prefer return-delta contracts, delta-aging reviews, parity-debt proofs, return-delta timelines, and return-delta receipts over scattered KB-driven normalization lore

Primary sources:

- Disconnecting and Removing Folders
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- Folders are duplicating with an index (i) in their name
  https://help.resilio.com/hc/en-us/articles/204753869-Folders-are-duplicating-with-an-index-i-in-their-name

- How to manually set the location of the folders synced across linked devices?
  https://help.resilio.com/hc/en-us/articles/206216615-How-to-manually-set-the-location-of-the-folders-synced-across-linked-devices

- Folder Types and Management
  https://help.resilio.com/hc/en-us/articles/204762459-Folder-Types-and-Management

- Synchronization Modes
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- Can I connect two pre-populated pre-existing folders?
  https://help.resilio.com/hc/en-us/articles/205506569-Can-I-connect-two-pre-populated-pre-existing-folders

- Folder not empty
  https://help.resilio.com/hc/en-us/articles/204753689-Folder-not-empty

- Can I move or rename a syncing folder?
  https://help.resilio.com/hc/en-us/articles/205450655-Can-I-move-or-rename-a-syncing-folder

- User Management
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management''')

print('apply_rev0386.py prepared and content written')
