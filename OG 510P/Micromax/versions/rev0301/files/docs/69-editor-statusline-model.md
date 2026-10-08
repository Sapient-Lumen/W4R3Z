# Editor statusline / infobar model (rev213)

Micromax-editor is still intentionally headless-first, but UI layers still need a
shared answer to a basic question:

- what state should appear in the status line / infobar?

The status-model thread keeps growing as Micromax learns which tiny editor states are worth making explicit instead of leaving renderer-local. Rev210 extends that same portable surface to active capture keymodes, rev211 adds one tiny unified bottom-row interaction snapshot (`interaction_*`) so future terminal UIs, tests, scripts, and LLMs can all inspect the same prompt/capture line instead of inventing their own semantics, rev212 adds a sibling shared bottom-chrome row model (`bottom_rows_model(width)` / `ed.bottom-rows`) so the full visible keymenu / interaction-or-infobar / statusline stack is inspectable too, rev213 adds a tiny `statusline_model(width)` / `ed.statusline-model` layout snapshot so even the visible left/right/padding/truncation policy of the final status row is inspectable instead of trapped inside `statusline_text(width)`, and rev214 adds tiny sibling `keymenu_model(width)` / `ed.keymenu-model` and `infobar_model(width)` / `ed.infobar-model` row snapshots so the visible help/message rows are inspectable in the same style, and rev215 closes the last visible bottom-row gap with a tiny width-aware `interaction_model(width)` / `ed.interaction-model` snapshot so the prompt/capture row itself is inspectable without re-ellipsizing raw `interaction_line` text.

## Why now?

The editor already has enough moving parts that ad-hoc status rendering becomes
risky:

- prompts (`command`, `find`, `palette`, `topic`, `binding`)
- multi-cursor state
- selection state
- dirty/read-only file state
- macro recording / playback
- active keymode / transient keymode state
- last user-facing message

A tiny, shared data model is a cheap way to keep future UIs honest.

## Host surface

New hostcalls:

- `ed.status` — `( -- m )`
- `ed.status-summary` — `( -- "text" )`
- `ed.bottom-rows` — `( width -- rows )`
- `ed.statusline-model` — `( width -- m )`
- `ed.interaction-model` — `( width -- m )`
- `ed.keymenu-model` — `( width -- m )`
- `ed.infobar-model` — `( width -- m )`

User-facing command:

- `showstatus`

`showstatus` is mainly for headless debugging. UIs should prefer `ed.status`.

## `ed.status` shape

The returned map currently contains:

```text
{
  "mode": "normal|command|find|...",
  "keymode": "" | "nav" | "goto" | ...,
  "keymode_once": 0|1,
  "keymode_capture": 0|1,
  "buffer_name": "*scratch*",
  "file_name": "notes.txt",
  "display_name": "/tmp/notes.txt"|"notes.txt",
  "buffer_index": 1|2|3|...,
  "buffer_count": n,
  "buffer_summary": "1/1"|"2/5",
  "filetype": "text|python|markdown|micromax|...",
  "path": "/abs/or/relative/path/or/empty",
  "cwd": "/current/working/directory",
  "dirty": 0|1,
  "readonly": 0|1,
  "line": 0-based-line,
  "col": 0-based-col,
  "display_line": 1-based-line,
  "display_col": 1-based-col,
  "position": "line:col" ,
  "line_count": n,
  "cursor_count": n,
  "primary_cursor_index": 0-based-index,
  "selection_count": n,
  "primary_selection_chars": n,
  "prompt_kind": ""|"command"|"find"|"palette"|"topic"|"binding",
  "capture_kind": ""|"qreplace"|"openurl",
  "capture_summary": ""|"?replace [1/2]"|"?open external link from help",
  "capture_detail": ""|"one -> X"|"https://...",
  "capture_progress": ""|"1/2",
  "capture_source": ""|"help"|"cursor"|"command",
  "capture_search": ""|"one",
  "capture_replace": ""|"X",
  "capture_url": ""|"https://...",
  "capture_examined": 0|1|2|...,
  "capture_count": 0|1|2|...,
  "capture_replaced": 0|1|2|...,
  "interaction_active": 0|1,
  "interaction_kind": ""|"command"|"find"|"palette"|"topic"|"binding"|"qreplace"|"openurl",
  "interaction_prefix": ""|":"|"/"|"?",
  "interaction_summary": ""|":open README.md"|"?replace [1/2]",
  "interaction_detail": ""|"Commands: showstatus — show portable statusline summary"|"one -> X"|"https://...",
  "interaction_position": ""|"1/3"|"2/9 • Commands 2/6",
  "interaction_line": ""|":status  [1/4 • Commands 1/4]  | Commands: showstatus — show portable statusline summary"|"?replace [1/2]  | one -> X",
  "prompt_text": "...",
  "prompt_cursor": 0|1|2,
  "prompt_current_insert": ""|"showword"|...,
  "prompt_current_kind": ""|"command"|"action"|"word"|"binding",
  "prompt_current_menu": "...",
  "prompt_current_info": "...",
  "prompt_current_section": ""|"Recent Files"|"Recent"|"Commands"|"Actions"|"Words"|"Prompt"|"nav"|"Global"|"Help"|"Scratch"|"Errors"|"Loaded"|"Available"|"Current"|"Back"|"Forward"|"Docs"|"Files"|"External"|"Headings"|"00–09 Project"|"10–19 Research"|"20–29 Language + VM"|"/project/root"|"Heading breadcrumb",
  "prompt_current_preview": ""|"Commands: showword — show visible micromax word"|"Recent Files: /tmp/demo.txt — demo.txt | /tmp"|"nav: Ctrl-x — @nav command:quit | request editor quit"|"00–09 Project: Vision — **Micromax** is a small, embeddable, concatenative language intended to be a *sane* plugin/config/macro system."|"/project/root: /project/root/src/main.py — project | src/main.py",
  "prompt_index": 0|1|2|...,
  "prompt_count": 0|1|2|...,
  "prompt_section_index": 0|1|2|...,
  "prompt_section_count": 0|1|2|...,
  "prompt_position_summary": ""|"1/5"|"2/9 • Commands 2/6"|"1/2 • /project/root 1/2",
  "search_query": ""|"alpha"|"[A-Z]+",
  "search_literal": 0|1,
  "search_case_sensitive": 0|1,
  "search_match_index": 0|1|2|...,
  "search_match_count": 0|1|2|...,
  "search_summary": ""|"1/3"|"0/3"|"0/0",
  "last_message": "...",
  "macro_recording": 0|1,
  "macro_playing": 0|1,
  "macro_name": ""|"last"|"named-slot"
}
```

