# Search-position summary / `i/n` (rev173)

Micromax already had the search substrate (`find`, `FindNext`, `FindPrevious`,
`incsearch`, `hlsearch`). Rev173 adds one more tiny shared layer on top:

- a whole-buffer search-position model in the editor core
- status-model fields future UIs/scripts/LLMs can inspect directly
- a visible `[current/total]` cue in the live find prompt

That keeps search awareness from living only inside TUI row-highlighting.

## Shared model

`Editor.search_position_model()` returns a tiny map:

```text
{
  "query": "alpha",
  "literal": 1,
  "case_sensitive": 0,
  "index": 1,
  "count": 3,
  "summary": "1/3"
}
```

Policy:

- empty search query → empty summary
- literal searches count non-overlapping substring hits
- regex searches count **non-empty** matches only
- `index` is 1-based when the primary cursor sits exactly on a known match start,
  otherwise `0`

The status model mirrors that as:

- `search_query`
- `search_literal`
- `search_case_sensitive`
- `search_match_index`
- `search_match_count`
- `search_summary`

So future statuslines, alternate TUIs, and LLM/debug tooling can reuse the same
contract instead of re-counting matches themselves.

## Live TUI cue

When the find prompt is open, the minimal curses TUI now appends the same shared
summary to the prompt line:

```text
/alpha  [1/3]
```

This intentionally stays tiny:

- no new theme system
- no off-screen/async search jobs
- no separate search widget state

It is just enough to answer “where am I in this search?” while typing.

## Statusline use

Because `statusformat` already falls back to `status_model()` keys, custom
statuslines can render the same summary directly:

```text
set statusformatr "$(search_summary) $(position) $(mode)"
```

## Files / tests

- `src/micromax_editor/search.py` — shared whole-buffer search counting helper
- `src/micromax_editor/editor.py` — `search_position_model()` + status fields
- `src/micromax_editor/tui.py` — live find-prompt `[i/n]` cue
- `tests/test_editor_statusline.py`
- `tests/test_tui_hlsearch.py`
