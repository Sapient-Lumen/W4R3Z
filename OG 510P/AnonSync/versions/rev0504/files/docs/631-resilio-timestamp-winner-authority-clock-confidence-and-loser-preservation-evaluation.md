# Resilio timestamp-winner authority, clock confidence, and loser-preservation evaluation

## What current Resilio still gets right

Another current official Resilio pass still deserves credit for being candid about one very ordinary truth:

- same-path divergent files really do need a winner story
- chronology really can depend on peer clocks and time zones
- offline return really can change which version becomes live
- loser preservation in Archive really is different from clean continuity
- restore timing really can matter because chronology is re-evaluated on live detection versus later rescan

That candor matters.
Resilio is not pretending all `conflicts` are the same.

## The sharper non-clone reason

The current official docs still show one especially sharp workflow failure:

> the product can still let `latest timestamp`, `latest file that comes online`, or `restored` stand in for **winner authority**, while the evidence about chronology trust and loser fate lives on other pages.

The current docs still spread that ambiguity across several pages:

- `Can I connect two pre-populated pre-existing folders?` still says same-hash files are skipped, other files merge, and differing-content same-path files let the latest timestamp win, replacing the remote copy.
- `What if several people make changes to the same file?` still says online edits replay in chronological order, but an offline peer that comes back later can still take priority over later online edits, with overwritten versions moved to Archive.
- `Time difference` still says Sync decides which file is newer by comparing modification times converted to GMT, and that more than 600 seconds of clock or time-zone drift produces warnings and empty-list fallout on mobile.
- `Using Archive for file versioning and restoring deleted files` still says restoring while Sync is not running can make the restored file look older on rescan and move it back into Archive.
- that same Archive article still says Archive does not itself say which peer made the change.

Those are useful implementation facts.
They are not a strong interface contract.

## Why this matters more than nicer conflict labels

This is not just wording polish.
It changes what the product is allowed to claim.
If the product can still say:

- `newer version won`
- `latest version restored`
- `older version archived`
- `conflict resolved`

without first publishing whether the winner basis was:

1. strong content/authority proof
2. guarded timestamp order
3. offline-return replay rule
4. manual settlement
5. blocked because chronology was not trustworthy enough

then the product is still collapsing four materially different objects:

- candidate comparison
- chronology evidence strength
- loser-preservation shape
- post-commit claim ceiling

That blur produces ordinary overclaims:

- `newest` when clocks or time zones are not trustworthy enough for that sentence
- `winner` when the ranking was only guarded timestamp order
- `restored` when the file may still be re-archived on the next rescan
- `safe overwrite` when the loser is only weakly preserved or hard to reopen
- `resolved` when the honest answer was still `manual settlement remains safer`

All of those can be false according to Resilio's own docs.

## Better product move for AnonSync

AnonSync should keep Resilio's candor that chronology, offline return, and loser preservation are real.
It should reject the silent-winner contract.

The better move is:

- same-path winner choice must have a first-class review page
- chronology evidence for that specific decision must show clock window, timestamp source, and ranking strength
- loser fate must be reviewed before apply, not rediscovered in hidden Archive later
- the receipt must later prove whether the event was a strong-authority winner, guarded timestamp winner, offline-return winner, manual settlement, or blocked divergence

## New page family required

This pass therefore adds four more direct replacement pages:

1. **Same-path winner review** — candidate set, winner basis, chronology confidence, and loser risk.
2. **Decision chronology evidence** — clock window, mtime source, and ranking strength for this exact decision.
3. **Losing-version fate** — Archive, branch, export, quarantine, and live-path protection before apply.
4. **Divergence-resolution receipt** — what won, why it won, what happened to the loser, and what stronger sentence was rejected.

## Condensed design verdict

Borrow Resilio's practical candor that chronology and loser preservation are real.
Do not clone a product contract where `latest timestamp`, `latest file that comes online`, or `restored` can still stand in for winner authority while clock confidence and loser fate remain spread across several help articles.