Notes:

- `line` / `col` stay **0-based** to match core editor APIs.
- `file_name` stays the raw basename-ish logical file label for compatibility, while `display_name` is the user-facing status/infobar label that honors `basename`.
- `buffer_index` uses the same stable sorted buffer order returned by `buffer_names()`, so the value is deterministic for tests, hostcalls, and future UIs/LLMs.
- `display_line` / `display_col` and `position` are the human-facing forms.
- `mode` is intentionally tiny for now. Prompt state is the main editor mode we
  currently expose directly; macro recording/playback are orthogonal flags.
- `keymode` is separate from `mode`: it reports the active keymap layer (if any)
  without pretending the whole editor has become a fully modal system.
- `keymode_once` is `1` when the top active keymode is one-shot / transient.
- `keymode_capture` is `1` when the top active keymode is a capture/confirmation layer that intentionally intercepts keys (for example `qreplace` or `openurl`) instead of falling through to global bindings.
- the prompt-current fields are best-effort metadata for the active suggestion item.
  They are especially useful for the searchable `palette`, `topic`, and `binding` prompts, but they are
  also populated for ordinary command completion sessions when a current row exists.
- the `search_*` fields are a tiny whole-buffer search-position contract. They intentionally
  describe the editor's current search state even when no dedicated search widget is visible.
- the `capture_*` fields intentionally mirror active capture keymodes like `qreplace` and `openurl` without promoting a larger prompt subsystem: `capture_summary` is the short question/header, `capture_detail` is the actionable subject (replacement or URL), and the remaining fields keep mode-specific structure available for future UIs/statuslines/scripts.
- the `interaction_*` fields sit one level above the raw prompt/capture fields: they describe the *current visible bottom-row interaction line* that the minimal TUI would show, regardless of whether that line comes from an ordinary prompt or a capture keymode.


## `ed.bottom-rows`

`ed.bottom-rows WIDTH` returns the currently visible bottom chrome as a list of row maps ordered **top-to-bottom** exactly as the minimal curses TUI paints them. Each row is intentionally tiny:

```text
{
  "kind": "keymenu"|"interaction"|"infobar"|"statusline",
  "slot": "help"|"prompt"|"status",
  "text": "already-rendered single-line text clipped to WIDTH"
}
```

Notes:
- `keymenu` is present only when the option is enabled.
- `interaction` replaces `infobar` whenever an ordinary prompt or capture keymode owns the bottom prompt row.
- `statusline` disappears entirely when `statusline=false`, matching the real row-reclaim policy.
- This stays intentionally text-first and tiny: the row *order* and semantic `kind`/`slot` are the portable contract; styling remains a renderer concern.

