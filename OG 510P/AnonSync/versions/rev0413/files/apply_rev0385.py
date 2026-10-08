from pathlib import Path

root = Path('/mnt/data/work0385')
docs = root / 'docs'

new_files = {
'1450-resilio-control-rearm-return-to-protection-and-post-bypass-reconciliation-fragmentation-evaluation.md': r'''# Resilio control re-arm, return-to-protection, and post-bypass reconciliation fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- promote a guardrail from a case
- attest whether the control is still trusted
- suspend or bypass that control truthfully
- preserve what still survives during the bypass window

What it still lacked was one ordinary operator answer to the next harder question:

> once the bypass ends, what exactly does it mean to come back, what structural deltas must be reconciled first, and when is the stronger protection sentence safe again?

That is the seam this pass locks.
A real operator cannot afford a vague `resume` button.
The product needs a first-class answer for **control re-arm, return-to-protection, and post-bypass reconciliation**.

Current official Resilio material is useful here because it already proves that several kinds of `coming back` are materially different:

- `How to pause syncing`
- `Sync Preferences`
- `Disconnecting and Removing Folders`
- `Synchronization Modes`
- `How to manually set the location of the folders synced across linked devices?`
- `Can I connect two pre-populated pre-existing folders?`
- `Selective Sync`
- `Settings on mobile platforms`
- `User Management`

## Current official Resilio evidence that matters here

Current official docs still show all of the following:

- `How to pause syncing` still says resuming a paused folder is just repeating the same steps and using `Resume syncing`. That is a same-surface return, but it only makes sense because the underlying topology was not fully detached.
- `Sync Preferences` still says Global Pause/Resume only affects shares that are not paused individually. So even the simplest return verb already depends on which pause surface owns the current state.
- `Disconnecting and Removing Folders` still says reconnect may propose a default path different from the original path, may create a new directory, and may append `(1)` if a same-name folder already exists. So some returns are not mere resumes at all; they are path-selection and directory-creation events.
- The same article still says disconnect keeps the folder in the file system, removes placeholders if Selective Sync was enabled, and requires `Connect` later to re-establish syncing. That means the operator must reconcile more than one dimension on return: bytes, placeholders, path, and relationship.
- `Synchronization Modes` still says disconnected folders have no path associated with them locally until connect, while Selective Sync returns files as placeholders and `Remove from this device` preserves remote copies but not full local bytes. So a return from `disconnected`, `selective placeholder`, and `full sync` are not the same recovery path.
- `How to manually set the location...` still says devices in Selective Sync or Synced modes place new folders in the default location, while Disconnected mode lets the operator choose the path at connect time. On Android, Simple mode must be disabled to pick a custom path. That means return-to-protection may depend on lane-specific prerequisites and path authority, not just resuming motion.
- `Can I connect two pre-populated pre-existing folders?` still says connecting to an existing directory merges same-hash files without re-sync, resolves differing hashes by latest timestamp, and merges other files into the tree. So one form of `return` is really a compare-and-merge event with its own survivor logic, not a pure restoration of the previous protected state.
- `Selective Sync` still says removing a Selective Sync share removes all placeholders from the file system on that device. So after some detach classes, later re-entry cannot honestly be described as a simple resume because local witness state was actually removed.
- `Settings on mobile platforms` still says Android Simple mode controls whether the operator can choose share location and still says default folder location with Simple mode can create a `(1)` suffixed path when a same-name folder already exists. Again, return can silently fork path state.
- `User Management` still says peer disconnect revokes future updates but leaves already-synchronized files in place. So permission restoration and content continuity are separate return questions.

So current Resilio still clearly admits serious re-entry truths:

- `resume` is not one thing
- same-surface resume is weaker and cheaper than reconnect
- reconnect may land on a different path than the old protected state
- connect-to-existing-directory is a compare-and-merge event, not just a re-enable
- some detach classes delete placeholders or local witness traces before return
- peer relationship restoration is different from local transport resume
- mobile return may be gated by mode or default-path behavior

But those truths still do not become one operator-facing **return-to-protection / reconciliation / trust-requalification** object.

## What Resilio still gets right

### 1) It is candid that not all returns are equal

Pause/resume, disconnect/connect, connect-to-existing-directory, and permission reconnection are not hidden under one false story.
That distinction is worth borrowing.

### 2) It preserves structural side effects of return

Different path proposals, `(1)` path creation, placeholder removal, and merge rules are all admitted.
That honesty is useful.

### 3) It exposes lane-specific prerequisites

Android Simple mode and disconnected-mode path choice both make clear that a return may require prerequisites before the operator can recreate the intended state.
That is worth preserving.

## Where current Resilio still fragments the operator answer

### A) There is no canonical answer to `did we actually get back to the same protected state?`

A careful operator can read several KB pages and infer it.
But the product still does not answer in one place:

- whether the return reused the same path
- whether placeholder or full-byte posture changed
- whether the return merged into an existing directory
- whether peer permissions and future-update rights match the previous state
- whether the old trust sentence is back or only weaker motion is back

### B) Return and reconciliation are too easy to confuse

A folder can be active again while still being different:

- new default path
- `(1)` directory fork
- placeholders recreated instead of full bytes
- merged pre-populated directory with winner-by-timestamp rules
- re-enabled transport but not requalified protection

Current docs explain each edge in isolation, but still do not compose them into one re-entry contract.

### C) The proof of restored protection is not first-class

Current docs explain how to resume, reconnect, or connect to an existing directory.
What they do not give is one explicit answer to:

- what structural deltas were reconciled
- what remained intentionally different
- whether old trust can return immediately or only after new attestation
- what stronger sentence is still blocked after activity restarts

## Hard product decision unlocked by this pass

AnonSync should not let `resumed`, `reconnected`, `reattached`, `merged`, and `requalified` collapse into one success badge.
It should promote every meaningful return into a first-class object that can separately express:

- return class
- intended restored state
- structural deltas since bypass start
- reconciliation work still pending
- trust requalification requirements
- strongest sentence safe right now

That is the right next seam because it answers the operator question that always follows a bypass:

> motion is back, but are we actually back to the same protected state we intended, and what exactly still needs to be reconciled before saying yes?

## Replacement line for AnonSync

Borrow from Resilio:

- candor that return paths differ materially
- honesty that reconnect can create new paths or merge into existing trees
- explicit lane prerequisites and placeholder consequences

Do not clone from Resilio:

- any contract where `Resume` hides path, mode, or permission deltas
- any workflow where reconnect and restore-to-same-protection share one vague success story
- any product shape where the operator must reconstruct post-bypass equivalence from several separate articles

AnonSync should instead ship explicit pages for:

- return-to-protection contract
- re-arm readiness review
- return proof and requalification
- post-bypass reconciliation timeline
- return-to-protection lineage receipt
''',
'1451-return-to-protection-contract-sheet-page-intended-restoration-structural-delta-and-return-class-interface-spec.md': r'''# Return-to-protection contract sheet page: intended restoration, structural delta, and return class interface spec

## Purpose

After the archive learned how to suspend a control truthfully, it still needed one ordinary page for the next operator question:

> now that we want protection back, what exact state are we trying to restore, what changed while the bypass was active, and what kind of return are we actually performing?

## Core decision

AnonSync must expose one first-class **Return-to-protection contract sheet** whenever an operator ends, narrows, or reverses a bypass and wants a control, path, permission, or policy effect back.

## Fixed page order

1. **Return header**
2. **Target-restoration card**
3. **Structural-delta card**
4. **Return-class card**
5. **Requalification card**
6. **Decision sentence**

### 1) Return header

Show:

- return id
- affected suspension id
- affected control id
- source case / rollout / maintenance window id
- current return status
- owner
- requested return time
- current strongest safe sentence

Supported `current_return_status` values:

- `requested-not-yet-started`
- `blocked-by-prerequisite`
- `ready-for-reconciliation-review`
- `return-in-progress`
- `motion-restored-awaiting-requalification`
- `partially-restored`
- `fully-restored`
- `closed-with-intentional-delta`

Hard rule:

A return object may not inherit `fully restored` language just because the underlying transport is moving again.

### 2) Target-restoration card

This card states what protected state is being sought.
Required rows:

- target protected sentence
- target path / topology / permission posture
- target coverage scope
- target byte/materialization posture
- target policy/profile posture
- whether exact parity or acceptable-delta return is intended

Supported `target_restoration_intent` values:

- `exact-pre-bypass-return`
- `same-protection-new-path-accepted`
- `same-protection-new-mode-accepted`
- `permission-only-restoration`
- `transport-only-restoration`
- `intentional-weaker-successor-return`

Hard rule:

The target must be stated in operator language, not implied from the last button used.

### 3) Structural-delta card

This card records what is different between pre-bypass state and the proposed return.
Required rows:

- path delta
- topology delta
- permission delta
- placeholder / full-byte delta
- policy/profile delta
- observer/witness delta

Supported `structural_delta_flag` values:

- `same-path`
- `new-default-path-proposed`
- `new-directory-created`
- `existing-directory-merge-return`
- `placeholder-state-changed`
- `peer-rights-not-yet-restored`
- `scope-narrower-than-before`
- `world-or-lane-changed`

Hard rule:

A return is incomplete unless every material delta is either reconciled, accepted, or blocked.

### 4) Return-class card

Required rows:

- return class
- initiating surface
- prerequisite class
- reconciliation depth
- whether same-path continuity exists
- whether manual attestation is required after motion returns

Supported `return_class` values:

- `same-surface-resume`
- `scheduled-window-exit`
- `environment-gate-clear`
- `reconnect-same-path`
- `reconnect-new-path`
- `connect-existing-directory-merge`
- `permission-restoration`
- `recreate-and-requalify`
- `partial-scope-return`

Hard rule:

`same-surface-resume` may not be used if the return changes path, topology, permission, or byte posture.

### 5) Requalification card

Required rows:

- first point at which motion may return
- first point at which structure matches target
- first point at which trust may return
- proof needed to close remaining delta
- stronger sentence still blocked
- linked case / control / rollout reopened if return fails

Supported `requalification_class` values:

- `none-motion-equals-claim`
- `path-parity-check-required`
- `merge-result-check-required`
- `peer-rights-check-required`
- `attestation-required`
- `new-baseline-required`

Hard rule:

`resumed` and `requalified` may never be treated as the same answer unless the target restoration intent explicitly allows that weaker claim.

### 6) Decision sentence

The page ends with one sentence in this shape:

> `Return <id> seeks <target restoration intent> for <scope>; compared with the pre-bypass state, <structural delta summary> is still relevant, so the current safe sentence is <current sentence> until <requalification requirement>.`
''',
'1452-rearm-readiness-review-page-path-mode-peer-and-placeholder-reconciliation-interface-spec.md': r'''# Re-arm readiness review page: path, mode, peer, and placeholder reconciliation interface spec

## Purpose

The return contract carries the desired destination.
What the archive still needs before it executes the return is one comparison page answering:

> are we actually ready to re-arm, what structural mismatches remain, and which return route recreates the intended protection with the least semantic distortion?

## Core decision

AnonSync must expose one first-class **Re-arm readiness review** whenever more than one return route could plausibly restore motion or protection.

## Fixed page order

1. **Review header**
2. **Candidate-return lattice**
3. **Structural-mismatch card**
4. **Return-risk comparison**
5. **Requalification plan card**
6. **Approval sentence**

### 1) Review header

Show:

- target control or subject id
- source suspension id
- compared return candidates
- selected return candidate
- rejected cheaper candidates
- rejected more destructive candidates
- current recommendation

### 2) Candidate-return lattice

Each row compares one candidate route.
Required columns:

- candidate route
- motion restored how
- path outcome
- byte/materialization outcome
- permission/topology outcome
- structural reconciliation cost
- proof ceiling after activation

Supported `candidate_route` values:

- `resume-in-place`
- `resume-global-surface`
- `reconnect-original-path`
- `accept-new-default-path`
- `connect-existing-directory`
- `restore-permission-only`
- `recreate-from-scratch`
- `keep-partial-return`

Hard rule:

Candidates may not be sorted by convenience alone; they must be sorted by least-distorting route to the target protected state.

### 3) Structural-mismatch card

This card highlights the easiest false-friend returns.
Required rows:

- same-name but different path risk
- existing-directory merge risk
- placeholder versus full-byte mismatch
- permission restored but future updates still blocked risk
- lane/world mismatch risk
- witness removed versus witness preserved difference

Supported `structural_mismatch_flag` values:

- `looks-resumed-but-new-path`
- `looks-same-but-index-suffixed-directory`
- `looks-restored-but-placeholder-only`
- `looks-reconnected-but-merge-still-pending`
- `looks-permitted-but-peer-rights-not-symmetric`
- `looks-active-but-trust-still-pending`

### 4) Return-risk comparison

Required rows:

- risk of path fork
- risk of silent merge overwrite or timestamp winner
- risk of losing old witness or placeholders
- risk of returning in weaker mode than intended
- risk of overclaim after motion returns
- rollback or abort options

Hard rule:

A candidate that restarts activity quickly but worsens structural divergence must not be hidden.

### 5) Requalification plan card

Required rows:

- first required proof after activation
- reviewer / owner
- whether attestation is mandatory
- whether new baseline must be accepted
- blocked sentence until review closes
- when related case / control / rollout reopens automatically

Supported `requalification_plan_style` values:

- `direct-close-after-resume`
- `resume-then-verify-path`
- `resume-then-verify-merge`
- `resume-then-reattest-control`
- `resume-then-rebaseline`
- `do-not-return-blocked`

### 6) Approval sentence

The page ends with one sentence in this shape:

> `We choose <candidate route> instead of <rejected alternative> because it restores <target effect> with lower structural distortion; after motion returns, <remaining mismatch> still blocks <overclaim> until <requalification step>.`
''',
'1453-return-to-protection-proof-page-resume-reconnect-rebind-and-requalification-interface-spec.md': r'''# Return-to-protection proof page: resume, reconnect, rebind, and requalification interface spec

## Purpose

Once a return route is approved, the archive needs one explicit page for the next question:

> what exactly came back, what proof shows the system is moving again, what structural deltas were actually resolved, and what still has to be requalified before the stronger protection sentence returns?

## Core decision

AnonSync must expose one first-class **Return-to-protection proof** whenever a control bypass, detachment, permission revoke, or path/mode divergence is ended.

## Fixed page order

1. **Proof header**
2. **Motion-restoration card**
3. **Structural-reconciliation card**
4. **Residual-delta card**
5. **Requalification verdict card**
6. **Proof sentence**

### 1) Proof header

Show:

- return id
- proof time
- proof owner
- active scope
- return verdict
- chosen return class
- current protection state
- resulting trust state

Supported `return_verdict` values:

- `motion-restored-as-intended`
- `motion-restored-with-structural-delta`
- `reconnected-but-new-path-created`
- `merge-return-completed-awaiting-review`
- `permission-restored-awaiting-attestation`
- `inconclusive-return-state`
- `fully-requalified`

### 2) Motion-restoration card

Required rows:

- surface or mechanism used to restore motion
- direct evidence that motion or eligibility returned
- evidence that the chosen route matches the approved candidate
- missing evidence if any
- observers and timestamps

Supported `motion_restoration_evidence_class` values:

- `ui-resume-state`
- `scheduled-window-ended`
- `environment-gate-cleared`
- `reconnect-completed`
- `permission-restored`
- `directory-merge-begun`
- `new-baseline-accepted`

Hard rule:

A badge or button flip alone cannot prove path parity, permission parity, or return-to-same-protection unless the product says that is all it is claiming.

### 3) Structural-reconciliation card

Required rows:

- path parity result
- placeholder/full-byte posture result
- peer/topology result
- merge or overwrite result
- lane/world result
- observer/witness restoration result

Supported `structural_reconciliation_verdict` values:

- `same-path-confirmed`
- `new-path-accepted`
- `index-suffixed-path-created`
- `existing-directory-merge-under-review`
- `placeholder-posture-changed`
- `future-updates-restored`
- `relationship-restored-but-not-baselined`
- `world-lane-delta-remains`

### 4) Residual-delta card

Required rows:

- delta still present
- delta accepted intentionally or not
- risk if delta persists
- linked object impacted
- whether rollback or re-detach remains allowed
- earliest next review

Supported `residual_delta_class` values:

- `none`
- `accepted-new-path`
- `accepted-weaker-mode`
- `merge-review-pending`
- `permission-asymmetry-pending`
- `attestation-pending`
- `rebaseline-pending`

### 5) Requalification verdict card

Required rows:

- strongest sentence now safe
- stronger sentence still blocked
- next proof needed
- whether old baseline was restored or replaced
- case / control / rollout reopened if proof later fails

Hard rule:

`activity restored` may not imply `same protection restored` unless the structural-reconciliation card proves parity or the target restoration intent explicitly accepted the delta.

### 6) Proof sentence

The page must end with one sentence in this shape:

> `Return <id> is <return verdict> across <scope>; motion has returned by <evidence>, but <residual delta or none> means the strongest safe sentence is <current sentence> until <next proof>.`
''',
'1454-post-bypass-reconciliation-timeline-page-resume-path-fork-merge-and-trust-return-events-interface-spec.md': r'''# Post-bypass reconciliation timeline page: resume, path fork, merge, and trust-return events interface spec

## Purpose

After a return begins, the product still needs one durable page for the events that change what `back to normal` actually means over time:

> when did motion resume, when did path or mode fork, when did merge review complete, when did trust return, and when did we accept a new baseline instead of restoring the old one?

## Core decision

AnonSync must expose one first-class **Post-bypass reconciliation timeline** for every return that lasts long enough to matter, changes structure, or changes what sentence is safe.

## Fixed page order

1. **Timeline header**
2. **Return-history stream**
3. **Structural-shift card**
4. **Requalification ladder**
5. **Sentence-restoration card**
6. **Linked-object hooks**

### 1) Timeline header

Show:

- return id
- current restoration state
- current strongest safe sentence
- last restoration event
- next review or attestation
- current baseline state

Supported `current_restoration_state` values:

- `resume-possible-not-started`
- `motion-restored-structure-pending`
- `merge-or-path-review-pending`
- `partially-requalified`
- `fully-requalified`
- `new-baseline-accepted`
- `reopened-after-failed-return`

### 2) Return-history stream

Each row must include:

- event time
- event class
- impacted scope
- old state
- new state
- withdrawn or restored sentence
- linked proof or review id

Supported `event_class` values:

- `resume-requested`
- `resume-confirmed`
- `reconnect-started`
- `reconnect-completed`
- `new-path-created`
- `existing-directory-merge-started`
- `merge-review-completed`
- `permission-restored`
- `placeholder-posture-changed`
- `attestation-restored`
- `new-baseline-accepted`
- `same-cause-return-failed`

### 3) Structural-shift card

When the selected timeline row changes meaning materially, show:

- what structural fact changed
- old return truth
- new return truth
- whether path parity improved or worsened
- whether trust moved or stayed blocked
- whether rollback remains allowed

Supported `structural_shift_source` values:

- `simple-resume-confirmed`
- `reconnect-landed-new-path`
- `operator-corrected-to-original-path`
- `merge-chose-existing-directory`
- `placeholder-footprint-removed`
- `future-updates-restored`
- `baseline-replaced`
- `trust-restored-after-requalification`

### 4) Requalification ladder

The page must preserve this ladder:

1. `motion-only`
2. `motion-plus-structure-known`
3. `structure-reconciled`
4. `trust-restored`
5. `new-baseline-adopted-or-old-baseline-restored`
6. `reopened-on-return-failure`

Hard rule:

The timeline must preserve the gap between `motion resumed` and `protection restored` whenever that gap exists.

### 5) Sentence-restoration card

Required rows:

- earliest point motion resumed
- earliest point structure matched the target or accepted successor
- actual point trust sentence returned
- witness that allowed stronger sentence
- stronger sentence still blocked if any

Hard rule:

The timeline must show whether the old sentence returned or whether a new weaker or successor sentence replaced it.

### 6) Linked-object hooks

Each hook must show:

- linked object type (case / control / rollout / policy / baseline)
- why it is linked
- whether it reopened automatically
- first required next page
- sentence withdrawn or restored there
''',
'1455-return-to-protection-lineage-receipt-page-rearm-class-residual-delta-and-blocked-stronger-sentences-interface-spec.md': r'''# Return-to-protection lineage receipt page: re-arm class, residual delta, and blocked stronger sentences interface spec

## Purpose

The return contract, readiness review, proof page, and reconciliation timeline carry detail.
What the archive still needs at handoff time is one compact receipt answering:

> what kind of return happened, what structural delta still remains, and what exactly must be proven before the stronger pre-bypass sentence is safe to say again?

## Core decision

AnonSync must emit one **Return-to-protection lineage receipt** whenever a bypass ends, a reconnect lands, a merge return is accepted, a new baseline replaces the old one, or trust is restored after requalification.

## Required receipt fields

### Identity block

- `return_id`
- affected suspension id
- affected control or subject id
- owner
- chosen return class
- current return status

### Restoration-truth block

- target restoration intent
- motion restored yes/no
- current strongest safe sentence
- stronger sentence still blocked
- old baseline restored or successor baseline adopted
- next required review page

### Structural-delta block

- path result
- placeholder/full-byte result
- permission/topology result
- merge result if any
- accepted intentional deltas
- risk if delta persists

### Requalification block

- trust restored yes/no
- latest proof class
- next proof still required
- reopened linked object if any
- next forbidden shortcut

## Supported compact verdict language

The receipt must support compact phrases such as:

- `resumed in place; same path confirmed; trust restored`
- `reconnected; new path accepted; old sentence replaced by successor sentence`
- `connected to existing directory; merge under review; trust still pending`
- `permission restored; future updates resumed; attestation still required`
- `motion back, but placeholder posture changed; parity claim blocked`
- `activity restored, baseline replaced, stronger old equivalence claim retired`

## Hard rules

### 1) Motion and parity stay separate

A receipt is incomplete if it says only that syncing resumed.
It must say whether the return recreated the same protected state, an accepted successor state, or neither.

### 2) Residual delta is mandatory unless none truly remains

A receipt must always distinguish `no structural delta`, `accepted delta`, and `unresolved delta`.

### 3) Trust restoration must name its proof

If trust returned, the receipt must identify which proof or review allowed that stronger sentence.

### 4) Handoff must preserve the next shortcut to avoid

The receipt is not complete unless it records the next unsafe assumption, such as `motion resumed does not prove same-path parity`.

### 5) New baseline adoption may not masquerade as exact restoration

If the operator accepted a successor state instead of recreating the old one, the receipt must say so explicitly.
'''
}

