# Resilio estate certification, scope exclusion, and freshness fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- represent changed returns as parity debt
- settle many such debts through convergence campaigns
- publish bounded wins without lying about stragglers
- keep broader success language blocked until settlement proof really covered the claimed scope

What it still lacked was the next ordinary operator answer:

> after the campaigns, what exact estate scope can we now honestly certify as back in bounds, what is excluded, how fresh is the proof, and what event revokes that certification later?

That is the seam this pass locks.
The operator does not only need campaign truth.
They also need **estate certification truth**.
They need a durable answer to whether a meaningful estate, fleet, or governed family is now in-bounds again, not merely improving.

Current official Resilio material is useful here because it already exposes many inspection surfaces an operator would use when trying to answer that question manually:

- `Sync Main View (Desktop)`
- `How do I perform a search in Sync?`
- `Folder Types and Management`
- `Running Sync in configuration mode`
- `Sync Service Troubleshooting on Windows`
- `Settings on mobile platforms`
- `User Management`

## Current official Resilio evidence that matters here

Current official docs still show all of the following:

- `Sync Main View (Desktop)` still says the main UI lets operators filter connected and disconnected shares, perform search, enable or disable columns, and inspect a History lane that shows general syncing activity for the last 30 days. It also still says a green checkmark means files are synced with all connected peers. That is useful status inspection, but it is not yet a certification object.
- The same article still says the peers list shows `X of Y`, where `X` is online peers and `Y` includes offline peers, and that a peer offline for 7 days gets disconnected from the folder unless configured otherwise. So even the ordinary healthy-looking share view already has a horizon and freshness boundary built into it.
- `How do I perform a search in Sync?` still says search is available for folders, shared files, connected devices, and users in the UI. That is useful for locating evidence, but it is still a locator, not a scoped certification answer.
- `Folder Types and Management` still says disconnected folders remain visible for future action even though they have no folder path and take no space on the device. That means an estate can contain subjects that still belong to the logical set while no longer looking like ordinary active folders.
- The same article still shows that folder view can be customized with columns and sorting. That is useful inspection and triage support, but again it is not a durable statement of certified scope.
- `Running Sync in configuration mode` still says config mode is helpful for applying the same settings on a number of different machines, and still says that setting a non-default `storage_path` creates new settings there. So broad configuration alignment exists, but it can also create another settings world.
- `Sync Service Troubleshooting on Windows` still says switching the service to `Local System` creates another storage folder in another directory, after which the old added folders are absent and operators need to re-add and re-share or reconnect them. That is a strong example of an estate looking partially familiar while no longer being one continuous governed world.
- The same service article still says Web UI exposure may require separate config changes and a service restart. So even operator visibility is a separate certifiable plane, not just a byproduct of sync activity.
- `Settings on mobile platforms` still documents a separate mobile settings lane covering identity, auto-start, battery saver, auto-sleep, mobile data, proxy, listening port, and UPnP. That means current Resilio still has parallel settings and operating surfaces beyond the desktop main view.
- `User Management` still says peer disconnect suspends future updates while already-synchronized files remain in place. So visible bytes and future update rights can still diverge inside the estate.

So current Resilio still clearly admits serious certification truths:

- operators use many surfaces to inspect whether the estate looks healthy
- visible healthy activity is not the same thing as a durable estate-wide certification
- disconnected or partially detached subjects can remain in logical scope
- configuration, service principal, storage root, and mobile lanes can create scope or world boundaries
- status surfaces have freshness limits and horizon assumptions

But those truths still do not become one operator-facing **estate certification / explicit exclusions / freshness / revocation** object.

## What Resilio still gets right

### 1) It exposes several of the raw surfaces a careful operator would consult

Filters, search, columns, peer counts, history, configuration mode, service troubleshooting, and mobile settings are all real evidence planes.
That is worth borrowing.

### 2) It is honest that world changes can invalidate naive fleet-wide assumptions

Config `storage_path`, service principal changes, and detached or disconnected folder states all show that one installation family can fork into materially different operational worlds.
That matters.

### 3) It preserves that some non-active subjects still deserve operator attention

Disconnected folders and disconnected peers remain meaningful estate members for later action.
That is useful.

## Where current Resilio still fragments the operator answer

### A) There is no canonical certification object

A careful operator can inspect folders, peers, search results, history, service state, and settings.
But the product still does not give one place to answer:

- what exact scope is being certified
- which worlds or subjects are excluded
- how fresh the proof must be
- what weaker sentence still survives if certification is too broad

### B) There is no durable exclusions register tied to the stronger sentence

Current docs let operators learn that disconnected folders exist, that service or config changes can create new worlds, and that mobile has its own settings lane.
What they do not provide is one durable answer to:

- whether those subjects are inside the current certification scope
- whether they are intentionally excluded
- whether they block broader certification
- who owns their follow-on treatment

### C) There is no explicit revocation contract

Current surfaces expose activity, history, peer counts, and topology changes.
What they do not provide is one first-class certification answer to:

- what event revokes this certification
- what witness freshness window keeps it alive
- when quiet time is enough to preserve it
- what drift, exclusion change, or world fork automatically downgrades it

## Hard product decision unlocked by this pass

AnonSync should not let `campaigns completed` impersonate `estate certified`.
It should promote any material post-settlement confidence claim into a first-class **estate certification object** that separately expresses:

- certification target sentence
- exact certified scope
- explicit exclusions and whether they block broader certification
- witness classes and freshness window
- stronger blocked sentence
- automatic revocation triggers

That is the right next seam because it answers the operator question that always follows successful cleanup work:

> what exactly can we now certify as back in bounds, what remains outside that certificate, and how do we know when that certificate silently expires or is revoked?

## Replacement line for AnonSync

Borrow from Resilio:

- candor that operators inspect multiple evidence surfaces
- honesty that service, config, mobile, and disconnected states create real scope boundaries
- explicit admission that visible healthy status is narrower than universal truth

Do not clone from Resilio:

- any workflow where estate certification remains an informal synthesis across folders, devices, users, history, service state, and config state
- any contract where exclusions are only remembered in the operator's head
- any product shape where certification freshness and revocation are not explicit first-class data

AnonSync should instead ship explicit pages for:

- estate certification contract sheet
- estate certification shaping review
- estate certification proof
- estate certification timeline
- estate certification lineage receipt
