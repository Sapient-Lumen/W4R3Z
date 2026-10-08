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
  "prompt_current_section": ""|"Command"|"Action"|"Word"|"Binding",
  "prompt_current_preview": ""|"Command: showword — show visible micromax word"|"Binding: Ctrl-x — @nav command:quit | request editor quit",
  "last_message": "...",
  "macro_recording": 0|1,
  "macro_playing": 0|1,
  "macro_name": ""|"last"|"named-slot"
}
```

Notes:

- `line` / `col` stay **0-based** to match core editor APIs.
- `display_line` / `display_col` and `position` are the human-facing forms.
- `mode` is intentionally tiny for now. Prompt state is the main editor mode we
  currently expose directly; macro recording/playback are orthogonal flags.
- `keymode` is separate from `mode`: it reports the active keymap layer (if any)
  without pretending the whole editor has become a fully modal system.
- `keymode_once` is `1` when the top active keymode is one-shot / transient.
- the prompt-current fields are best-effort metadata for the active suggestion item.
  They are especially useful for the searchable `palette`, `topic`, and `binding` prompts, but they are
  also populated for ordinary command completion sessions when a current row exists.

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
mode=normal buffer='notes.txt' dirty=1 readonly=0 pos=12:4 cursors=1/3 sels=2 selchars=5
```

## Portability notes

- The model is host/editor-facing, not required for the smallest standalone VM.
- The values are intentionally plain strings / ints / maps / lists.
- Future revisions can add fields, but should avoid breaking or renaming the
  existing ones casually.