## Design choice: model first, rendering later

This is deliberately closer to a *semantic snapshot* than to a final rendered
statusline string.

Why:

- terminal UIs may want left/center/right layout
- some UIs may dedicate a separate message line
- some hosts may hide prompt state from the main statusline entirely
- later we may add diagnostics, filetype, indentation, git branch, etc.

A map is a better long-term contract than a pre-rendered piece of text.

## `ed.status-summary`

This is a deterministic summary string for tests, debugging, and the headless
REPL. It intentionally does **not** try to be pretty or final-UI quality.

Example:

```text
mode=normal buffer='notes.txt' dirty=1 readonly=0 pos=12:4 cursors=1/3 sels=2 selchars=5 buf_pos='2/5' search_pos='1/7'
```

When a capture keymode is active, `ed.status-summary` now also appends compact capture metadata such as `capture='qreplace'`, `capture_pos='1/2'`, and `capture_item='one -> X'`. During ordinary picker-style prompts, it now also appends tiny interaction metadata such as `interaction='palette'`, `interaction_pos='1/4 • Commands 1/4'`, and `interaction_item='Commands: showstatus — show portable statusline summary'`.

## Portability notes

- The model is host/editor-facing, not required for the smallest standalone VM.
- The values are intentionally plain strings / ints / maps / lists.
- Future revisions can add fields, but should avoid breaking or renaming the
  existing ones casually.
- For grouped picker kinds, `prompt_current_section` intentionally mirrors the *visible* section labels shown by the live picker/TUI (`Commands`, `Recent Files`, `Docs`, `Files`, `External`, `Headings`, etc.) rather than older singular fallback nouns.


## `ed.statusline-model`

`ed.statusline-model WIDTH` returns a tiny shared layout map for the visible
status row:

```text
{
  "active": 0|1,
  "width": n,
  "left_raw": "...",
  "right_raw": "...",
  "left": "...",
  "right": "...",
  "padding": "   ",
  "padding_width": n,
  "truncated_left": 0|1,
  "truncated_right": 0|1,
  "text": "final single-line status row"
}
```

This stays intentionally tiny and text-first: future UIs/scripts/LLMs can see
the deterministic layout policy without having to reverse-engineer the final
statusline string.


## `ed.interaction-model`

`ed.interaction-model WIDTH` returns a tiny shared snapshot of the visible prompt/capture row:

```json
{
  "active": 0|1,
  "width": 80,
  "kind": ""|"command"|"find"|"palette"|"topic"|"binding"|"qreplace"|"openurl",
  "prefix": ""|":"|"/"|"?",
  "summary": ""|":open README.md"|"?replace [1/2]",
  "detail": ""|"Commands: showstatus — show portable statusline summary"|"one -> X"|"https://...",
  "position": ""|"1/3"|"2/9 • Commands 2/6",
  "raw_line": ""|":status  [1/4 • Commands 1/4]  | Commands: showstatus — show portable statusline summary",
  "text": ""|":status  [1/4 • Commands 1/4]  | Commands: showstatus — show portable statusline summary",
  "truncated": 0|1
}
```

This is the width-aware sibling of the `interaction_*` fields in `ed.status`: it keeps the same prompt/capture metadata while also exposing the final visible row text that the minimal curses TUI would paint for that width.


## `ed.keymenu-model`

`ed.keymenu-model WIDTH` returns a tiny shared snapshot of the visible help row:

```text
{
  "active": 0|1,
  "width": n,
  "context": "normal|command|find|palette|qreplace|openurl|...",
  "entries": [{"key": "^Q", "label": "Quit", "text": "^Q Quit"}, ...],
  "text": "single visible keymenu row",
  "truncated": 0|1
}
```

The row stays intentionally text-first, but the structured `entries` array means future UIs/scripts/LLMs do not need to split dimmed prose back into shortcut pairs.

## `ed.infobar-model`

`ed.infobar-model WIDTH` returns a tiny shared snapshot of the visible idle message row:

```text
{
  "active": 0|1,
  "width": n,
  "message_raw": "saved ok",
  "summary_raw": "Ln 10/120, Col 4 (8%)",
  "message": "saved ok",
  "summary": "Ln 10/120, Col 4 (8%)",
  "padding": "      ",
  "padding_width": n,
  "constantshow": 0|1,
  "truncated_message": 0|1,
  "truncated_summary": 0|1,
  "text": "saved ok      Ln 10/120, Col 4 (8%)"
}
```

The model is idle-only: active prompts/capture keymodes still own the prompt row through `interaction_*` / `ed.bottom-rows`.
