# Prompt history (command bar / find bar)

Command-bar history is a small feature that dramatically improves "flow".

micro's docs emphasize the command bar as a one-line buffer opened with `Ctrl-e`
(see `commands.md`). While the history behavior isn't called out explicitly in the
help files, it's a standard expectation in command-driven editors.

Primary sources:

- micro commands: https://raw.githubusercontent.com/micro-editor/micro/master/runtime/help/commands.md
- micro default keys (command prompt + find):
  https://raw.githubusercontent.com/micro-editor/micro/master/runtime/help/defaultkeys.md

## micromax-editor behavior (v10)

- We maintain separate histories for `command`, `find`, `palette`, `topic`, and `binding` prompts.
- History is appended when:
  - the prompt is submitted, and
  - a command is executed via `command:` bindings or `:cmd ...` in the REPL.
- History navigation actions:
  - `PromptHistoryPrev`
  - `PromptHistoryNext`

Bindings in the core plugin use micro-style action chaining:

- `UpArrow` → `PromptHistoryPrev|CursorUp`
- `DownArrow` → `PromptHistoryNext|CursorDown`

So Up/Down do history navigation only when a prompt is active.


## Searchable prompt note (rev54)

The searchable `palette`, `topic`, and `binding` prompts all re-rank their rows whenever the query text changes.
History recall still just restores the saved query/selection text; the ranked rows are recomputed from that text, so picker-style state stays derived rather than stored separately.


## Persistence option naming (rev197)

Prompt history persistence still uses the same `cap.persist` boundary and JSON file format, but the editor now also accepts micro-esque `savehistory` as an alias for the canonical `history.persist` option. That keeps existing Micromax config readable while making ported micro muscle-memory less surprising.
