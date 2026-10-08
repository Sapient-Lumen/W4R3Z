# Rev456 — plugins get one tiny exact detail row

## What changed

Micromax already had the right broad plugin surfaces:

- plain `plugin list` exposed the current state/version/dependency/error-count inventory for humans
- `pluginpick [QUERY]` / `ed.plugin-section-rows` exposed grouped browse state by `Errors`, `Loaded`, and `Available`
- rev439 added `showplugins [QUERY]` / `plugin_section_summary_rows(QUERY)` / `ed.plugin-section-summary-rows` for the lighter broad-summary question

But one small inspectability seam still remained: there was still no official side-effect-free exact answer to the adjacent question future humans/LLMs often ask next:

> what is true about this one plugin right now?

Rev456 keeps the fix deliberately small:

- add `plugin_detail_row(NAME)` in the editor core
- expose it as `ed.plugin-detail-row`
- add a small convenience word, `plugin-detail`
- add plain `showplugin NAME` for humans
- make `showplugin` completion reuse that same exact metadata

## Row shape

`plugin_detail_row(NAME)` / `ed.plugin-detail-row` return:

```text
[query name state version deps error_count detail]
```

Where:

- `query` preserves the caller's requested plugin spelling
- `name` is the canonical known plugin name
- `state` is `loaded`, `available`, or `error`
- `version` is the current plugin version when known
- `deps` is the same comma-joined dependency summary already used by the tiny inventory surfaces
- `error_count` is the current recorded load-error count for that plugin
- `detail` is the last load error when the plugin is broken, otherwise the plugin description when available

The shape intentionally stays smaller than full `plugin info NAME` / `plugin errors NAME`. Those commands still own the broader dependency/error walkthroughs.

## Human command

Plain command-bar inspection gets the same side-effect-free exact surface:

```text
showplugin NAME
```

Examples:

```text
showplugin a
plugin a [loaded, v1.0.0] errors=0 — demo plugin
```

```text
showplugin b
plugin b [error, deps:missingdep] errors=1 — missing dependency: missingdep
```

Missing plugins stay typed and boring:

```text
showplugin nope
showplugin: no such plugin: nope
```

## Why this matters

This keeps plugin inspection coherent at three useful scales:

- flat inventory via `plugin list` / `plugin_inventory_rows()` / `ed.plugin-inventory-rows`
- grouped browse state via `pluginpick` / `ed.plugin-section-rows` plus broad summaries via `showplugins [QUERY]` / `ed.plugin-section-summary-rows`
- one exact side-effect-free row via `showplugin NAME` / `plugin_detail_row(NAME)` / `ed.plugin-detail-row`

That is a small trust win because scripts and future UIs no longer need to reopen verbose multi-line plugin detail just to inspect one known plugin, and a small flow win because the human command path now matches the headless row directly.

## Focused tests

- `tests/test_editor_pluginpick.py`
- `tests/test_editor_prompt_completion_hostcalls.py`
- `tests/test_editor_capabilities_registry.py`

## Next tiny seams

- some multi-line exact inspection paths still do not have a smaller one-row sibling
- a few picker/detail surfaces still expose broad summaries before they expose exact one-item rows
