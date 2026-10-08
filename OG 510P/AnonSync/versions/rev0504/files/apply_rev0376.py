from pathlib import Path

root = Path('/mnt/data/work0376')
docs = root / 'docs'

new_files = {
    '1396-resilio-policy-supersession-retirement-and-successor-world-fragmentation-evaluation.md': r'''# Resilio policy supersession, retirement, and successor-world fragmentation evaluation

## Why this pass exists

The archive already had stronger doctrine for:

- policy profiles
- binding classes
- conformance review
- typed waivers and exception debt

What it still lacked was one explicit answer to the next ordinary operator question:

> we have a new policy now — is it just a revision, a partial successor, a world-specific successor, a split, a merge, or a retirement with no safe successor, and what exactly happens to the subjects and waivers living under the old one?

Current official Resilio material is again useful, but it still spreads that answer across several families:

- `Power user preferences`
- `What's the difference between Standard and Advanced folders?`
- `Disconnecting and Removing Folders`
- `Running Sync in configuration mode`
- `Running Sync as a service on Windows`
- `Sync Service Troubleshooting on Windows`
- `Sync Private Identity & Linking My Devices`
- `Can I change the name of my Sync identity?`
- `How to uninstall Sync?`

## Current official Resilio evidence that matters here

Current official docs still show all of the following:

- `Power user preferences` still says the article covers today's latest Sync version and that older versions may be missing some settings or still have deprecated ones.
- `What's the difference between Standard and Advanced folders?` still says some capability changes are not on-the-fly for Standard folders and instead require removing the share and re-adding it with a new key.
- `Disconnecting and Removing Folders` still distinguishes disconnecting a folder on one device from removing it from all devices linked with the personal identity, and still says reconnect may propose a different default path and create a new directory unless the operator manually rebinds to the old path.
- `Running Sync in configuration mode` still says config mode can help apply the same settings on a number of different machines, but only Standard folders can be set up there, and a non-default `storage_path` creates new settings there.
- The same config-mode doc still says putting shared folders in config disables WebUI and overrides folders previously added from WebUI.
- `Running Sync as a service on Windows` still says service installation offers either migration of existing settings/shares or a clean installation that requires re-sharing the needed folders.
- `Sync Service Troubleshooting on Windows` still says switching the service to `Local System` creates another service storage world with no old folders present and requires re-add / re-share.
- `Sync Private Identity & Linking My Devices` still says linking two already-running devices can replace one certificate and remove Advanced folders from the app on the device that takes over the new certificate.
- `Can I change the name of my Sync identity?` still says changing identity name requires unlinking and creating a new identity, after which Advanced folders are removed from the Sync instance while Standard folders remain.
- `How to uninstall Sync?` still says uninstall is not only app removal; the operator may also remove settings and manually clear storage folders, with service storage paths differing by service account.

So current Resilio still clearly admits real lifecycle events:

- revision drift between versions and deprecated settings
- capability replacement that requires remove/re-add rather than live mutate
- local detachment versus identity-wide retirement
- reconnect as rebind rather than guaranteed continuity
- config-authored successor worlds
- migrated service successors versus clean-install forks
- principal-induced storage-world replacement
- identity regeneration as a discontinuity event
- hard teardown through settings removal

But those events do not yet become one first-class operator-facing **policy lifecycle / supersession object**.

## What Resilio still gets right

### 1) It admits that continuity and replacement are different truths

Migration is not the same as clean install.
Reconnect is not the same as continuing in place.
Changing a service principal can widen access while still moving the operator into another storage world.
That distinction is real and useful.

### 2) It admits that some changes require successor creation rather than live mutation

Standard-folder permission changes, identity regeneration, and some service/config moves are not `just edit the old thing` stories.
They are successor or rebind stories.

### 3) It admits that retirements have different scopes

Disconnect one device, remove from linked devices, unlink identity, or uninstall with settings removal do not mean the same thing.
This is good raw material for a stronger lifecycle contract.

### 4) It admits that world-specific successors exist

Config `storage_path`, service storage location, Local System switch, and linked-identity takeover all create or imply another effective world.
That is exactly the place where policy lifecycle needs typed successor classes rather than folklore.

## Where current Resilio still fragments the operator answer

### A) Successor relation is present, but not modeled as one typed object

An operator can piece together that a new situation is:

- just a new version with some deprecated settings
- a capability replacement that needs remove/re-add
- a local disconnect/reconnect
- a migrated service successor
- a clean-install service fork
- a config-authored successor world
- an identity replacement event
- a total storage/settings teardown

But current docs do not give that divergence one canonical object with:

- predecessor
- successor
- relation class
- subject coverage
- waiver carry-forward rule
- retirement scope
- rollback posture

### B) Deprecation, supersession, and deletion are too easy to blur

Those are different truths:

- `deprecated` means still present but no longer preferred
- `superseded` means a successor policy should now govern some or all subjects
- `retired` means the predecessor is no longer an active governance target
- `deleted` means historical evidence may have been removed entirely

Current Resilio docs help expose replacement events, but the product contract still does not own these distinctions in one place.

### C) Waiver carry-forward has no first-class story

Once a subject already has a waiver under one profile, the operator still has to remember whether the waiver should:

- carry forward unchanged
- be re-proven on the successor
- collapse because the successor fixes the gap
- split by world or field coverage
- block retirement of the predecessor

That is too much policy-memory burden for one ordinary lifecycle review.

### D) Coverage after promotion is too easy to overclaim

Without a first-class lifecycle object, `we moved to the new policy` can accidentally hide that some subjects are:

- still pinned to the old one
n- grandfathered temporarily
- blocked by successor prerequisites
- outside successor scope
- orphaned because the predecessor retired without an adopted successor

### E) Retirement and rollback remain separate stories

Config forks, service migration choices, identity replacement, remove/re-add transitions, and uninstall-level reset all affect whether rollback is even meaningful.
But current Resilio material still does not yield one stable answer to:

- what exactly retired
- what successor replaced it
- who remained on the predecessor
- what evidence preserves the old contract
- what rollback route still exists

## Hard product decisions now locked for AnonSync

### 1) Every governed profile belongs to a policy family and every family change gets a typed successor relation

Supported relation classes must include at least:

- `in-place-revision`
- `compatible-successor`
- `split-successor`
- `merged-successor`
- `world-specific-successor`
- `rollback-successor`
- `sunset-no-successor`
- `unknown`

### 2) Retirement is a first-class state, not silent deletion

The product must preserve:

- predecessor id
- retirement time
- remaining bound subjects
- live waivers
- blocked migrations
- historical receipt chain

### 3) Waivers never auto-carry silently across supersession

The lifecycle object must explicitly say whether each waiver:

- carries forward
- must be re-proven
- collapses as resolved
- splits by field/world
- blocks successor adoption

### 4) Subject posture after supersession stays explicit

At minimum the product must distinguish:

- `on-current`
- `on-deprecated`
- `grandfathered`
- `blocked-from-successor`
- `orphaned`
- `retired-with-no-successor`

### 5) Promotion and retirement are compare-first, mutate-second

A product may not say `promote new policy` or `retire old policy` without first publishing:

- predecessor coverage
- successor coverage
- excluded subjects
- grandfathered subjects
- orphan risk
- rollback class
- waiver migration results

## Required page family

This seam now requires five AnonSync pages:

- **Policy-lifecycle contract sheet**
- **Supersession review**
- **Promotion and retirement proof**
- **Policy-family timeline**
- **Policy-lifecycle lineage receipt**

## New borrow line

Borrow Resilio's candor that migration, clean-install fork, remove/re-add replacement, disconnect/reconnect rebind, identity regeneration, and settings-world teardown are materially different lifecycle truths.

## New veto line

Do not clone any policy contract where the operator can still ask `is this new thing just the next revision, a partial successor, a split, or a replacement world, what happened to the waivers, and did we actually retire the predecessor?` and the honest answer is still `it depends which install, service, config, identity, or removal article you remember`.
''',
    '1397-policy-lifecycle-contract-sheet-page-predecessor-successor-relation-and-retirement-scope-interface-spec.md': r'''# Policy-lifecycle contract sheet page — predecessor, successor, relation, and retirement scope

## Purpose

This page answers the lifecycle question that profile binding and waivers still do not finish:

> we have a new policy candidate now — what exactly is replacing what, what relation class is this, what subjects are in scope, and what would retiring the predecessor actually mean?

## Core decision

Every serious policy promotion, replacement, split, merge, rollback, or sunset must render one first-class **Policy-lifecycle contract sheet** before the product allows `make current`, `replace default`, `deprecate old`, or `retire` language.
The page owns:

- predecessor identity
- successor identity
- relation class
- scope of replacement
- waiver carry-forward rule
- retirement consequence
- strongest safe lifecycle sentence

## Fixed page order

1. family strip
2. predecessor card
3. successor card
4. relation-class card
5. scope-and-coverage card
6. waiver-carry-forward card
7. retirement consequence card
8. lifecycle receipt

### 1) Family strip

Show:

- canonical policy family id
- focused predecessor id and revision
- focused successor id and revision
- lifecycle action: `publish`, `promote`, `deprecate`, `split`, `merge`, `rollback`, `sunset`, `unknown`
- status: `draft`, `proposed`, `active`, `blocked`, `retired`, `rolled-back`, `unknown`
- top question being answered: `what exactly is replacing what?`

### 2) Predecessor card

Show the old contract clearly:

- predecessor profile id
- predecessor revision
- supported worlds
- live bound subject count
- active waiver count
- retirement eligibility
- strongest safe sentence about the predecessor now

## Hard rule

The page may not let `old defaults` stand in for a canonical predecessor object.

### 3) Successor card

Show the proposed new contract:

- successor profile id
- successor revision
- supported worlds
- field coverage delta versus predecessor
- prerequisite delta
- expected subject reach
- activation posture

## Hard rule

The page may not call a successor `current` until its relation class and coverage delta are explicitly computed.

### 4) Relation-class card

Render exactly one top-line relation:

- `in-place-revision`
- `compatible-successor`
- `split-successor`
- `merged-successor`
- `world-specific-successor`
- `rollback-successor`
- `sunset-no-successor`
- `unknown`

For the chosen class show:

- what is preserved
- what is not preserved
- whether subject movement is automatic, optional, blocked, or impossible
- stronger sentence blocked

## Hard rule

`deprecated` may never stand in for a relation class.
`Deprecated` is a status, not the shape of replacement.

### 5) Scope-and-coverage card

List exactly what the lifecycle action covers:

- worlds included
- worlds excluded
- field families included
- field families dropped
- subject classes expected to move
- subject classes expected to remain
- orphan risk

## Hard rule

Anything not listed in scope stays outside the lifecycle action.
The page must not let a family-level promotion silently overclaim subject or world coverage.

### 6) Waiver-carry-forward card

For every active waiver class in scope, show one verdict:

- `carry-forward`
- `re-prove-on-successor`
- `resolved-by-successor`
- `split-by-field-or-world`
- `blocks-retirement`
- `unknown`

Also show:

- affected waiver ids
- owner count
- rereview debt after promotion
- strongest safe sentence about waiver migration

## Hard rule

Waivers never carry forward by implication.
The page must issue a verdict for every active waiver family in scope.

### 7) Retirement consequence card

Show what retiring the predecessor would do:

- subjects that would still remain bound
- grandfathered subjects
- blocked subjects
- subjects that would become orphaned
- receipt and audit preservation class
- rollback availability
- last safe retirement moment

## Hard rule

The product may not offer `retire predecessor` if any still-bound subject lacks an explicit destination posture.

### 8) Lifecycle receipt

Emit one compact receipt with:

- family id
- predecessor id
- successor id
- relation class
- subject coverage summary
- waiver migration summary
- retirement verdict
- rollback class
- strongest safe lifecycle sentence
- blocked stronger sentence

## Copy rules

- Never say `new default` without naming predecessor and successor.
- Never say `deprecated` when the truer sentence is `retired` or `still current but discouraged`.
- Never say `everything moved` unless every subject posture is resolved.
- Never say `same policy, just newer` when field coverage, world scope, or prerequisite burden changed.
- Never say `rollback available` unless the predecessor still has preserved receipts and an allowed rebind path.

## Example strongest-safe sentence patterns

- `This is a compatible-successor promotion: most predecessor-bound subjects can adopt the new revision, but active migration-gap waivers must be re-proven before predecessor retirement.`
- `This is a world-specific-successor only: desktop and service-subjects can move, while mobile-local lanes stay outside successor scope and remain on the deprecated predecessor.`
- `This is a sunset-no-successor action: the predecessor is being retired without a replacement, so currently bound subjects will become explicitly orphaned unless detached first.`
- `This is a rollback-successor: the newer profile remains historically recorded, but the predecessor revision becomes current again for the covered cohort.`
''',
    '1398-supersession-review-page-cohort-adoption-waiver-carryforward-and-orphan-risk-interface-spec.md': r'''# Supersession review page — cohort adoption, waiver carry-forward, and orphan risk

## Purpose

This page is the operator's comparison workspace for answering:

> if we promote this successor or retire this predecessor, who auto-adopts, who stays pinned, who needs a waiver decision, who becomes grandfathered, and who would be orphaned?

## Core decision

Every serious policy supersession must render one **Supersession review** before the product allows promotion or retirement.
The page exists to prevent `everyone moves` folklore.

## Fixed page order

1. cohort summary strip
2. adoption bucket matrix
3. waiver carry-forward review
4. field/world mismatch review
5. retirement risk review
6. operator decision ledger

### 1) Cohort summary strip

Show:

- predecessor id
- successor id
- relation class
- total candidate subjects
- clean auto-adopt count
- grandfathered count
- blocked count
- orphan-risk count
- unknown count

### 2) Adoption bucket matrix

Bucket every subject into exactly one current outcome:

- `auto-adopts`
- `needs-confirmation`
- `keeps-pin`
- `requires-branch`
- `blocked-by-waiver`
- `out-of-scope`
- `grandfathered`
- `orphan-risk`
- `unknown`

For each bucket show:

- subject count
- worlds represented
- field families involved
- strongest safe summary sentence

## Hard rule

`same values today` may never place a subject into `auto-adopts` by itself.
Future-governance posture is required.

### 3) Waiver carry-forward review

For every active waiver cluster, show:

- predecessor waiver id(s)
- carry-forward verdict
- successor fields affected
- rereview deadline
- whether the waiver blocks promotion, blocks retirement, or merely downgrades the subject

## Hard rule

The page may not collapse `resolved by successor` and `still tolerated on successor` into one green outcome.

### 4) Field/world mismatch review

Surface mismatches that change successor truth:

- subjects in unsupported worlds
- subjects losing coverage under successor
- subjects newly covered by successor
- fields removed from scope
- fields added to scope
- world-specific successors and exclusions

## Hard rule

Any mismatch that changes subject posture must remain visible even if the current displayed values still match.

### 5) Retirement risk review

Show the costs of retiring the predecessor now:

- subjects still relying on predecessor-only fields
- subjects whose waivers have no successor verdict
- subjects with no valid successor destination
- audit/receipt debt
- rollback readiness

Render one retirement posture:

- `safe-now`
- `safe-after-listed-actions`
- `promotion-only-no-retirement`
- `retirement-blocked`
- `unknown`

### 6) Operator decision ledger

For each bucket, allow only explicit decisions:

- `promote with auto-adopt`
- `promote and grandfather`
- `promote but keep pinned`
- `split branch`
- `carry waiver forward`
- `re-prove waiver`
- `defer retirement`
- `retire predecessor`
- `rollback`

The ledger must preserve subject counts for every choice.

## Copy rules

- Never say `migrate all` if any subject is grandfathered, blocked, or out of scope.
- Never say `waivers carried` unless the page names which ones and how.
- Never say `old policy can go away` while orphan-risk subjects remain.
- Never say `same profile family` when the relation class is split or merge.
- Never say `no impact` when the only truth is `no value delta for already-matching subjects`.

## Example strongest-safe sentence patterns

- `Most covered desktop subjects auto-adopt the successor, but the predecessor cannot retire yet because service-world waivers still lack carry-forward verdicts.`
- `The successor is narrower than the predecessor: some mobile-local subjects remain explicitly out of scope and will be grandfathered until a world-specific branch is published.`
- `Retirement is blocked because 14 subjects would become orphaned and 3 waivers still depend on predecessor-only fields.`
''',
    '1399-promotion-and-retirement-proof-page-successor-cutover-coverage-and-blocked-subjects-interface-spec.md': r'''# Promotion and retirement proof page — successor cutover, coverage, and blocked subjects

## Purpose

This page is the last pre-commit proof before the product publishes a new current policy or retires an old one.
It answers:

> are we actually ready to promote this successor and/or retire this predecessor, for what exact coverage, with what exceptions, and with what rollback class?

## Core decision

Every serious lifecycle mutation must emit one **Promotion and retirement proof** page before commit.
The proof is stricter than review.
It compiles the final action contract.

## Fixed page order

1. action proof strip
2. promotion proof card
3. retirement proof card
4. subject-outcome card
5. waiver-resolution card
6. activation-and-rollback card
7. commit receipt

### 1) Action proof strip

Show:

- predecessor id
- successor id
- requested action: `promote`, `retire`, `promote-and-retire`, `rollback`, `abort`
- proof status: `ready`, `ready-with-debt`, `blocked`, `unknown`
- total covered subjects
- total blocked subjects

### 2) Promotion proof card

Show:

- successor relation class
- covered worlds
- covered field families
- auto-adopt count
- explicit-confirmation count
- pinned/grandfathered count
- blocked count
- strongest safe promotion sentence

## Hard rule

The page may not show `ready` if any subject classified as `unknown` is still inside the requested coverage set.

### 3) Retirement proof card

Show:

- predecessor retirement posture
- remaining live bindings
- remaining predecessor-only waivers
- orphan-risk count
- historical receipt preservation status
- strongest safe retirement sentence

## Hard rule

The page may not offer `retire now` if predecessor-only waivers exist without explicit disposition.

### 4) Subject-outcome card

Publish the final subject outcomes:

- `moves-to-successor`
- `stays-on-predecessor-temporarily`
- `grandfathered-under-deprecated-profile`
- `blocked-until-action`
- `detached-before-retirement`
- `orphaned-if-proceed`
- `rolled-back`

For each outcome show:

- subject count
- representative worlds
- action owner
- next review moment

### 5) Waiver-resolution card

For each waiver cohort show final verdict:

- `resolved`
- `carried-forward`
- `re-prove-required`
- `blocks-retirement`
- `split`
- `expired`
- `unknown`

Also show:

- count by verdict
- owner count
- next rereview date
- unresolved debt headline

### 6) Activation-and-rollback card

Show the change mechanics:

- activation rung for successor currentness
- when predecessor becomes deprecated
- when predecessor becomes retired
- rollback class: `clean`, `partial`, `branch-only`, `receipt-only`, `none`, `unknown`
- rollback prerequisites

## Hard rule

Rollback may never be advertised as `clean` when subjects were detached, orphaned, or moved into narrower world scope.

### 7) Commit receipt

Emit one compact receipt with:

- predecessor id
- successor id
- requested action
- final readiness verdict
- subject outcome counts
- waiver verdict counts
- retirement posture
- rollback class
- strongest safe commit sentence
- blocked stronger sentence

## Copy rules

- Never say `promotion complete` if the predecessor is only deprecated, not retired.
- Never say `retirement complete` if grandfathered subjects remain.
- Never say `fully migrated` if any subject stayed pinned or out of scope.
- Never say `rollback ready` without naming rollback class and prerequisites.
- Never say `no blockers` when the real truth is `no blockers inside the narrowed coverage set`.

## Example strongest-safe sentence patterns

- `Promotion is ready with debt: 842 subjects move to the successor now, 19 are grandfathered under the deprecated predecessor, and predecessor retirement remains blocked on 4 carry-forward waiver decisions.`
- `Retirement is not ready: 6 predecessor-only bindings and 2 unresolved migration-gap waivers would become orphaned if we proceed.`
- `Rollback is branch-only: the predecessor receipts survive, but subjects already detached into the successor branch will not cleanly re-enter live inheritance.`
''',
    '1400-policy-family-timeline-page-promotion-deprecation-split-merge-rollback-and-sunset-events-interface-spec.md': r'''# Policy-family timeline page — promotion, deprecation, split, merge, rollback, and sunset events

## Purpose

This page turns policy-family history into a legible event stream so later operators can answer:

> when did this family become current, when was the predecessor deprecated, when did the split happen, which waivers were re-evaluated, and when did retirement actually become true?

## Core decision

Every policy family needs one durable **Policy-family timeline**.
Promotion, deprecation, split, merge, rollback, and sunset are not footnotes.
They are public lifecycle events.

## Fixed page order

1. family history strip
2. lifecycle event stream
3. subject-posture drift graph
4. waiver migration stream
5. retirement and rollback checkpoints
6. timeline receipt

### 1) Family history strip

Show:

- policy family id
- current profile id and revision
- deprecated predecessors count
- retired predecessors count
- open successor proposals count
- active waiver debt count tied to family changes

### 2) Lifecycle event stream

Render chronologically typed events:

- `published`
- `made-current`
- `deprecated-predecessor`
- `retired-predecessor`
- `split-successor-created`
- `merged-successor-created`
- `world-branch-published`
- `rollback-made-current`
- `sunset-without-successor`
- `history-preserved`

For every event show:

- actor
- affected predecessor/successor ids
- worlds in scope
- subject counts affected
- strongest safe event sentence

### 3) Subject-posture drift graph

Track counts over time for:

- `on-current`
- `on-deprecated`
- `grandfathered`
- `blocked-from-successor`
- `orphaned`
- `rolled-back`

## Hard rule

The graph may not compress `on-deprecated` and `grandfathered` into one line.
Those are different governance truths.

### 4) Waiver migration stream

For every lifecycle event preserve waiver outcomes:

- waiver ids touched
- verdict (`carried`, `re-proved`, `resolved`, `split`, `expired`, `blocked`)
- rereview deadlines moved or created
- unresolved debt after event

## Hard rule

Waiver movement must be visible on the same family timeline as promotion and retirement.
It may not be hidden in a separate waiver-only view.

### 5) Retirement and rollback checkpoints

Publish milestone checkpoints:

- last moment predecessor was still current
- first moment predecessor was merely deprecated
- first moment predecessor became retired
- latest safe rollback point
- latest actual rollback event
- receipt retention horizon

### 6) Timeline receipt

Emit one compact receipt with:

- family id
- current profile id
- latest predecessor id touched
- latest lifecycle event
- subject posture counts now
- waiver migration counts now
- rollback posture now
- strongest safe family-history sentence
- blocked stronger sentence

## Copy rules

- Never say `history shows upgrade` when the truer event was split or merge.
- Never say `old policy disappeared` when it was only deprecated.
- Never say `fully retired since date X` if rollback later made the predecessor current again.
- Never say `no remaining debt` when waiver rereviews are still open from the promotion.
- Never say `stable family` if currentness depends on a world-specific branch.
''',
    '1401-policy-lifecycle-lineage-receipt-page-predecessor-successor-status-and-blocked-stronger-sentences-interface-spec.md': r'''# Policy-lifecycle lineage receipt page — predecessor, successor, status, and blocked stronger sentences

## Purpose

This receipt is the durable artifact for later operators who need one compact answer to:

> what policy changed, what replaced it, what posture the predecessor is in now, who did not move, what happened to the waivers, and what stronger lifecycle sentence did the product refuse to make?

## Receipt fields

Every policy-lifecycle receipt must include:

- receipt id
- policy family id
- predecessor id and revision
- successor id and revision
- relation class
- requested action
- final action taken
- predecessor posture now: `current`, `deprecated`, `retired`, `rolled-back`, `unknown`
- successor posture now: `draft`, `current`, `blocked`, `rolled-back`, `unknown`
- subject outcome counts by posture
- waiver migration counts by verdict
- orphan-risk count
- rollback class
- strongest safe lifecycle sentence
- blocked stronger sentence
- issuance time
- actor

## Display order

1. lifecycle headline
2. predecessor/successor pair
3. action verdict
4. subject outcomes
5. waiver migration verdicts
6. rollback posture
7. blocked stronger sentence

## Hard rules

- A receipt may never omit the predecessor just because the successor is now current.
- A receipt may never say `replaced` without naming relation class.
- A receipt may never say `retired` if any subject remained grandfathered under the predecessor.
- A receipt may never say `all moved` if any subject outcome bucket other than `moves-to-successor` is nonzero.
- A receipt may never say `waivers preserved` without listing verdict counts.

## Example strongest-safe sentence patterns

- `Profile P-042 revision 7 is now current as a compatible successor to P-042 revision 6; most covered subjects moved, but 19 remain grandfathered and predecessor retirement is still deferred.`
- `Profile P-077 branch B is current only for the service world; the desktop predecessor remains deprecated but not retired, and carry-forward waivers remain under rereview.`
- `The predecessor was sunset with no successor; affected subjects were detached before retirement, and no live inheritance path remains.`
''',
}

