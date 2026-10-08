# Resilio effect direction, reverse-lane ceiling, and flow-role fragmentation evaluation

## Why this pass exists

The archive already had stronger doctrine for seat posture, presence, salvage readiness, subject-kind override, archive restore, and byte custody.
What it still lacked was one direct current Resilio evaluation for a narrower but important question:

> when a share is visible and present, which side is actually allowed to originate change, which side can only retain or serve, which delete directions are live, and what recovery lane can ever run in reverse?

Current official Resilio docs still show a useful, living product, but they also still show that one ordinary answer is spread across several article families at once:

- `Synchronization Modes`
- `Folder Types and Management`
- `Folder Preferences`
- `How to Back up data (Android only)`
- `How to use Camera Backup (all mobiles)?`
- `Encrypted folders`

## Current official Resilio evidence that matters here

Current official docs still say all of the following:

- `Synchronization Modes` and `Folder Types and Management` still say **Synced / Full Sync** is the ordinary bidirectional mode: all content is synchronized and additions, deletions, and changes propagate across connected peers.
- `Folder Types and Management` still says **Read Only** means you may not send changes, additions, or deletions to the rest of the swarm.
- `Folder Preferences` still says remote Read & Write changes or deletions propagate to other peers, and `Overwrite any changed files` for Read Only folders can destructively replace local divergence.
- `How to Back up data (Android only)` still says mobile backup is not ordinary collaboration: if you delete backed up files on the phone, copies remain on the computer; and because the desktop has Read-only access, deletes there remain on the phone as well.
- `How to use Camera Backup (all mobiles)?` still says camera backup is for storage purposes only, creates 1.4 folders with Read Only keys, and disconnecting the backup leaves already-present pictures on both devices.
- `Encrypted folders` still says encrypted nodes are Read Only, cannot decrypt locally, can only re-share in encrypted format, and cannot restore deleted files back from their own Archive to the source because they both follow source delete state and lack upload authority.

So current Resilio still contains a real but scattered answer to `what direction does effect actually flow here, and what reverse lane is truly available if something goes wrong?`

## What Resilio still gets right

### 1) It is candid that not every present share is bidirectional

The docs do not pretend `present`, `connected`, `Read Only`, `backup`, and `encrypted` all differ only cosmetically.
They openly describe materially different effect directions.
That honesty is valuable.

### 2) It is candid that delete direction is a separate truth from byte presence

The docs still say a backup copy can remain on desktop after mobile deletion, and desktop deletion in that backup lane does not remove the phone copy.
They also still say encrypted nodes follow source delete state instead of reversing it.
That candor matters.

### 3) It is candid that recovery direction is narrower than storage direction

The docs still admit that encrypted nodes can help recovery only under saved-key and database-continuity conditions, while ordinary Archive replay must come from Read-Write peers.
That is an important distinction.

## Why this is still a good reason not to clone them

### 1) Materialization mode still overstates directional meaning

Current docs still let operators absorb `Disconnected`, `Selective Sync`, `Synced`, `Read Only`, `backup`, and `encrypted` from different places even though those labels answer different questions:

- whether bytes materialize locally
- whether local edits can publish
- whether local deletes can publish
- whether reverse restore is possible
- whether the node is only a storage or serve lane

AnonSync should not inherit a contract where a single row state or icon must carry all of that.

### 2) `Read Only` still hides several different reverse-effect ceilings

Current Resilio still uses `Read Only` across at least three materially different situations:

- ordinary read-only collaboration, where local divergence may suspend updates or be auto-overwritten
- mobile backup storage, where reverse deletion is explicitly blocked and already-landed storage survives disconnect
- encrypted custody, where reverse restore from local Archive is blocked by both read-only posture and source-delete following

A serious sync product should not let one posture label flatten those different effect-direction contracts.

### 3) Recovery and publication direction still have to be reconstructed from several pages

One ordinary operator sentence — `can this side ever push, delete back, restore back, or only hold bytes?` — still depends on combining Sync Guides, Folder Preferences, backup guides, and encrypted-folder rescue instructions.
That is too much archaeology for such a basic truth.

## What AnonSync should do instead

AnonSync should make **effect direction** a first-class contract object.
For every subject-seat pair it should publish, separately:

- authoring lane
- delete lane
- serve lane
- reverse-recovery lane
- onward-reshare lane
- survivor behavior after disconnect

It should also stop treating local materialization mode as a proxy for directional power.
A placeholder-backed seat, a full local copy, a storage-only backup sink, and an encrypted custody node can all hold bytes while having very different reverse-effect ceilings.

## Replacement pages in this revision

This revision adds five fixed pages:

- `1343` — Effect-direction contract sheet
- `1344` — Flow-direction review
- `1345` — Reverse-lane proof
- `1346` — Effect-direction timeline
- `1347` — Effect-direction lineage receipt

## The doctrinal line

Borrow directly:

- the candor that bidirectional sync, read-only replication, mobile backup, and encrypted custody are not the same lane
- the explicit admission that delete direction can differ from storage direction
- the explicit admission that reverse restore from an encrypted node is much narrower than ordinary storage presence

Do not clone directly:

- any contract that lets materialization mode impersonate directionality
- any contract that lets `Read Only` hide several materially different reverse-effect ceilings
- any contract that forces the operator to merge sync-mode docs, folder-type docs, backup guides, and encrypted-rescue prose to know which side can actually publish or recover

## Conclusion

The correct AnonSync response is not `rename the statuses more clearly`.
It is stronger than that:

> keep Resilio's candor that not every share is bidirectional, but own effect direction as a first-class interface family so the operator can see exactly which side can author, delete, serve, re-share, or recover in reverse without reconstructing it from scattered docs.
