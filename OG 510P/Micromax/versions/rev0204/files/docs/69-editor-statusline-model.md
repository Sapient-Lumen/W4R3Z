# Editor statusline / infobar model (rev38)

Micromax-editor is still intentionally headless-first, but UI layers still need a
shared answer to a basic question:

- what state should appear in the status line / infobar?

Rev36 continues the **portable status model** story so future terminal UIs, tests, scripts,
and LLMs can all inspect the same editor state instead of inventing their own
semantics.

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
- the prompt-current fields are best-effort metadata for the active suggestion item.
  They are especially useful for the searchable `palette`, `topic`, and `binding` prompts, but they are
  also populated for ordinary command completion sessions when a current row exists.
- the `search_*` fields are a tiny whole-buffer search-position contract. They intentionally
  describe the editor's current search state even when no dedicated search widget is visible.

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

## Portability notes

- The model is host/editor-facing, not required for the smallest standalone VM.
- The values are intentionally plain strings / ints / maps / lists.
- Future revisions can add fields, but should avoid breaking or renaming the
  existing ones casually.
- For grouped picker kinds, `prompt_current_section` intentionally mirrors the *visible* section labels shown by the live picker/TUI (`Commands`, `Recent Files`, `Docs`, `Files`, `External`, `Headings`, etc.) rather than older singular fallback nouns.

