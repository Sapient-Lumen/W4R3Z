# Resilio setting-impact cohort, detached overrides, and inheritance-reset fragmentation evaluation

## Why this pass exists

The archive already had stronger doctrine for:

- finding the canonical setting object
- proving where it can be edited
- proving which surface wins
- proving when activation occurs

What it still lacked was one explicit answer to a second ordinary operator question:

> if I change this setting now, who exactly will change, who will stay detached, who is only parallel rather than governed by this route, and what does `None` or `default` actually mean here?

Current official Resilio material is again useful, but it still spreads the impact answer across several families:

- `Sync Preferences`
- `Folder Preferences`
- `Power user preferences`
- `File download priority`
- `Settings on mobile platforms`
- `Sync interface on Android`
- `Running Sync in configuration mode`
- `Running Sync as a service on Windows`
- `Resilio Sync change log`

## Current official Resilio evidence that matters here

Current official docs still show all of the following:

- `Sync Preferences` still places desktop-global settings such as rates, scheduler, and listening port at installation scope.
- `Folder Preferences` still places other settings at one selected share only, and still says this route is desktop-only.
- `Power user preferences` still exposes advanced defaults such as `folder_defaults.transfer_priority`.
- `File download priority` still says the same conceptual policy can be authored either per share or through the global power-user default.
- That same current priority article still says the global default applies to existing shares only if their priority was not altered manually, and to new shares as well.
- That same article also still says a share whose priority was manually set in Share Preferences is no longer affected by later power-user-default changes, even if the share was later manually set back to `None`.
- `Settings on mobile platforms` still says mobile has device-level settings of its own.
- `Sync interface on Android` still says each mobile share has its own details and advanced route, which means some same-looking concepts live in a separate local/share lane there.
- `Running Sync in configuration mode` still says advanced preferences can instead be authored in `sync.conf`, that config mode can author only Standard folders, and that storage path can move the settings world.
- `Running Sync as a service on Windows` still says service installation can either migrate existing settings/shares or create a clean installation that requires re-sharing folders, which means the governing subject cohort can fork by world choice.
- The current change log still shows convenience work such as search in power user settings and remembered share-dialog settings, but these are still local-surface improvements rather than one explicit impact planner.

So current Resilio still contains a real but scattered answer to:

> if I mutate this setting from this route, exactly what cohort changes, what stays detached, and what requires a different world or explicit reattach?

## What Resilio still gets right

### 1) It admits defaults and overrides are not the same thing

This is the strongest and most useful current evidence.
The priority docs plainly distinguish:

- no prioritization
- per-share manual setting
- global default
- future changes that do not reach manually detached shares

That candor is valuable.

### 2) It admits world choice changes the governed cohort

The service-install docs are unusually useful because they say migration and clean installation do not mean the same thing.
A migrated service preserves one continuity class.
A clean service world requires re-sharing and reconnecting.
That is real impact truth.

### 3) It admits config authorship is not the same lane as interactive mutation

Config mode again usefully shows that startup-authored config, storage-path change, and ordinary interactive edits are not one thing.
That matters for cohort reasoning.

## Where current Resilio still fragments the operator answer

### A) Impact is discoverable only by reconstructing several planes at once

To understand one future mutation, the operator may still have to combine:

- the route surface
- the scope class
- whether a share is inheriting or manually detached
- whether mobile is parallel rather than governed
- whether config or service owns a different world

That is too much reconstruction for one ordinary setting change.

### B) `None` and `inherit` still remain too easy to confuse

The current file-download-priority article is the most revealing example.
It says a share can be manually set and later manually set back to `None`, yet still remain outside later changes to the global default.
That means the ordinary label the operator sees is not enough to know whether the share is:

- inheriting
- explicitly set to no prioritization
- detached from future default changes

This is a very good reason not to clone the contract shape.

### C) Resilio still lacks one pre-commit impact proof

Current docs help explain where a setting lives.
They do not provide one product-owned view that answers:

- these 47 subjects will change
- these 8 are detached and will not change
- these 3 are in a parallel mobile lane
- these 2 belong to another service/config world
- these 5 require explicit reattach before a default shift can reach them

### D) Convenience search is not the same thing as cohort truth

`search in power user settings` is useful.
Remembered share-dialog state is useful.
But neither solves pre-commit blast radius, detached exceptions, or inherit-vs-explicit-none truth.

## Hard product decisions now locked for AnonSync

### 1) Every settings mutation must compile to an explicit target cohort before commit

No serious settings action may ship with only `Save` or `Apply to all`.
The product must say who will change and who will not.

### 2) `inherit` is a first-class state and may not be represented by the same control state as explicit `none/off`

If there is a meaningful difference between:

- inherit the current default
- explicitly set this subject to `none`

then the interface must expose those as different states.

### 3) Detached subjects must remain visible at the moment a default changes

Default-changing UI must publish the protected exception ledger, not bury it in later support archaeology.

### 4) Parallel worlds and parallel surfaces are never part of the cohort unless explicitly joined

Mobile-local, startup-owned, service-owned, and successor worlds are separate until proven joined.

### 5) Reattach is its own action

A subject that once detached from inheritance must not silently re-enter the default cohort because its visible value looks similar.

## Required page family

This seam now requires five AnonSync pages:

- **Setting-impact contract sheet**
- **Impact-cohort review**
- **Pre-commit impact proof**
- **Impact-drift timeline**
- **Impact-lineage receipt**

## New borrow line

Borrow Resilio's candor that global defaults, share overrides, mobile-local routes, startup-owned config, and service-world forks are materially different truths.

## New veto line

Do not clone any settings contract where the operator can still ask `who exactly will this change reach, who stays detached, and does this mean inherit or explicit none?` and the product's honest answer is still `it depends on which article and surface you remember to check`.