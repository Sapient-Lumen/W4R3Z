# Resilio manual-bind right, default-root policy, and duplicate-suffix fallback evaluation

## What current Resilio still gets right

Another current official Resilio pass still deserves credit for being candid about one real convenience cluster:

- linked devices really do have a seat-level default connect mode
- mobile really can have a default folder / Simple Mode posture
- reconnect really can propose a path for you
- same-name collisions really do happen during automatic placement
- existing material really can still be intentionally re-adopted instead of always starting empty

That candor matters.
Resilio is not pretending that path placement is trivial.
It is admitting that seat defaults, root suggestions, reconnects, and pre-existing local material all shape the operator's next step.

## The sharper non-clone reason

The current official docs still show that Resilio makes one important right hard to exercise cleanly:

> the right to bind **this one incoming or reconnecting share** to the path I mean, without first mutating the whole seat posture or accepting duplicate-creation folklore.

The current docs still spread that right across several pages:

- `Synchronization Modes` and `How to manually set the location of the folders synced across linked devices?` still say linked-device default connect mode controls what later arrivals do, and that if you want to choose a custom location for new linked-device arrivals you should switch the device into `Disconnected` first.
- `Settings on mobile platforms` and `Simple Mode (Android)` still say Android default-folder / Simple Mode auto-places new shares and adds `(1)` when the same name already exists.
- `Disconnecting and Removing Folders` still says reconnect may propose a default path different from the original one and may create a new directory with `(1)` suffix, and that re-establishing the old directory requires changing the path manually.
- The same reconnect guidance still says that on Android the operator may see `Destination folder is not empty. Add anyway?` and should click `OK`.

Those are useful implementation facts.
They are not a strong product contract.

## Why this is more than cosmetic UX debt

This is not just about nicer dialogs.
It changes what the product is allowed to claim.
If the easiest path to safe one-share placement is still `change whole-device mode`, `disable Simple Mode`, `disconnect`, `connect`, `ignore Add anyway`, and later clean up duplicates, then the product is still blurring together four different objects:

- seat-wide future-arrival defaults
- one-share bind choice
- existing-folder adoption
- duplicate-risk handling

That blur produces several ordinary overclaims:

- `changing mode is how you place this share`
- `default path is the right path unless you opt out`
- `same-name collision can be safely handled by suffixing`
- `existing non-empty target only needs a warning, not an adoption verdict`
- `reconnect succeeded` when the product really created a fresh sibling directory beside the intended old path

All of those can be false according to Resilio's own docs.

## Better product move for AnonSync

AnonSync should keep Resilio's candor that defaults, suggested roots, reconnects, and pre-existing local bytes are real.
It should reject the ritualized contract.

The better move is:

- every incoming or reconnecting share always retains a **manual bind right**
- seat defaults may suggest roots and byte posture, but may not become the only practical way to place one share safely
- suffix fallback such as `(1)` is never a silent or routine duplicate-resolution strategy; it is a **review trigger**
- non-empty existing targets require **adoption / compare / reject** review, not `Add anyway`
- the receipt must later prove whether the bind consumed a default suggestion, restored a remembered path, adopted an existing directory, or created a new clean bind

## New page family required

This pass therefore adds four more direct replacement pages:

1. **Future-arrival defaults** — seat scope, default root, and manual-bind right.
2. **Bind choice review** — this share versus seat default, suggestion source, and current-share-only override.
3. **Existing-folder adoption review** — non-empty target, lineage proof, and duplicate-suffix veto.
4. **Arrival bind receipt** — what default was in force, what bind right was exercised, and what adoption verdict actually happened.

## Condensed design verdict

Borrow Resilio's practical candor that arrival defaults, default roots, reconnect proposals, and pre-existing paths are real.
Do not clone a product contract where the operator must still change whole-seat mode or accept `(1)` duplicate folklore in order to safely place one share.
