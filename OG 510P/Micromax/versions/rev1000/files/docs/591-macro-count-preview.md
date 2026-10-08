# Rev650 - truthful macro playback-count completion

## Why

Micromax had already made the macro surface much more honest before and after Enter: root `macro` showed live status, subcommand rows previewed blockers, alias rows stopped feeling second-class, blocked runtime paths echoed the same tiny witnesses, and exact slot rows stopped looking more runnable than the parent command. But one narrow seam remained one token later in the same automation loop: after `macro play NAME` or `macro run NAME`, the count token still had no preview substrate.

That left three small trust/flow problems in a row:

- `macro play demo 3` looked no more informative than a blank token even though Micromax already knew the slot existed and would replay three times.
- `macro play demo 0` or `macro run demo nope` stayed silent until runtime even though the same dispatcher already knew the eventual validation error.
- empty count completion could not tell the difference between a real slot and a missing one, so the command bar could look more optimistic than the runtime.

## What changed

Rev650 adds one tiny exact-count preview helper, `_prompt_macro_count_row(...)`, for `macro play|run NAME COUNT`. It keeps the behavior deliberately small and aligned with nearby macro truth surfaces:

- known slots preview `play Nx`
- malformed counts preview `count must be an int`
- non-positive counts preview `count must be > 0`
- playback-active states reuse the same `wait for playback` blocker witness as the parent play/run row
- missing slots stay typed as `missing macro` / `no such macro`

Completion also grows one tiny ordered common-count menu — `1 2 3 5 10` — but only when the typed slot actually exists. That keeps the path helpful without teaching the wrong next step for missing targets.

## Validation

Focused prompt tests cover:

- exact `macro play|run NAME COUNT` rows for good counts, bad integers, non-positive counts, missing slots, and playback blockers
- ordered common-count suggestions for known slots
- no optimistic count menu for missing slots

## Result

The macro surface keeps one more token of pre-Enter truth. Once Micromax knows which macro will run, the count token now says whether Enter will replay, reject, or wait — instead of hiding that answer until runtime.
