from pathlib import Path

root = Path('/mnt/data/work0373')
docs = root / 'docs'

new_files = {
    '1384-resilio-policy-profile-pack-binding-revision-and-conformance-fragmentation-evaluation.md': r'''# Resilio policy-profile pack, binding revision, and conformance fragmentation evaluation

## Why this pass exists

The archive already had stronger doctrine for:

- locating a canonical setting object
- proving which surface or world owns it
- proving who a mutation will touch
- comparing a subject to an explicit baseline

What it still lacked was one explicit answer to the next ordinary operator question:

> what reusable policy bundle am I actually using, which fields does it cover, which subjects are truly bound to it, and what exactly would a profile revision change?

Current official Resilio material is again useful, but it still spreads the answer across several families:

- `Sync Private Identity & Linking My Devices`
- `Synchronization Modes`
- `Sync Preferences`
- `Folder Preferences`
- `Power user preferences`
- `File download priority`
- `Running Sync in configuration mode`
- `Running Sync as a service on Windows`
- `Settings on mobile platforms`
- `Sync interface on Android`

## Current official Resilio evidence that matters here

Current official docs still show all of the following:

- `Sync Private Identity & Linking My Devices` still says linked devices make all folders automatically available across the linked set and lets each device pick a synchronization mode for new arrivals.
- `Synchronization Modes` still says the device-level default connect behavior lives in `Preferences -> Identity -> Default connect folder mode`.
- `Sync Preferences` still says there is a default folder/file location for where new arrivals are created when the device is in `Selective Sync` or `Synced` mode.
- `Folder Preferences` still says per-folder behavior such as Archive, overwrite-on-read-only, relay/tracker/LAN/predefined-host discovery, and file-download priority are configured on the selected folder.
- `Power user preferences` together with `File download priority` still show a global default layer, including `folder_defaults.transfer_priority`, while also saying manually altered shares stop following later global-default changes even if later set back to `None`.
- `Settings on mobile platforms` and `Sync interface on Android` still show device-level settings and per-share advanced preferences as distinct local routes.
- `Running Sync in configuration mode` still says config mode is useful when you need to apply the same settings on a number of different machines, that advanced preferences can be added to `sync.conf`, that only Standard folders can be configured there, that a non-default `storage_path` creates new settings there, and that config-authored shared folders override folders previously added from WebUI while disabling WebUI.
- `Running Sync as a service on Windows` still says service installation can migrate existing shares/settings or create a clean installation that requires re-sharing folders.

So current Resilio still contains real profile-like ingredients:

- device-family defaults
- per-device arrival defaults
- per-folder policy lanes
- global advanced defaults
- config-authored fleet replication
- mobile-local share policy lanes
- migrated vs forked successor worlds

But those ingredients do not yet become one first-class operator-facing **policy-profile object**.

## What Resilio still gets right

### 1) It admits there is reusable policy, not just one-off clicks

Config mode plainly says it is useful when the same settings must be applied to a number of different machines.
That is real profile intent even if the product does not model it as a named profile object.

### 2) It admits per-device defaults and per-folder overrides are different kinds of truth

The linked-device and synchronization-mode docs make it clear that one device can default to `Disconnected`, `Selective Sync`, or `Synced`, while per-folder preferences still shape the local subject afterward.
That distinction matters.

### 3) It admits a global default can coexist with manual detachment

`File download priority` plus `Power user preferences` still show one of the clearest examples: a default exists, existing unchanged shares can follow it, new shares can inherit it, and manually touched shares can detach from later revisions.
That is a useful warning for any profile system.

### 4) It admits world authorship changes the meaning of reuse

Config mode, service migration, clean-install service forks, and storage-path changes all show that `same settings` is weaker than `same governing world`.
That is another valuable distinction.

## Where current Resilio still fragments the operator answer

### A) Reusable policy is present, but not modeled as one named object

An operator can piece together something profile-like from:

- linked-device default mode
- default arrival root
- folder preferences
- power-user defaults
- config-authored settings
- mobile-local share settings

But current docs do not give that bundle one canonical identity with:

- explicit field coverage
- version/revision id
- supported subject classes
- world scope
- conformance status

### B) Binding class is implicit rather than product-owned

Today the operator may still have to infer whether a subject is:

- live-inheriting a default
- manually pinned at one field
- effectively similar but detached
- mobile-local and therefore parallel
- config-owned in another world
- a migrated service successor
- a clean-install fork

That is too much archaeology for one ordinary `is this on profile?` question.

### C) Revision rollout is not a first-class review object

Current docs help explain separate setting lanes, but they do not yield one stable answer to:

- which subjects will adopt profile revision `N+1`
- which remain pinned
- which are snapshots that only look conformant
- which worlds are outside the rollout envelope
- which subjects require explicit rejoin rather than value coincidence

### D) Conformance is too easy to overclaim

Without a first-class profile object, current workflows can too easily blur:

- `shows the same value`
- `inherits from this profile`
- `matches current revision`
- `belongs to this world`
- `is safe to bulk-roll forward`

### E) Fleet replication and local route variation are still separate stories

Config mode speaks in machine replication terms.
Mobile docs speak in device-local and share-local preference routes.
Folder preferences speak in per-folder local behavior.
These are individually useful but still too separate to answer one operator-facing conformance question cleanly.

## Hard product decisions now locked for AnonSync

### 1) Every reusable defaults bundle must be a first-class versioned policy profile

A profile must have:

- canonical profile id
- profile revision id
- explicit field coverage
- supported subject classes
- supported world scope
- author and issuance time

### 2) Subjects bind to profiles by binding class, not by visible similarity alone

Supported binding classes must include at least:

- `live-inherit`
- `field-pin`
- `frozen-snapshot`
- `branched-profile`
- `unbound`
- `unknown`

### 3) Profile coverage may not silently cross worlds or surfaces

A profile can span multiple worlds only if the product explicitly models that join.
Config-authored worlds, service forks, mobile-local lanes, and desktop-interactive lanes must remain distinct until explicitly joined.

### 4) Profile revision rollout is compare-first, mutate-second

Before revision apply, the product must show:

- target cohort
- out-of-scope cohort
- pinned fields
- frozen snapshots
- branched descendants
- blocked subjects
- activation and verification plan

### 5) Exception types must remain typed

`Same current value` must not collapse:

- live inheritance
- field pin
- frozen snapshot
- branch-from-profile
- unbound coincidence

## Required page family

This seam now requires five AnonSync pages:

- **Policy-profile contract sheet**
- **Profile conformance review**
- **Profile attach and rollout proof**
- **Profile drift timeline**
- **Profile lineage receipt**

## New borrow line

Borrow Resilio's candor that reusable policy can live across device defaults, per-folder settings, global advanced defaults, config-authored machine replication, and mobile-local lanes.

## New veto line

Do not clone any settings contract where the operator can still ask `what named policy profile governs this subject, what revision is it on, and what exactly will the next profile change touch?` and the honest answer is still `it depends on which settings route, machine world, and remembered override history you manually reconstruct`.''',
    '1385-policy-profile-contract-sheet-page-profile-signature-field-coverage-and-binding-class-interface-spec.md': r'''# Policy-profile contract sheet page — profile signature, field coverage, and binding class

## Purpose

This page answers the reusable-policy question that baseline comparison alone does not finish:

> what policy profile exists here, what exact fields does it govern, which subjects can bind to it, and what binding class is the focused subject in right now?

## Core decision

Every serious reusable defaults bundle must render one first-class **Policy-profile contract sheet** before bulk attachment, revision rollout, or conformance claims are offered.
The page owns:

- profile signature
- field coverage
- supported subject classes
- supported world scope
- current revision
- focused-subject binding class
- strongest safe profile sentence

## Fixed page order

1. profile strip
2. profile signature card
3. field-coverage card
4. supported-subject-and-world card
5. focused-subject binding card
6. revision-safety card
7. profile receipt

### 1) Profile strip

Show:

- canonical profile id
- profile title
- current profile revision id
- profile status: `draft`, `active`, `retired`, `superseded`, `unknown`
- focused subject id
- focused world id
- focused binding class
- top question being answered: `what profile governs this subject?`

### 2) Profile signature card

Emit one normalized signature with:

- canonical profile id
- canonical setting-family ids covered
- revision id
- author and issuance time
- allowed mutation surfaces
- allowed activation rungs
- witness confidence

## Hard rule

A profile may not be identified only by:

- a UI section title
- a remembered settings cluster
- a screenshot of current values
- `the defaults we usually use`

If the operator started from any of those, the page must resolve them to one canonical profile id first.

### 3) Field-coverage card

List every field the profile explicitly governs.
For each field show:

- canonical field id
- target value state
- whether inheritance is part of the field contract
- activation rung
- unsupported surfaces/worlds
- stronger sentence blocked if witness is incomplete

## Hard rule

Anything not listed in field coverage is **outside the profile**.
The page must never imply that a profile governs nearby settings by vibe, menu adjacency, or prior operator memory.

### 4) Supported-subject-and-world card

Show where the profile is allowed to bind:

- supported subject classes
- supported world classes
- excluded subject classes
- excluded world classes
- known parallel lanes
- required prerequisites for attachment

Examples of world classes include:

- interactive desktop world
- service world
- config-authored world
- mobile-local share lane
- linked-family arrival lane

### 5) Focused-subject binding card

For the focused subject render exactly one binding class:

- `live-inherit`
- `field-pin`
- `frozen-snapshot`
- `branched-profile`
- `unbound`
- `unknown`

For the chosen class show:

- what is proven
- which fields are still live to profile revisions
- which fields are pinned away
- whether current value coincidence is misleading
- what stronger class remains blocked

## Hard rule

`same visible values as profile` may never overclaim `live-inherit`.

### 6) Revision-safety card

Show what a future profile revision would do to this focused subject:

- `auto-adopts next revision`
- `adopts only unpinned fields`
- `never changes until explicit rebind`
- `belongs to another branch`
- `outside supported world`
- `unknown`

### 7) Profile receipt

Emit one compact receipt with:

- profile id
- profile revision id
- focused subject id
- field coverage count
- focused binding class
- next-revision adoption posture
- strongest safe profile sentence
- blocked stronger sentence

## Copy rules

- Never say `on profile` unless a binding class stronger than `unbound` is proven.
- Never say `inherits this profile` when the subject is only value-equal.
- Never say `same defaults` unless the field-coverage contract actually matches.
- Never say `profile governs this world` unless world scope is explicitly listed.
- Never let `all the usual settings` stand in for the coverage list.

## Example strongest-safe sentence patterns

- `This subject currently matches the profile's visible values, but it is a frozen snapshot and will not adopt later profile revisions.`
- `This subject is live-bound to profile rev12 for covered fields, while two explicitly pinned fields remain outside live inheritance.`
- `The profile governs desktop interactive worlds only; this service world remains outside supported scope.`
- `No canonical policy profile has yet been proven for this subject, even though several nearby defaults currently coincide.`''',
    '1386-profile-conformance-review-page-live-bindings-field-pins-frozen-copies-and-unbound-subjects-interface-spec.md': r'''# Profile conformance review page — live bindings, field pins, frozen copies, and unbound subjects

## Purpose

This page answers the cohort question that one-subject profile inspection does not finish:

> across all candidate subjects, who is truly live on this profile, who only looks similar, who is partially pinned away, and who is outside the profile entirely?

## Core decision

Every serious profile audit must render one first-class **Profile conformance review**.
The page owns:

- profile-wide cohort counts
- conformance grades
- false-friend matches
- pin/freeze/branch reasons
- safe next actions

## Fixed page order

1. conformance summary strip
2. grade ledger
3. cohort buckets
4. false-friend review
5. safe action tray
6. conformance receipt

### 1) Conformance summary strip

Show:

- canonical profile id
- active revision id
- reviewed cohort id
- reviewed world scope
- total candidate subjects
- total proven live-bound subjects
- total partial/pinned subjects
- total frozen or branched subjects
- total unbound subjects
- total unknown subjects

### 2) Grade ledger

Every reviewed subject must receive exactly one top-line conformance grade:

- `full live conformance`
- `partial live conformance`
- `snapshot conformance`
- `branched conformance`
- `value-only coincidence`
- `unbound`
- `unknown`

For each grade the page must define:

- what is proven
- what is not proven
- whether next profile revision will apply
- blocked stronger sentence

## Hard rule

`value-only coincidence` may never be rendered in the same visual style as `full live conformance`.

### 3) Cohort buckets

Group the reviewed subjects into explicit buckets:

- fully live-bound
- live-bound with pinned fields
- frozen snapshots
- branched descendants
- unsupported-world subjects
- unbound but similar
- unknown or insufficient-witness subjects

For each bucket show:

- count
- representative fields causing placement
- next safe action

### 4) False-friend review

Catch at least the following misleading similarities:

- same displayed values but pinned fields
- same values from another branch revision
- same values in an unsupported world
- same values in a frozen snapshot
- same values from manual coincidence after detach
- same label but different profile id

### 5) Safe action tray

Only actions compatible with the proven grade may be offered:

- `leave live-bound`
- `pin selected fields`
- `unpin and rejoin`
- `capture snapshot`
- `branch new profile`
- `bind from unbound state`
- `exclude from profile`
- `collect more evidence`

For each action show:

- whether value changes
- whether revision adoption changes
- whether world support changes
- whether future drift remains expected

### 6) Conformance receipt

Emit one compact receipt with:

- profile id
- profile revision id
- cohort id
- subject counts by grade
- false-friend count
- offered safe actions
- strongest safe cohort sentence
- blocked stronger sentence

## Copy rules

- Never say `all subjects conform` unless no weaker bucket remains.
- Never say `same profile` when only `same visible values` is proven.
- Never hide pinned fields inside the `conformant` bucket.
- Never let frozen snapshots masquerade as live-bound subjects.
- Never allow unsupported-world rows to count as profile members.

## Example strongest-safe sentence patterns

- `Forty-eight subjects are fully live-bound to this profile revision; six more currently match values but remain outside live adoption because of field pins.`
- `Three subjects look conformant at today's values, but they are frozen snapshots and will not adopt revision rev13.`
- `This service-world cohort is similar to the profile but remains outside supported binding scope.`
- `Conformance is unknown for nine subjects because the product has not yet proven their active world or field-pin posture.`''',
    '1387-profile-attach-and-rollout-proof-page-target-cohort-adoption-mode-and-revision-safety-interface-spec.md': r'''# Profile attach and rollout proof page — target cohort, adoption mode, and revision safety

## Purpose

This page answers the pre-commit mutation question for reusable policy:

> if I bind these subjects to this profile or roll them forward to a new profile revision, which subjects will change, what adoption mode will each one enter, and which worlds or fields remain excluded?

## Core decision

Every serious profile attachment or revision rollout must compile into one **Profile attach and rollout proof** before apply.
The page owns:

- target cohort
- excluded cohort
- adoption mode per subject
- field-level pin preservation
- world-scope blocking
- activation plan
- strongest safe rollout sentence

## Fixed page order

1. rollout strip
2. target-and-exclusion card
3. adoption-mode ledger
4. field-change preview
5. activation-and-verification card
6. rollout receipt

### 1) Rollout strip

Show:

- canonical profile id
- from revision id
- to revision id
- rollout mode: `first bind`, `revision bump`, `rejoin`, `branch from live`, `unknown`
- target cohort id
- world scope
- top question being answered: `what exactly will this rollout do?`

### 2) Target-and-exclusion card

Publish explicit counts for:

- will bind live
- will remain live with partial pins
- will be converted to frozen snapshots
- will be branched
- will remain unbound
- blocked by unsupported world
- blocked by missing evidence

## Hard rule

`apply profile` may never be offered without explicit exclusion counts.

### 3) Adoption-mode ledger

For every affected subject emit one adoption mode:

- `bind live`
- `bind live with field pins preserved`
- `capture frozen snapshot`
- `branch new profile lineage`
- `rejoin existing live profile`
- `leave unbound`
- `blocked`

For each mode show:

- whether current value changes now
- whether future revisions apply automatically
- whether current world is supported
- whether any stronger adoption mode is blocked

### 4) Field-change preview

For all fields in the profile coverage list show:

- fields that will change value now
- fields already matching and remaining live
- fields already matching but remaining pinned
- fields outside profile coverage
- fields blocked by unsupported world or missing witness

### 5) Activation-and-verification card

Show for the rollout:

- activation rung per affected field family
- whether restart, reconnect, or rebind is required
- verification witness required after apply
- rollback or rejoin path
- receipts to emit on success or partial block

### 6) Rollout receipt

Emit one compact receipt with:

- profile id
- from/to revision ids
- target cohort id
- adoption-mode counts
- changed-field count
- blocked-subject count
- strongest safe rollout sentence
- blocked stronger sentence

## Copy rules

- Never say `roll out to all` unless blocked and excluded subjects are still published.
- Never let `same current value` stand in for `will adopt next revision`.
- Never convert a pinned subject into live inheritance without explicit review.
- Never silently bind unsupported worlds because the values happen to be representable there.
- Never let `update profile` hide whether this is live rollout, snapshot capture, or branch creation.

## Example strongest-safe sentence patterns

- `This rollout will bind 42 subjects live to profile rev13, preserve field pins on 5 subjects, and leave 3 service-world subjects outside scope.`
- `No values change today for these 9 subjects, but attaching them live will cause future revisions to apply automatically.`
- `These 4 rows require an explicit rejoin because they are frozen snapshots, not detached live bindings.`
- `The rollout is blocked for the mobile-local lane because the profile does not govern that parallel world.`''',
    '1388-profile-drift-timeline-page-revision-bump-field-pin-freeze-branch-and-rejoin-events-interface-spec.md': r'''# Profile drift timeline page — revision bump, field pin, freeze, branch, and rejoin events

## Purpose

This page preserves the history that makes profile conformance legible later:

> when did this subject stop being live-bound, which profile revision was current then, which fields were pinned or frozen, and when did the subject rejoin or branch away?

## Core decision

Every serious reusable-policy system must preserve one **Profile drift timeline**.
The page owns:

- profile revision chronology
- binding-class transitions
- field-pin and unpin events
- freeze and branch events
- rejoin events
- blocked-coverage events

## Event classes

The timeline must distinguish at least:

- `profile created`
- `profile revision published`
- `subject live-bound`
- `field pinned`
- `field unpinned`
- `snapshot captured`
- `branch created`
- `subject rejoined live profile`
- `world became unsupported`
- `world became supported`
- `profile retired`
- `receipt emitted`

## Fixed page order

1. timeline strip
2. revision spine
3. subject binding transitions
4. field-pin ledger
5. branch-and-rejoin ledger
6. drift receipt

### 1) Timeline strip

Show:

- canonical profile id
- focused subject or cohort id
- timeline scope: `profile-wide`, `subject`, `cohort`
- current revision id
- current binding class
- current drift verdict

### 2) Revision spine

For each profile revision show:

- revision id
- publication time
- changed fields
- activation class
- subject counts that auto-adopted
- subject counts that did not adopt because of pins, snapshots, branches, or unsupported worlds

### 3) Subject binding transitions

For the focused subject or cohort show the chronology of:

- first bind
- detach to pins
- snapshot capture
- branch creation
- rejoin
- retirement or exclusion

### 4) Field-pin ledger

For each field pin/unpin event show:

- field id
- previous state
- resulting state
- whether live inheritance was broken or restored
- whether current value changed immediately

### 5) Branch-and-rejoin ledger

Show separately:

- branch source revision
- branch target profile id
- subjects moved
- reason for branch
- rejoin preconditions
- rejoin proof emitted

### 6) Drift receipt

Emit one compact receipt with:

- profile id
- revision id in force now
- focused subject/cohort id
- current binding class
- outstanding pins
- last branch/rejoin event if any
- strongest safe drift sentence
- blocked stronger sentence

## Copy rules

- Never compress `pin`, `snapshot`, and `branch` into one generic `override` event.
- Never say `fell out of profile` without naming the actual transition class.
- Never say `rejoined` unless live inheritance is proven restored.
- Never let revision publication imply subject adoption.
- Never treat unsupported-world exclusion as a normal live drift event.

## Example strongest-safe sentence patterns

- `Profile rev13 was published on this date, but this subject did not adopt it because two fields were pinned at rev12.`
- `This subject matched profile values for a period as a frozen snapshot, not as a live binding.`
- `Branch profile ops-lan-only was created from rev11 and remains a separate lineage rather than a temporary exception.`
- `Live inheritance was restored at this event; earlier visible equality did not yet prove rejoin.`''',
    '1389-profile-lineage-receipt-page-profile-signature-binding-class-and-blocked-stronger-sentences-interface-spec.md': r'''# Profile lineage receipt page — profile signature, binding class, and blocked stronger sentences

## Purpose

This page is the durable handoff object for reusable policy:

> which exact profile and revision were involved, what binding class was proven, what action was taken or withheld, and what stronger profile sentence did the product refuse to make?

## Core decision

Every serious profile inspection, conformance review, or rollout must emit one durable **Profile lineage receipt**.
The receipt is the smallest artifact that later operators can trust without replaying the whole workflow.

## Required receipt fields

The receipt must include:

- canonical profile id
- profile title
- profile revision id
- field coverage hash or signature
- focused subject or cohort id
- world id or world scope
- proven binding class
- conformance grade if reviewed
- rollout action taken or withheld
- changed-field count
- blocked-subject count if applicable
- witness confidence
- strongest safe sentence
- blocked stronger sentence
- author and timestamp

## Rendering rules

### Header

Show:

- profile title
- profile id
- revision id
- receipt class: `inspection`, `conformance`, `rollout`, `rejoin`, `branch`, `retirement`

### Signature block

Show:

- field coverage signature
- supported world scope
- supported subject classes
- activation class summary

### Binding block

Show exactly one binding class verdict:

- `live-inherit`
- `field-pin`
- `frozen-snapshot`
- `branched-profile`
- `unbound`
- `unknown`

If more than one subject is included, show counts by class and explicitly mark the strongest class not universally proven.

### Action block

Show what happened:

- no mutation, inspection only
- bound live
- preserved pins
- snapshot captured
- branch created
- rejoined live profile
- left unbound
- rollout blocked

### Safety language block

The receipt must preserve:

- strongest safe sentence
- blocked stronger sentence
- reason that stronger sentence remains blocked

## Hard rule

A receipt may not use `on profile` or `matches profile` language without recording the exact binding class and conformance grade that justified it.

## Example strongest-safe sentence patterns

- `This subject is live-bound to profile backup-wan-safe rev13 for all covered fields.`
- `This subject currently matches profile rev13 values but remains a frozen snapshot outside future live adoption.`
- `This cohort was rolled to rev13 with pins preserved on two covered fields.`
- `This world remains outside supported profile scope, so no profile-membership claim is made.`

## Blocked stronger sentence patterns

- `Blocked: "all subjects are on profile rev13" — three subjects remain unbound value matches only.`
- `Blocked: "this subject will follow future profile changes" — binding class is frozen snapshot.`
- `Blocked: "profile governs this whole deployment" — service/config worlds remain outside supported scope.`
- `Blocked: "rejoin complete" — live inheritance has not yet been re-proven.`''',
}

