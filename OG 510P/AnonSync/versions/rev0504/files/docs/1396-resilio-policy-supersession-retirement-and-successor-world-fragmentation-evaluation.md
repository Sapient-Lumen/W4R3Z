# Resilio policy supersession, retirement, and successor-world fragmentation evaluation

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
- grandfathered temporarily
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