for name, content in new_files.items():
    (docs / name).write_text(content + '\n', encoding='utf-8')

prepends = {
    root / 'README.md': r'''## Revision addendum — rev0376 policy lifecycle, supersession, and safe retirement

This pass locks the next seam after policy profiles and typed waivers: **policy lifecycle / successor relation / retirement truth**.
The archive already knew how to define a profile, measure conformance, and explain exceptions.
What it still lacked was one explicit product answer to:

> when a new policy appears, is it actually the next revision, a partial successor, a world-specific successor, a split, a merge, a rollback, or a retirement with no safe successor — and what happens to subjects and waivers still living under the old one?

This revision adds that answer.
It contributes:

- one new **Resilio evaluation** focused on supersession, retirement, successor worlds, rebind-vs-continuity, and lifecycle evidence debt
- five new **interface specs** for policy-lifecycle contract sheet, supersession review, promotion-and-retirement proof, policy-family timeline, and policy-lifecycle lineage receipt
- a tighter non-clone line based on current official Resilio evidence about deprecated or version-specific settings, Standard-folder remove/re-add replacement, disconnect vs remove vs reconnect rebind, config-authored successor worlds, service migrate-vs-clean-install forks, Local System storage-world replacement, identity regeneration, and storage/settings teardown
- four hard product decisions:
  - **every governed profile belongs to a policy family and every family change gets a typed successor relation**
  - **retirement is a first-class state, not silent deletion**
  - **waivers never auto-carry silently across supersession**
  - **subject posture after supersession stays explicit: on-current, on-deprecated, grandfathered, blocked-from-successor, orphaned, or retired-with-no-successor**

New docs in this tranche:

- `1396-resilio-policy-supersession-retirement-and-successor-world-fragmentation-evaluation.md`
- `1397-policy-lifecycle-contract-sheet-page-predecessor-successor-relation-and-retirement-scope-interface-spec.md`
- `1398-supersession-review-page-cohort-adoption-waiver-carryforward-and-orphan-risk-interface-spec.md`
- `1399-promotion-and-retirement-proof-page-successor-cutover-coverage-and-blocked-subjects-interface-spec.md`
- `1400-policy-family-timeline-page-promotion-deprecation-split-merge-rollback-and-sunset-events-interface-spec.md`
- `1401-policy-lifecycle-lineage-receipt-page-predecessor-successor-status-and-blocked-stronger-sentences-interface-spec.md`

''',
    docs / '00-status.md': r'''## Revision addendum — policy lifecycle, supersession, and safe retirement after rev0375

This pass locks the next seam after typed waivers: **policy family lifecycle**.
The archive already knew how to define profile truth and explain divergence.
What it still lacked was one explicit answer to:

> when a newer policy arrives, what exact relation does it have to the old one, who really moves, what happens to waivers, and when is the predecessor actually retired rather than merely deprecated?

This revision adds that answer.
It contributes:

- one new **Resilio evaluation** focused on supersession, successor worlds, migration-vs-fork, and retirement evidence debt
- five new **interface specs** for lifecycle contract sheet, supersession review, promotion/retirement proof, family timeline, and lifecycle receipt
- a tighter non-clone line based on current official Resilio evidence about deprecated settings, Standard-folder remove/re-add replacement, disconnect vs remove vs reconnect, config-world forks, migrated-vs-clean service successors, Local System storage-world replacement, identity regeneration, and settings teardown
- four hard product decisions:
  - **every governed profile belongs to a policy family and every family change gets a typed successor relation**
  - **retirement is a first-class state rather than silent deletion**
  - **waivers never auto-carry silently across supersession**
  - **subjects stay explicitly classified as on-current, on-deprecated, grandfathered, blocked-from-successor, orphaned, or retired-with-no-successor**

New docs in this tranche:

- `1396-resilio-policy-supersession-retirement-and-successor-world-fragmentation-evaluation.md`
- `1397-policy-lifecycle-contract-sheet-page-predecessor-successor-relation-and-retirement-scope-interface-spec.md`
- `1398-supersession-review-page-cohort-adoption-waiver-carryforward-and-orphan-risk-interface-spec.md`
- `1399-promotion-and-retirement-proof-page-successor-cutover-coverage-and-blocked-subjects-interface-spec.md`
- `1400-policy-family-timeline-page-promotion-deprecation-split-merge-rollback-and-sunset-events-interface-spec.md`
- `1401-policy-lifecycle-lineage-receipt-page-predecessor-successor-status-and-blocked-stronger-sentences-interface-spec.md`

## Current status

The archive now has a clearer settings-governance staircase:

- find the canonical setting
- prove who a change touches
- compare subjects to a baseline
- bind subjects to named profiles
- explain why nonconforming subjects are excluded or waived
- prove when a newer policy truly succeeds, branches, rolls back, or retires an older one

That last rung is what this revision adds.
It means later operators no longer need to remember whether a `new policy` story is really a revision bump, service-world fork, config-world successor, identity reset, grandfathered predecessor, or a true retirement event.
The receipt family now carries that burden directly.

''',
    docs / '10-resilio-sync-evaluation.md': r'''## Revision addendum — policy lifecycle, supersession, and safe retirement after rev0375

This revision continues directly from `rev0375` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **version-specific and deprecated power-user settings, Standard-folder capability changes that require remove/re-add, disconnect vs remove vs reconnect rebind, config-mode successor worlds, service migrate-vs-clean-install forks, Local System storage-world replacement, identity regeneration, and uninstall/settings teardown**.
2. Tightens the non-clone line again: borrow Resilio's candor that `revision drift`, `remove-readd replacement`, `disconnect`, `identity-wide removal`, `reconnect rebind`, `config-world successor`, `migrated service successor`, `clean-install fork`, `identity regeneration`, and `hard teardown` are different lifecycle truths; refuse any contract where the operator still has to reconstruct `is this the next policy, a branch, a rollback, or an actual retirement, and what happens to the waivers?` from several surfaces and articles.
3. Adds one new **Resilio evaluation** document focused on why present-day policy supersession and retirement reasoning are still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for a policy-lifecycle contract sheet, supersession review, promotion-and-retirement proof, policy-family timeline, and policy-lifecycle lineage receipt.
5. Makes one hard product decision explicit: **every governed profile belongs to a policy family and every family change gets a typed successor relation.**
6. Makes another hard product decision explicit: **retirement is a first-class state, not silent deletion, and deprecated is weaker than retired.**
7. Makes a third hard product decision explicit: **waivers never auto-carry silently across supersession; the product must issue a carry-forward verdict for each waiver family in scope.**
8. Packages the result as another continuation archive whose new tranche makes the `policy-lifecycle / successor-relation / supersession-review / retirement-proof / lifecycle-receipt` seam explicit in the reading order and page family.

### Why this pass matters

The previous tranche answered `why is this subject not cleanly on profile?`
This tranche answers the next harder question:

> `when a newer policy arrives, what exact relation does it have to the old one, who truly moves, which waivers survive, and when is the predecessor actually retired rather than merely deprecated?`

Current official Resilio material is useful here precisely because it is candid about lifecycle discontinuities, but still too scattered for a clone.
The clearest current cluster is:

- current power-user docs still admit version drift and deprecated settings
- current Standard-vs-Advanced docs still admit some capability changes require remove/re-add rather than live mutation
- current disconnect/remove docs still separate local detachment, identity-wide removal, and reconnect rebind
- current config-mode docs still admit same-settings replication, Standard-only authoring, WebUI override, and non-default storage-path successor worlds
- current service docs still admit migrate-vs-clean-install forks and Local System storage-world replacement
- current identity docs still admit linking already-running devices or regenerating identity can remove Advanced folders from the app and replace certificates
- current uninstall docs still admit hard teardown through settings removal and service-account-specific storage roots

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's policy lifecycle contract**

This time the reason is especially clear around **supersession, retirement, rebind-vs-continuity, and waiver carry-forward debt**.
Current official materials simultaneously show that:

- current `Power user preferences` docs still say older versions may miss some settings or still have deprecated ones
- current `What's the difference between Standard and Advanced folders?` docs still say some permission/capability changes are not on-the-fly for Standard folders and require remove/re-add
- current `Disconnecting and Removing Folders` docs still distinguish one-device disconnect from identity-wide removal and still say reconnect may land on a new default path unless the operator manually rebinds to the original one
- current `Running Sync in configuration mode` docs still say config mode helps apply the same settings on multiple machines, but only for Standard folders, while non-default `storage_path` creates a new settings world and config-authored shares override WebUI-added folders
- current `Running Sync as a service on Windows` and `Sync Service Troubleshooting on Windows` docs still say service install can migrate existing shares or create a clean-install fork, and principal changes can create another storage world with no prior folders present
- current `Sync Private Identity & Linking My Devices` and `Can I change the name of my Sync identity?` docs still say linking already-running devices or regenerating identity can replace one certificate and remove Advanced folders from the app on the affected device
- current `How to uninstall Sync?` docs still say settings teardown can be full and storage-root-specific, including service roots that vary by principal

That candor is useful.
The lifecycle contract is the problem.
AnonSync should not clone a world where the operator still has to translate `new version`, `remove and re-add`, `disconnect`, `reconnect`, `service migration`, `clean install`, `Local System`, `new identity`, and `remove settings` into one stable answer about predecessor, successor relation, subject coverage, waiver carry-forward, retirement scope, rollback class, and blocked stronger sentence by stitching together several KB articles.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because policy succession is a real contract with separate truths for predecessor, successor, relation class, waiver migration, retirement state, subject posture, and rollback class — but the present contract still scatters the answer to `is the old policy actually replaced yet?` across several KB articles instead of owning it as one stable page family.**

''',
    docs / '11-resilio-borrow-line-and-non-clone-scorecard.md': r'''## Revision addendum — policy lifecycle scorecard after rev0375

The new evaluated seam is **policy lifecycle / successor relation / retirement truth**.

| Seam | Current Resilio posture | Borrow / clone / reject | Why | Required AnonSync pages |
| --- | --- | --- | --- | --- |
| Policy families, successor relation, deprecation, retirement, split/merge, waiver carry-forward, and rollback posture | Useful but too article-shaped | **Adapt** | Current docs are admirably candid that version drift, remove-readd replacement, disconnect vs remove, reconnect rebind, config-world succession, service migration vs clean-install fork, identity regeneration, and settings teardown are different lifecycle truths — but the operator still has to reconstruct `what exactly replaced what, who really moved, what happened to the waivers, and is the predecessor merely deprecated or actually retired?` from separate power-user, identity, remove/reconnect, config, service, and uninstall articles | **Policy-lifecycle contract sheet**, **Supersession review**, **Promotion and retirement proof**, **Policy-family timeline**, and **Policy-lifecycle lineage receipt** |

> borrow Resilio's candor that migration, clean-install fork, rebind, identity replacement, and teardown are materially different lifecycle truths; refuse any product contract where `new policy`, `deprecated`, `reconnect`, or `migrated` still hides predecessor/successor relation, waiver carry-forward, retirement state, and rollback class.

''',
    docs / '12-resilio-interface-clone-veto-tests-and-page-obligations.md': r'''## Revision addendum — clone-veto obligations for policy lifecycle, supersession, and retirement after rev0375

### New veto seam

A sync product fails the clone test on this seam if it cannot answer, in one operator-facing review:

- what exact predecessor is being replaced
- what exact successor relation class applies
- what subject and world coverage the successor truly has
- what happens to live waivers during promotion
- whether the predecessor is current, deprecated, grandfathered, retired, rolled back, or sunset with no successor
- what rollback class still survives after the action

### Required AnonSync page obligations

Any serious policy-family workflow must ship with:

1. a **policy-lifecycle contract sheet** that names predecessor, successor, relation class, scope, waiver carry-forward rule, and retirement consequence
2. a **supersession review** that separates auto-adopters, pinned subjects, grandfathered subjects, blocked subjects, out-of-scope subjects, and orphan-risk subjects
3. a **promotion and retirement proof** that publishes subject outcome counts, waiver verdict counts, retirement readiness, and rollback class before commit
4. a **policy-family timeline** that keeps promotion, deprecation, retirement, split, merge, rollback, and waiver migration legible over time
5. a **policy-lifecycle lineage receipt** that records predecessor, successor, relation class, final posture, waiver migration, and blocked stronger sentence

### Explicit clone vetoes

Do not clone any contract where:

- `new policy` is allowed to stand in for a typed successor relation
- `deprecated` is allowed to stand in for `retired` or `still current but discouraged`
- waivers are allowed to carry forward silently during promotion
- retirement is allowed while orphan-risk subjects remain unresolved
- `everyone moved` is allowed without subject posture counts
- rollback is allowed to sound clean when subjects were grandfathered, detached, or moved into narrower world scope
- deleting the old record is allowed to masquerade as a clean retirement

''',
    docs / '20-product-direction.md': r'''## Revision addendum — product direction after rev0375: policy lifecycle must compile into one reviewed successor contract

Another current Resilio pass sharpens one more direction-level decision:

- **policy family lifecycle is first-class product state**
- **predecessor, successor, relation class, waiver carry-forward, and retirement state are separate public truths**
- **`deprecated` must never overclaim `retired`**
- **`new policy` must never overclaim `everyone moved`**
- **durable receipts, not migration folklore, preserve what replaced what and what stronger lifecycle sentence remained blocked**

From that, five product-direction rules follow:

1. A sync product may not let one `new default` sentence stand in for in-place revision, compatible successor, split successor, merged successor, world-specific successor, rollback successor, or sunset with no successor.
2. Any policy promotion must publish subject posture counts — on-current, on-deprecated, grandfathered, blocked-from-successor, orphaned, or rolled-back — before commit.
3. Any retirement action must keep predecessor receipts and waiver history visible instead of letting deletion masquerade as completion.
4. Waiver carry-forward must be explicit; no exception debt may silently cross a supersession boundary.
5. Durable receipts, not KB archaeology, must preserve predecessor id, successor id, relation class, waiver verdicts, retirement posture, rollback class, and blocked stronger sentence.

''',
    docs / 'sources.md': r'''## Revision addendum — official sources emphasized in rev0376

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about policy succession, replacement, retirement, rebind-vs-continuity, and teardown.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `deprecated setting`, `remove-readd replacement`, `disconnect`, `identity-wide remove`, `reconnect rebind`, `config-world successor`, `migrated service successor`, `clean-install fork`, `identity regeneration`, and `remove settings` are different lifecycle truths?

> where do those same current docs still show that the ordinary operator answer about `is this really the next policy, what happened to the old one, and what happens to the waivers and out-of-scope subjects?` depends on several articles instead of one stable product-owned lifecycle workspace?

The most load-bearing source set for this pass was:

- Resilio's current `Power user preferences` article, which still says the article covers today's latest Sync version and that older versions may be missing some settings or still have deprecated ones.
- Resilio's current `What's the difference between Standard and Advanced folders?` article, which still says some Standard-folder changes are not on-the-fly and require removing the share and re-adding it with a new key.
- Resilio's current `Disconnecting and Removing Folders` article, which still distinguishes one-device disconnect from identity-wide remove and still says reconnect may propose a different default path and create a new directory unless the operator manually rebinds to the old path.
- Resilio's current `Running Sync in configuration mode` article, which still says config mode helps apply the same settings on multiple machines, only supports Standard folders there, lets non-default `storage_path` create another settings world, and lets config-authored shared folders override WebUI-added folders while disabling WebUI.
- Resilio's current `Running Sync as a service on Windows` article, which still says service installation can migrate existing shares/settings or create a clean installation that requires re-sharing folders.
- Resilio's current `Sync Service Troubleshooting on Windows` article, which still says switching the service to `Local System` creates another service storage world with no old folders present and requires re-add / re-share.
- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says linking already-running devices can replace one certificate and remove Advanced folders from the app on the affected device.
- Resilio's current `Can I change the name of my Sync identity?` article, which still says changing identity name requires unlinking and creating a new identity, after which Advanced folders are removed from the Sync instance while Standard folders remain.
- Resilio's current `How to uninstall Sync?` article, which still says uninstall plus settings removal is a stronger teardown and that service storage roots differ by service account.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that migration, fork, rebind, and teardown are materially different lifecycle truths
- but current Resilio still answers `what replaced what, who really moved, and is the predecessor actually retired yet?` too diffusely
- AnonSync should therefore prefer explicit lifecycle sheets, supersession reviews, promotion/retirement proof pages, family timelines, and durable lifecycle receipts over succession folklore

Primary sources:

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- What's the difference between Standard and Advanced folders?  
  https://help.resilio.com/hc/en-us/articles/204754679-What-s-the-difference-between-Standard-and-Advanced-folders

- Disconnecting and Removing Folders  
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Running Sync as a service on Windows  
  https://help.resilio.com/hc/en-us/articles/207701296-Running-Sync-as-a-service-on-Windows

- Sync Service Troubleshooting on Windows  
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Can I change the name of my Sync identity?  
  https://help.resilio.com/hc/en-us/articles/206163443-Can-I-change-the-name-of-my-Sync-identity

- How to uninstall Sync?  
  https://help.resilio.com/hc/en-us/articles/204775029-How-to-uninstall-Sync

''',
}

for path, block in prepends.items():
    old = path.read_text(encoding='utf-8')
    path.write_text(block + old, encoding='utf-8')