for name, content in new_files.items():
    (docs / name).write_text(content.strip() + "\n", encoding='utf-8')

readme_addendum = r'''## Revision addendum — control re-arm, return-to-protection, and post-bypass reconciliation after rev0384

This pass locks the next seam after control suspension and break-glass: **how protection actually comes back after a bypass ends, and how we distinguish motion restored from the same protected state restored**.
The archive already knew how to attest a control, suspend it truthfully, and preserve what still survives while it is weakened.
What it still lacked was one explicit answer to:

> after we unpause, reconnect, reattach, or restore permissions, are we truly back to the same protected state, what structural deltas remain, and what proof is still required before the stronger sentence returns?

This revision adds that answer.
It contributes:

- one new **Resilio evaluation** focused on why current re-entry truth still fragments across resume, reconnect, disconnected-mode connect, existing-directory merge, placeholder behavior, path defaults, Android Simple mode, and permission restoration instead of one durable return-to-protection contract
- five new **interface specs** for return-to-protection contract sheet, re-arm readiness review, return proof, post-bypass reconciliation timeline, and return-to-protection lineage receipt
- a tighter non-clone line based on current official Resilio evidence that several current `come back` verbs are materially different but still do not become one operator-facing answer to `did we actually recreate the same protected state or only restart activity in a changed one?`
- five hard product decisions:
  - **`resumed`, `reconnected`, `reattached`, `merged`, and `requalified` remain separate states**
  - **every return must publish structural deltas, not just the fact that motion resumed**
  - **same-path restoration and accepted-successor return are separate truths**
  - **connect-to-existing-directory and new-path reconnect are reconciliation events, not simple resumes**
  - **the strongest pre-bypass sentence stays blocked until requalification closes the remaining delta**

New docs in this tranche:

- `1450-resilio-control-rearm-return-to-protection-and-post-bypass-reconciliation-fragmentation-evaluation.md`
- `1451-return-to-protection-contract-sheet-page-intended-restoration-structural-delta-and-return-class-interface-spec.md`
- `1452-rearm-readiness-review-page-path-mode-peer-and-placeholder-reconciliation-interface-spec.md`
- `1453-return-to-protection-proof-page-resume-reconnect-rebind-and-requalification-interface-spec.md`
- `1454-post-bypass-reconciliation-timeline-page-resume-path-fork-merge-and-trust-return-events-interface-spec.md`
- `1455-return-to-protection-lineage-receipt-page-rearm-class-residual-delta-and-blocked-stronger-sentences-interface-spec.md`

### Why this pass matters

The previous tranche answered `what still survives while the control is bypassed?`
This tranche answers the next harder question:

> `when activity comes back, are we really back to the same protected state, or did we return through a path/mode/topology change that still blocks the stronger claim?`

Current official Resilio material is useful here because it already proves that re-entry is not one thing:

- `How to pause syncing` still says resume is just repeating the same action, which is a cheap same-surface return
- `Sync Preferences` still says Global Pause/Resume applies only to shares not already paused individually, exposing re-entry ownership by surface
- `Disconnecting and Removing Folders` still says reconnect may propose a different default path, may create a new directory, and may append `(1)` if a same-name folder exists
- `Synchronization Modes` still says disconnected folders have no local path until connect, while Selective Sync returns placeholder-only posture instead of full local bytes
- `How to manually set the location of the folders synced across linked devices?` still says Disconnected mode enables path choice at connect time, while Android Simple mode must be disabled to choose location manually
- `Can I connect two pre-populated pre-existing folders?` still says connecting to an existing directory merges trees, skips same-hash files, and resolves same-name different-hash files by latest timestamp
- `Selective Sync` still warns that removing a Selective Sync share removes all placeholders from the local file system
- `User Management` still says peer disconnect suspends future updates while already-synchronized files remain

That candor is useful.
The contract shape is the problem.
AnonSync should not clone a world where several return-like states exist but the product still cannot answer in one place:

- whether the return reused the same path or silently forked it
- whether the return recreated full local witness state or only placeholder posture
- whether the return merged into an existing directory and therefore changed proof obligations
- whether permission or future-update rights actually match the old state
- whether motion resumed, protection resumed, or a weaker successor state was merely accepted

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because return-to-protection is a real contract with separate truths for motion restoration, path/topology/permission parity, merge-versus-resume behavior, accepted structural delta, and trust requalification, but the present contract still scatters the answer across resume guides, disconnect/reconnect notes, synchronization modes, path-choice articles, and merge workflows instead of owning it as one stable page family.**
'''

