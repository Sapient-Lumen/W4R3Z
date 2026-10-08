# Rev352: plugin picker error rows should open plugin errors, not generic info

Rev347 through rev351 made the **plugin inspection loop** increasingly honest:

- `plugin list` became a compact health inventory
- `plugin reload NAME` confirmed the resulting state
- `plugin info NAME` began with the same summary dialect
- `plugin errors NAME` distinguished unknown, healthy, and broken plugins
- plain `plugin errors` became grouped inventory instead of a raw log dump

That left one small but visible mismatch behind: **picker-driven selection from the `Errors` section**.

Before this revision, selecting a broken plugin from `pluginpick` still ran `plugin info NAME`. That was not wrong, but it was lower-value than the surface the picker itself was already hinting at. When a plugin is grouped under **Errors**, the most useful next thing is usually the filtered error detail path, not the generic metadata view.

## What changed

`pluginpick` now routes selections like this:

- loaded plugin -> `plugin reload NAME`
- broken plugin with recorded load errors -> `plugin errors NAME`
- other known plugin -> `plugin info NAME`

So a broken selection now opens with the same explicit summary dialect used elsewhere in the plugin loop:

- `plugin errors: b [error, deps:missingdep]`
- `  errors: 1`
- `    - missing dependency: missingdep`

## Why this is worth doing

This is a tiny change, but it improves **flow** and **trust** at the same time:

- the picker's section labels become behaviorally meaningful
- the most common next question for an error-row selection (“why is this broken?”) is answered immediately
- searchable plugin navigation stops sending broken rows through a lower-information path

This keeps the plugin loop coherent:

1. inspect plugin health with `plugin list` or `pluginpick`
2. reload loaded plugins
3. inspect healthy/available plugins with `plugin info NAME`
4. inspect broken plugins with `plugin errors NAME`

That is a better match for the repo's current direction: small, explicit, inspectable flows that reduce inference.
