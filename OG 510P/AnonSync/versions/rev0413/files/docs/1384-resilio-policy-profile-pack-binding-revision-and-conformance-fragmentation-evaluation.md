# Resilio policy-profile pack, binding revision, and conformance fragmentation evaluation

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

Do not clone any settings contract where the operator can still ask `what named policy profile governs this subject, what revision is it on, and what exactly will the next profile change touch?` and the honest answer is still `it depends on which settings route, machine world, and remembered override history you manually reconstruct`.