status_addendum = r'''## Revision addendum — control re-arm, return-to-protection, and post-bypass reconciliation after rev0384

This pass locks the next seam after control suspension: **control re-arm / return-to-protection / post-bypass reconciliation**.
The archive already knew how to suspend a control truthfully and preserve what survives during the bypass.
What it still lacked was one ordinary operator answer to:

> when activity comes back, did we actually recreate the same protected state, what structural delta remains, and what proof is still required before the stronger sentence returns?

This revision adds that answer.
It contributes:

- one new **Resilio evaluation** focused on current re-entry fragmentation across resume, reconnect, disconnected-mode connect, existing-directory merge, placeholder behavior, path defaults, Android Simple mode, and permission restoration
- five new **interface specs** for return contract, re-arm readiness review, return proof, post-bypass reconciliation timeline, and return lineage receipt
- five hard product decisions:
  - **`resumed`, `reconnected`, `reattached`, `merged`, and `requalified` remain separate states**
  - **every return must publish structural deltas, not just motion resumed**
  - **exact restoration and accepted-successor return are separate truths**
  - **connect-to-existing-directory and new-path reconnect are reconciliation events, not simple resumes**
  - **the strongest pre-bypass sentence stays blocked until requalification closes the remaining delta**

New docs in this tranche:

- `1450-resilio-control-rearm-return-to-protection-and-post-bypass-reconciliation-fragmentation-evaluation.md`
- `1451-return-to-protection-contract-sheet-page-intended-restoration-structural-delta-and-return-class-interface-spec.md`
- `1452-rearm-readiness-review-page-path-mode-peer-and-placeholder-reconciliation-interface-spec.md`
- `1453-return-to-protection-proof-page-resume-reconnect-rebind-and-requalification-interface-spec.md`
- `1454-post-bypass-reconciliation-timeline-page-resume-path-fork-merge-and-trust-return-events-interface-spec.md`
- `1455-return-to-protection-lineage-receipt-page-rearm-class-residual-delta-and-blocked-stronger-sentences-interface-spec.md`

### Why this pass matters

The previous tranche answered `what still survives while the control is bypassed?`
This tranche answers the next harder question:

> `when activity comes back, are we back to the same protected state or only moving again in a changed one?`
'''

