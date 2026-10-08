# Editor command bar (micro-inspired)

Micromax-editor borrows micro’s “command bar” idea:

- opened by `Ctrl-e`
- single-line prompt
- arguments parsed with shell-like quoting (`'...'`, `"..."`, backslash escaping)

Micro’s docs state the command bar parser uses the same rules `/bin/sh` would use
for parsing arguments, and lists built-in commands like `help`, `bind`, `save`,
`quit`, `set`, `toggle`, `show`, `reload`, etc. We also add a small `macro` command for recording/playing named macros, a `showword` inspection command so the embedded Micromax dictionary is visible from the same prompt, `apropos QUERY` so commands/actions/words can be searched without already knowing the exact topic name, `topicpick [QUERY]` as a dedicated searchable topic/help prompt, and `bindingpick [QUERY]` as a dedicated searchable prompt over the *currently reachable* keymap. We also add `bufferpick [QUERY]` and `markpick [QUERY]` so navigation targets (buffers and marks) can be searched and selected without a UI.

In micromax-editor (rev60):

- prompt model: `micromax_editor.commandbar.Prompt`
- parsing: `micromax_editor.cmdline.parse_cmdline` (Python `shlex.split`)
- dispatch: `micromax_editor.command_dispatcher.CommandDispatcher`

We also implemented micro-like `replace` / `replaceall` commands (regex by
default; `-l` for literal), which exercise parsing + undo + buffer rewriting.

Both `replace` and `qreplace` follow the editor's `ignorecase` option (like `find`): when enabled, they match case-insensitively in both literal and regex modes.

Rev86 adds `qreplace` / `queryreplace`: a tiny interactive "confirm each" loop
(`y`/`Enter` replace, `n` skip, `a` all, `l` last, `q`/`Esc` quit) implemented as
a capture keymode so global bindings can't accidentally fire during the loop.

### Keybinding integration

Micro also allows binding keys directly to commands:

- `command:pwd` executes the command immediately
- `command-edit:help ` opens command mode with the line prefilled

We support these prefixes inside action chains (see `Editor._run_action_spec`).

*(rev63: prompt editing is now first-class: printable keys type into the prompt when open, prompt-mode bindings override arrows/backspace/delete, and `quit` warns/arms when any buffers are dirty; `quit -f` or `quit!` force. Default bindings include `Ctrl-s` → `command:save`, `Ctrl-q` → `command:quit`, and `Ctrl-l` → `command-edit:goto `.)*

*(rev74: added `close` / `close!` to close buffers safely (dirty buffers require a second `close`), plus a recent-files MRU with `recent` / `recentpick`.)*

*(rev85: the core plugin now binds `Ctrl-o` → `open` (prefilled), `Ctrl-r` → `replace` (prefilled), `Ctrl-b` → `bufferpick`, `Ctrl-Space` → command palette, and `Alt-g` → binding discovery. The minimal curses TUI also interprets ESC-prefixed Alt/Meta chords so `Alt-*` bindings are reachable.)*

*(rev86: core defaults now also bind `Alt-%` → `qreplace` (prefilled), matching Emacs-ish "query replace" muscle memory.)*

### Design note

We keep “actions” and “command-bar commands” as separate concepts, but `help` is now deliberately broader: it first resolves editor commands/actions, then falls back to the currently visible Micromax word if no editor topic matches.

*(rev76: `help TOPIC` also falls back to opening a matching `docs/*.md` page into a protected read-only help buffer; `helppick [QUERY]` opens a docs picker; in a docs buffer, `helplinkpick` lists links and `helpoutlinepick` lists headings. The core plugin binds `Ctrl-g` to `command:helppick`, matching micro’s “open help menu” muscle memory.)*

*(rev77: help buffers gained tiny navigation helpers: `helpfollow` follows a markdown link under the cursor, and `helpback` returns to the previous docs page. This is deliberately inspired by “doc buffers with followable links” patterns seen in editors like Kakoune.)*

- Actions are keybind targets and return success/failure for chaining.
- Commands are human-oriented strings (parsed) and can call actions internally.
- `showword NAME` is the explicit bridge from the editor prompt to Micromax dictionary metadata.
- `apropos QUERY` is the search-first sibling: it ranks command/action/word topics by subsequence match, can fall back to topic summary/doc text, and now also supports small multi-term / out-of-order queries (for example `apropos word show`).
- failed `help NAME` now shows a few likely `apropos`-style matches instead of only returning a dead end; if the user typed multiple words, the suggestion path now searches that whole query rather than only the first token.


### Searchable command/action palette

The editor now also has a dedicated **palette** prompt kind. It is the execution-oriented sibling of `topicpick`: instead of opening help for commands/actions/words, it searches only **commands + actions** and then either runs the action or stages the command in the normal command bar.

Ways to open it:

- `commandpick [QUERY]` from the command bar
- the `CommandPalette` action
- the `ed.command-palette` hostcall from Micromax

Behavior:

- opening the prompt preloads ranked command/action rows
- successful palette selections are remembered in a tiny palette-local MRU
- empty queries show a `Recent Files` bucket first (opens files immediately), then the palette-local `Recent` commands/actions bucket
- changing the query live-refreshes ranked rows
- equivalent matches can use palette recency as a tiebreaker
- `Tab` / `Shift-Tab` cycle ranked items
- `Enter` on an **action** executes it immediately
- `Enter` on a **command** opens the ordinary `command` prompt prefilled with `name `
- palette-prompt history is stored under prompt kind `palette`
- grouped section rows are available via `ed.command-palette-section-rows`
- the same current-row / preview / status-model surfaces used by other searchable prompts apply here too

## Topic prompt

The editor now also has a dedicated `topic` prompt kind. It is intentionally tiny and headless: it reuses the ordinary prompt suggestion-session model, but its candidates come from ranked topic rows (`help_topic_rows()` / `apropos_rows()`) instead of shell-ish command tokens.

Ways to open it:

- `topicpick [QUERY]` from the command bar
- the `TopicPrompt` action
- the `ed.topic-prompt` hostcall from Micromax

Behavior:

- opening the prompt preloads ranked command/action/word topics
- changing the query live-refreshes those ranked topics
- `Tab` / `Shift-Tab` cycle those ranked topics
- `Enter` opens help for the selected/best-ranked topic
- topic-prompt history is stored under prompt kind `topic`
- the active ranked row is visible headlessly via `ed.prompt-current-row`
- grouped sections for future pickers are exposed via `ed.topic-section-rows` / `ed.apropos-section-rows`
- compact current-item preview text is exposed via `ed.prompt-current-section` / `ed.prompt-current-preview`


## Searchable binding prompt

The same headless prompt/session model now also powers a small **binding** prompt.

Open it via:

- `bindingpick [QUERY]` from the command bar
- action `BindingPrompt`
- hostcall `ed.binding-prompt`

Behavior:

- it searches the **currently reachable** bindings after active keymode precedence is applied
- rows carry `[key kind menu info]` where `menu` includes mode + action-spec and `info` carries the resolved human description
- changing the query live-refreshes ranked bindings; small multi-term / out-of-order queries can match across the key itself, the action-spec, and the human description
- `Tab` / `Shift-Tab` cycle the ranked keys
- `Enter` runs `showkey KEY` for the selected/best-ranked binding

This deliberately stays on the discovery side of the line: it is a searchable `whichkey`-style surface, not yet a popup/menu rendering contract.