for name, content in new_files.items():
    (docs / name).write_text(content + '\n', encoding='utf-8')


def prepend(path: Path, text: str):
    old = path.read_text(encoding='utf-8')
    path.write_text(text.rstrip() + '\n\n' + old, encoding='utf-8')

readme_add = r'''## Revision addendum — policy-profile pack, binding class, and conformance rollout after rev0373

This revision continues directly from `rev0373` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **linked-device auto-availability, device default connect mode, default arrival roots, per-folder preferences, global power-user defaults, config-mode replication for the same settings on multiple machines, config-only standard-folder limits, storage-path world forks, service migration vs clean-install forks, and mobile/share-local preference routes**.
2. Tightens the non-clone line again: borrow Resilio's candor that `linked-family default mode`, `default arrival root`, `per-share policy`, `global advanced default`, `mobile-local share lane`, `config-authored fleet replication`, `storage-path world fork`, and `service successor world` are different truths; refuse any contract where the operator still has to reconstruct `what named policy profile exists, what exact fields it covers, which subjects are truly bound to it, and what the next profile revision will actually change` from several surfaces and articles.
3. Adds one new **Resilio evaluation** document focused on why present-day policy-profile and conformance reasoning are still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for a policy-profile contract sheet, profile conformance review, profile attach-and-rollout proof, profile drift timeline, and profile lineage receipt.
5. Makes one hard product decision explicit: **every reusable defaults bundle must be a first-class versioned policy-profile object with explicit field coverage, subject scope, and world scope.**
6. Makes another hard product decision explicit: **binding classes are real — `live-inherit`, `field-pin`, `frozen-snapshot`, `branched-profile`, and `unbound` are different truths.**
7. Makes a third hard product decision explicit: **profile revision rollout is compare-first, mutate-second, and `same current values` must stay visibly weaker than `will adopt future profile revisions`.**
8. Packages the result as another continuation archive whose new tranche makes the `policy-profile / binding-class / conformance-review / rollout-proof / profile-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1384-resilio-policy-profile-pack-binding-revision-and-conformance-fragmentation-evaluation.md`
- `1385-policy-profile-contract-sheet-page-profile-signature-field-coverage-and-binding-class-interface-spec.md`
- `1386-profile-conformance-review-page-live-bindings-field-pins-frozen-copies-and-unbound-subjects-interface-spec.md`
- `1387-profile-attach-and-rollout-proof-page-target-cohort-adoption-mode-and-revision-safety-interface-spec.md`
- `1388-profile-drift-timeline-page-revision-bump-field-pin-freeze-branch-and-rejoin-events-interface-spec.md`
- `1389-profile-lineage-receipt-page-profile-signature-binding-class-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's profile-shaped settings contract**

This time the reason is especially clear around **linked-family defaults, per-device arrival posture, per-folder policy, global advanced defaults, config-mode replication, storage/world forks, and mobile/share-local lanes**.
Current official materials simultaneously show that:

- current `Sync Private Identity & Linking My Devices` and `Synchronization Modes` docs still describe automatic linked-device availability plus per-device default connect behavior
- current `Sync Preferences` docs still describe default arrival roots for new folders and single-file landings
- current `Folder Preferences`, `Power user preferences`, and `File download priority` docs still distribute one reusable policy family across per-folder, advanced-default, and manually detached lanes
- current Android and mobile settings docs still keep device-level and share-level advanced preferences in separate local routes
- current `Running Sync in configuration mode` docs still say config mode is useful for applying the same settings on multiple machines, still allow advanced preferences in `sync.conf`, still limit config-authored shares to Standard folders, still disable WebUI when shared folders are specified there, and still let non-default storage create another settings world
- current `Running Sync as a service on Windows` docs still say service installation can preserve continuity by migration or create a clean-install fork that requires re-sharing folders

That candor is useful.
The profile contract is the problem.
AnonSync should not clone a world where the operator still has to translate `default mode`, `same settings`, `folder preference`, `advanced default`, `config replica`, `mobile share setting`, and `migrated service copy` into one stable answer about canonical profile id, field coverage, binding class, conformance grade, revision adoption, and blocked stronger sentence by stitching together several KB articles.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because reusable policy is a real contract with separate truths for profile identity, field coverage, binding class, world scope, revision adoption, and conformance — but the present contract still scatters the answer to `what profile governs this subject, and what exactly will the next profile revision change?` across several KB articles instead of owning it as one stable page family.**'''

