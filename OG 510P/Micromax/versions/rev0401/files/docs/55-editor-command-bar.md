# Editor command bar (micro-inspired)

Micromax-editor borrows micro’s “command bar” idea:

- opened by `Ctrl-e`
- single-line prompt
- arguments parsed with shell-like quoting (`'...'`, `"..."`, backslash escaping)

Micro’s docs state the command bar parser uses the same rules `/bin/sh` would use
for parsing arguments, and lists built-in commands like `help`, `bind`, `save`,
`quit`, `set`, `toggle`, `show`, `reload`, etc. We also add a small `macro` command for recording/playing named macros, tiny `undo` / `redo` mirrors so edit recovery is reachable from the same prompt with the same honest feedback as key-driven actions, a `showword` inspection command so the embedded Micromax dictionary is visible from the same prompt, `apropos QUERY` so commands/actions/words can be searched without already knowing the exact topic name, `topicpick [QUERY]` as a dedicated searchable topic/help prompt, and `bindingpick [QUERY]` as a dedicated searchable prompt over the *currently reachable* keymap. We also add `bufferpick [QUERY]` and `markpick [QUERY]` so navigation targets (buffers and marks) can be searched and selected without a UI.

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

*(rev74: added `close` / `close!` to close buffers safely (dirty buffers require a second `close`), plus a recent-files MRU with `recent` / `recentpick`; rev267 adds the directory-grouped sibling `recentdirpick`; rev332 makes the ordinary success path more orienting by having `buffer`, `prevbuf`, `bufferpick`, `close`, `only`, and `closeall` report the landed active buffer/cursor target instead of only reporting that a switch/close happened; rev344 makes the plain `buffers` inventory stop collapsing open state to raw names by showing the active marker, `dirty` / `readonly` flags, and current cursor target for each entry; rev345 makes plain `recent` stop collapsing MRU state to raw numbered paths by showing open/active state, visible flags, and current cursor targets for still-open entries; rev365 makes plain `buffers` / `marks` keep one count-aware inventory prefix too, and rev366 does the same for plain `recent`, so all three inventories now start with `N` before the existing entry detail instead of falling back to `(none)` or silent manual counting; rev372 makes the empty `prevbuf` path fail plainly as `prevbuf: no previous buffer` so buffer recovery no longer falls back to a raw placeholder; rev377 makes named `buffer NAME` / `close NAME` misses fail plainly as `buffer: no such buffer: NAME` / `close: no such buffer: NAME` so explicit buffer-target commands keep the command family visible on a miss; rev387 makes successful `close` / `closeall` calls self-identify too as `close: ...` / `closeall -> ...` instead of older `closed...` lines, and rev391 keeps unexpected bulk-close faults in the same typed family by making raised `only` / `closeall` failures report `only: error: ...` / `closeall: error: ...`, so buffer cleanup reads like the rest of the typed command dialect on both success and failure.)*

*(rev85: the core plugin now binds `Ctrl-o` → `open` (prefilled), `Ctrl-r` → `replace` (prefilled), `Ctrl-b` → `bufferpick`, `Ctrl-Space` → command palette, and `Alt-g` → binding discovery. The minimal curses TUI also interprets ESC-prefixed Alt/Meta chords so `Alt-*` bindings are reachable.)*

*(rev86: core defaults now also bind `Alt-%` → `qreplace` (prefilled), matching Emacs-ish "query replace" muscle memory.)*

### Design note

We keep “actions” and “command-bar commands” as separate concepts, but `help` is now deliberately broader: it first resolves editor commands/actions, then falls back to the currently visible Micromax word if no editor topic matches.

*(rev76: `help TOPIC` also falls back to opening a matching `docs/*.md` page into a protected read-only help buffer; `helppick [QUERY]` opens a docs picker; in a docs buffer, `helplinkpick` lists links, `helpoutlinepick` lists headings, and `helpjump [QUERY]` can now use parent breadcrumb terms like `Guide Links` and stable fragment/id terms like `custom-frag` instead of only the leaf heading title, and `helplinkpick` / the link side of `helpnavpick` can now use owning-section terms like `External micro editor` or `Reference Vision ref`, plus destination-title queries like `image metadata` or `hidden image metadata anchor`, instead of only the bare link label. The core plugin binds `Ctrl-g` to `command:helppick`, matching micro’s “open help menu” muscle memory.)*

*(rev77: help buffers gained tiny navigation helpers: `helpfollow` follows a markdown link under the cursor, and `helpback` returns to the previous docs page. This is deliberately inspired by “doc buffers with followable links” patterns seen in editors like Kakoune. Rev334 adds a small flow/trust follow-up: picker-driven docs navigation (`helpoutlinepick`, `helpnavpick`, `helplinkpick`) now reuses the same “tell me where I landed” rule as direct jump commands. Rev342 applies the same honesty rule to recovery commands too: command-bar `undo` / `redo` now mirror key-driven `Undo` / `Redo` and report the actual edit description plus touched target instead of mutating text silently.)*

- Actions are keybind targets and return success/failure for chaining.
- Commands are human-oriented strings (parsed) and can call actions internally.
- `showword NAME` is the explicit bridge from the editor prompt to Micromax dictionary metadata.
- `apropos QUERY` is the search-first sibling: it ranks command/action/word topics by subsequence match, can fall back to topic summary/doc text, supports small multi-term / out-of-order queries (for example `apropos word show`), and now keeps the visible discovery slice count-aware as `apropos QUERY: N topic(s), ...` instead of falling back to `(none)` or forcing manual counting.
- failed `help NAME` now shows a few likely `apropos`-style matches instead of only returning a dead end; if the user typed multiple words, the suggestion path now searches that whole query rather than only the first token.


