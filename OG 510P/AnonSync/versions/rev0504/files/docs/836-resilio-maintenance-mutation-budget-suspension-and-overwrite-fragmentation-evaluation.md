## Revision addendum — maintenance mutation budgets, suspended edits, and overwrite folklore after rev0281

Current official Resilio docs are still admirably candid that maintenance is not only about motion between peers.
The active v3 line still runs through `3.1.2.1076`.
Current `User Management` docs still say a Read Only peer that modifies files or adds new ones will not propagate those changes and that further synchronization of the changed files will be suspended for that peer.
Current `Folder Preferences` docs still say `Overwrite any changed files` on Read Only shares will overwrite local changes, including files the operator added, and warn that the option is potentially destructive to the operator's data.
That same current article still says the option is disabled for Read-only folders with Selective Sync ON.
Current `Encrypted folders` docs still say encrypted backup nodes are Read Only, always have `Overwrite any changed files` activated, and do not allow Selective Sync.
Current `How to Back up data (Android only)` docs still say backup intentionally preserves copies in both directions rather than acting like ordinary symmetric sync.
Current `Sync interface on iOS devices` docs still say `Remove from this device` disconnects the folder only on that iOS device and removes its files there while preserving them on others.

That is real candor.
It still does **not** earn direct interface cloning.

The reason is the next clone-veto rule now applied to another seam:

> one ordinary operator question should have one stable page answer.

Current Resilio still spreads the ordinary maintenance-mutation answer across permission docs, folder preferences, encrypted-backup docs, backup docs, mobile remove semantics, and remembered side effects.
So the product idea stays useful while the page contract still fails.

The missing operator-owned question is simple:

> while this hold or narrow-maintenance posture is active, what local work is tolerated, what work gets suspended, what work will be overwritten, and what safer escape hatch exists before I touch the files?

Current official docs still expose ingredients of that answer without one stable product object.
They still show that:

- read-only is not merely `can look but cannot break anything`
- local edits on a read-only seat can create suspended continuity rather than safe local scratch space
- `Overwrite any changed files` is not a harmless repair switch, but a destructive rewrite contract
- encrypted backup hardwires that destructive overwrite posture rather than leaving it optional
- backup / remove-on-device semantics are preservation-oriented on some surfaces, which makes later local cleanup or editing expectations even easier to misread

That is why this revision adds four narrower replacement pages:

- `837` Maintenance mutation budget page
- `838` Maintenance mutation review page
- `839` Maintenance mutation ledger page
- `840` Maintenance mutation receipt page

These pages keep the Resilio candor and reject the need to improvise a mutation-fate contract from several unrelated feature articles.

## Why this matters for AnonSync

A serious sync product should not make operators learn mutation fate by suffering it.
The product should own at least these distinctions explicitly:

- **inspect-only** — do not mutate here; local reads are safe but local writes are out of budget
- **local scratch, no continuity** — local edits are tolerated but will not rejoin the shared line automatically
- **suspend-until-repair** — local edits keep bytes here but suspend future delivery on those paths until a deliberate repair choice
- **overwrite-on-heal** — later repair or remote authority will replace local edits unless they are exported elsewhere first
- **preserve-elsewhere-first** — local work should be diverted into a side branch, export, or successor workspace before maintenance continues

Resilio's current docs still make those classes legible only if the operator already knows how to translate between Read Only, overwrite preferences, encrypted backup hardwiring, and mobile backup/remove semantics.
AnonSync should not clone that burden.

## Concrete product stance

Borrow from Resilio:

- candid admission that narrow or backup-like seats can still receive local mutations with non-obvious fate
- candid admission that `Overwrite any changed files` is materially destructive
- candid admission that some preservation-oriented modes intentionally keep copies while others suspend or replace local edits

Do not clone from Resilio:

- leaving mutation tolerance, suspension, overwrite, and escape hatches scattered across permission and backup docs
- letting operators discover only after the fact whether a local maintenance edit became stranded, overwritten, or silently outside the shared line
- leaving no first-class reviewed object that says what local work is in budget during a hold and what repair or export is needed later

## Evaluation summary

Resilio still deserves credit for publishing the ingredients of maintenance-local mutation fate honestly.
But the current product/docs path still leaves a missing object:

> there is no first-class reviewed answer to `while this hold is active, what local work survives, what gets suspended, what gets overwritten, and what stronger safe-work sentence remains unsupported?`

AnonSync should therefore make **maintenance mutation budget and mutation-fate review** first-class product objects.
Every serious evidence hold, read-only inspection window, preservation node, repair sandbox, and backup-like endpoint should publish allowed local work, suspension behavior, overwrite risk, escape hatch, strongest safe sentence, and reopen boundary before the product treats `safe to edit here` as implied.