status_add = r'''## Revision addendum — policy-profile pack, binding class, and conformance rollout after rev0373

This tranche locks the next seam around **reusable policy profile truth**.
The key decisions now made explicit in the archive are:

- **every reusable defaults bundle must be a first-class versioned policy-profile object rather than a remembered cluster of global, per-share, config, and mobile settings**
- **`live-inherit`, `field-pin`, `frozen-snapshot`, `branched-profile`, and `unbound` are different binding truths**
- **field coverage is explicit, so nearby settings can no longer quietly ride along under `the usual defaults` language**
- **profile scope is world-aware, so config-authored worlds, service forks, mobile-local lanes, and interactive desktop lanes remain separate until explicitly joined**
- **profile revision rollout is compare-first, mutate-second, and `same current values` is weaker than `will adopt future revisions`**
- **every serious profile inspection or rollout now needs one receipt that preserves profile id, revision, field coverage, binding class, conformance grade, and blocked stronger sentence**

New docs added in this tranche:

- `1384-resilio-policy-profile-pack-binding-revision-and-conformance-fragmentation-evaluation.md`
- `1385-policy-profile-contract-sheet-page-profile-signature-field-coverage-and-binding-class-interface-spec.md`
- `1386-profile-conformance-review-page-live-bindings-field-pins-frozen-copies-and-unbound-subjects-interface-spec.md`
- `1387-profile-attach-and-rollout-proof-page-target-cohort-adoption-mode-and-revision-safety-interface-spec.md`
- `1388-profile-drift-timeline-page-revision-bump-field-pin-freeze-branch-and-rejoin-events-interface-spec.md`
- `1389-profile-lineage-receipt-page-profile-signature-binding-class-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `our defaults profile` can no longer hide whether the product is talking about linked-device arrival posture, per-folder behavior, advanced defaults, config-authored replication, or a mobile-local share lane
- profile membership now has binding classes, so value coincidence can no longer impersonate live inheritance
- future profile revisions now publish which subjects will adopt them, which will stay pinned, which are frozen snapshots, and which belong to another branch or world
- batch profile rollout can no longer quietly bind unsupported worlds or erase intentional pins
- later operators can open one receipt and see what profile revision was in force, what field coverage actually existed, what class of binding was proven, what rollout happened or was blocked, and which stronger `on profile` sentence the product refused to make'''

