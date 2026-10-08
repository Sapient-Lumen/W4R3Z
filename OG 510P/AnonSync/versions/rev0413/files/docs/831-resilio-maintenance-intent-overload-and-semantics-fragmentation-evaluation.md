## Revision addendum — overloaded quiet controls, backup islands, and missing maintenance intent after rev0280

Current official Resilio docs are still admirably candid that `stop activity for a while` is not one single semantic class.
The active v3 line still runs through `3.1.2.1076`.
Current `How to pause syncing` docs still say pause stops only bits transfer while zero-sized files and deletions still sync and new files are still rescanned and indexed.
Current `Running Sync on schedule` docs still say scheduled `Paused` is only a speed-zero posture, still leaves those residual behaviors alive, and can still let paused peers upload to non-paused peers while not downloading.
Current `Is one-way synchronization possible?` docs still say Read Only permission gives full download while changes made in the read-only folder do not sync back.
Current `How to Back up data (Android only)` docs still say backup intentionally preserves copies even after later deletion on the phone, and that the desktop side has read-only access so changes do not sync back.

That is real candor.
It still does **not** earn direct interface cloning.

The reason is the next clone-veto rule now applied to another seam:

> one ordinary operator question should have one stable page answer.

Current Resilio still spreads the ordinary maintenance-intent answer across pause docs, scheduler docs, read-only docs, Android backup docs, and remembered side effects.
So the product idea stays useful while the page contract still fails.

The missing operator-owned question is simple:

> what kind of quiet or freeze do I actually need here — transfer silence, no delete propagation, no writeback, graceful drain, or a true maintenance hold — and what motion is still intentionally allowed under that choice?

Current official docs still expose ingredients of that answer without one stable product object.
They still show that:

- `pause` is not a full freeze
- scheduled `Paused` is not a full freeze either
- read-only is a directional writeback ceiling, not a quiet window
- Android backup is a preservation contract, not the same thing as ordinary sync or pause
- the operator still has to map maintenance intent to feature choice by memory

That is why this revision adds four narrower replacement pages:

- `832` Maintenance intent page
- `833` Maintenance semantics review page
- `834` Maintenance transition plan page
- `835` Maintenance contract receipt page

These pages keep the Resilio candor and reject the need to improvise a maintenance contract from several unrelated feature articles.

## Why this matters for AnonSync

A serious sync product should not make operators reverse-engineer maintenance semantics from a pile of toggles.
The product should own at least these distinctions explicitly:

- **transfer quiet** — byte motion should stop, but this may not freeze metadata or control traffic
- **writeback quiet** — this seat should not send local mutations back upstream
- **delete freeze** — destructive propagation must stop even if some non-destructive observation continues
- **drain then hold** — in-flight work may finish, but no new work should start afterward
- **preserve only** — act like a capture/backup endpoint rather than a symmetric participant

Resilio's current docs still make those classes legible only if the operator already knows how to translate between pause, schedule, read-only, and backup semantics.
AnonSync should not clone that burden.

## Concrete product stance

Borrow from Resilio:

- candid admission that different controls imply different motion contracts
- candid admission that `pause` does not mean `nothing changes`
- candid admission that one-way/read-only and backup are materially different from ordinary two-way sync

Do not clone from Resilio:

- overloading one quiet word across several incompatible maintenance intents
- forcing the operator to remember which motion classes survive which control
- leaving no first-class reviewed object that says which maintenance semantics were requested versus which were actually achieved

## Evaluation summary

Resilio still deserves credit for publishing the ingredients of maintenance semantics honestly.
But the current product/docs path still leaves a missing object:

> there is no first-class reviewed answer to `what exact kind of maintenance hold do I need, what still moves under it, and what stronger freeze sentence remains unsupported?`

AnonSync should therefore make **maintenance intent and maintenance semantics review** first-class product objects.
Every serious upgrade window, evidence capture, migration cut, destructive repair, and staged backlog release should publish requested hold class, achieved semantics, allowed residuals, counterpart requirements, transition plan, strongest safe sentence, and reopen boundary before the product treats `paused` or `backup` as enough.
