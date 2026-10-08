# Statusline buffer-position summary (rev184)

Micromax already had a shared prompt-position model (`1/9 • Commands 2/6`) and a shared search-position model (`1/3`).

Rev184 adds the matching tiny *buffer-position* model so ordinary statuslines/UIs do not need to rediscover one basic bit of editor context by hand: **which open buffer am I on?**

## What changed

The shared editor status model (`ed.status` / `status_model()`) now includes:

- `buffer_index` — 1-based index of the active buffer
- `buffer_count` — number of open buffers
- `buffer_summary` — compact `i/n` string

The order is intentionally the same deterministic sorted order returned by `buffer_names()`, not MRU order, so tests, scripts, future UIs, and LLMs all get the same answer.

## Statusformat token

The reference statusline formatter now understands:

- `$(bufpos)`
- `$(bufferpos)`
- `$(buffers)`

These render ` [i/n]` **only when more than one buffer is open**.

That keeps the default statusline small for the common single-buffer case while still surfacing useful context during multi-buffer navigation.

## Default formatter

The default right-side `statusformatr` now includes `$(bufpos)` next to the existing search count / cursor position cues, so the tiny curses TUI inherits the new signal automatically.

## Why this stays shared-model-first

This is not a tab bar and not a renderer-only adornment.

Micromax already exposes:

- prompt position
- search position
- cursor / selection counts

Adding one more small shared `buffer_summary` contract keeps multi-buffer context available to:

- the curses TUI
- future TUIs/GUI frontends
- Micromax scripts/plugins
- tests
- future LLMs reading the archive

without forcing every surface to count or order buffers independently.