### Searchable command/action palette

The editor now also has a dedicated **palette** prompt kind. It is the execution-oriented sibling of `topicpick`: instead of opening help for commands/actions/words, it searches only **commands + actions** and then either runs the action or stages the command in the normal command bar.

Ways to open it:

- `commandpick [QUERY]` from the command bar
- the `CommandPalette` action
- the `ed.command-palette` hostcall from Micromax

Behavior:

- opening the prompt preloads ranked command/action rows
- the live `commandpick` prompt now flattens the same grouped palette sections exposed headlessly through `ed.command-palette-section-rows`, so visible section labels stay aligned across hostcalls, TUI headers, and prompt preview/status surfaces
- successful palette selections are remembered in a tiny palette-local MRU
- empty queries show a `Recent Files` bucket first (opens files immediately), then the palette-local `Recent` commands/actions bucket, and now budget the initial browse window across visible sections so `Actions` stay visible when `Commands` are numerous
- `recentpick` now also reuses grouped project-root sections live, so the same recent-file buckets can drive TUI headers/sticky headers, `Alt-Up` / `Alt-Down`, and prompt preview/status surfaces
- `recentdirpick` now does the same for the existing directory-grouped recent rows exposed through `ed.recent-dir-section-rows`, giving the live editor a second honest MRU scan mode when project buckets are too coarse
- path-like queries can split into `Directories`, `Files`, and `Open` buckets so drill-down rows do not get buried among ordinary file targets
- changing the query live-refreshes ranked rows
- equivalent matches can use palette recency as a tiebreaker
- `Tab` / `Shift-Tab` cycle ranked items
- `Enter` on an **action** executes it immediately
- `Enter` on a **command** opens the ordinary `command` prompt prefilled with `name `
- palette-prompt history is stored under prompt kind `palette`
- grouped section rows are available via `ed.command-palette-section-rows`
- the same current-row / preview / status-model surfaces used by other searchable prompts apply here too, including the compact shared picker-position summary (`index/count • section i/n`) now mirrored into the minimal TUI prompt line

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
- the live `topicpick` prompt now flattens those same grouped families too, and empty-query browse windows budget rows across `Commands` / `Actions` / `Words` so Actions/Words stay visible instead of disappearing behind the command list cap
- compact current-item preview text is exposed via `ed.prompt-current-section` / `ed.prompt-current-preview`
- grouped docs families are also exposed headlessly via `ed.doc-section-rows`, so future UIs/scripts can inherit the same `helppick` section labels the TUI uses


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


Rev336 follow-up: selecting `recentfile` / `openpath` rows from `commandpick` now reports `opened: path @ line:col`, keeping searchable file-open flows aligned with the explicit `open ...` command rather than behaving like a quieter success path.
- missing `showcmd NAME` / `showword NAME` lookups now fail plainly as `showcmd: no such command: NAME` / `showword: no such word: NAME` so command-bar inspection stays explicit even on a miss.
- mistyped ordinary command-bar commands now fail plainly as `command: no such command: NAME` instead of the older `Unknown command: NAME`, so the first command-entry miss matches the newer inspection/navigation dialect too.
- known commands that raise unexpectedly now fail as `command NAME: error: DETAILS` instead of a generic `Command error: ...`, so the dispatcher keeps the failing command visible during plugin/dev-command debugging.
- Micromax-defined commands registered through `ed.cmd-add` now reuse that same `command NAME: error: DETAILS` dialect on Micromax/runtime faults too, so scripted commands do not regress into a weaker bridge-specific error surface.
- missing `showkey KEY`, `binddoc KEY DOC...`, `bindmodedoc MODE KEY DOC...`, `unbind KEY`, and `unbindmode MODE KEY` targets now fail plainly as `...: no such binding: ...` instead of collapsing to `(unbound)`.
- successful `unbind KEY` / `unbindmode MODE KEY` edits now report `unbind: KEY` / `unbindmode: KEY@MODE`, so small keymap surgery stays self-identifying in message logs.
- successful `bind KEY ACTIONSPEC`, `bindmode MODE KEY ACTIONSPEC`, `bindprefix KEY MODE [DOC...]`, and `bindmodeprefix OWNERMODE KEY MODE [DOC...]` edits now also report typed feedback (`bind: ...`, `bindmode: ...`, `bindprefix: ...`, `bindmodeprefix: ...`) so the creation side of the same loop reads in the same dialect.
- successful `binddoc KEY DOC...` / `bindmodedoc MODE KEY DOC...` edits now also report typed feedback (`binddoc: KEY -> DOC...`, `bindmodedoc: KEY@MODE -> DOC...`) so key descriptions do not fall back to an older ad-hoc success line.
- successful `set OPTION VALUE`, `setlocal OPTION VALUE`, `toggle OPTION`, and `togglelocal OPTION` edits now also report typed feedback (`set: name=value`, `setlocal: name(local)=value`, `toggle: name=value`, `togglelocal: name(local)=value`) so small configuration changes stay attributable in logs instead of collapsing to bare value lines.

  - searchable `apropos QUERY`, `topicpick`, `commandpick`, and `helppick` discovery surfaces for command/word/docs exploration
  - plain typed miss feedback for `help` too: `help docs TOPIC` -> `help docs: no such doc: TOPIC`, ordinary lookup misses -> `help: no such topic: QUERY` (with the same `Try: ...` suggestion preview when ranked matches exist)
