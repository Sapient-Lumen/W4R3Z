# Rev653: macro playback-blocked count menus stop advertising repeats

## Why

Rev650 made exact `macro play|run NAME COUNT` rows truthful: typed counts already
said `play Nx`, validation errors, `no such macro`, or `wait for playback`.
But the empty count menu still had one optimistic blind spot. During active
playback, `macro play demo ` and `macro run demo ` still offered the friendly
common-repeat list `1 2 3 5 10`, which implied a next step that Micromax could
already prove was blocked.

That made the suggestion menu slightly less honest than the exact row beneath
it. Trust-first command surfaces should not advertise impossible next steps just
because the user has not typed the final token yet.

## What changed

- `_prompt_command_token_candidates(...)` now checks playback state before
  offering the common repeat-count menu for `macro play|run NAME `.
- When playback is active and the target slot exists:
  - empty count completion returns no suggestions
  - a typed exact count (for example `2`) is still preserved as a fallback
    candidate so the exact blocker row can stay visible
- Exact count rows still come from `_prompt_macro_count_row(...)`, so the
  existing blocker wording remains shared and consistent.

## Why this is the right size

This is a tiny trust/flow cleanup, not a new macro feature. It does not change
runtime playback rules, count parsing, or macro storage. It only prevents the
empty suggestion menu from getting ahead of what the runtime already knows.

## Tests

Focused prompt tests cover:

- no `1 2 3 5 10` menu during active playback for `macro play demo `
- preserved typed fallback candidate for `macro run demo 2`
- exact typed-count row still showing `playing · demo (1 step) · wait for
  playback`
