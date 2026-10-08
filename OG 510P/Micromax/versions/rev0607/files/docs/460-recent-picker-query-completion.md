# Recent picker query completion truth

Rev518 closes one small flow/trust seam in Micromax's recent-file loop.

Micromax already had the nearby honest surfaces:

- plain `recent` showed numbered MRU inventory with tiny file/state truth
- rev512 made command-bar completion for `recent [N|clear]` explicit before Enter
- exact `showrecent PATH` completion rows already reused one visible recent-file row with section/location/disk/action truth
- rev517 made `recentpick` / `recentdirpick` submit feedback keep the selected pre-open MRU slot instead of rediscovering a new one after MRU mutation

But one small command-bar seam still lingered at the filtered picker entry point:

- `recentpick QUERY` and `recentdirpick QUERY` accepted a free-form first argument
- that argument still had no completion help at all
- so the recent-file loop went blind again exactly when you wanted to prefilter the picker toward one known target

## What changed

Rev518 keeps the change deliberately small.

- command-bar completion for `recentpick QUERY` / `recentdirpick QUERY` now offers matching recent-file paths
- those completion rows reuse the same exact recent-file metadata already trusted by `showrecent PATH`
- matching rows keep the visible MRU slot plus the same small location/disk/action truth Micromax already knows
- focused tests pin both filtered picker commands and the adjacent `showrecent` completion path

## Why it matters

This is tiny, but it keeps the recent-file loop coherent.

If Micromax already knows that one query token matches a specific recent-file target — and already knows how to describe that target honestly for `showrecent PATH` — the filtered picker entry points should reuse that same truth instead of becoming a blind free-text gap. Keeping one exact recent row visible before the picker opens makes the command bar easier to trust and easier to drive quickly.

## Focused tests

- `tests/test_editor_prompt_completion_hostcalls.py`