eval_addendum = r'''## Revision addendum — control re-arm, return-to-protection, and post-bypass reconciliation after rev0384

The next non-clone seam is now explicit: **current Resilio has several real return paths, but still lacks one operator-facing return-to-protection contract**.
Current official material remains useful and candid:

- `How to pause syncing` still says resume is performed by repeating the pause action, which is a cheap same-surface return
- `Sync Preferences` still says Global Pause/Resume affects only shares that are not paused individually, exposing surface-owned return semantics
- `Disconnecting and Removing Folders` still distinguishes reconnect from remove, still says reconnect may propose a different path, and still says a new directory may be created with `(1)` appended when a same-name folder already exists
- the same article still says disconnect removes placeholders if Selective Sync was enabled, meaning return may lack old witness state
- `Synchronization Modes` still says disconnected folders have no local path until connect and still distinguishes disconnected, placeholder-only, and full-sync postures
- `How to manually set the location of the folders synced across linked devices?` still says Disconnected mode enables path choice on connect and Android Simple mode must be disabled to choose location manually
- `Can I connect two pre-populated pre-existing folders?` still says existing-directory connect merges trees, skips same-hash files, and resolves same-name different-hash files by latest timestamp
- `Selective Sync` still warns that removing a Selective Sync share removes all placeholders from the local file system
- `User Management` still says peer disconnect suspends future updates while already-synchronized files remain

That is enough to justify a sharper product stance:

- **borrow Resilio's candor that return paths are materially different**
- **borrow the honesty that reconnect can fork path state and existing-directory connect is a merge event**
- **do not clone a world where the operator still has to infer whether motion restored also means same protection restored**

The replacement line for AnonSync is now stronger:

- model **return-to-protection and requalification** directly
- keep motion restoration, structural parity, accepted delta, and trust restoration separate
- force every return to publish path/mode/permission/placeholder deltas
- treat merge returns and new-path reconnects as reconciliation events, not mere resumes
- preserve the stronger sentence that remains blocked until requalification closes the remaining delta
'''

