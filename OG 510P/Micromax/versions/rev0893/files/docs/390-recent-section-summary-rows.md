# Recent section summary rows

Rev448 closes one small symmetry gap in Micromax's recent-file navigation loop.

Micromax already had the right recent-file surfaces:

- plain `recent` exposed the MRU inventory for humans
- `recent_inventory_rows()` / `ed.recent-inventory-rows` exposed that same ordered register to scripts and future UIs
- `recentpick [QUERY]` / `ed.recent-section-rows` already made grouped recent-file project buckets browseable
- `recentdirpick [QUERY]` / `ed.recent-dir-section-rows` already offered the coarser directory-grouped sibling when project buckets were not the right scan shape

But one small inspectability seam still lingered underneath that model: recent-file state was stronger at flat full inventory and full grouped browse state than at the smaller first question future humans/LLMs often ask first:

> what broad recent-file buckets are visible right now, and roughly what lives in each one?

Rev448 keeps the follow-up deliberately small:

- add one tiny count-aware project-bucket summary register
- expose it as `ed.recent-section-summary-rows`
- add one plain side-effect-free human command, `showrecentgroups [QUERY]`
- keep the row shape aligned with the newer summary surfaces instead of inventing a recent-only dialect

## Shared row shape

`recent_section_summary_rows(QUERY)` / `ed.recent-section-summary-rows` return:

```text
[[label count sample_name sample_detail] ...]
```

Where:

- `label` is the visible project-root bucket label already used by grouped `recentpick`
- `count` is the number of matching visible recent-file rows in that bucket
- `sample_name` is the first visible recent-file path in that bucket
- `sample_detail` is the first visible row's detail field, typically the path relative to the detected project root (or the existing fallback detail when no project root is known)

That keeps the broad-summary layer aligned with the grouped picker layer instead of forcing scripts to reopen `recentpick` or walk every grouped row just to learn what major recent buckets exist.

## Human command

Plain command-bar discovery gets the same side-effect-free surface:

```text
showrecentgroups [QUERY]
```

Example:

```text
showrecentgroups intro
showrecentgroups intro: 1 section(s), 1 file(s)
/tmp/demo: 1 (e.g. /tmp/demo/guide/intro.md — guide/intro.md)
```

Zero-result queries stay explicit instead of collapsing to silence:

```text
showrecentgroups nope
showrecentgroups nope: 0 section(s), 0 file(s)
```

## Why this matters

This is a small trust/flow improvement for everyday file movement.

Recent files were already inspectable as a flat MRU inventory and browseable as grouped `recentpick` / `recentdirpick` rows, but there was still no official first-stop register for the smaller broad question of what recent-file buckets currently exist. The new summary rows and plain `showrecentgroups [QUERY]` keep that answer inspectable without opening picker state, scraping grouped headers, or walking every grouped row.

That keeps the recent-file loop aligned with the other tiny honest summary surfaces Micromax has been adding for topics, docs, plugins, hooks, keymaps, options, palette buckets, and buffers.

## Tests

Focused coverage pins the contract in:

- `tests/test_editor_buffer_mru_and_closeall.py`
- `tests/test_editor_capabilities_registry.py`

## Next tiny seams

- `recentdirpick` still only exposes its full grouped directory rows, not a matching lighter directory-summary sibling
- some exact inventory surfaces still depend on plain command formatting even when adjacent grouped/summary layers are now shared