scorecard_add = r'''## Revision addendum — policy-profile pack scorecard after rev0373

The new evaluated seam is **reusable policy profile / binding class / revision rollout / conformance truth**.

| Seam | Current Resilio posture | Borrow / clone / reject | Why | Required AnonSync pages |
| --- | --- | --- | --- | --- |
| Linked-device default modes, arrival roots, per-folder preferences, power-user defaults, config-authored multi-machine replication, mobile/share-local lanes, and migrated vs forked service worlds | Useful but too profile-implicit | **Adapt** | Current docs are admirably candid that reusable policy exists across linked-device defaults, global advanced defaults, per-folder lanes, config replication, and mobile-local routes — but the operator still has to reconstruct canonical profile identity, field coverage, binding class, revision adoption, and conformance state from separate UI and help surfaces | **Policy-profile contract sheet**, **Profile conformance review**, **Profile attach and rollout proof**, **Profile drift timeline**, **Profile lineage receipt** |

> borrow Resilio's candor that reusable policy can live across multiple settings lanes and worlds; refuse any product contract where `our profile`, `same defaults`, or `roll this out` still hides which canonical profile exists, which fields it actually covers, which subjects are live-bound, and which will adopt the next revision.'''

veto_add = r'''## Revision addendum — policy-profile clone veto after rev0373

### New veto seam

A sync product fails the clone test on this seam if it cannot answer, in one operator-facing review:

- what exact policy profile exists
- what exact fields it covers
- what worlds and subject classes it can legitimately govern
- what binding class the focused subject is in right now
- whether the next profile revision will really apply to this subject

### Required AnonSync page obligations

Any serious reusable-policy workflow must ship with:

1. a **policy-profile contract sheet** that names the profile, revision, field coverage, supported worlds, and focused binding class
2. a **profile conformance review** that separates live bindings, field pins, frozen snapshots, branched descendants, unbound lookalikes, and unsupported worlds
3. a **profile attach and rollout proof** that publishes target cohort, excluded cohort, adoption modes, activation plan, and blocked subjects before apply
4. a **profile drift timeline** that keeps revision publication, pinning, freezing, branching, rejoin, and retirement legible over time
5. a **profile lineage receipt** that records profile signature, revision, binding class, action taken or withheld, and blocked stronger sentence

### Explicit clone vetoes

Do not clone any contract where:

- `same current values` is allowed to stand in for `live profile binding`
- `defaults` is allowed to stand in for an explicit field-coverage list
- config/world forks are allowed to masquerade as one profile domain without explicit join
- rollout is allowed to say `apply to all` without publishing excluded, pinned, frozen, and blocked subjects
- profile membership is allowed to blur `live-inherit`, `field-pin`, `snapshot`, `branch`, and `unbound` into one generic `override` story'''

