# Plugin picker section counts (rev355)

The plugin loop had become honest almost everywhere by rev354:

- `plugin list` reported overall plugin counts
- `plugin reload NAME` confirmed resulting state
- `plugin info NAME` and `plugin errors [NAME]` started with the same compact summary dialect
- `pluginpick` rows and previews reused that dialect too

One small searchable gap remained: the picker still grouped rows under plain section labels like `Errors`, `Loaded`, and `Available`, which meant the picker quietly dropped one piece of glanceable state that nearby plugin commands had already learned to expose — **how big each bucket is right now**.

## What changed

`pluginpick` section labels are now count-aware:

- `Errors (1)`
- `Loaded (2)`
- `Available (3)`

That applies in the grouped section rows used by hostcalls / future UIs, and in current-row previews such as:

- `Errors (1): broken [error, deps:missingdep] — missing dependency: missingdep`
- `Loaded (2): alpha [loaded]`

The count tracks the **visible query-filtered slice**, not just the total unfiltered plugin tree.

## Why this matters

This is another tiny trust/flow move, not a new subsystem.

The searchable picker should not regress from the more glanceable command surfaces around it. When someone narrows the plugin list with a query, the picker should keep making the shape of the result obvious:

- how many broken plugins match this search?
- how many loaded plugins are still in view?
- am I looking at a singleton error bucket or a broader loaded set?

That keeps searchable plugin inspection aligned with the repo's current direction: concise, honest state surfaces that reduce inference for both humans and future LLMs.