scorecard_addendum = r'''## Revision addendum — non-clone line hardens around return-to-protection after rev0384

Another current Resilio pass makes the next non-clone obligation clearer:

- **AnonSync should model return-to-protection as a first-class contract instead of letting `resume`, `reconnect`, and `connect` impersonate one success story.**

Resilio still deserves credit for exposing the ingredients:

- same-surface resume exists
- global and per-share pause ownership differ
- reconnect may propose a different path and create a new directory
- disconnected folders have no local path until connect
- existing-directory connect is a merge workflow with hash/timestamp rules
- Selective Sync removal can delete placeholders locally
- Android Simple mode gates manual path choice
- peer disconnect preserves old bytes while future updates remain suspended

But that is exactly why the product should not clone the contract shape.
The current operator still has to reconstruct from multiple pages whether a return:

- recreated the same path
- recreated the same byte/materialization posture
- restored future-update rights
- merged into an existing tree with new proof obligations
- or merely restarted activity in a structurally changed state

So the borrow line sharpens again:

### Keep

- candid distinction between resume, reconnect, connect, and permission restoration
- explicit admission that path and placeholder state may change during return
- explicit lane-specific prerequisites for manual path choice

### Do not clone

- any `resume succeeded` story that hides path/topology/permission delta
- any contract where merge-return and same-path resume look equivalent
- any workflow where the operator must infer whether old trust is back from several KB pages

### Replace with

- return-to-protection contract sheets
- re-arm readiness reviews
- return proofs with structural reconciliation
- post-bypass reconciliation timelines
- return lineage receipts with blocked stronger sentences
'''

