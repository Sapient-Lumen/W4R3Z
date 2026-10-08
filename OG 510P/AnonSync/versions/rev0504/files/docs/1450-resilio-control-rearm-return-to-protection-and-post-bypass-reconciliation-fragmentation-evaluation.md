# Resilio control re-arm, return-to-protection, and post-bypass reconciliation fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- promote a guardrail from a case
- attest whether the control is still trusted
- suspend or bypass that control truthfully
- preserve what still survives during the bypass window

What it still lacked was one ordinary operator answer to the next harder question:

> once the bypass ends, what exactly does it mean to come back, what structural deltas must be reconciled first, and when is the stronger protection sentence safe again?

That is the seam this pass locks.
A real operator cannot afford a vague `resume` button.
The product needs a first-class answer for **control re-arm, return-to-protection, and post-bypass reconciliation**.

Current official Resilio material is useful here because it already proves that several kinds of `coming back` are materially different:

- `How to pause syncing`
- `Sync Preferences`
- `Disconnecting and Removing Folders`
- `Synchronization Modes`
- `How to manually set the location of the folders synced across linked devices?`
- `Can I connect two pre-populated pre-existing folders?`
- `Selective Sync`
- `Settings on mobile platforms`
- `User Management`

## Current official Resilio evidence that matters here

Current official docs still show all of the following:

- `How to pause syncing` still says resuming a paused folder is just repeating the same steps and using `Resume syncing`. That is a same-surface return, but it only makes sense because the underlying topology was not fully detached.
- `Sync Preferences` still says Global Pause/Resume only affects shares that are not paused individually. So even the simplest return verb already depends on which pause surface owns the current state.
- `Disconnecting and Removing Folders` still says reconnect may propose a default path different from the original path, may create a new directory, and may append `(1)` if a same-name folder already exists. So some returns are not mere resumes at all; they are path-selection and directory-creation events.
- The same article still says disconnect keeps the folder in the file system, removes placeholders if Selective Sync was enabled, and requires `Connect` later to re-establish syncing. That means the operator must reconcile more than one dimension on return: bytes, placeholders, path, and relationship.
- `Synchronization Modes` still says disconnected folders have no path associated with them locally until connect, while Selective Sync returns files as placeholders and `Remove from this device` preserves remote copies but not full local bytes. So a return from `disconnected`, `selective placeholder`, and `full sync` are not the same recovery path.
- `How to manually set the location...` still says devices in Selective Sync or Synced modes place new folders in the default location, while Disconnected mode lets the operator choose the path at connect time. On Android, Simple mode must be disabled to pick a custom path. That means return-to-protection may depend on lane-specific prerequisites and path authority, not just resuming motion.
- `Can I connect two pre-populated pre-existing folders?` still says connecting to an existing directory merges same-hash files without re-sync, resolves differing hashes by latest timestamp, and merges other files into the tree. So one form of `return` is really a compare-and-merge event with its own survivor logic, not a pure restoration of the previous protected state.
- `Selective Sync` still says removing a Selective Sync share removes all placeholders from the file system on that device. So after some detach classes, later re-entry cannot honestly be described as a simple resume because local witness state was actually removed.
- `Settings on mobile platforms` still says Android Simple mode controls whether the operator can choose share location and still says default folder location with Simple mode can create a `(1)` suffixed path when a same-name folder already exists. Again, return can silently fork path state.
- `User Management` still says peer disconnect revokes future updates but leaves already-synchronized files in place. So permission restoration and content continuity are separate return questions.

So current Resilio still clearly admits serious re-entry truths:

- `resume` is not one thing
- same-surface resume is weaker and cheaper than reconnect
- reconnect may land on a different path than the old protected state
- connect-to-existing-directory is a compare-and-merge event, not just a re-enable
- some detach classes delete placeholders or local witness traces before return
- peer relationship restoration is different from local transport resume
- mobile return may be gated by mode or default-path behavior

But those truths still do not become one operator-facing **return-to-protection / reconciliation / trust-requalification** object.

## What Resilio still gets right

### 1) It is candid that not all returns are equal

Pause/resume, disconnect/connect, connect-to-existing-directory, and permission reconnection are not hidden under one false story.
That distinction is worth borrowing.

### 2) It preserves structural side effects of return

Different path proposals, `(1)` path creation, placeholder removal, and merge rules are all admitted.
That honesty is useful.

### 3) It exposes lane-specific prerequisites

Android Simple mode and disconnected-mode path choice both make clear that a return may require prerequisites before the operator can recreate the intended state.
That is worth preserving.

## Where current Resilio still fragments the operator answer

### A) There is no canonical answer to `did we actually get back to the same protected state?`

A careful operator can read several KB pages and infer it.
But the product still does not answer in one place:

- whether the return reused the same path
- whether placeholder or full-byte posture changed
- whether the return merged into an existing directory
- whether peer permissions and future-update rights match the previous state
- whether the old trust sentence is back or only weaker motion is back

### B) Return and reconciliation are too easy to confuse

A folder can be active again while still being different:

- new default path
- `(1)` directory fork
- placeholders recreated instead of full bytes
- merged pre-populated directory with winner-by-timestamp rules
- re-enabled transport but not requalified protection

Current docs explain each edge in isolation, but still do not compose them into one re-entry contract.

### C) The proof of restored protection is not first-class

Current docs explain how to resume, reconnect, or connect to an existing directory.
What they do not give is one explicit answer to:

- what structural deltas were reconciled
- what remained intentionally different
- whether old trust can return immediately or only after new attestation
- what stronger sentence is still blocked after activity restarts

## Hard product decision unlocked by this pass

AnonSync should not let `resumed`, `reconnected`, `reattached`, `merged`, and `requalified` collapse into one success badge.
It should promote every meaningful return into a first-class object that can separately express:

- return class
- intended restored state
- structural deltas since bypass start
- reconciliation work still pending
- trust requalification requirements
- strongest sentence safe right now

That is the right next seam because it answers the operator question that always follows a bypass:

> motion is back, but are we actually back to the same protected state we intended, and what exactly still needs to be reconciled before saying yes?

## Replacement line for AnonSync

Borrow from Resilio:

- candor that return paths differ materially
- honesty that reconnect can create new paths or merge into existing trees
- explicit lane prerequisites and placeholder consequences

Do not clone from Resilio:

- any contract where `Resume` hides path, mode, or permission deltas
- any workflow where reconnect and restore-to-same-protection share one vague success story
- any product shape where the operator must reconstruct post-bypass equivalence from several separate articles

AnonSync should instead ship explicit pages for:

- return-to-protection contract
- re-arm readiness review
- return proof and requalification
- post-bypass reconciliation timeline
- return-to-protection lineage receipt