product_add = r'''## Revision addendum — product direction after rev0373: reusable defaults must become named policy profiles

This pass locks the next direction seam: **settings reuse must compile into named policy profiles instead of remaining archaeology across defaults, folders, config, and worlds**.
The key direction choices now added are:

- **AnonSync should model reusable defaults as first-class policy-profile objects with canonical ids, revisions, field coverage, supported subject classes, and supported world scope.**
- **Profile membership needs binding classes — `live-inherit`, `field-pin`, `frozen-snapshot`, `branched-profile`, and `unbound` are different product truths with different future consequences.**
- **Conformance is a reviewed object, not a side effect of visible value similarity.**
- **Profile rollout is compare-first and cohort-aware, so the product previews who will adopt the next revision, who will remain pinned, who is only a snapshot, and who is outside scope before any apply.**
- **A profile can never govern fields it does not explicitly list, and it can never silently govern worlds it does not explicitly support.**
- **Receipts must preserve profile id, revision, coverage, binding class, conformance grade, and blocked stronger sentence so later operators do not rebuild profile truth from memory.**

This sharpens the older counter-model line that `profiles install explicit policies, not hidden side effects`.
The archive now treats that sentence literally: the product needs one visible profile object, one conformance workspace, one rollout proof, one drift history, and one receipt family rather than a loose pile of defaults, toggles, and remembered exceptions.'''

