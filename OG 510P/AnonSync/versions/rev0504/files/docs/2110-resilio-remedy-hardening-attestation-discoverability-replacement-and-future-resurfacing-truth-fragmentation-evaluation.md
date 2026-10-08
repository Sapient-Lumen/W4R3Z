# Resilio remedy-hardening attestation discoverability replacement and future resurfacing truth fragmentation evaluation

## Why this seam matters now

The archive can already say:

- the beneficiary was legitimate
- the beneficiary stayed on the canonical correction lane
- the beneficiary noticed, acknowledged, adopted, and may have durably adhered to the corrected working state
- the governed downstream audience may have retired stale dependencies for the named boundary
- named public representations may have been withdrawn, superseded, or disclaimed

That is still weaker than a harder question:

**if somebody rediscovers the stale thing later, do they reliably find the corrected replacement, or does resurfacing still route them back into stale residue?**

Public-claim repair is not automatically discoverability repair.
Discoverability repair requires a rediscovery surface map, a canonical replacement pointer, a late-arrival route, and an explicit resurfacing horizon.
Without those, `we corrected or withdrew the stale thing` quietly expands into folklore about outsiders now finding the right thing by default.

## Why current Resilio still leaves this too diffuse to clone

Current official Resilio material is candid about several rediscovery and resurfacing ingredients, but it still spreads them across separate pages:

- `Link structure and flow` says Sync links open through a Resilio landing page that shows basic folder information such as folder name and size, and that the hash parameters are not actually sent to Resilio's server
- `How do I perform a search in Sync?` says search is a UI feature over folders, shared files, devices, and users, and on iOS it runs only at the current subfolder level
- `Configuring WebUI` says clicking a link or placing it in the browser address bar does not add the share in Sync WebUI and requires manual entry instead
- `Setting custom name for sync shares` says custom names are local to the Sync UI, do not rename the folder on disk, and do not propagate to other peers or linked devices, though a generated link can carry an inserted name
- `Sharing single file` says file-transfer links can be made non-expiring, cannot restrict devices or usage count, and allow recipients to share the files further

This is good operational candor.
It is not yet one first-class answer to **if the stale thing resurfaces later, will the rediscovering outsider reach the corrected replacement or only another stale representation?**

## The non-clone line

AnonSync should not clone a contract where all of these are allowed to blur together:

- the stale artifact was withdrawn or superseded
- a corrected replacement exists somewhere
- the operator can still search it locally
- one link landing page exists
- WebUI can still accept a link via manual entry
- the stale file-transfer link may remain non-expiring or be reshared
- display names vary by local UI or by individual generated links
- a later outsider therefore will reliably arrive at the corrected replacement

Those are separate truths.

## Product decision frozen in this tranche

This revision freezes a stronger line:

- **external representation retirement is weaker than discoverability replacement and future resurfacing truth**
- **withdrawing a stale artifact is weaker than giving late rediscovery a canonical route to the corrected replacement**
- **local searchability, local naming, or manual WebUI recovery may never impersonate `late outsiders now reliably find the corrected replacement`**

## What AnonSync should model explicitly instead

AnonSync should add one first-class family for:

- source public-claim receipt identifier
- rediscovery surface identifier
- rediscovery surface boundary rule
- canonical replacement pointer class
- late-arrival route quality
- replacement coverage threshold
- residual resurfacing channel set
- resurfacing horizon class
- strongest honest replacement-findability sentence
- blocked stronger rediscovery-safe sentence

## Interface consequence

That is why this tranche adds five more first-class pages:

- **discoverability contract sheet**
- **discoverability review**
- **discoverability proof**
- **discoverability timeline**
- **discoverability lineage receipt**
