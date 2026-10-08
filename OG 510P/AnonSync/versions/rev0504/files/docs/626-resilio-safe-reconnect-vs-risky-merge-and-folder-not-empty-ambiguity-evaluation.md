# Resilio safe-reconnect versus risky-merge and `Folder not empty` ambiguity evaluation

## What current Resilio still gets right

Another current official Resilio pass still deserves credit for being candid about one very practical truth:

- existing local directories really can matter during bind
- reconnect to the old directory really is a normal case
- pre-populated trees really can be reused
- merge/overwrite risk on non-empty targets is real
- linked-device path choice really can require a different seat posture before the operator reaches the intended directory

That candor matters.
Resilio is not pretending every bind starts from an empty lane.

## The sharper non-clone reason

The current official docs still show one especially sharp workflow failure:

> the same small `Folder not empty` / `Add anyway` warning is still expected to cover both **safe same-lineage reconnect** and **risky merge into an existing populated tree**.

The current docs still spread that ambiguity across several pages:

- `Folder not empty` still says the warning appears both when adding shared files to an already existing folder **and** when reconnecting a folder to a location where it synced before.
- The same article still warns that files already present in the receiving folder might be deleted or overwritten.
- The same article also still says that if the operator is reconnecting to the location where the folder synced before, they should just ignore the message and proceed.
- `Can I connect two pre-populated pre-existing folders?` still says click `OK` on the non-empty confirmation, and on linked devices often route the operator through `Disconnected` posture or disconnect/reconnect ritual before picking the existing directory.
- `Disconnecting and Removing Folders` still says reconnect may draft a different default path, may create a `(1)` sibling, and may again ask the operator to accept `Destination folder is not empty. Add anyway?`
- `How to manually set the location of the folders synced across linked devices?` still says custom placement for linked-device arrivals is exercised by making the seat `Disconnected` first.

Those are useful implementation facts.
They are not a strong interface contract.

## Why this matters more than nicer warnings

This is not just dialog polish.
It changes what the product is allowed to claim.
If the same warning can mean both:

- `yes, this is the old tree, reconnect is appropriate`
- and `careful, this existing tree may lose or overwrite bytes`

then the product is still collapsing four materially different objects:

1. same-lineage reconnect proof
2. non-empty-target divergence comparison
3. preserve-before-adopt decision
4. post-commit safe sentence

That blur produces ordinary overclaims:

- `connected` when continuity was only guarded, not proven
- `restored old location` when the path was only same-name or default-root convenient
- `warning accepted` when the real event was timestamp-guided merge with overwrite risk
- `add anyway` when the stronger honest next step was preserve-first compare
- `reconnect succeeded` when the product really created a fresh sibling or merged against a different tree

All of those can be false according to Resilio's own docs.

## Better product move for AnonSync

AnonSync should keep Resilio's candor that reconnect and pre-populated reuse are real.
It should reject the overloaded warning contract.

The better move is:

- same-lineage reconnect must have a first-class proof page
- non-empty target comparison must classify identical, local-only, remote-only, and same-path divergent material before commit
- preserve-before-adopt must be an ordinary choice whenever local material could be deleted, overwritten, or lose its easiest recovery path
- the receipt must later prove whether the event was `same-lineage reconnect`, `guarded merge`, `preserve-first attach`, or `blocked`

## New page family required

This pass therefore adds four more direct replacement pages:

1. **Same-lineage reconnect proof** — remembered path, subject evidence, and target equivalence.
2. **Non-empty target divergence review** — compared classes, same-path disagreement, and overwrite risk.
3. **Preserve-before-adopt** — copy-aside, quarantine, side-branch, and reversibility before merge.
4. **Reconnect-vs-merge receipt** — what was proven, what stayed guarded, and what preservation step actually happened.

## Condensed design verdict

Borrow Resilio's practical candor that reconnect and pre-populated reuse are real.
Do not clone a product contract where the same `Folder not empty` warning is still expected to stand for both harmless same-lineage reconnect and risky merge into existing bytes.
