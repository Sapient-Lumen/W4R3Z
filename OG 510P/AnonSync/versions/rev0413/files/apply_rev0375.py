from pathlib import Path
root = Path('/mnt/data/work0374')
docs = root / 'docs'

new_files = {
    '1390-resilio-policy-waiver-class-exception-expiry-and-applicability-fragmentation-evaluation.md': r'''# Resilio policy-waiver class, exception expiry, and applicability fragmentation evaluation

## Why this pass exists

The archive already had stronger doctrine for:

- locating canonical settings
- proving settings impact
- comparing settings to a baseline
- binding subjects to named policy profiles

What it still lacked was one explicit answer to the next ordinary operator question:

> this subject is not cleanly on profile — is that because the world is unsupported, the field is ignored here, the lane is local-only, a prerequisite is missing, or we intentionally waived it for now?

Current official Resilio material is again useful, but it still spreads that answer across several families:

- `Folder Preferences`
- `Power user preferences`
- `Settings on mobile platforms`
- `Sync interface on Android`
- `Running Sync in configuration mode`
- `Running Sync as a service on Windows`
- `Sync Service Troubleshooting on Windows`
- `Sync Private Identity & Linking My Devices`

## Current official Resilio evidence that matters here

Current official docs still show all of the following:

- `Folder Preferences` still says folder preferences are available on desktop platforms only.
- `Power user preferences` still says at least one advanced control (`disable_remove_from_all_devices`) is ignored in Linux WebUI.
- `Settings on mobile platforms` still shows a narrower device settings surface on mobile, while `Sync interface on Android` still exposes share-local advanced preferences as another route.
- `Settings on mobile platforms` still shows Android `Simple mode` as a lane that changes whether operators may choose a share location or pick an existing folder.
- `Running Sync in configuration mode` still says config mode is useful when you need to apply the same settings on a number of different machines, but also says only Standard folders can be set up there.
- The same config-mode doc still says advanced preferences can be added to `sync.conf`, that a non-default `storage_path` creates new settings there, and that specifying shared folders in config disables WebUI while overriding folders previously added from WebUI.
- `Running Sync as a service on Windows` still says service install may migrate existing shares/settings or may instead create a clean installation that requires re-sharing folders.
- `Sync Service Troubleshooting on Windows` still says changing service principal to `Local System` can widen path access while also creating a new service storage world with no prior folders present and requiring re-add / re-share.
- `Sync Private Identity & Linking My Devices` still says linked devices can automatically make folders available across the linked family, but it also says linking two already-running devices can replace one certificate and remove Advanced folders from the app on the device that takes over the new certificate.

So current Resilio still clearly admits real exception classes:

- unsupported surface
- ignored field
- local-parallel lane
- missing prerequisite
- config-authored applicability limit
- migrated successor world
- clean-install fork
- identity replacement side effect

But those classes do not yet become one first-class operator-facing **waiver / exception object**.

## What Resilio still gets right

### 1) It admits that unsupported and ignored are not the same thing

`Desktop only` is not the same as `ignored in Linux WebUI`.
That distinction matters because one describes absence of a route while the other describes presence of a route with weaker effect.

### 2) It admits local-parallel lanes exist

Android's device settings and per-share advanced preferences are not one surface.
`Simple mode` also changes what the operator is allowed to choose.
That is real applicability drift.

### 3) It admits world shifts can invalidate earlier assumptions

Config `storage_path`, config-authored shared folders, service migration, clean-install service forks, and service-principal changes all alter what settings world the operator is actually acting in.
That is exactly the kind of thing that should generate typed exceptions instead of hidden folklore.

### 4) It admits prerequisites and capability gaps are real

A profile-like rule might be legitimate in one lane while being unsupported, ignored, or locally constrained in another.
That is useful candor.

## Where current Resilio still fragments the operator answer

### A) Exception class is present, but not modeled as one typed object

An operator can piece together that a subject is out of line because it is:

- desktop-only
- ignored in Linux WebUI
- local-only on mobile
- blocked by Simple mode
- outside config-authored folder capability
- in a fresh service world
- in a successor identity/world after linking

But current docs do not give that divergence one canonical object with:

- typed class
- exact affected fields
- supported scope
- expiry or rereview time
- owner
- removal condition

### B) Unsupported, ignored, local-only, and not-yet-migrated are too easy to blur

Those are different truths:

- unsupported-world means the policy should not claim this world yet
- ignored-by-runtime means the field may appear but does not take effect here
- local-parallel lane means the subject may have a valid local control outside profile governance
- migration gap means continuity has not yet been re-established
- missing prerequisite means profile attachment is blocked but fixable

Current Resilio docs help expose these distinctions, but the product contract still does not own them in one place.

### C) Exceptions have no first-class expiry or rereview story

When a subject is out of profile because of lane limits, world fork, or migration gap, the operator still has to remember:

- whether this is temporary
- what event should retire the exception
- when it should be rereviewed
- whether rollout should block or proceed around it

That is too much memory burden for one ordinary fleet-governance question.

### D) Conformance counts can overclaim reality

Without a typed waiver object, it is too easy for `similar enough`, `mobile is special`, `service is separate`, or `Linux ignores that one` to dissolve into vague operator folklore instead of a durable contract.

### E) Rollout and exception handling remain separate stories

Config replication, service forks, mobile-local routes, and surface limitations all affect whether a profile revision should apply.
But current Resilio material still does not yield one stable answer to:

- who is excluded
- why they are excluded
- whether exclusion is temporary
- what must happen before they can rejoin profile conformance

## Hard product decisions now locked for AnonSync

### 1) Every material profile divergence must become either a typed waiver or a hard non-support verdict

The product may not leave serious divergence as a note in someone's head.

Supported waiver / exception classes must include at least:

- `unsupported-world`
- `unsupported-surface`
- `ignored-by-runtime`
- `local-parallel-lane`
- `missing-prerequisite`
- `migration-gap`
- `temporary-hold`
- `evidence-gap`
- `hard-out-of-policy`

### 2) Waivers are first-class governed objects

A waiver must have:

- canonical waiver id
- referenced profile id and revision
- affected subject set
- affected fields
- class
- owner
- issue time
- expiry / rereview time
- removal condition
- strongest safe sentence

### 3) Unsupported or ignored subjects must not count as conformant

`Looks similar` and `excluded for now` are weaker than `conforms`.
The product must keep those categories visible.

### 4) Every waiver expires unless explicitly justified otherwise

Open-ended exceptions are allowed only with a stronger owner, rationale, and rereview rule.
The default posture is timeboxed exception debt.

### 5) Rollout must be waiver-aware before commit

A profile rollout may not say `apply to cohort` without publishing:

- waived subjects
- blocked subjects
- unsupported worlds
- ignored fields
- local-parallel lanes
- migration gaps
- required rereview schedule

## Required page family

This seam now requires five AnonSync pages:

- **Policy-waiver contract sheet**
- **Waiver cohort review**
- **Waiver issuance proof**
- **Waiver drift timeline**
- **Waiver lineage receipt**

## New borrow line

Borrow Resilio's candor that desktop-only surfaces, ignored Linux WebUI fields, mobile-local share routes, config capability limits, service-world forks, and successor identity shifts are materially different truths.

## New veto line

Do not clone any settings contract where the operator can still ask `why is this subject not really on profile, is that temporary, and when can we safely remove the exception?` and the honest answer is still `it depends which article, surface, or migration story you remember`.
''',
    '1391-policy-waiver-contract-sheet-page-exception-scope-prerequisite-gap-and-expiry-interface-spec.md': r'''# Policy-waiver contract sheet page — exception scope, prerequisite gap, and expiry

## Purpose

This page answers the exception question that profile conformance alone does not finish:

> this subject is not cleanly on profile — what exact exception class explains that, what fields are affected, what must happen before the exception can end, and when must we review it again?

## Core decision

Every serious policy exception must render one first-class **Policy-waiver contract sheet** before the product allows silent exclusion, deferred rollout, or `special case` language.
The page owns:

- waiver identity
- profile reference
- exception class
- affected scope
- removal condition
- expiry / rereview
- strongest safe waiver sentence

## Fixed page order

1. waiver strip
2. profile-reference card
3. exception-class card
4. scope-and-field card
5. removal-condition card
6. conformance consequence card
7. waiver receipt

### 1) Waiver strip

Show:

- canonical waiver id
- linked profile id
- linked profile revision
- focused subject id
- focused world id
- waiver status: `proposed`, `active`, `expired`, `satisfied`, `rejected`, `unknown`
- top question being answered: `why is this subject not cleanly on profile?`

### 2) Profile-reference card

Show the exact profile context:

- profile id
- profile revision
- target cohort or subject
- intended binding class if the waiver did not exist
- currently blocked binding class
- witness confidence

## Hard rule

The page may not issue a waiver against a vague `defaults pack`.
It must anchor to one canonical profile id and revision first.

### 3) Exception-class card

Render exactly one top-line class:

- `unsupported-world`
- `unsupported-surface`
- `ignored-by-runtime`
- `local-parallel-lane`
- `missing-prerequisite`
- `migration-gap`
- `temporary-hold`
- `evidence-gap`
- `hard-out-of-policy`
- `unknown`

For the chosen class show:

- what is proven
- what is not proven
- whether the exception is expected to be temporary
- stronger sentence blocked

## Hard rule

`ignored-by-runtime` may never be collapsed into `unsupported-surface`.
A visible but ineffective control is a different truth from no supported control at all.

### 4) Scope-and-field card

List exactly what the waiver covers:

- affected subjects
- affected worlds
- affected fields
- unaffected fields that still conform
- whether value similarity exists despite the exception
- whether the exception blocks rollout, merely downgrades conformance, or both

## Hard rule

Anything not listed in scope is outside the waiver.
The page must not let one exception blur across neighboring fields or worlds.

### 5) Removal-condition card

Show what must happen before the waiver can end:

- prerequisite to satisfy
- migration step to complete
- surface/world join that must be proven
- evidence still missing
- review owner
- review schedule
- expiry time

If no expiry is set, the page must demand a stronger justification and owner class.

### 6) Conformance consequence card

Show how this waiver changes profile truth:

- `excluded from profile counts`
- `included but downgraded`
- `rollout blocked`
- `rollout proceeds around subject`
- `cannot bind until prerequisite met`
- `unknown until evidence collected`

Also show the exact stronger sentence the product refuses to make.

### 7) Waiver receipt

Emit one compact receipt with:

- waiver id
- profile id
- profile revision
- focused subject id
- exception class
- field count
- expiry / rereview
- removal condition headline
- strongest safe waiver sentence
- blocked stronger sentence

## Copy rules

- Never say `special case` without naming the exception class.
- Never say `temporary` without expiry or rereview.
- Never say `still on profile` if the waiver excludes the subject from conformance counts.
- Never say `unsupported here` when the truer sentence is `visible here but ignored`.
- Never say `just mobile behavior` when the real class is `local-parallel-lane`.

## Example strongest-safe sentence patterns

- `This subject is excluded by an active local-parallel-lane waiver: the profile governs desktop fields, while this mobile share keeps its own supported local route for the affected settings.`
- `This field is visible in Linux WebUI but currently treated as ignored-by-runtime, so profile conformance is blocked for that field until a stronger witness or product change exists.`
- `The subject is under a migration-gap waiver after service-world fork; profile attachment remains blocked until the successor world is explicitly re-bound.`
- `No waiver class has yet been proven; the product currently knows only that conformance evidence is incomplete.`
''',
    '1392-waiver-cohort-review-page-unsupported-worlds-ignored-fields-device-local-lanes-and-debt-class-interface-spec.md': r'''# Waiver cohort review page — unsupported worlds, ignored fields, device-local lanes, and debt class

## Purpose

This page answers the cohort exception question that one-subject waiver inspection does not finish:

> across all candidate subjects, who is cleanly conformant, who is excluded by a typed waiver, which waiver classes dominate the debt, and which exceptions are nearing expiry or safe retirement?

## Core decision

Every serious profile rollout or audit must render one first-class **Waiver cohort review**.
The page owns:

- exception counts
- debt classes
- expiry risk
- removable vs sticky exceptions
- safe next actions

## Fixed page order

1. waiver summary strip
2. debt-class ledger
3. cohort buckets
4. expiry-and-rereview queue
5. safe action tray
6. waiver cohort receipt

### 1) Waiver summary strip

Show:

- profile id
- active profile revision
- reviewed cohort id
- total subjects reviewed
- fully conformant subjects
- active-waiver subjects
- expired-waiver subjects
- hard-out-of-policy subjects
- unknown subjects

### 2) Debt-class ledger

Every non-clean subject must receive exactly one top-line debt class:

- `unsupported-world debt`
- `unsupported-surface debt`
- `ignored-runtime debt`
- `local-parallel debt`
- `missing-prerequisite debt`
- `migration-gap debt`
- `temporary-hold debt`
- `evidence-gap debt`
- `hard-out-of-policy debt`
- `unknown`

For each class show:

- count
- affected fields
- whether rollout is blocked
- whether expiry exists
- what stronger sentence remains blocked

## Hard rule

`expired waiver` may never be rendered in the same visual style as `active waiver`.
The product must make debt staleness obvious.

### 3) Cohort buckets

Group subjects into explicit buckets:

- cleanly conformant
- conformant except for active typed waiver
- blocked pending prerequisite
- blocked by migration gap
- allowed local-parallel exception
- unsupported-world exclusions
- expired exceptions requiring rereview
- hard out-of-policy subjects
- unknown or insufficient-witness subjects

For each bucket show:

- count
- representative reason
- next safe action

### 4) Expiry-and-rereview queue

Sort all active and expired waivers by operational urgency:

- already expired
- expires soon
- prerequisite now satisfied
- migration apparently complete but not rechecked
- still blocked with no owner
- durable justified exception

For each row show:

- waiver id
- owner
- days to expiry
- likely retirement trigger
- whether rollout is waiting on it

### 5) Safe action tray

Only actions compatible with the proven debt class may be offered:

- `renew waiver`
- `retire waiver`
- `collect missing evidence`
- `complete prerequisite`
- `rebind successor world`
- `convert to hard out-of-policy`
- `exclude from rollout`
- `roll forward around exception`

For each action show:

- whether conformance count changes
- whether rollout eligibility changes
- whether the action changes values, governance, or neither

### 6) Waiver cohort receipt

Emit one compact receipt with:

- profile id
- profile revision
- cohort id
- subject counts by debt class
- expired-waiver count
- near-expiry count
- offered safe actions
- strongest safe cohort sentence
- blocked stronger sentence

## Copy rules

- Never say `mostly conformant` without publishing typed waiver counts.
- Never hide expired waivers inside an `exceptions` subtotal.
- Never let unsupported worlds count as profile members.
- Never let active waivers impersonate permanent design decisions.
- Never let `mobile is different` stand in for a debt class.

## Example strongest-safe sentence patterns

- `Eighty-three subjects are cleanly conformant; twelve more are currently excluded by active typed waivers, most of them local-parallel mobile lanes and one migration-gap service fork.`
- `Five subjects remain blocked by missing prerequisites, so the next profile revision cannot yet be applied to them.`
- `Two Linux WebUI subjects currently show the field but remain classified as ignored-runtime debt rather than supported conformance.`
- `Three waivers are expired and now block any stronger claim that this cohort is governance-clean.`
''',
    '1393-waiver-issuance-proof-page-approve-timebox-recheck-and-rollout-blocking-interface-spec.md': r'''# Waiver issuance proof page — approve, timebox, recheck, and rollout blocking

## Purpose

This page answers the pre-approval question that a waiver summary alone does not finish:

> should this exception actually be granted, how long is it allowed to live, what condition retires it, and does rollout stop here or proceed around the subject?

## Core decision

Every serious exception grant, renewal, or conversion must render one first-class **Waiver issuance proof** before commit.
The page owns:

- grant basis
- timebox
- owner
- retirement trigger
- rollout consequence
- blocked stronger sentence

## Fixed page order

1. issuance strip
2. trigger-and-basis card
3. timebox-and-owner card
4. retirement-trigger card
5. rollout-consequence card
6. issuance receipt

### 1) Issuance strip

Show:

- waiver id or proposed waiver draft id
- profile id and revision
- target subject/cohort
- requested class
- requested duration
- requested owner
- top question being answered: `should this waiver exist at all?`

### 2) Trigger-and-basis card

Show why the waiver is being requested:

- observed divergence
- evidence supporting the divergence
- why ordinary conformance is blocked
- why simple exclusion is insufficient
- whether the divergence is expected, accidental, or still unknown

## Hard rule

A waiver may not be issued from a free-form note alone.
The page must show at least one explicit basis: unsupported world, ignored runtime, local lane, missing prerequisite, migration gap, temporary hold, or evidence gap.

### 3) Timebox-and-owner card

Require:

- explicit owner
- issue time
- expiry or next rereview
- renewal policy
- maximum allowed age under current risk class

## Hard rule

No waiver without an owner.
No indefinite waiver without stronger approval class and rationale.

### 4) Retirement-trigger card

Show the exact event that would let the waiver end:

- prerequisite fulfilled
- migration complete
- world rejoined
- stronger evidence collected
- product support widened
- policy changed
- explicit decision to mark hard out-of-policy

Also show what verification step must happen before retirement is accepted.

### 5) Rollout-consequence card

Show the effect on the pending change:

- `rollout blocked`
- `rollout proceeds around waived subject`
- `rollout allowed for unaffected fields only`
- `rollout postponed pending rereview`
- `no rollout in scope`

For each outcome show:

- value changes allowed
- governance changes allowed
- follow-up review duty

### 6) Issuance receipt

Emit one compact receipt with:

- waiver id
- profile id
- profile revision
- subject/cohort id
- exception class
- owner
- expiry / rereview
- rollout consequence
- strongest safe issuance sentence
- blocked stronger sentence

## Copy rules

- Never say `approved for now` without a timebox.
- Never say `we'll remember` instead of naming owner and rereview.
- Never say `doesn't matter for rollout` without publishing whether values, governance, or both are excluded.
- Never issue a waiver just because the current values happen to match.
- Never let `unsupported` and `temporarily postponed` share the same approval language.

## Example strongest-safe sentence patterns

- `The requested waiver is approved as a 30-day migration-gap exception owned by the service cutover operator; rollout proceeds around the successor world until rebind proof is completed.`
- `This exception is granted only for the ignored-runtime field and does not excuse the rest of the profile from conformance review.`
- `The waiver is denied because the divergence is actually hard out-of-policy rather than temporarily blocked by a prerequisite.`
- `The product cannot approve this waiver yet because the evidence only proves a mismatch, not the correct exception class.`
''',
    '1394-waiver-drift-timeline-page-prerequisite-met-expiry-renewal-and-unplanned-coverage-loss-interface-spec.md': r'''# Waiver drift timeline page — prerequisite met, expiry, renewal, and unplanned coverage loss

## Purpose

This page answers the history question that active waiver state alone does not finish:

> how did this exception arise, when should it have ended, what changed while it stayed open, and did the profile silently lose or regain coverage over time?

## Core decision

Every serious exception family must render one first-class **Waiver drift timeline**.
The page owns:

- origin event
- renewal history
- expiry history
- retirement attempts
- unplanned coverage loss
- blocked stronger sentence over time

## Fixed page order

1. timeline summary strip
2. origin event ledger
3. waiver-life event ledger
4. coverage-loss and recovery ledger
5. current debt posture card
6. timeline receipt

### 1) Timeline summary strip

Show:

- waiver id
- profile id
- affected subject/cohort
- issue date
- current age
- current status
- total renewals
- total missed rereviews
- top question being answered: `how did this waiver evolve?`

### 2) Origin event ledger

Record the event that first caused the exception, such as:

- subject entered unsupported world
- field discovered ignored by runtime
- mobile-local lane took over
- prerequisite became missing
- config/service world fork occurred
- successor identity replaced prior world
- profile scope changed and exposed the gap

### 3) Waiver-life event ledger

Record every governance event:

- waiver proposed
- waiver approved
- waiver renewed
- waiver expired
- waiver rereviewed
- waiver denied
- waiver satisfied
- waiver converted to hard out-of-policy

For each event show:

- who acted
- what evidence existed
- what stronger sentence remained blocked afterward

### 4) Coverage-loss and recovery ledger

Keep profile-coverage changes visibly separate from waiver paperwork:

- product support widened
- support narrowed
- field moved surfaces
- migration completed
- local-only lane retired
- stronger evidence proved effect
- previous assumption collapsed

### 5) Current debt posture card

Summarize the present state:

- active or expired
- oldest unresolved blocker
- next required action
- whether rollout remains blocked
- whether the waiver now looks stale, justified, or misclassified

### 6) Timeline receipt

Emit one compact receipt with:

- waiver id
- profile id
- subject/cohort id
- age
- renewal count
- missed-rereview count
- current posture
- strongest safe timeline sentence
- blocked stronger sentence

## Copy rules

- Never let renewal history disappear once the waiver is retired.
- Never treat expiry as a no-op.
- Never let product-support changes masquerade as operator review.
- Never say `still exceptional` without showing how long and why.
- Never let coverage regain count as automatic conformance without recheck.

## Example strongest-safe sentence patterns

- `This waiver began as a migration-gap exception during service cutover, expired once without rereview, and remains active only because successor-world rebind proof is still missing.`
- `The ignored-runtime exception is now likely stale because the supporting product limitation was removed two revisions ago but no recheck has been recorded.`
- `Profile coverage narrowed after the subject moved into an unsupported world; the waiver now reflects a scope change rather than a temporary hold.`
- `The subject regained eligibility after the prerequisite was met, but conformance is still unproven until retirement review completes.`
''',
    '1395-waiver-lineage-receipt-page-profile-gap-expiry-review-duty-and-blocked-stronger-sentences-interface-spec.md': r'''# Waiver lineage receipt page — profile gap, expiry, review duty, and blocked stronger sentences

## Purpose

This page provides the smallest durable artifact that later operators can read without reconstructing exception history from memory.

## Core decision

Every serious profile exception must end with one durable **Waiver lineage receipt**.
The receipt preserves:

- what profile was involved
- what subject or cohort diverged
- why the divergence was classified the way it was
- how long the exception is allowed to live
- who must review it
- what stronger claim remained blocked

## Fixed page order

1. receipt strip
2. profile-gap block
3. expiry-and-owner block
4. rollout consequence block
5. blocked-claim block

### 1) Receipt strip

Show:

- waiver id
- profile id
- profile revision
- subject/cohort id
- issue timestamp
- current status

### 2) Profile-gap block

Show:

- exception class
- affected fields
- affected worlds
- intended clean binding class
- currently blocked binding or conformance state
- strongest safe sentence

### 3) Expiry-and-owner block

Show:

- owner
- expiry or rereview timestamp
- renewal posture
- removal condition
- next verification step

### 4) Rollout consequence block

Show:

- blocked / proceed-around / partial-field / no-rollout verdict
- whether values changed
- whether governance changed
- whether conformance counts included or excluded the subject

### 5) Blocked-claim block

State the stronger sentence the product refused to make, for example:

- `This subject conforms to profile rev14.`
- `This rollout covers the full cohort.`
- `This field is supported and effective in Linux WebUI.`
- `This mobile share is governed by the desktop profile without local exceptions.`

## Copy rules

- Never emit a waiver receipt without expiry or stronger justification for no expiry.
- Never hide owner identity.
- Never record only the symptom; record the typed class.
- Never omit whether the subject counted as conformant.
- Never omit the blocked stronger sentence.

## Example strongest-safe sentence patterns

- `Waiver W-204 remains active as an ignored-runtime exception for one field on Linux WebUI; the subject is excluded from clean conformance counts until rereview on 2026-05-01.`
- `Waiver W-311 is a local-parallel mobile-lane exception covering two share-local fields; rollout of the desktop profile proceeds around this subject with no governance claim for the excluded fields.`
- `Waiver W-412 has expired; no stronger cohort-wide conformance sentence may be issued until rereview is completed or the exception is retired.`
''',
}

