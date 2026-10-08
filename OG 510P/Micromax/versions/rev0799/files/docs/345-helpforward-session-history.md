# Rev403: docs forward history should stay local, inspectable, and honest

## What changed

- Micromax now has `helpforward` as the small forward twin of `helpback`
- successful `helpback` now preserves the current docs page as a forward target before reopening the earlier page
- successful `helpforward` restores the saved forward target without re-pushing or fabricating extra history
- ordinary docs opens (`help docs ...`, `help QUERY` docs fallback, `helpfollow`, picker opens) clear stale forward history when they branch to a different page
- `status_model()` / `help_navigation_model()` now expose `help_forward_*` fields together with `help_navigation_scope=session` and `help_navigation_persisted=0`

## Why

Rev402 made docs history exact and inspectable, but it still only modeled one side of the tiny navigation loop.
After a `helpback`, Micromax knew where you came from, yet future UIs, scripts, and humans still could not retrace that return path except by replaying a different navigation choice.

That asymmetry mattered because the project had already crossed the line from "terminal feedback" into a genuinely inspectable docs-navigation surface. Once current page and back target were modeled explicitly, the missing forward half became a real gap rather than a missing convenience.

The right import from the other datacubes was not "full browser history everywhere".
It was the smaller rule: **keep local navigation history witnessable, keep branch semantics explicit, and say when the history is only session-local instead of letting it look durable by accident.**

## Resulting contract

Docs navigation now behaves like a tiny local browser with narrower scope:

- `helpback` and `helpforward` are separate actions with separate typed empty-stack feedback
- stale missing-doc forward/back targets keep the replay action visible too: `helpback: missing doc: TOPIC` / `helpforward: missing doc: TOPIC`
- a new docs branch clears older forward history instead of mixing incompatible futures
- docs-navigation state is still inspectable, but now says plainly that it is **session-local** rather than persisted

## Non-goal

This is **not** full editor history and **not** saved-state persistence.
Micromax is only modeling the docs/help navigation lane here.
