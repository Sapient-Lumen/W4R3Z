# Resilio policy-waiver class, exception expiry, and applicability fragmentation evaluation

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
