# Recent directory section summary rows

Rev449 closes the remaining small symmetry gap in Micromax's recent-file navigation loop.

Micromax already had the right recent-file surfaces:

- plain `recent` exposed the MRU inventory for humans
- `recent_inventory_rows()` / `ed.recent-inventory-rows` exposed that same ordered register to scripts and future UIs
- `recentpick [QUERY]` / `ed.recent-section-rows` already made grouped recent-file project buckets browseable
- `recentdirpick [QUERY]` / `ed.recent-dir-section-rows` already offered the coarser directory-grouped sibling when project buckets were not the right scan shape
- rev448 added `recent_section_summary_rows()` / `ed.recent-section-summary-rows` / `showrecentgroups [QUERY]` for the lighter project-bucket summary question

But one small inspectability seam still lingered underneath that model: directory-grouped recent-file state still exposed full grouped browse state without a matching first-stop answer to the smaller question future humans/LLMs often ask first:

> what broad recent-file directory buckets are visible right now, and roughly what lives in each one?

Rev449 keeps the follow-up deliberately small:

- add one tiny count-aware directory-bucket summary register
- expose it as `ed.recent-dir-section-summary-rows`
- add one plain side-effect-free human command, `showrecentdirgroups [QUERY]`
- add one small convenience word, `recent-dir-section-summaries`
- keep the row shape aligned with the newer summary surfaces instead of inventing a recentdir-only dialect

## Shared row shape

`recent_dir_section_summary_rows(QUERY)` / `ed.recent-dir-section-summary-rows` return:

```text
[[label count sample_name sample_detail] ...]
```

Where:

- `label` is the visible parent-directory bucket label already used by grouped `recentdirpick`
- `count` is the number of matching visible recent-file rows in that bucket
- `sample_name` is the first visible recent-file path in that bucket
- `sample_detail` is the first visible row's detail field, which for directory-grouped rows is the visible parent directory label

That keeps the broad-summary layer aligned with the grouped directory picker instead of forcing scripts to reopen `recentdirpick` or walk every grouped row just to learn what major recent-directory buckets exist.

## Human command

Plain command-bar discovery gets the same side-effect-free surface:

```text
showrecentdirgroups [QUERY]
```

Example:

```text
showrecentdirgroups b.txt
showrecentdirgroups b.txt: 1 section(s), 1 file(s)
/tmp/demo/proj/tests: 1 (e.g. /tmp/demo/proj/tests/b.txt — /tmp/demo/proj/tests)
```

Zero-result queries stay explicit instead of collapsing to silence:

```text
showrecentdirgroups nope
showrecentdirgroups nope: 0 section(s), 0 file(s)
```

## Why this matters

This is a small trust/flow improvement. Recent files now expose a clean three-scale loop in both grouping modes:

- flat MRU inventory (`recent` / `ed.recent-inventory-rows`)
- full grouped browse state (`recentpick` / `ed.recent-section-rows`, `recentdirpick` / `ed.recent-dir-section-rows`)
- tiny count-aware broad summaries (`showrecentgroups` / `ed.recent-section-summary-rows`, `showrecentdirgroups` / `ed.recent-dir-section-summary-rows`)

That makes the archive easier to inspect headlessly without teaching future callers to scrape grouped picker rows when they only need the broad directory buckets.

## Focused tests

- `tests/test_editor_buffer_mru_and_closeall.py`
- `tests/test_editor_capabilities_registry.py`

## Next tiny seams

- some exact inventory surfaces still depend on plain command formatting even when adjacent grouped/summary layers are now shared
- other search-first picker families may still be worth a tiny exact detail row if one concrete daily loop keeps needing it