prepend_map = {
    root / 'README.md': r'''## Revision addendum — policy-waiver pack, exception class, and expiry review after rev0374

This revision continues directly from `rev0374` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **desktop-only folder preferences, Linux-WebUI-ignored advanced settings, mobile device settings versus Android share-local advanced preferences, Android Simple-mode capability limits, config-mode replication for the same settings on multiple machines, config-only Standard-folder limits, config-authored WebUI suppression and folder override, storage-path world forks, service migration vs clean-install forks, and service-principal world changes**.
2. Tightens the non-clone line again: borrow Resilio's candor that `supported world`, `supported surface`, `ignored field`, `local-parallel lane`, `missing prerequisite`, `migration gap`, `clean-install fork`, and `temporary waiver` are different truths; refuse any contract where the operator still has to reconstruct `why isn't this subject really on profile, is that temporary, and when can the exception be removed?` from several surfaces and articles.
3. Adds one new **Resilio evaluation** document focused on why present-day policy-waiver and applicability reasoning are still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for a policy-waiver contract sheet, waiver cohort review, waiver issuance proof, waiver drift timeline, and waiver lineage receipt.
5. Makes one hard product decision explicit: **every material profile divergence must become either a typed waiver object or a hard non-support verdict.**
6. Makes another hard product decision explicit: **`unsupported-world`, `unsupported-surface`, `ignored-by-runtime`, `local-parallel-lane`, `missing-prerequisite`, `migration-gap`, and `hard-out-of-policy` are different truths and must not collapse into one generic `exception`.**
7. Makes a third hard product decision explicit: **waivers expire by default, open-ended exceptions need stronger approval and ownership, and waived subjects do not count as clean conformance.**
8. Packages the result as another continuation archive whose new tranche makes the `policy-waiver / debt-class / expiry-review / rollout-blocking / waiver-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1390-resilio-policy-waiver-class-exception-expiry-and-applicability-fragmentation-evaluation.md`
- `1391-policy-waiver-contract-sheet-page-exception-scope-prerequisite-gap-and-expiry-interface-spec.md`
- `1392-waiver-cohort-review-page-unsupported-worlds-ignored-fields-device-local-lanes-and-debt-class-interface-spec.md`
- `1393-waiver-issuance-proof-page-approve-timebox-recheck-and-rollout-blocking-interface-spec.md`
- `1394-waiver-drift-timeline-page-prerequisite-met-expiry-renewal-and-unplanned-coverage-loss-interface-spec.md`
- `1395-waiver-lineage-receipt-page-profile-gap-expiry-review-duty-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's profile-exception contract**

This time the reason is especially clear around **desktop-only preference surfaces, Linux-WebUI ignored advanced fields, Android share-local advanced lanes, Simple-mode capability limits, config-only Standard-folder scope, WebUI suppression by config-authored shares, storage/world forks, and service migration vs clean-install gaps**.
Current official materials simultaneously show that:

- current `Folder Preferences` docs still say per-folder preferences are desktop-only
- current `Power user preferences` docs still say at least one advanced field is ignored in Linux WebUI
- current `Settings on mobile platforms` and `Sync interface on Android` docs still keep device settings and per-share advanced preferences on separate local routes, while Android `Simple mode` still changes whether a share location can be chosen manually
- current `Running Sync in configuration mode` docs still say config mode is useful for applying the same settings on multiple machines, still limit config-authored shares to Standard folders, still allow advanced preferences in `sync.conf`, still let non-default `storage_path` create a new settings world, and still disable WebUI plus override previously WebUI-added folders when shared folders are declared in config
- current `Running Sync as a service on Windows` and `Sync Service Troubleshooting on Windows` docs still say service install can migrate existing settings or create a clean-install fork, and still say principal changes such as `Local System` can widen access while creating another service storage world that requires re-add / re-share
- current `Sync Private Identity & Linking My Devices` docs still say linking already-running devices can replace one certificate and remove Advanced folders from the app on the device that takes over the new certificate

That candor is useful.
The waiver contract is the problem.
AnonSync should not clone a world where the operator still has to translate `desktop-only`, `ignored in Linux WebUI`, `mobile local`, `Simple mode`, `config replica`, `clean install`, `service fork`, and `identity replacement` into one stable answer about exception class, affected fields, expiry, owner, removal condition, rollout consequence, and blocked stronger sentence by stitching together several KB articles.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because profile exceptions are a real contract with separate truths for exception class, applicability scope, removal condition, expiry, owner, and rollout consequence — but the present contract still scatters the answer to `why isn't this subject really on profile, is that temporary, and when can the exception be removed?` across several KB articles instead of owning it as one stable page family.**

''',
    docs / '00-status.md': r'''## Revision addendum — policy-waiver pack, exception class, and expiry review after rev0374

This pass locks the next seam after named policy profiles: **typed policy waivers and exception debt**.
The archive already knew how to name a profile and compare conformance.
What it still lacked was one explicit product answer to:

> this subject is not cleanly on profile — is that unsupported, ignored, local-only, mid-migration, or intentionally waived, and when must we revisit that judgment?

This revision adds that answer.
It contributes:

- one new **Resilio evaluation** focused on policy-waiver, applicability, and expiry fragmentation
- five new **interface specs** for waiver contract sheet, waiver cohort review, waiver issuance proof, waiver drift timeline, and waiver lineage receipt
- a tighter non-clone line based on current official Resilio evidence about desktop-only surfaces, Linux-WebUI ignored advanced fields, mobile share-local routes, Android Simple-mode capability limits, config-only Standard-folder scope, config-authored WebUI suppression, storage/world forks, service migration vs clean-install forks, and identity replacement side effects
- three hard product decisions:
  - **every material profile divergence becomes either a typed waiver or a hard non-support verdict**
  - **waiver classes stay explicit — unsupported world, unsupported surface, ignored runtime, local-parallel lane, missing prerequisite, migration gap, and hard out-of-policy are not one thing**
  - **waivers expire by default, require owners and removal conditions, and do not count as clean conformance**

New docs in this tranche:

- `1390-resilio-policy-waiver-class-exception-expiry-and-applicability-fragmentation-evaluation.md`
- `1391-policy-waiver-contract-sheet-page-exception-scope-prerequisite-gap-and-expiry-interface-spec.md`
- `1392-waiver-cohort-review-page-unsupported-worlds-ignored-fields-device-local-lanes-and-debt-class-interface-spec.md`
- `1393-waiver-issuance-proof-page-approve-timebox-recheck-and-rollout-blocking-interface-spec.md`
- `1394-waiver-drift-timeline-page-prerequisite-met-expiry-renewal-and-unplanned-coverage-loss-interface-spec.md`
- `1395-waiver-lineage-receipt-page-profile-gap-expiry-review-duty-and-blocked-stronger-sentences-interface-spec.md`

## Current status

The archive now has a clearer and tighter settings-governance staircase:

- find the canonical setting
- prove who a change touches
- compare subjects to a baseline
- bind subjects to named profiles
- explain why nonconforming subjects are excluded, degraded, blocked, or timeboxed

That last rung is what this revision adds.
It means later operators no longer need to remember whether a nonconforming subject was `really unsupported`, `temporarily waived`, `ignored by runtime`, `local-only`, or just never rechecked after a fork.
The receipt family now carries that burden directly.

''',
    docs / '10-resilio-sync-evaluation.md': r'''## Revision addendum — policy-waiver pack, exception class, and expiry review after rev0374

This revision continues directly from `rev0374` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **desktop-only folder preferences, Linux-WebUI-ignored advanced settings, mobile device settings versus Android share-local advanced preferences, Android Simple-mode capability limits, config-mode replication for the same settings on multiple machines, config-only Standard-folder limits, config-authored WebUI suppression and folder override, storage-path world forks, service migration vs clean-install forks, and service-principal world changes**.
2. Tightens the non-clone line again: borrow Resilio's candor that `supported world`, `supported surface`, `ignored field`, `local-parallel lane`, `missing prerequisite`, `migration gap`, `clean-install fork`, and `temporary waiver` are different truths; refuse any contract where the operator still has to reconstruct `why isn't this subject really on profile, is that temporary, and when can the exception be removed?` from several surfaces and articles.
3. Adds one new **Resilio evaluation** document focused on why present-day policy-waiver and applicability reasoning are still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for a policy-waiver contract sheet, waiver cohort review, waiver issuance proof, waiver drift timeline, and waiver lineage receipt.
5. Makes one hard product decision explicit: **every material profile divergence must become either a typed waiver object or a hard non-support verdict.**
6. Makes another hard product decision explicit: **`unsupported-world`, `unsupported-surface`, `ignored-by-runtime`, `local-parallel-lane`, `missing-prerequisite`, `migration-gap`, and `hard-out-of-policy` are different truths and must not collapse into one generic `exception`.**
7. Makes a third hard product decision explicit: **waivers expire by default, open-ended exceptions need stronger approval and ownership, and waived subjects do not count as clean conformance.**
8. Packages the result as another continuation archive whose new tranche makes the `policy-waiver / debt-class / expiry-review / rollout-blocking / waiver-receipt` seam explicit in the reading order and page family.

### Why this pass matters

The previous tranche answered `what named profile exists and who is live-bound to it?`
This tranche answers the next harder question:

> `when a subject is not cleanly on profile, what exact class of exception explains that, is it temporary, and what must happen before we can safely remove it?`

Current official Resilio material is useful here precisely because it is candid about distinctions, but still too scattered for a clone.
The clearest current cluster is:

- some preference surfaces are desktop-only
- some advanced settings are visible but ignored in Linux WebUI
- mobile keeps device settings and share-local advanced preferences on separate local routes
- Android Simple mode changes whether manual landing/location choice is even available
- config mode can replicate settings across machines but only for Standard folders, can create another settings world, and can disable WebUI while replacing its folder roster
- service install can preserve continuity by migration or create a clean-install fork
- service principal changes can widen access while still moving the subject into another storage world
- linking already-running devices can replace one certificate and invalidate parts of the old advanced-folder picture

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's policy-exception contract**

This time the reason is especially clear around **applicability limits, ignored fields, local-parallel lanes, missing prerequisites, world forks, and successor gaps**.
Current official materials simultaneously show that:

- current `Folder Preferences` docs still say per-folder preferences are desktop-only
- current `Power user preferences` docs still say at least one advanced field is ignored in Linux WebUI
- current `Settings on mobile platforms` and `Sync interface on Android` docs still keep device settings and per-share advanced preferences on separate local routes, while Android `Simple mode` still changes whether a share location can be chosen manually
- current `Running Sync in configuration mode` docs still say config mode is useful for applying the same settings on multiple machines, still limit config-authored shares to Standard folders, still allow advanced preferences in `sync.conf`, still let non-default `storage_path` create a new settings world, and still disable WebUI plus override previously WebUI-added folders when shared folders are declared in config
- current `Running Sync as a service on Windows` and `Sync Service Troubleshooting on Windows` docs still say service install can migrate existing settings or create a clean-install fork, and still say principal changes such as `Local System` can widen access while creating another service storage world that requires re-add / re-share
- current `Sync Private Identity & Linking My Devices` docs still say linking already-running devices can replace one certificate and remove Advanced folders from the app on the device that takes over the new certificate

That candor is useful.
The waiver contract is the problem.
AnonSync should not clone a world where the operator still has to translate `desktop-only`, `ignored in Linux WebUI`, `mobile local`, `Simple mode`, `config replica`, `clean install`, `service fork`, and `identity replacement` into one stable answer about exception class, affected fields, expiry, owner, removal condition, rollout consequence, and blocked stronger sentence by stitching together several KB articles.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because profile exceptions are a real contract with separate truths for exception class, applicability scope, removal condition, expiry, owner, and rollout consequence — but the present contract still scatters the answer to `why isn't this subject really on profile, is that temporary, and when can the exception be removed?` across several KB articles instead of owning it as one stable page family.**

''',
    docs / '11-resilio-borrow-line-and-non-clone-scorecard.md': r'''## Revision addendum — policy-waiver scorecard after rev0374

The new evaluated seam is **profile exception / waiver class / expiry review / applicability debt**.

| Seam | Current Resilio posture | Borrow / clone / reject | Why | Required AnonSync pages |
| --- | --- | --- | --- | --- |
| Desktop-only folder preferences, Linux-WebUI ignored advanced fields, mobile share-local advanced lanes, Android Simple-mode capability limits, config-only Standard-folder scope, config-authored WebUI suppression, storage/world forks, service migration vs clean-install gaps, and identity replacement side effects | Useful but too exception-implicit | **Adapt** | Current docs are admirably candid that `unsupported surface`, `ignored field`, `local-parallel lane`, `missing prerequisite`, `migration gap`, and `successor world fork` are materially different realities — but the operator still has to reconstruct typed exception class, affected scope, expiry, owner, removal condition, and rollout consequence from separate UI and help surfaces | **Policy-waiver contract sheet**, **Waiver cohort review**, **Waiver issuance proof**, **Waiver drift timeline**, **Waiver lineage receipt** |

> borrow Resilio's candor that unsupported, ignored, local-only, mid-migration, and successor-gap situations are not the same thing; refuse any product contract where `special case`, `not supported here`, or `we'll handle this later` still hides typed exception class, expiry, review duty, and whether the subject actually counts as conformant.

''',
    docs / '12-resilio-interface-clone-veto-tests-and-page-obligations.md': r'''## Revision addendum — clone-veto obligations for policy waivers, applicability debt, and expiry review after rev0374

### New veto seam

A sync product fails the clone test on this seam if it cannot answer, in one operator-facing review:

- why a subject is not cleanly on profile
- whether the issue is unsupported, ignored, local-parallel, missing-prerequisite, mid-migration, or hard out-of-policy
- what exact fields and worlds the exception touches
- when the exception expires or must be rereviewed
- whether rollout blocks, proceeds around the subject, or applies only to unaffected fields

### Required AnonSync page obligations

Any serious profile-governance workflow must ship with:

1. a **policy-waiver contract sheet** that names the profile, subject, exception class, affected fields, removal condition, and expiry
2. a **waiver cohort review** that separates clean conformance from active waivers, expired waivers, unsupported worlds, ignored-runtime fields, local-parallel lanes, and hard out-of-policy subjects
3. a **waiver issuance proof** that requires owner, timebox, retirement trigger, and explicit rollout consequence before approval or renewal
4. a **waiver drift timeline** that preserves origin event, renewal history, missed rereviews, coverage changes, and retirement attempts over time
5. a **waiver lineage receipt** that records typed class, expiry, review duty, rollout consequence, and blocked stronger sentence

### Explicit clone vetoes

Do not clone any contract where:

- `special case` is allowed to stand in for a typed waiver class
- `temporary` is allowed to stand in for an actual expiry or rereview time
- unsupported worlds are allowed to count as conformant profile members
- `ignored here` and `not supported here` are allowed to blur together
- rollout is allowed to say `apply to cohort` without publishing waived, blocked, expired, or out-of-policy subjects
- expired waivers are allowed to keep masquerading as healthy exceptions
- open-ended exceptions are allowed without stronger ownership and rationale

''',
    docs / '20-product-direction.md': r'''## Revision addendum — product direction after rev0374: named policy profiles require typed waivers with expiry

This pass locks the next direction seam: **profile governance must own typed exception debt instead of treating nonconformance as folklore**.
The key direction choices now added are:

- **AnonSync should model every material profile divergence as either a typed waiver object or a hard non-support verdict.**
- **Unsupported world, unsupported surface, ignored runtime, local-parallel lane, missing prerequisite, migration gap, temporary hold, evidence gap, and hard out-of-policy are different product truths.**
- **Waived subjects are weaker than conformant subjects, and expired waivers are weaker than active approved waivers.**
- **Waivers expire by default, require owners and removal conditions, and demand rereview rather than silent survival.**
- **Rollout must be waiver-aware before commit, so excluded, blocked, partial-field, and proceed-around outcomes are explicit rather than implied.**
- **Receipts must preserve typed class, affected scope, expiry, owner, removal condition, rollout consequence, and blocked stronger sentence so later operators do not rebuild exception truth from memory.**

This sharpens the older counter-model line that `profiles install explicit policies, not hidden side effects`.
The archive now treats the other half of that sentence literally too: explicit policy requires explicit exception objects.
The product therefore needs one waiver sheet, one cohort debt review, one issuance proof, one drift history, and one durable receipt family rather than a loose pile of remembered caveats.

''',
    docs / 'sources.md': r'''## Revision addendum — official sources emphasized in rev0375

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about unsupported surfaces, ignored fields, local-parallel lanes, applicability limits, world forks, successor gaps, and temporary exception debt.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `desktop-only`, `ignored in Linux WebUI`, `mobile share-local`, `Simple mode capability limit`, `config-only Standard-folder scope`, `config-authored WebUI suppression`, `service clean-install fork`, and `identity replacement` are different truths?

> where do those same current docs still show that the ordinary operator answer about `why isn't this subject really on profile, is that temporary, and when can the exception be removed?` depends on several articles instead of one stable product-owned waiver workspace?

The most load-bearing source set for this pass was:

- Resilio's current `Folder Preferences` article, which still says folder preferences are available on desktop platforms only.
- Resilio's current `Power user preferences` article, which still says `disable_remove_from_all_devices` is ignored in Linux WebUI.
- Resilio's current `Settings on mobile platforms` article, which still distinguishes device-level settings from mobile-local advanced routes and still says Android `Simple mode` changes whether new shares are simply placed in the default directory.
- Resilio's current `Sync interface on Android` article, which still exposes `Advanced-Preferences` as per-folder settings on the share details surface.
- Resilio's current `Running Sync in configuration mode` article, which still says config mode helps apply the same settings on multiple machines, allows advanced preferences in `sync.conf`, limits config-authored shares to Standard folders, lets non-default `storage_path` create another settings world, and disables WebUI while overriding folders previously added from WebUI when shared folders are declared in config.
- Resilio's current `Running Sync as a service on Windows` article, which still says service install can migrate existing shares/settings or create a clean installation that requires re-sharing folders.
- Resilio's current `Sync Service Troubleshooting on Windows` article, which still says changing the service principal to `Local System` can widen access while creating another service storage world with no previous folders present and requiring re-add / re-share.
- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says linking already-running devices can replace one certificate and remove Advanced folders from the app on the device that takes over the new certificate.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that unsupported, ignored, local-only, and successor-gap situations are materially different
- but current Resilio still answers `why is this subject not really on profile, is that temporary, and when can we retire the exception?` too diffusely
- AnonSync should therefore prefer explicit waiver sheets, cohort debt reviews, issuance-proof pages, drift timelines, and durable waiver receipts over exception folklore

Primary sources:

- Folder Preferences  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Settings on mobile platforms  
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- Sync interface on Android  
  https://help.resilio.com/hc/en-us/articles/213500383-Sync-interface-on-Android

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Running Sync as a service on Windows  
  https://help.resilio.com/hc/en-us/articles/207701296-Running-Sync-as-a-service-on-Windows

- Sync Service Troubleshooting on Windows  
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

''',
}

for name, content in new_files.items():
    (docs / name).write_text(content.rstrip() + '\n', encoding='utf-8')

for path, add in prepend_map.items():
    original = path.read_text(encoding='utf-8')
    path.write_text(add.rstrip() + '\n\n' + original, encoding='utf-8')
