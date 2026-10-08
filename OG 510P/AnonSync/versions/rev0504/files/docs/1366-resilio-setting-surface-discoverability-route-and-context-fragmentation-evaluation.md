# Resilio setting-surface discoverability, route locality, and context fragmentation evaluation

## Why this pass exists

The archive already had stronger doctrine for governance planes, action surfaces, activation boundaries, policy authorship, and witness locality.
What it still lacked was one direct current Resilio evaluation for a narrower but still important question:

> where do I actually go to change this setting, on what surface does that change belong, what scope will it govern, and what stronger sentence is still blocked because this surface is only a witness or only one route among several?

Current official Resilio docs still show a useful, living product, but they also still show that one ordinary answer is spread across several article families at once:

- `Sync Main View (Desktop)`
- `Sync Preferences`
- `Folder Preferences`
- `Power user preferences`
- `File download priority`
- `Settings on mobile platforms`
- `Sync interface on Android`
- `Running Sync in configuration mode`
- `Running Sync as a service on Windows`
- `Updating Sync to latest version`
- `Resilio Sync change log`

## Current official Resilio evidence that matters here

Current official docs still say all of the following:

- `Sync Main View (Desktop)` still says the desktop shell has its own filter/search/column controls, routes to Sync Preferences and Folder Preferences, and exposes share-specific actions through a row menu.
- `Sync Preferences` still says desktop global settings include update checks, startup behavior, notifications, default paths, bandwidth limits, scheduler, listening port, UPnP, proxy, debug logging, and a jump into Power user preferences.
- `Folder Preferences` still says per-folder options are a separate desktop-only surface with archive, overwrite, relay, tracker, LAN search, predefined hosts, and file download priority.
- `Power user preferences` still says there is a distinct advanced surface whose entries include lower-level settings and whose article still carries activation notes such as restart requirements for some items.
- `File download priority` still says the same conceptual setting can be authored in share preferences or via the global power-user default, with share-level manual choice surviving later global changes.
- The current change log still says search was added in power user settings, which is a useful move but still only improves one sub-surface.
- `Settings on mobile platforms` still says Android settings separately expose identity, general, network, notifications, advanced, and support.
- `Sync interface on Android` still says each share has its own details and advanced preferences route with force rescan, Archive, overwrite, relay, tracker, LAN search, predefined hosts, and allowed network.
- `Running Sync in configuration mode` still says many parameters, including advanced preferences, can instead be authored in `sync.conf`, and that config mode on service has its own route.
- `Running Sync as a service on Windows` still says service-mode `sync.conf` belongs in the service storage folder and that a restart is needed.
- `Updating Sync to latest version` still says `Check now` is available in general settings but not in WebUI.

So current Resilio still contains a real but scattered answer to `where does this setting live, who owns it, and what surface can actually change it?`

## What Resilio still gets right

### 1) It is candid that route and scope are not one thing

The docs do not pretend every setting belongs to one universal preferences page.
They openly distinguish desktop-global, desktop-per-folder, power-user, mobile-global, mobile-per-share, config-mode, and service-specific routes.
That honesty is valuable.

### 2) It is candid that the same concept can have more than one authorship lane

The current file-download-priority docs openly distinguish a global default from a manual share override.
Config-mode docs openly distinguish startup-authored config from interactive UI mutation.
That matters.

### 3) It is candid that some surfaces are weaker or missing

Current docs still say some things are desktop-only, some are mobile-only, some are WebUI-missing, and some belong to service storage plus restart.
That is exactly the kind of operational truth worth borrowing.

## Why this is still a good reason not to clone them

### 1) Current docs still make one ordinary settings answer too archaeological

An operator still has to merge multiple articles to answer:

- is this a global setting, a per-share setting, a power-user default, a mobile setting, or a startup-config value?
- can I change it on this current surface, or can I only observe it from here?
- if I edit it in one route, does that replace a broader default, merely override it, or do nothing until startup or restart?

AnonSync should not inherit a contract where `Preferences`, `Advanced`, `Folder Preferences`, `Settings`, `sync.conf`, and `service` silently carry all of that.

### 2) Search and menu locality are still too weak as the primary contract

The current change log makes it clear that search inside power user settings is useful.
But that still leaves the operator answering a broader question by menu archaeology.
A serious sync product should not force the user to start from the menu name rather than the setting object.

### 3) Visibility, editability, and authority are still too easy to confuse

Current docs still say some values are exposed only on some surfaces, some are set in config mode, some are per-share, and some are not available in WebUI.
That means `I found it` and `I can edit it here` are different truths.
A serious sync product should never leave that implicit.

## What AnonSync should do instead

AnonSync should make **setting discoverability** first-class.
Every meaningful setting sentence needs one stable answer for:

- canonical setting identity
- aliases and search handles
- scope
- winning authority surface
- witness-only surfaces
- current edit route
- activation rung
- weakest missing proof still blocking a stronger settings sentence

The product should never let `open settings`, `advanced`, `folder preferences`, `mobile settings`, or `sync.conf` blur into one vague control story.

## Hard decisions now locked

1. **Every meaningful setting is a canonical object.**
   Menu names are not the contract; the setting object is.

2. **Visibility, editability, authority, and activation are separate truths.**
   A surface may show a value without owning it, or own it without hot-applying it.

3. **Search resolves to the setting object first.**
   Product search should not merely dump the operator into one menu where a label happens to match.

4. **Cross-surface sameness must be proven, not implied.**
   The same label on desktop, mobile, WebUI, and config must publish whether those are linked, overridden, detached, or merely parallel witnesses.

5. **Every meaningful settings path ends in a receipt.**
   Later operators should be able to see what was asked, where the edit really belonged, what scope changed, what activation boundary applied, and what stronger sentence stayed blocked.

## What this tranche adds to the archive

This revision adds five more first-class pages:

- **Setting-locator contract sheet**
- **Setting-route review**
- **Setting-context proof**
- **Setting-change itinerary**
- **Setting-lineage receipt**

Together they let AnonSync answer one ordinary operator question without archaeology:

> where do I change this, why here rather than elsewhere, what scope will it govern, and what stronger settings sentence is still blocked?
