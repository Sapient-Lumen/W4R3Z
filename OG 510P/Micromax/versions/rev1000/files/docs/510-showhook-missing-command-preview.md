# Rev568: keep exact `showhook NAME` completion truthful on missing targets

## Why

`showhook NAME` was already honest after Enter: known hooks printed the shared exact
handler-count/sample row, and missing names failed as `showhook: not a hook: NAME`.
But the command bar still only surfaced known hook names during completion, so a
typed missing target simply vanished from the suggestion list before Enter.

That made one-hook inspection slightly less trustworthy than nearby exact surfaces
like `showplugin NAME`: Micromax already knew the typed token was not a hook, but
the prompt could not say so yet.

## What changed

- `_prompt_hook_row(...)` now accepts `strict_missing=True`
- exact `showhook` suggestion rows now reuse that helper
- token completion preserves an unmatched typed hook name long enough to render
  `missing hook · not a hook` instead of dropping the token outright
- focused prompt-completion tests pin both preserved-token candidates and the
  new missing-hook row

## Result

Exact one-hook inspection now stays honest before Enter too:

- known hook: `1 handler (e.g. h1#cfg) · h1#cfg@<file>:line:col`
- missing hook: `missing hook · not a hook`

This is intentionally small. It does not widen hook semantics or invent a new
dialect; it just lets the command bar surface the same missing-hook truth the
real command already knows.
