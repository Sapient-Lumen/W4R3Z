# Recent detail row

Rev451 closes one small exact-inspection seam in Micromax's recent-file loop.

Micromax already had the right broad recent surfaces:

- plain `recent` exposed the MRU inventory for humans
- `recent_inventory_rows()` / `ed.recent-inventory-rows` exposed that same ordered register to scripts and future UIs
- `recentpick [QUERY]` / `ed.recent-section-rows` exposed grouped project-bucket browse state
- `recentdirpick [QUERY]` / `ed.recent-dir-section-rows` exposed the directory-grouped sibling
- rev448 / rev449 added `showrecentgroups [QUERY]` / `ed.recent-section-summary-rows` and `showrecentdirgroups [QUERY]` / `ed.recent-dir-section-summary-rows` for the lighter broad summary question

But one small inspectability seam still lingered underneath that model: there was still no official side-effect-free exact answer to the smaller question future humans/LLMs often ask next:

> what is true about this one recent file right now?

The closest plain human surface was still mutating `recent N`, which opens a file. Scripts could inspect the whole MRU inventory and filter it themselves, but there was no tiny exact register matching a plain human `show...` surface.

Rev451 keeps the follow-up deliberately small:

- add one tiny exact recent-detail row
- expose it as `ed.recent-detail-row`
- add one small convenience word, `recent-detail`
- add one plain side-effect-free human command, `showrecent PATH`

## Exact row shape

`recent_detail_row(PATH)` / `ed.recent-detail-row` return:

```text
[query path index position active open dirty readonly section detail]
```

Where:

- `query` is the exact path spelling the caller asked about
- `path` is the canonical stored MRU entry that matched that query via Micromax's existing best-effort path normalization
- `index` is the current 1-based MRU slot
- `position` is the current primary cursor label for still-open buffers as `line:col`
- `active` / `open` / `dirty` / `readonly` are `0` / `1` flags matching the plain `recent` inventory cues
- `section` is the same visible project-root bucket label grouped `recentpick` already uses
- `detail` reuses that grouped project row's detail field, typically the path relative to the detected project root

Example:

```text
['/tmp/demo/guide/intro.md', '/tmp/demo/guide/intro.md', 2, '2:1', 1, 1, 1, 0, '/tmp/demo', 'guide/intro.md']
```

The shape intentionally stays small. Full grouped browse state still belongs to `recentpick` / `recentdirpick`, and bulk inventory still belongs to `recent` / `ed.recent-inventory-rows`.

## Human command

Plain command-bar inspection gets the same side-effect-free surface:

```text
showrecent PATH
```

Example:

```text
showrecent /tmp/demo/guide/intro.md
recent #2 /tmp/demo/guide/intro.md [active, dirty] @ 2:1 — section=/tmp/demo | guide/intro.md
```

Equivalent path spellings stay explicit instead of requiring the exact stored MRU string:

```text
showrecent /tmp/demo/guide/../guide/intro.md
recent #2 /tmp/demo/guide/../guide/intro.md -> /tmp/demo/guide/intro.md [active, dirty] @ 2:1 — section=/tmp/demo | guide/intro.md
```

Missing names stay typed instead of falling through to the mutating `recent N` dialect:

```text
showrecent nope
showrecent: no such recent file: nope
```

## Why this matters

This is a small trust/flow improvement.

Recent files already had a clean three-scale loop for flat inventory and grouped browse state, but there was still no first-stop exact inspector for one named MRU entry. `showrecent PATH` and `ed.recent-detail-row` keep that answer inspectable without opening a file, scraping the bulk `recent` summary, or reopening grouped picker state.

That makes the archive easier to inspect headlessly and keeps recent-file discovery aligned with the other exact row surfaces Micromax already exposes for commands, actions, words, docs, topics, options, buffers, keymodes, and hooks.

## Focused tests

- `tests/test_editor_buffer_mru_and_closeall.py`
- `tests/test_editor_prompt_completion_hostcalls.py`
- `tests/test_editor_capabilities_registry.py`

## Next tiny seams

- some other everyday inventories may still rely on plain command formatting even when adjacent grouped/summary layers are now shared
- if another daily loop keeps needing it, one concrete picker-only family may still be worth a tiny exact detail row instead of more formatter-only surface area
