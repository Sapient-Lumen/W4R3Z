# micro inspirations (notes)

This repo is not trying to clone `micro`, but `micro` is an excellent reference point
for a **sane terminal editor** with modern defaults.

Primary sources (micro upstream docs):

- micro homepage: https://micro-editor.github.io/
- micro default keys: https://raw.githubusercontent.com/micro-editor/micro/master/runtime/help/defaultkeys.md
- micro command bar + commands: https://raw.githubusercontent.com/micro-editor/micro/master/runtime/help/commands.md

Secondary/adjacent things worth stealing:

- micro has a small ecosystem of plugins that implement "missing" navigation affordances.
  Example: the `micro-bookmark` plugin adds bookmark/next/prev/clear commands for jumping between saved locations.
  This informed our decision to ship tiny built-in **marks** early and add a searchable `markpick` picker before any UI exists.
- micro keybindings (including chaining + command: bindings): https://raw.githubusercontent.com/micro-editor/micro/master/runtime/help/keybindings.md
- micro options (incsearch, ignorecase, clipboard backends): https://raw.githubusercontent.com/micro-editor/micro/master/runtime/help/options.md
- micro plugin help (lifecycle + callbacks): https://raw.githubusercontent.com/micro-editor/micro/master/runtime/help/plugins.md
- micro has a `raw` command that opens a buffer showing the escape sequence for every terminal event it receives — a practical way to debug “why doesn’t this key bind?”.
  We likely want an equivalent TUI-only toggle (even if it’s just a statusline readout) once we start caring about more key variants.
- micro has a small ecosystem of “command palette” plugins (e.g. Palettero) that fuzzy-search commands and then prefill the command bar; one neat UX trick is **double-enter** to execute immediately without editing.
  Rev85 follow-on: we now bind `Ctrl-Space` to our built-in command palette and the curses TUI interprets ESC-prefixed Alt/Meta chords, so the micro-esque default Alt bindings are actually usable.

## What we steal first (low-hanging, high leverage)

### 1) Action chains with success/failure control

Micro lets you bind a key to a *chain* of actions with three separators:

- `,` always continues to the next action
- `|` aborts the chain if the previous action *succeeded*
- `&` aborts the chain if the previous action *failed*

The docs also note that you can escape separators with `\\` or wrap them in quotes.

Example from micro docs:

- `Tab` is bound to: `Autocomplete|IndentSelection|InsertTab`

We implemented this behavior in:

- `micromax_editor.keymap.parse_action_chain`
- `Editor.run_action_chain`

### 2) Desktop-default selection + clipboard

Micro's default keys include:

- Shift+arrows: select
- Ctrl-c/x/v: copy/cut/paste selection
- Ctrl-k: cut line
- Ctrl-d: duplicate line
- Ctrl-a: select all

We implemented the same *shape* (and then upgraded it):

- v9: selection + internal clipboard
- v10: per-cursor selections + micro-esque `CutLine` accumulation until paste

See: `docs/56-editor-selection-clipboard.md`.

### 3) Command bar (Ctrl-e) + shell-like argument parsing

Micro opens its command bar with `Ctrl-e` and describes it as a single-line buffer.
It also states the command parser uses **/bin/sh-like** parsing rules (quotes + escaping).

We mirrored that design with:

- `Editor.enter_prompt(kind='command')`
- `micromax_editor.cmdline.parse_cmdline` using `shlex.split`
- `micromax_editor.command_dispatcher` (help/bind/showkey/goto/jump/open/save/quit/set/show/toggle/reload/replace/...)

### 4) Bindings that run commands: `command:` and `command-edit:`

Micro supports keybindings that execute commands by prefixing the binding with `command:`.
It also supports `command-edit:` which opens command mode with a prefilled line.

We mirrored this in action-chain execution:

- `command:...` executes via the command dispatcher
- `command-edit:...` opens the command prompt prefilled

### 5) Incremental search (incsearch)

Micro exposes an `incsearch` option (default `true`) that enables incremental search
in the Find prompt (matching as you type), and `ignorecase` (default `true`) for
case-insensitive searching.

We mirrored this as a headless option + search substrate:

- `Options` registry in `micromax_editor.options`
- `SearchState` + `find_next/find_prev` in `micromax_editor.search`
- the REPL UI demonstrates incsearch by calling `ed.find(...)` on prompt edits

### 6) Macros

Micro binds:

- `Ctrl-u` toggle recording
- `Ctrl-j` play latest

We implemented action-level macros in v10. See `docs/58-editor-macros.md`.

### 7) Multiple cursors

Micro binds:

- `Alt-n` add cursor from selection/word
- `Alt-Shift-Up/Down` spawn above/below
- `Alt-p` remove last cursor
- `Alt-c` remove all
- `Alt-x` skip selection
- `Alt-m` spawn a cursor at the start of each selected line

We implemented a pragmatic subset in v10. See `docs/57-editor-multicursor.md`.

## Not doing yet (on purpose)

- syntax highlighting
- terminal emulator panes
- mouse support
- split panes and tabs

We keep the substrate small and **unit testable** while we iterate on language + embedding.