veto_addendum = r'''## Revision addendum — interface clone veto tests extend to return-to-protection after rev0384

The page-family veto line is now stricter.
After this pass, any interface that treats `resume`, `reconnect`, `connect existing directory`, and `trust restored` as one undifferentiated success path should be treated as a clone smell.

New veto tests:

1. **If the page says activity resumed but does not say whether the same protected state was restored, fail it.**
2. **If reconnect can create a new path or `(1)` directory but the page still presents it as a simple resume, fail it.**
3. **If existing-directory connect can merge or timestamp-resolve files but the page omits the new proof obligation, fail it.**
4. **If placeholder/full-byte posture changed and the page still implies exact restoration, fail it.**
5. **If trust restoration is not explicitly separated from motion restoration, fail it.**

New page obligations:

- every return page must publish the chosen return class
- every return page must publish structural deltas since bypass start
- every return page must say whether the old baseline returned or a successor state was accepted
- every return receipt must preserve the next blocked stronger sentence
- every timeline must preserve the gap between motion resumed and protection requalified
'''

product_addendum = r'''## Revision addendum — product direction shift toward return-to-protection and requalification after rev0384

The archive now has enough structure that the next product obligation becomes explicit:

- suspending a control truthfully is still not enough
- the next obligation is to prove what kind of return actually happened and whether it recreated the same protected state or only restarted motion in a changed one

This matters because the product is now deliberately choosing not to let `resumed` impersonate `restored`.

The direction hardens around five decisions:

1. **motion restoration, structural parity, and trust restoration are separate product truths**
2. **return class is first-class product data, not UI folklore**
3. **path forks, merge returns, and accepted successor states are legitimate outcomes but must be explicit**
4. **requalification is compare-first, overclaim-later**
5. **new baseline adoption must not masquerade as exact restoration**

This gives the archive a cleaner long-range direction:

- controls can be trusted
- trusted controls can be suspended through typed bypass objects
- bypasses can end through typed return objects
- return objects reconcile structural deltas before stronger claims come back
- requalification either restores the old sentence, replaces it with a successor sentence, or reopens the linked case/control/rollout
'''

