# Resilio modification-time authority, offline winner, time-skew gate, and archive-republish fragmentation evaluation

## Why this pass exists

The archive already had strong doctrine for byte custody, archive witness, change detection, placeholder reality, and maintenance health.
What it still lacked was one direct current Resilio pass about a narrower operator question:

> when two edits race, what truth actually decides the winner: live chronology, offline rejoin order, UTC-normalized modification time, a time-skew hard stop, a manual touch, a file-class delay, or an archive restore that only republishes if the runtime is alive at the right moment?

Current official Resilio docs are unusually useful here because they are candid about the real mechanics while still leaving the operator to reconstruct them across `What if several people make changes to the same file?`, `"Time difference" error`, `Using Archive for file versioning and restoring deleted files`, `Power user preferences`, `How to touch files?`, and `Setting Delay Time For Syncing`.

Today those docs still show that:

- when peers are online, Resilio describes synchronization as chronological by modification time
- when one peer edited offline returns later, that returning version can outrank later online edits and overwrite them
- overwritten versions are placed in Archive rather than surfaced as a first-class chronology verdict object
- time comparison is based on modification time converted to GMT/UTC and transfer stops if peer time drift exceeds 600 seconds by default
- mobile clients can degrade all the way to an empty-list symptom under the same time-skew condition
- restoring an older version from Archive is not self-proving republish authority: if Sync is not running at restore time, the older file can be re-archived as stale on rescan
- Sync treats a file as changed when mtime or size changes, so manual `touch` is an explicit remediation path when change detection or mtime propagation is weak
- file-class delay exists specifically to reduce edit-time conflict risk, defaults to 10 seconds for listed classes, and requires restart after config edits
- power-user settings still keep `sync_max_time_diff` and `ignore_mtime_assign_errors` separate from ordinary conflict or restore surfaces

That is a strong operator-truth corpus.
It is also a strong reason not to clone the exact page contract.

## What current Resilio still gets right

### 1) It admits that `latest` is not one flat idea

Current docs distinguish at least four materially different stories:

- online chronological progression
- offline-return winner
- time-skew refusal to decide
- manual older-byte republish from Archive

That honesty is worth keeping.

### 2) It admits that clock trust is operational, not cosmetic

The current docs say outright that Sync converts peer time to GMT/UTC and refuses transfer if drift exceeds the allowed window.
That is much better than silently pretending that modification time is always trustworthy.

### 3) It admits that archive restore is weaker than authoritative republish

The current docs do not say `restore and you are done`.
They say Sync must be running at restore time or the older version can lose again.
That distinction is useful and rare.

### 4) It admits that change detection and conflict mitigation are separate from chronology

`Touch` exists because change detection can miss a meaningful edit if mtime or notifications do not move as expected.
`FileDelayConfig` exists because conflict-prone applications are a different problem again.
Those are useful distinctions.

## Why AnonSync still should not clone it

### 1) Winner basis is still too scattered

The operator still has to merge an FAQ, a time-skew warning, archive docs, a tips article, and power-user preferences to answer one ordinary question:

> why did this version win, and how certain is that verdict?

AnonSync should not make chronology truth depend on article archaeology.

### 2) Time authority is still too easy to over-trust

The current docs still separate `clock drift`, `mtime`, `database fallback`, and `touch` into different surfaces.
AnonSync should publish the authority ladder directly where chronology claims are made.

### 3) Archive restore is still too easy to misread as rollback

`I copied an old file out of Archive` is not the same as `the mesh now recognizes this as the winner`.
AnonSync should put runtime witness and republish certainty on the same review page as the restore action.

### 4) Prevention and aftermath are still disconnected

The current docs still keep conflict-avoidance delay away from conflict-winner explanation.
AnonSync should keep `why this happened` adjacent to `how to reduce this class next time`.

## Hard decisions now locked for AnonSync

1. **Mutation chronology is a first-class contract object, not a side effect of file mtimes.**
2. **Online sequence, offline-return winner, time-skew refusal, manual older-byte republish, and detection remediation are separate truths.**
3. **Clock correctness is weaker than time-authority proof, and time-authority proof is weaker than winner certainty.**
4. **Archive presence is weaker than republish authority, and republish authority is weaker than stable convergence proof.**
5. **Every serious conflict or rollback action needs one receipt that preserves winner basis, time-certainty class, loser survivor map, and the blocked stronger sentence.**

## Replacement page family justified by this pass

This pass therefore justifies five more product-owned surfaces:

- **Mutation chronology contract sheet**
- **Concurrent edit review**
- **Time authority proof**
- **Older-byte republish review**
- **Mutation chronology lineage receipt**

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still right that live chronology, offline-return winner, time-skew refusal, manual touch, file-class delay, and archive-based republish are materially different truths. But it still makes one ordinary operator answer — `why did this version win, how trustworthy was the time basis, and what exactly must I prove before an older byte version becomes authoritative again?` — depend on several pages instead of one stable product-owned family. AnonSync should keep the candor and refuse the fragmentation.

