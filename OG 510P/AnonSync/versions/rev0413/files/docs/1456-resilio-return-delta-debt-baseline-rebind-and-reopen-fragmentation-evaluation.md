# Resilio return-delta debt, baseline rebind, and reopen fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- suspend a control truthfully
- bring activity back through typed return paths
- distinguish motion restored from protection restored
- preserve structural delta while requalification is still pending

What it still lacked was the next ordinary operator answer:

> once a changed return is accepted and the system is working again, is that change a temporary debt, a deliberate successor state, or a reason to reopen because we never truly got back to the intended protected state?

That is the seam this pass locks.
A real operator cannot afford a vague `still syncing` verdict.
The product needs a first-class answer for **accepted return delta, parity debt, baseline rebind, and honest reopen**.

Current official Resilio material is useful here because it already proves that a changed but working state can persist after return:

- `Disconnecting and Removing Folders`
- `Folders are duplicating with an index (i) in their name`
- `How to manually set the location of the folders synced across linked devices?`
- `Folder Types and Management`
- `Synchronization Modes`
- `Can I connect two pre-populated pre-existing folders?`
- `Folder not empty`
- `Can I move or rename a syncing folder?`
- `User Management`

## Current official Resilio evidence that matters here

Current official docs still show all of the following:

- `Disconnecting and Removing Folders` still says reconnect may propose a default path different from the original path, may create a new directory, and may append `(1)` if a same-name folder already exists. So a changed path can become the active working state even when the operator wanted the original home back.
- The same article still says disconnect removes placeholder files if Selective Sync was enabled. So some returns re-enter with less local witness state than before even when activity later resumes.
- `Folders are duplicating with an index (i) in their name` still says devices in Selective Sync or Synced mode place arriving folders into the default storage location, and that choosing Disconnected mode is the way to force explicit manual placement later. That means a changed path is not an exotic edge case; it is a normal byproduct of default-mode behavior.
- `How to manually set the location of the folders synced across linked devices?` still says disabling Simple mode on Android causes new linked-device folders to arrive in Disconnected mode so the operator can choose a custom path at each connect. That is useful, but it also confirms that path authority and return authority do not live in one obvious place.
- `Folder Types and Management` still says disconnected folders have no folder path associated locally, while Selective Sync preserves a visible tree through placeholders and Full Sync keeps all bytes. So a working post-return state may differ materially in what kind of local residency and witness it actually provides.
- `Synchronization Modes` still distinguishes Disconnected, Selective Sync, and Synced as three different data-movement postures. A return that lands in a different posture can still look healthy while preserving different local guarantees.
- `Can I connect two pre-populated pre-existing folders?` still says same-hash files will not be re-synced, same-name different-hash files resolve by latest timestamp, and other files are merged into the folder tree. So one operator path to a working state is explicitly a merge-successor state, not a restoration of exact prior parity.
- `Folder not empty` still warns that if you add or reconnect into an already existing non-empty directory, files that were already present there might be deleted or overwritten. That is a huge clue that some working returns have durable survivor debt rather than clean parity.
- `Can I move or rename a syncing folder?` still says renaming a folder affects only the device where it is renamed, and other devices are not updated with the new name. It also still says that moving to a new partition on Windows or Mac requires disconnect and reconnect. So a path/name successor can remain active without becoming a globally aligned baseline.
- `User Management` still says disconnecting a peer suspends future updates while already-synchronized files remain in the folder. So a working content tree may persist after rights changed underneath.

So current Resilio still clearly admits serious post-return truths:

- an active working state may still have a different path than the old intended home
- a working state may preserve different local residency or placeholder posture than before
- a merge-based return can remain active after timestamp winner rules changed the tree
- local rename and move semantics can drift name/path parity without ending sync activity
- permission/future-update posture can differ while old bytes remain visible

But those truths still do not become one operator-facing **return-delta debt / baseline rebind / honest reopen** object.

## What Resilio still gets right

### 1) It is candid that working does not always mean same-place or same-shape

Path forks, `(1)` suffixes, disconnected mode, placeholder posture, and merge rules are openly documented.
That honesty is worth borrowing.

### 2) It exposes path authority and mode authority as real constraints

Default storage behavior, Disconnected mode, and Android Simple mode make clear that re-entry can be correct or drifted depending on where authority lives.
That matters.

### 3) It preserves some survivor warnings

`Folder not empty`, placeholder removal, and peer-disconnect behavior all admit that visible bytes may survive even when the underlying contract changed.
That is useful.

## Where current Resilio still fragments the operator answer

### A) There is no canonical answer to `is this changed return still a temporary debt or the new intended baseline?`

A careful operator can infer it.
But the product still does not answer in one place:

- whether the new path is temporary or adopted
- whether placeholder/full-byte posture is an accepted successor or a debt
- whether merge results were merely tolerated or formally blessed
- whether rights/topology deltas are temporary or intentional
- when the changed return must be fixed, promoted, or reopened

### B) `Still syncing` is allowed to masquerade as parity

Current docs explain how to reconnect, connect to an existing directory, disable Simple mode, or change synchronization mode.
What they do not provide is one durable verdict about whether the resulting active state is:

- exact restoration
- temporary accepted delta
- permanent successor state
- unresolved debt requiring later exact restore
- or grounds to reopen the associated case/control/rollout

### C) There is no first-class aging model for accepted return debt

Current docs tell operators how to reach a working state.
They do not tell them when a changed working state expires as a tolerable compromise.
The product still lacks one object that can say:

- owner of the accepted delta
- expiry date for the tolerated mismatch
- proof needed to promote the successor state to the new baseline
- triggers that worsen the debt and reopen the case

## Hard product decision unlocked by this pass

AnonSync should not let a changed-but-working return silently become the new normal.
It should promote every material post-return mismatch into a first-class object that can separately express:

- accepted delta class
- whether the delta is exact-restoration debt or intentional successor candidate
- owner and expiry
- next required proof or reconciliation step
- whether the stronger old sentence is still blocked
- whether the next honest move is exact restore, successor promotion, or reopen

That is the right next seam because it answers the operator question that always follows a messy but successful return:

> we are working again, but is this merely a tolerated changed state, when does that tolerance expire, and what must happen before calling it the new baseline instead of drift?

## Replacement line for AnonSync

Borrow from Resilio:

- candor that path, mode, and merge results can produce a working but changed state
- explicit admission that rights, placeholders, and default paths can diverge from the old state
- honesty that some warnings imply durable survivor debt

Do not clone from Resilio:

- any contract where `still syncing` silently rounds up to `same protected state`
- any workflow where changed path/mode/topology becomes the new baseline without explicit promotion
- any product shape where the operator must remember expiry, owner, and reopen triggers out of band

AnonSync should instead ship explicit pages for:

- return-delta contract sheet
- delta-aging review
- parity-debt proof and baseline rebind
- return-delta timeline
- return-delta lineage receipt
