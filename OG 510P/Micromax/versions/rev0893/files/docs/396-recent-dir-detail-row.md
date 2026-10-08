# Recent directory detail row

Rev454 closes one small exact-inspection seam in Micromax's recent-file loop.

Micromax already had the right recent-directory surfaces:

- `recentdirpick [QUERY]` / `ed.recent-dir-section-rows` exposed grouped recent-file buckets by parent directory
- rev449 added `showrecentdirgroups [QUERY]` / `ed.recent-dir-section-summary-rows` for the lighter broad directory-bucket summary question
- rev451 added `showrecent PATH` / `recent_detail_row(PATH)` / `ed.recent-detail-row` for exact one-file MRU inspection

But one small inspectability seam still lingered underneath that model: there was still no official side-effect-free exact answer to the adjacent question future humans/LLMs often ask next:

> what is true about this one visible recent-directory bucket right now?

Grouped browse state and broad summaries were both there, but exact one-directory inspection still required reopening `recentdirpick` or re-counting one bucket by hand.

Rev454 keeps the follow-up deliberately small.

## What landed

- add `recent_dir_detail_row(DIR)` on the editor
- expose it as hostcall `ed.recent-dir-detail-row`
- add one small convenience word, `recent-dir-detail`
- add one plain side-effect-free human command, `showrecentdir DIR`
- make `showrecentdir` completion reuse those same exact recent-directory rows instead of a thinner directory-name list

## Exact row shape

`recent_dir_detail_row(DIR)` / `ed.recent-dir-detail-row` return:

```text
[query directory count active_count open_count dirty_count readonly_count sample_path sample_detail]
```

Where:

- `query` is the exact spelling the caller asked about
- `directory` is the canonical visible parent-directory bucket label that matched that query
- `count` is how many recent-file rows currently live in that bucket
- `active_count` / `open_count` / `dirty_count` / `readonly_count` count matching currently open recent files in that bucket with those cues
- `sample_path` reuses the first visible recent-file path in that bucket
- `sample_detail` reuses that same first row's detail field

Example:

```text
['/tmp/demo/proj/tests', '/tmp/demo/proj/tests', 2, 1, 2, 1, 0, '/tmp/demo/proj/tests/c.txt', '/tmp/demo/proj/tests']
```

The shape intentionally stays small. Full grouped browse state still belongs to `recentdirpick` / `ed.recent-dir-section-rows`, and broad summary still belongs to `showrecentdirgroups [QUERY]` / `ed.recent-dir-section-summary-rows`.

## Human command

Plain command-bar inspection gets the same side-effect-free surface:

```text
showrecentdir DIR
```

Example:

```text
showrecentdir /tmp/demo/proj/tests
recentdir /tmp/demo/proj/tests: 2 files [active, open=2, dirty=1] — e.g. /tmp/demo/proj/tests/c.txt
```

Equivalent directory spellings stay explicit instead of requiring the exact stored bucket label:

```text
showrecentdir /tmp/demo/proj/tests/../tests
recentdir /tmp/demo/proj/tests/../tests -> /tmp/demo/proj/tests: 2 files [active, open=2, dirty=1] — e.g. /tmp/demo/proj/tests/c.txt
```

Missing directory labels stay typed and boring:

```text
showrecentdir nope
showrecentdir: no such recent directory: nope
```

## Why this matters

This is a small trust/flow improvement.

Recent files already exposed a clean four-part loop across flat MRU inventory, exact one-file detail, grouped directory browse state, and broad directory summaries, but exact one-directory inspection still lagged behind. `showrecentdir DIR` and `ed.recent-dir-detail-row` close that gap without adding new navigation behavior or new hidden state. They just make one visible recent-directory bucket honest and inspectable.

## Focused tests

- `tests/test_editor_buffer_mru_and_closeall.py`
- `tests/test_editor_prompt_completion_hostcalls.py`
- `tests/test_editor_capabilities_registry.py`

## Next tiny seams

- some grouped navigation families still have either a broad summary or an exact row, but not both
- a few command-bar completion surfaces may still depend on thinner raw-name lists even when a nearby exact row now exists
