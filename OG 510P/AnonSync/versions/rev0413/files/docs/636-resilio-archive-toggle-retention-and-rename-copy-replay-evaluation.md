# Resilio Archive-toggle retention, replay dependence, and recovery-ceiling evaluation

## What current Resilio still gets right

Another current official Resilio pass still deserves credit for being candid about one ordinary but important truth:

- Archive is not just a passive graveyard for old bytes
- Archive policy changes practical replay behavior for rename and copy cases
- retention and access limits really vary by platform and path class
- per-share controls really can narrow recovery power differently on desktop, Android, and iOS

That candor matters.
Resilio is not pretending Archive is only a generic `keep versions` checkbox.

## The sharper non-clone reason

The current official docs still show one especially sharp workflow failure:

> the product can still let `Use Archive` read like a simple retention preference even though the same toggle also changes remote rename/copy replay efficiency, local recovery scope, and platform-specific access ceilings.

The current docs still spread that meaning across several pages:

- `Folder Preferences` still says Archive stores remotely changed or deleted prior versions, and that disabling it also makes remote renames or copies re-download instead of being replayed locally.
- `What happens when file is renamed` still says rename reuse on remote peers works by moving the old name to Archive and restoring it under the new name when the hash matches.
- `Using Archive for file versioning and restoring deleted files` still says retention defaults differ by desktop and mobile, Android Archive does not work for SD-card shares, and Archive is not accessible on iOS.
- current iOS share details still say `Use Archive` is the thing through which renamed files are processed.
- current Android share details still expose `Use Archive` only for shares on internal phone memory.

Those are useful implementation facts.
They are not yet one strong interface contract.

## Why this matters more than a preference label

This is not just wording polish.
It changes what the product is allowed to claim.
If the product can still say:

- `Archive disabled`
- `Use Archive off`
- `history disabled`
- `recovery reduced`

without first publishing whether that also means:

1. remote rename/copy replay will degrade into re-download
2. this seat loses local rollback bytes entirely or only shortens their lifetime
3. the current surface/path class could not access Archive anyway
4. some other seat remains the real recovery witness
5. later restore language becomes weaker than before

then the product is still collapsing four materially different objects:

- retention policy
- byte-reuse assistance
- local recovery access
- claim ceiling after the change

That blur produces ordinary overclaims:

- `history only` when the change also removes cheap rename/copy replay help
- `Archive off here` when another seat still silently holds the only useful rollback witness
- `recovery disabled` when the honest answer is only `local recovery disabled on this seat`
- `safe preference change` when the next replay-heavy rename now costs fresh transfer

All of those can be false according to Resilio's own docs.

## Better product move for AnonSync

AnonSync should keep Resilio's candor that Archive affects both rollback and replay.
It should reject the checkbox-only contract.

The better move is:

- archive-bearing policy must have a first-class retention/replay dependence page
- any archive-policy mutation must preview retained-byte loss, replay-cost change, and seat-local access limits before apply
- the operator must be able to see which seat still has the strongest recovery ceiling after the change
- the receipt must later prove whether the change only narrowed retention, also weakened rename/copy replay, or changed neither because the surface never had local Archive access anyway

## New page family required

This pass therefore adds four more direct replacement pages:

1. **Retention/replay dependence** — what this archive-bearing policy currently supports besides simple retention.
2. **Archive-policy change review** — what bytes, replay paths, and access limits would change if the toggle moves.
3. **Local recovery ceiling** — what this seat can still recover locally, for how long, and with what access caveats.
4. **Archive-policy receipt** — what changed, what did not, and what stronger sentence is now forbidden.

## Condensed design verdict

Borrow Resilio's practical candor that Archive affects both rollback and rename/copy replay.
Do not clone a product contract where `Use Archive` still looks like a harmless preference while recovery locality, replay cost, and platform/path ceilings remain spread across several help articles.
