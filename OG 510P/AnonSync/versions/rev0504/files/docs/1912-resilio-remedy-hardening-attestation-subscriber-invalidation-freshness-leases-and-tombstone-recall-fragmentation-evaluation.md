# Resilio remedy hardening attestation subscriber invalidation, freshness leases, and tombstone recall fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials still deserve credit for acknowledging that publication is not one surface and that state can propagate, drift, or fail differently across those surfaces.
That is useful.

The strongest present ingredients are:

- current `Configuring WebUI` docs still say WebUI is the default UI on Linux and Windows service installs and that even basic share-by-link behavior differs there
- current `Guide to Linux, and Sync peculiarities` docs still say Linux has no native GUI and relies on the browser-rendered Sync UI
- current `Running Sync as a service on Windows` docs still say the service opens Sync WebUI in the default browser and can migrate or clean-install into a different runtime world
- current `Setting custom name for sync shares` docs still say custom names are UI-only, do not propagate to peers, yet can be inserted into generated links
- current `Sync Main View (Desktop)` docs still say History is only a 30-day surface and that connected-peer views are bounded by their own horizon rules
- current `Resilio Sync change log` still records notifications synchronized across devices, API v2 enablement, version lookup through API, UI not updating in some cases, system notifications failing on root folders, lost history log entries after update, invalid API requests crashing, API-related settings not surviving restart in some versions, and WebUI reload or blank-UI fixes

## Where the current contract still fragments

The problem is not that Resilio lacks propagation ingredients.
The problem is that it still does not produce one first-class, case-scoped **subscriber invalidation and freshness lease** object.

Today an operator can often infer only weaker truths such as:

- a desktop UI row changed
- a browser-rendered WebUI eventually reflected the same state
- some notifications may have synchronized across devices
- some structured consumer can ask the API for current version-like data
- some copied label or link may carry a human-oriented custom name that is not canonical on peers
- some old history or notification line may disappear after its retention horizon or even after an update
- some API or UI behavior may have needed version-specific fixes to remain current after restart or after an invalid request

Those are useful clues.
They are not the same as an explicit answer to `which subscribers, caches, browser sessions, copied structured payloads, or exported receipts are still allowed to serve this sentence, for how long, under which freshness lease, and what successor pointer or tombstone must they publish when the governing receipt changes?`

## Why that matters for AnonSync

AnonSync needs stronger post-publication truth than `the page changed` or `a recall happened somewhere`.
It needs to support claims such as:

- the human detail page is current, but two machine consumers are still pinned to an older receipt until they revalidate
- browser-session caches may render the downgraded sentence only after a must-revalidate boundary, while exported structured packets must flip immediately to tombstone-with-successor mode
- one subscriber class is allowed to keep a historical snapshot, but only if the snapshot is non-authoritative and machine-readable as superseded
- a public feed is frozen because the product cannot yet prove downstream cache invalidation for prior broader wording
- a stale claim was recalled from visible UI surfaces, but an older copied JSON receipt remains live and must emit a tombstone instead of silence
- the strongest honest sentence is `internal truth updated, machine-consumer invalidation incomplete`, not because the product failed to reason correctly, but because subscription closure is a distinct problem from surface wording

AnonSync therefore needs first-class objects for **subscriber inventory, version token, freshness lease, must-revalidate deadline, invalidation fanout state, stale-serve blocker, tombstone policy, successor pointer, and subscriber acknowledgement or expiry coverage** rather than leaving operators to reconstruct machine truth from WebUI behavior, 30-day history, notifications, copied labels, API changelog notes, and restart folklore.

## Non-clone conclusion

Borrow the candor.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `did every subscriber or cached derivative stop being allowed to serve the stale claim, and what exactly should an outdated consumer render now?` — only by making the operator combine several partially overlapping surfaces:

- browser-rendered WebUI that behaves differently from desktop UI in some flows
- Linux and service deployments where WebUI is the primary or only interface
- UI-only custom names that may still be embedded into generated links
- a short-horizon History surface
- device-synchronized notifications with their own history and reliability quirks
- API-related capability and restart-sensitivity notes scattered through the change log
- fixes for blank UI, missing updates, missing notifications, and lost history entries

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model **subscriber invalidation and freshness leases** directly.
Its interface family should let the product separate at least these truths:

- current governing receipt changed
- subscriber cohort inventory known
- freshness lease still valid
- must-revalidate boundary reached
- push invalidation sent
- pull revalidation still pending
- tombstone published with successor pointer
- stale serving blocked
- stale serving still structurally possible
- historical snapshot allowed but non-authoritative
- public machine feed frozen pending invalidation closure
- broader machine-consumable sentence still blocked

That is why this revision adds five more first-class pages:
**Remedy-hardening-attestation-subscriber-invalidation contract sheet**, **Remedy-hardening-attestation-subscriber-invalidation review**, **Remedy-hardening-attestation-subscriber-invalidation proof**, **Remedy-hardening-attestation-subscriber-invalidation timeline**, and **Remedy-hardening-attestation-subscriber-invalidation lineage receipt**.
