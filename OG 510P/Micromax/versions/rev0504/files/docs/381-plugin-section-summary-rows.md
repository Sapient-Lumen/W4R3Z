# Rev439 — plugin state buckets get one tiny named summary row

## What changed

Micromax already had strong plugin inspection surfaces:

- `plugin list` exposed the broad plugin inventory
- `plugin info NAME` / `plugin errors [NAME]` handled exact detail
- `pluginpick` and `ed.plugin-section-rows` exposed grouped searchable plugin buckets
- grouped picker labels already kept visible counts like `Errors (1)` / `Loaded (2)` / `Available (3)`

But one small inspectability seam still remained: broad plugin state was easy to browse or list in full, yet there was still no tiny count-aware answer for what major plugin buckets currently exist without walking grouped picker rows or re-parsing the full `plugin list` line.

Rev439 keeps the fix deliberately small:

- add `plugin_section_summary_rows(QUERY)` in the editor core
- expose it as `ed.plugin-section-summary-rows`
- add plain `showplugins [QUERY]` for humans

## Row shape

`plugin_section_summary_rows(QUERY)` / `ed.plugin-section-summary-rows` return:

```
[label count sample_name sample_detail]
```

Where:

- `label` is the coarse plugin bucket (`Errors`, `Loaded`, `Available`)
- `count` is the number of currently visible rows in that bucket
- `sample_name` reuses the first visible plugin name in that bucket
- `sample_detail` reuses the first visible row's detail text (`info` when present, otherwise `menu`)

Examples:

- `['Errors', 1, 'broken', 'missing dependency: dep']`
- `['Loaded', 2, 'alpha', '[loaded, v1.0.0]']`

The shape intentionally stays tiny. It complements `ed.plugin-section-rows` instead of replacing it.

## Why this matters

This is a small trust/flow improvement. Plugins already had full inventory and searchable grouped rows, but there was still no official first-stop register for the simpler question future humans/LLMs often ask first:

> what broad plugin-state buckets exist right now?

The new summary rows and plain `showplugins [QUERY]` keep that answer inspectable without reopening picker state, walking every grouped row, or scraping counts back out of human command text.

## Focused tests

- `tests/test_editor_pluginpick.py`
- `tests/test_editor_capabilities_registry.py`

## Next tiny seams

- some other grouped picker families still only expose their full grouped row shapes and not a lighter summary sibling
- broad plugin inventory is now honest at both full-list and grouped-summary levels, but other query-aware inventories may still want the same tiny first-stop register later
