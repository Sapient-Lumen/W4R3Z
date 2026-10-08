# Recent prompt row truth

Rev502 closes one small but important trust/flow seam in Micromax's recent-file loop.

Micromax already had the right adjacent recent surfaces:

- palette `Recent Files` rows reused exact `recent_detail_row(PATH)` metadata
- palette rows and exact `showrecent PATH` inspection both kept tiny disk/action
  truth such as `existing file`, `new file`, `current buffer`, `switch buffer`,
  and `empty buffer @ 1:0`
- `recentpick [QUERY]` and `recentdirpick [QUERY]` already provided the direct
  first-class reopen/switch prompts humans actually use

But one small drift still lingered underneath that model: the dedicated recent
prompts were still built from the old thin `recent_prompt_rows()` shape, so the
most direct MRU pickers stayed visually less honest than both the command
palette and the explicit `showrecent PATH` inspector.

## What landed

Rev502 keeps the follow-up deliberately small.

- `recent_prompt_rows()` now reuses exact recent-file metadata/truth from
  `recent_detail_row(PATH)`
- visible recent prompt rows now keep MRU index, active/open/dirty/readonly,
  cursor position, and the same tiny disk/action truth cues Micromax already
  knows
- project-root row rewriting for `recentpick` now preserves trailing truth cues
  instead of discarding them when it rewrites the visible detail to a
  project-relative path

## Visible row shape

The row shape stays the same:

```text
[path kind menu info]
```

What changes is that `menu` / `info` now keep the richer recent-file truth the
editor already had elsewhere.

Examples:

```text
['/tmp/demo/proj/tests/c.txt', 'recent', 'proj', 'tests/c.txt | current buffer']
['/tmp/demo/proj/src/a.txt', 'recent', 'proj', 'src/a.txt | switch buffer']
['/tmp/demo/proj/guide/intro.md', 'recent', 'intro.md #1 [active] @ 2:1', '/tmp/demo/proj/guide | existing file | current buffer']
```

The project-grouped `recentpick` and literal-directory `recentdirpick` prompts
still keep their different grouping strategies. The follow-up only makes the
visible rows inside those prompts more honest.

## Why this matters

This is a small trust/flow improvement.

`recentpick` and `recentdirpick` are the boring daily reopen/switch loops. If
Micromax already knows one visible recent target is saved, missing, current, or
switchable, the direct recent-file prompts should say so before Enter instead of
forcing humans or future LLMs to infer it from a different surface.

## Focused tests

- `tests/test_editor_buffer_lifecycle_recent.py`
- `tests/test_editor_statusline.py`
- `tests/test_tui_prompt_display_lines_sticky_header.py`
- `tests/test_prompt_grouping_sections.py`