sources_add = r'''## Revision addendum — official sources emphasized in rev0374

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about reusable policy, linked-device defaults, per-folder and global defaults, config-authored replication, mobile/share-local lanes, and successor-world forks.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `linked-device default mode`, `default arrival root`, `per-folder policy`, `global advanced default`, `mobile-local share setting`, `config-authored settings replication`, and `service migration vs clean-install fork` are different truths?

> where do those same current docs still show that the ordinary operator answer about `what named policy profile exists, what fields it covers, which subjects are bound to it, and what a revision rollout will actually change` depends on several articles instead of one stable product-owned workspace?

The most load-bearing source set for this pass was:

- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says linked devices make all folders automatically available across the linked family and lets each device choose a synchronization mode for new arrivals.
- Resilio's current `Synchronization Modes` article, which still points the device default to `Preferences -> Identity -> Default connect folder mode`.
- Resilio's current `Sync Preferences` article, which still describes default folder and file locations for new arrivals.
- Resilio's current `Folder Preferences` article, which still exposes per-folder policy such as Archive, overwrite-on-read-only, relay/tracker/LAN/predefined-host discovery, and file download priority.
- Resilio's current `Power user preferences` plus `File download priority` articles, which still show a global advanced default layer and still show manually altered shares detaching from later default changes.
- Resilio's current `Running Sync in configuration mode` article, which still says config mode helps apply the same settings on multiple machines, allows advanced preferences in `sync.conf`, limits config-authored shares to Standard folders, disables WebUI when shared folders are specified there, and lets non-default `storage_path` create another settings world.
- Resilio's current `Running Sync as a service on Windows` article, which still says service installation can migrate existing shares/settings or create a clean installation that requires re-sharing folders.
- Resilio's current `Settings on mobile platforms` and `Sync interface on Android` articles, which still show device-level and share-level advanced preferences as separate local routes.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that reusable policy is spread across real defaults, overrides, device-family lanes, config authorship, and world forks
- but current Resilio still answers `what profile governs this subject, and will the next revision apply here?` too diffusely
- AnonSync should therefore prefer explicit policy-profile sheets, conformance reviews, rollout-proof pages, drift timelines, and durable profile receipts over defaults folklore

Primary sources:

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Synchronization Modes  
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- Sync Preferences  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Folder Preferences  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- File download priority  
  https://help.resilio.com/hc/en-us/articles/42328167759251-File-download-priority

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Running Sync as a service on Windows  
  https://help.resilio.com/hc/en-us/articles/207701296-Running-Sync-as-a-service-on-Windows

- Settings on mobile platforms  
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- Sync interface on Android  
  https://help.resilio.com/hc/en-us/articles/213500383-Sync-interface-on-Android'''

prepend(root / 'README.md', readme_add)
prepend(docs / '00-status.md', status_add)
prepend(docs / '10-resilio-sync-evaluation.md', readme_add.replace('## Revision addendum — policy-profile pack, binding class, and conformance rollout after rev0373', '## Revision addendum — policy-profile pack, binding class, and conformance rollout after rev0373'))
prepend(docs / '11-resilio-borrow-line-and-non-clone-scorecard.md', scorecard_add)
prepend(docs / '12-resilio-interface-clone-veto-tests-and-page-obligations.md', veto_add)
prepend(docs / '20-product-direction.md', product_add)
prepend(docs / 'sources.md', sources_add)

