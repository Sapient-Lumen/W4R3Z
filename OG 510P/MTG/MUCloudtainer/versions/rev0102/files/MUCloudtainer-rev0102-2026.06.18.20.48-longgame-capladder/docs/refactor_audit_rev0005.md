# rev0005 Refactor / Audit Notes

## Refactor: pregame logic extracted

Opening-hand logic now lives in `src/muc5/mulligan.py` instead of being baked directly into `start_game`. This keeps the engine's start-game function readable and makes future learned mulligan decisions easier to plug in.

## Refactor: card-conservation invariant

`src/muc5/invariants.py` adds a reusable card-conservation report. This is more useful than ad hoc tests because it can be run while games are in progress, including unusual limbo states.

Special limbo states now accounted for:

```text
Jace legend-rule choice: old/new Jace before keep choice
pending combat: attacking Overlords after removed from ready pool, before damage
stack: spells removed from hand but not yet resolved/countered
```

## Bug fixed during audit

Jace ultimate previously used a synthetic exile marker:

```text
JaceExiledLibraryCards += len(library)
library.clear()
```

That was enough for win/loss flow but bad for conservation and future public-zone audits. rev0005 now exiles the actual cards by card ID.

## Audit script cleanup

`scripts/audit_cube.py` was rewritten to remove duplicated rev0004 checks and to add rev0005 checks for:

```text
mulligan policy plumbing
mulligan feature visibility
card conservation after mulligan start
mulligan probe rows
sampled action-space summary
required rev0005 files
```

## Caution

The invariant is owner-based and five-card-specific. It is deliberately not a generic Magic zone invariant. That is good for MUC-5: smaller, faster, and easier to trust.
