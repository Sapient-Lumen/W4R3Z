# Resilio contested repair, read-only suspension, offline precedence, and archive ritual fragmentation evaluation

## Why this pass exists

The archive already had strong work on chronology, history, archive, and read-only divergence.
What it still lacked was one narrower current Resilio pass about an ordinary operator question:

> this file or subtree is contested — what exactly is happening, what repair paths exist, what will survive, and which move is actually safe right now?

Current official Resilio docs are useful here precisely because they are candid.
Today those docs still show that:

- `Conflict files in Sync` still says `.Conflict` items can arise from case-insensitive collisions, encoding differences, prohibited symbols, linked junctions, or controller problems, and still warns not to just delete a `.Conflict` file because it corresponds to the real file or folder on a remote peer.
- `User Management` still says that when a Read Only peer changes or adds files, those changes do not propagate and further synchronization of the changed files is suspended for that peer.
- `Is one-way synchronization possible?` still says that when `Overwrite any changed files` is enabled, renamed files remain while the old name is re-downloaded, deleted files are restored, edited files revert to the most recent RW version, and added files remain local-only and unsynced.
- `What if several people make changes to the same file?` still says that a peer coming back online with an older offline edit can outrank later online edits, and that overwritten versions are placed in Archive.
- `Using Archive for file versioning and restoring deleted files` still says only manual restoring is possible, Sync must be running during restore if replay is desired, Archive lacks per-peer authorship detail, and archive placement is asymmetric across peers.
- `My files don't sync` still says the repair step for Read Only local edits is to enable `Overwrite any changed` on the RO peer and restart Sync there.

That is a good reason to keep studying Resilio.
It is also another good reason not to clone the exact interface contract.

## What current Resilio still gets right

### 1) It admits that contested objects are materially different from clean sync

Resilio does not pretend that every stuck or divergent item is the same thing.
Current docs still distinguish named conflicts, suspended Read Only files, overwritten loser versions, Archive-held older versions, and local-only additions that remain unsynced.

### 2) It admits that loser fate matters

The docs still say that a restored or overwritten loser can survive in Archive, a renamed local file can remain while the old name returns, and an added file on a Read Only peer can remain local-only instead of disappearing.
That is useful and worth preserving.

### 3) It admits that repair can require runtime posture, not just byte copying

Archive restore still depends on Sync running if the operator expects replay rather than immediate demotion back to Archive.
The troubleshooting docs still tie some repair paths to restart.
That honesty is good.

## Why AnonSync still should not clone it

### 1) One ordinary repair answer still spans too many pages

To answer `what is the safe repair path for this contested file?` the operator may still need to combine:

- conflict-file delete warnings
- read-only permission docs
- one-way overwrite fate notes
- offline-writer precedence rules
- archive restore ritual
- troubleshooting / restart advice

That is too much archaeology for one ordinary decision.

### 2) Contest class is still too implicit

Current Resilio preserves the facts, but the product contract still makes the operator infer whether this is:

- blocked intake
- parallel survivor naming
- local-only residue
- archive-backed loser
- offline-returning winner
- manual-replay candidate

AnonSync should not leave that classification scattered.

### 3) Repair preview and survivor set are not owned strongly enough

The docs tell you the truth, but the product still does not own one ordinary page that previews exactly what remains live, what survives side-by-side, what is re-archived, and what becomes local-only.

### 4) Live repair and local inspection are still too easy to confuse

`copy the older bytes out`, `replay them into the live line while runtime is active`, `turn on overwrite`, and `keep a side survivor` are not one action.
AnonSync should productize those as separate reviewed paths.

## Hard decisions now locked for AnonSync

1. **Contest is a first-class object.** `blocked`, `parallel-survivor`, `overwrite-candidate`, `local-only residue`, and `archived loser` are separate verdicts.
2. **Repair path preview owns loser fate before apply.** The product must say what stays live, what survives side-by-side, and what falls out of the live line.
3. **Runtime posture is part of repair truth.** A restore or overwrite path that depends on runtime being active must say so.
4. **Local inspection and live replay are different verbs.** Exporting, side-by-side restore, overwrite, resume, and promote are not one repair action.
5. **Receipts preserve contest basis and survivor set.** Later operators must know why a repair path was chosen and what stronger claim stayed forbidden.

## Replacement page family justified by this pass

This pass therefore justifies six more product-owned surfaces:

- **Contested object contract sheet**
- **Repair path review**
- **Survivor set page**
- **Live repair approval**
- **Repair lineage receipt**
- **Repair supersession / reopening alert**

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still right to admit that contested bytes can be blocked, overwritten, restored, or preserved in parallel. But it still makes one ordinary operator answer — `what exactly is contested here, what survives, and what repair move is safe right now?` — depend on conflict naming, read-only caveats, archive ritual, restart advice, and chronology notes instead of one stable page family. AnonSync should keep the candor and refuse the archaeology.
