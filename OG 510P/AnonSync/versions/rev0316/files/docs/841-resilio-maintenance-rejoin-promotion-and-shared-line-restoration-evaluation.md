# Revision addendum — maintenance rejoin, promotion, and shared-line restoration after rev0282

Current official Resilio docs are still admirably candid about what happens **during** narrow or backup-like maintenance postures.
The live v3 line still runs through `3.1.2.1076`.
Current `User Management` docs still say that if a Read Only peer modifies files or adds new ones, those changes are not propagated and further synchronization of the changed files is suspended for that peer.
Current `Is one-way synchronization possible?` docs still say the same thing in operational terms and still add that `Overwrite any changed files` can restore deleted files, re-download the older name after a rename, revert edited contents to the most recent version from a RW peer, and keep newly added files local rather than syncing them.
Current `Folder Preferences` docs still say `Overwrite any changed files` is potentially destructive and is disabled for Read-only folders with Selective Sync ON.
Current `Encrypted folders` docs still say encrypted backup nodes are Read Only, always have overwrite activated, cannot decrypt locally, and can only be recovered through saved keys, preserved database continuity, or special local decrypt flow; they also say encrypted-archive restoration cannot simply upload the restored file back because the node is read-only and follows deleted state.
Current `How to use Camera Backup (all mobiles)?` docs still say backup folders are storage-oriented Read Only folders and that disconnecting backup leaves already-present files on both mobile and desktop.
Current `Sync Interface on iOS devices` docs still say `Remove from this device` disconnects only on that device and removes local files there while preserving them on others.

That is real candor.
It still does **not** earn direct interface cloning.

The reason is the next clone-veto rule now applied to another seam:

> one ordinary operator question should have one stable page answer.

Current Resilio still spreads the ordinary maintenance-rejoin answer across permissions docs, one-way-sync FAQ, folder preferences, encrypted backup docs, camera-backup docs, and mobile disconnect semantics.
So the product idea stays useful while the page contract still fails.

The missing operator-owned question is simple:

> after local work happened under a hold, read-only seat, backup-like lane, or other narrow posture, how exactly can that work rejoin the shared line now — in place, by widening rights, by export or side branch, by restored source authority, or not at all?

Current official docs still expose ingredients of that answer without one stable product object.
They still show that:

- some local work merely suspends continuity rather than disappearing
- some local work survives only as local residue and never becomes shared automatically
- some healing paths are explicitly destructive to local changes
- some backup-like or encrypted seats are preservation-oriented and need successor or restore flows rather than ordinary rejoin
- device-local disconnect or removal can preserve copies without saying anything about shared-line restoration

That is why this revision adds four narrower replacement pages:

- `842` Maintenance rejoin plan page
- `843` Maintenance rejoin review page
- `844` Maintenance rejoin ledger page
- `845` Maintenance rejoin receipt page

These pages keep the Resilio candor and reject the need to improvise a rejoin contract from several unrelated feature articles.

## Why this matters for AnonSync

A serious sync product should not make operators discover rejoin truth by trial, overwrite, or lucky survival.
The product should own at least these distinctions explicitly:

- **rejoin in place** — the held work can return to the shared line without side branching or destructive replacement
- **rejoin by widened authority** — continuity is restored only after a reviewed rights or posture change
- **rejoin by promotion** — local work must first become an exported branch, successor artifact, or reviewed candidate winner
- **preserve but do not rejoin** — the bytes stay valuable, but only as evidence, backup, or local residue
- **abandon or overwrite knowingly** — the local work does not rejoin and the product must say so plainly before heal or overwrite proceeds

Resilio's current docs still make those classes legible only if the operator already knows how to translate between Read Only suspension, overwrite preference, encrypted-backup hardwiring, backup storage semantics, and device-local disconnect behavior.
AnonSync should not clone that burden.

## Concrete product stance

Borrow from Resilio:

- candid admission that some local work survives but does not automatically rejoin
- candid admission that some heal paths are destructive and source-authority driven
- candid admission that backup-like and encrypted seats are preservation lanes, not ordinary symmetric rejoin lanes

Do not clone from Resilio:

- leaving rejoin strategy split across permissions docs, backup docs, encryption docs, and mobile disconnect prose
- forcing operators to infer whether a local edit should be promoted, exported, widened, or abandoned
- leaving no first-class reviewed object that says what shared-line restoration path is even available for this local work

## Evaluation summary

Resilio still deserves credit for publishing the ingredients of maintenance rejoin honestly.
But the current product/docs path still leaves a missing object:

> there is no first-class reviewed answer to `after local work happened under a narrow maintenance posture, what exact path can bring it back into the shared line, and what work must remain local, preserved elsewhere, or knowingly abandoned?`

AnonSync should therefore make **maintenance rejoin planning and shared-line restoration review** first-class product objects.
Every serious evidence hold, read-only inspection window, backup-like endpoint, encrypted custody seat, and repair sandbox should publish rejoin path, authority change needs, promotion requirement, overwrite barrier, strongest safe sentence, and successor boundary before the product treats `we can bring it back later` as implied.