sources_addendum = r'''## rev0385 source set — control re-arm, return-to-protection, and post-bypass reconciliation

The most load-bearing source set for this pass was:

- Resilio's current `How to pause syncing` article, which still says resuming a paused folder is done by repeating the same steps and using `Resume syncing`, proving that some returns are cheap same-surface resumes.
- Resilio's current `Sync Preferences` article, which still says Global Pause/Resume affects only shares that are not paused individually, exposing that return ownership depends on which pause surface owns the state.
- Resilio's current `Disconnecting and Removing Folders` article, which still distinguishes disconnect from remove and still says reconnect may propose a different path, create a new directory, and append `(1)` when a same-name folder already exists.
- Resilio's current `Synchronization Modes` article, which still says disconnected folders have no local path until connect and still distinguishes disconnected, placeholder-only, and full-sync postures.
- Resilio's current `How to manually set the location of the folders synced across linked devices?` article, which still says Disconnected mode enables path choice at connect time and Android Simple mode must be disabled to choose location manually.
- Resilio's current `Can I connect two pre-populated pre-existing folders?` article, which still says same-hash files are not re-synced, same-name different-hash files resolve by latest timestamp, and other files merge into the tree when connecting to an existing directory.
- Resilio's current `Selective Sync` article, which still warns that removing a Selective Sync share removes all placeholders from the local file system.
- Resilio's current `Settings on mobile platforms` article, which still says Android Simple mode controls whether share location can be selected manually and still says the default folder location can receive a `(1)` suffix when a same-name folder already exists.
- Resilio's current `User Management` article, which still says peer disconnect suspends future updates while already-synchronized files remain.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that return paths differ materially
- but current Resilio still answers `did we actually recreate the same protected state, or only restart motion in a changed one?` too diffusely
- AnonSync should therefore prefer return contracts, re-arm readiness reviews, return proofs, reconciliation timelines, and return receipts over scattered KB-driven re-entry lore

Primary sources:

- How to pause syncing
  https://help.resilio.com/hc/en-us/articles/206217325-How-to-pause-syncing

- Sync Preferences
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Disconnecting and Removing Folders
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- Synchronization Modes
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- How to manually set the location of the folders synced across linked devices?
  https://help.resilio.com/hc/en-us/articles/206216615-How-to-manually-set-the-location-of-the-folders-synced-across-linked-devices

- Can I connect two pre-populated pre-existing folders?
  https://help.resilio.com/hc/en-us/articles/205506569-Can-I-connect-two-pre-populated-pre-existing-folders

- Selective Sync
  https://help.resilio.com/hc/en-us/articles/205458095-Selective-Sync

- Settings on mobile platforms
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- User Management
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management
'''

prepend_map = {
    root / 'README.md': readme_addendum,
    docs / '00-status.md': status_addendum,
    docs / '10-resilio-sync-evaluation.md': eval_addendum,
    docs / '11-resilio-borrow-line-and-non-clone-scorecard.md': scorecard_addendum,
    docs / '12-resilio-interface-clone-veto-tests-and-page-obligations.md': veto_addendum,
    docs / '20-product-direction.md': product_addendum,
    docs / 'sources.md': sources_addendum,
}

for path, addendum in prepend_map.items():
    old = path.read_text(encoding='utf-8')
    path.write_text(addendum.strip() + "\n\n" + old, encoding='utf-8')

print('Applied rev0385 changes.')
