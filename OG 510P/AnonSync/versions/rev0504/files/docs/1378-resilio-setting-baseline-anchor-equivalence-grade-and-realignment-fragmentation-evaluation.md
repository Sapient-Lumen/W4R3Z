# Resilio setting-baseline anchor, equivalence grade, and realignment fragmentation evaluation

## Why this pass exists

The archive already had stronger doctrine for:

- finding the canonical setting object
- proving where it can be edited
- proving which cohort a mutation will touch
- proving when activation occurs

What it still lacked was one explicit answer to the next ordinary operator question:

> do these subjects actually match, or do they merely look similar right now because value, route label, local alias, or current world happen to line up?

Current official Resilio material is again useful, but it still spreads the answer across several families:

- `File download priority`
- `Power user preferences`
- `How do I perform a search in Sync?`
- `Resilio Sync change log`
- `Sync interface on Android`
- `Sync Interface on iOS devices`
- `Running Sync in configuration mode`
- `Running Sync as a service on Windows`
- `Setting custom name for sync shares`

## Current official Resilio evidence that matters here

Current official docs still show all of the following:

- `File download priority` still says a share can be configured in Share Preferences while a power-user default can also govern existing unchanged shares and new shares.
- That same priority article still says a share with manually set priority is no longer affected by later power-user-default changes, even if the priority was later manually set back to `None`.
- `Power user preferences` still says `folder_defaults.transfer_priority` is the default for shares whose priority was not altered manually in folder preferences.
- `Sync interface on Android` and `Sync Interface on iOS devices` still show per-share advanced preferences as their own route on each device, distinct from general settings.
- `Running Sync in configuration mode` still says config mode can set up only Standard folders, that a non-default `storage_path` creates settings in another storage location, and that shared folders specified in config override folders previously added from WebUI while disabling WebUI.
- `Running Sync as a service on Windows` still says service installation can either migrate existing shares/settings or create a clean installation that requires re-sharing and reconnecting folders.
- `Setting custom name for sync shares` still says a custom name is applied only in Sync UI, does not rename the folder on disk, does not propagate to other peers, and can remain in the UI after disconnect until reset.
- `How do I perform a search in Sync?` still describes UI search for folders, files, devices, and users, while the change log still calls out `search in power user settings` as a useful local improvement.

So current Resilio still contains a real but scattered answer to:

> are these two setting situations actually equivalent, what baseline are they being compared against, and what comparison result is merely a local false friend?

## What Resilio still gets right

### 1) It admits displayed value and governance lineage are not the same thing

The strongest current example remains `File download priority` plus `Power user preferences`.
A visible `None` is not enough to know whether the share:

- is inheriting the current default
- is explicitly set to no prioritization
- was manually detached from future default shifts

That candor is valuable.

### 2) It admits subject identity can differ from local presentation

`Setting custom name for sync shares` is unusually revealing here.
Resilio plainly says the custom name is only in Sync UI, does not rename the disk folder, does not propagate to other peers, and can survive disconnect until reset.
That is a strong reminder that local labels are not safe baseline anchors.

### 3) It admits world changes can invalidate comparison without changing the apparent control family

Config mode and service installation still show that storage root, startup-owned config, migrated service continuity, and clean-install service forks are not interchangeable worlds.
A setting may appear to be `the same kind of thing` while actually belonging to another authority world.

### 4) It keeps improving local findability

Resilio deserves credit for adding search in power user settings and exposing ordinary UI search for folders, files, devices, and users.
That is good locator work.

## Where current Resilio still fragments the operator answer

### A) Search is not equivalence

Current search help and change-log improvements help find strings and surfaces.
They do not provide one product-owned answer to whether two subjects are:

- merely showing the same visible value
- effectively the same right now
- governed by the same default / override lineage
- aligned to the same world and baseline

### B) Comparison still depends on reconstructing lineage from several articles

To compare two shares honestly, the operator may still need to reconstruct:

- whether the value comes from a global default or local override
- whether `None` is inherit or explicit none
- whether mobile per-share routes are parallel rather than shared authority
- whether config mode or service mode moved the governing world
- whether the displayed subject label is only a local alias

That is too much archaeology for one ordinary comparison task.

### C) Bulk alignment is still too easy to overclaim

Without a normalized comparison object, a bulk `make these match` action can silently blur together:

- `match the displayed value`
- `restore inheritance`
- `preserve explicit overrides`
- `apply only in this world`
- `rename / relabel the local subject only`

### D) Presentational sameness is too easy to confuse with subject sameness

The custom-name docs make this especially clear.
A local UI label can diverge from disk identity and peer-visible identity.
That means a baseline anchored only to the displayed share name is not reliable enough for serious settings work.

## Hard product decisions now locked for AnonSync

### 1) Every settings comparison must compile a normalized governance signature

Comparison may not rely on label plus visible value alone.
The signature must include at least:

- canonical setting id
- canonical subject id
- current world id
- value state
- inheritance / override state
- authority lane
- activation rung

### 2) Equality must have grades

The interface must distinguish at least:

- `same label only`
- `same visible value`
- `same effective value now`
- `same governance state`
- `same baseline conformance`

### 3) Baselines anchor to canonical ids, not local presentation

A local custom name, menu route, or imported alias can assist navigation but cannot be the anchor for parity claims.

### 4) Realignment is compare-first, mutate-second

The product must first show which subjects are already equivalent, which merely look similar, which would lose a local override, and which belong to another world before permitting batch alignment.

### 5) Restoring inheritance is a different action from matching the current displayed value

A subject that happens to show the same value as the baseline must not be treated as baseline-conformant unless its governance signature also matches.

## Required page family

This seam now requires five AnonSync pages:

- **Setting-baseline contract sheet**
- **Equivalence review**
- **Realignment proof**
- **Baseline-drift timeline**
- **Baseline-lineage receipt**

## New borrow line

Borrow Resilio's candor that visible value, manual override, local label, startup-owned config, and service-world continuity are materially different truths.

## New veto line

Do not clone any settings contract where the operator can still ask `do these actually match, and what baseline are you comparing against?` and the honest answer is still `it depends on which route, world, override history, and local alias you remember to inspect`.
