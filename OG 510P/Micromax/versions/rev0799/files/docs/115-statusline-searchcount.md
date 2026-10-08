# Statusline search-count token (rev174)

Rev173 introduced a shared whole-buffer search-position model (`search_position_model`)
and exposed it through `status_model()` / `ed.status` as `search_summary = "i/n"`.

Rev174 adds the smallest next step on top of that model: a dedicated statusformat
token that renders the active search count in statusline-friendly form.

## Token

These aliases are equivalent:

- `$(searchpos)`
- `$(search)`
- `$(searchcount)`

Behavior:

- active search with known position → ` [i/n]`
- no active search → `""`

The token deliberately reuses the editor's shared search-position model instead of
recounting matches in the formatter or the TUI.

## Default formatter

The default right-side status format now includes the token:

```
ft:$(opt:filetype) enc:$(opt:encoding) $(opt:fileformat)$(searchpos) $(position)$(cur)$(sel) $(percentage)% $(mode)$(keymode)$(macro)
```

That means an active search now shows up in the ordinary reference statusline too,
not only in the transient find prompt.

Example:

```
ft:text enc:utf-8 unix [2/5] 14:8 cur:1/1 63% normal
```

## Why a dedicated token?

Using raw `$(search_summary)` was already possible, but a dedicated token is nicer
for two reasons:

- it bakes in the tiny display shape users actually want (` [i/n]`)
- it keeps custom templates from repeating conditional spacing logic

This is the same general philosophy as `$(cur)` / `$(sel)` / `$(macro)`: keep the
underlying state structured, but offer one tiny display-friendly token for the
common statusline case.

## Portability side note

The same rev also adds `find-missing-returns-zero` to `portability/kernel_cases.json`,
making the `find` contract explicit on both success (`xt`) and failure (`0`).

## Pointers

- formatter: `src/micromax_editor/statusformat.py`
- defaults: `src/micromax_editor/editor.py`
- tests: `tests/test_editor_statusline.py`, `tests/test_tui_hlsearch.py`, `tests/test_portability_suite.py`
