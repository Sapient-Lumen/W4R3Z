# Rev520: recent picker rows are now first-class hostcall surfaces

## Why

The live `recentpick` / `recentdirpick` prompts already knew more than the
headless scripting boundary: they could rank one query, group rows by project
root or directory, and show the same small MRU/location/disk/action cues humans
saw before Enter. But scripts and future UIs still had no direct way to inspect
that exact row surface. The only workaround was opening a prompt and scraping
transient `ed.prompt-suggestion-rows`, which made replay and testing noisier
than necessary.

## What changed

Rev520 adds two tiny hostcalls and matching convenience words:

- `ed.recent-prompt-rows ( query -- rows )` / `recent-prompt-rows`
- `ed.recent-dir-prompt-rows ( query -- rows )` / `recent-dir-prompt-rows`

Both return the same visible `[[path kind menu info] ...]` rows the live
`recentpick` / `recentdirpick` prompts would show for one query. The
project-grouped picker and the directory-grouped picker keep their different
section policies, but scripts can now inspect either one directly without
opening prompt state first.

## Why it matters

This keeps the editor more headless-first and more replayable:

- future UIs can ask for the exact picker rows they want to render
- tests can pin the ranked pre-open row surface directly
- in-archive LLMs can inspect the picker state without driving a transient
  prompt
- the host boundary now matches another small but real human-facing row surface
  instead of forcing prompt scraping

## Contract

The row shape matches other visible prompt rows: `[[path kind menu info] ...]`.
Empty or failing queries return `[]` rather than raising.
