# Resilio remedy hardening attestation predecessor authority retirement, exclusive successor control, and split-world fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials still deserve credit for acknowledging several ingredients of old-world retirement, even if they do not yet elevate them into one typed control verdict.
That is useful.

The strongest present ingredients are:

- current `Key structure and flow` docs still say changing a Standard-folder key is not distributed automatically and that peers with the old Key continue syncing with each other while no longer syncing with the peer who changed the Key
- current `What's the difference between Standard and Advanced folders?` docs still say Standard-folder peers can share the key they have without limitation, that on-the-fly permission changes are unavailable there, and that revoke access from remote peers is only available for Advanced folders
- current `User Management` docs still say only Owners can revoke access rights from other peers and that this permission model applies only to Advanced folders
- current `Sync Private Identity & Linking My Devices` docs still say you cannot remotely unlink other devices
- current `Disconnecting and Removing Folders` docs still say removing a folder from linked devices may still leave it available on remote devices that are not linked to your personal identity
- current `Sharing single file` docs still say recipients can share files further
- current `Can Resilio team see and block/remove any Sync folders?` docs still say Resilio cannot control link or folder distribution and cannot remove content from users' devices or their peers' devices
- current `If your device is stolen` docs still say the serious response path is to remove shares, unlink identity if linked, remove synced data from storage, reinstall, regenerate identity, relink devices, and reshare folders
- current `Sync Service Troubleshooting on Windows` docs still say switching to Local System creates a new storage folder where seeing no old folders is expected and operators must re-add and re-share or reconnect folders

## Where the current contract still fragments

The problem is not that Resilio hides the ingredients.
The problem is that it still does not produce one first-class, case-scoped **predecessor authority retirement and exclusive successor control** object.

Today an operator can often infer only weaker truths such as:

- the successor world exists and can be found through newer links or keys
- some predecessor handles were rotated or replaced
- some peers were re-shared or relinked
- some devices were unlinked locally, but other devices could not be remotely unlinked
- some remote peers may still retain bytes, keys, or copied links outside the linked-identity boundary
- a Standard-folder cohort with the old key may still be live and mutually syncing even after one actor rotates away
- a stolen or compromised device may force a rebuild, but there is still no single page that says which predecessor authorities can still act right now

Those are useful clues.
They are not the same as an explicit answer to `can the predecessor world still write, seed, revoke, share, attract new dependents, or keep a split world alive, and has the successor become the only legitimate actor for the named slice?`

## Why that matters for AnonSync

AnonSync needs a stronger sentence than `the successor is legitimate` and stronger still than `the successor is the canonical pointer`.
It needs to support claims such as:

- the successor is canonical, but the predecessor still has live write capability through an old key cohort
- human-facing references were rebound, but a predecessor device can still act as an active controller or seed
- the predecessor is retired for one governed slice, while ungoverned remotes remain live and can still republish or mutate state
- a successor world inherited standing, yet split-world exclusivity is blocked because the predecessor still has unresolved actuation lanes
- the strongest honest sentence is `successor canonical, predecessor authority not fully extinguished`, not because discovery failed but because control retirement is a separate problem from pointer rebinding

AnonSync therefore needs first-class objects for **predecessor actor set, live predecessor capability, authority class, revocation reach, split-world status, quarantine posture, successor exclusivity scope, and blocked stronger control sentence** rather than leaving operators to reconstruct control truth from key rotation rules, folder-type differences, unlink limits, remote-retention notes, copied links, or stolen-device reset recipes.

## Non-clone conclusion

Borrow the candor.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `can the old world still act, and is the successor now the only legitimate controller for the intended slice?` — only by making the operator combine several partially overlapping mechanics:

- Standard-key continuation after one peer rotates away
- folder-type-specific revoke authority and permission mutation rules
- inability to remotely unlink other devices
- linked-identity removal that may still leave unlinked remotes live
- copied link and single-file forwarding beyond governance
- catastrophic reset guidance for stolen devices
- service-user storage forks that create distinct worlds requiring re-share or reconnect
- architectural statements that Resilio itself cannot block or remove other peers' content or distribution

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model **predecessor authority retirement and exclusive successor control** directly.
Its interface family should let the product separate at least these truths:

- successor valid, predecessor authority unreviewed
- successor canonical, predecessor handles rebound, predecessor actuation still possible
- predecessor writes blocked for named slice only
- predecessor sharing blocked, predecessor seeding still possible
- predecessor revocation authority removed, predecessor bytes still live off-world
- split-world active
- predecessor quarantined for named slice only
- successor exclusive controller for named slice only
- broader universal exclusivity blocked

That is why this revision adds five more first-class pages:
**Remedy-hardening-attestation-predecessor-authority-retirement contract sheet**, **predecessor-authority-retirement review**, **predecessor-authority-retirement proof**, **predecessor-authority-retirement timeline**, and **predecessor-authority-retirement lineage receipt**.
