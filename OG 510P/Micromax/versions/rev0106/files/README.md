# micromax (v97)
Micromax is a **small, embeddable, concatenative language + VM** designed to become the native
plugin/config/macro system for a lightweight terminal editor in the spirit of **micro**.

The project deliberately grows in two directions at once:

- **language/VM**: tiny, inspectable, heavily tested, pleasant to evolve by hand offline
- **editor core**: headless-first, deterministic, and unit-testable before any terminal UI hardens

Rev69 note: improved VM decompiler surfaces: `see` now includes a compact tier-2 disassembly and const pool when available, and tooling can fetch structured disassembly via `disasm-rows`. The editor embedding also exposes a small regex hostcall set (`re.search`/`re.sub` etc.) aligned with `replace`/`replaceall`.

Rev67 note: the VM now has a **dev-mode stack effect checker starter kit** (`stackcheck!` warn/error modes, `infer-effect`, `check-effect`), and quotations preserve leading paren-comments so you can annotate quote effects like `[ ( x -- y ) ... ]`.

Rev66 added the portable syntax highlight span model (`ed.highlight`) and a deterministic timer queue (`ed.after`/`ed.pump-timers`). Rev65 added autoindent + `tabsize`/`tabstospaces`; rev64 added `jumppick`, user rc/init loading, and the `include`/`require` search convention.

Rev72 note: the editor statusline is now configurable via micro-esque `statusformatl`/`statusformatr` templates (a tiny `$()` renderer), and the stdlib adds `ensure`/`finally` for always-run cleanup built on `catch`/`throw`.

Rev82 note: the docs help browser got a little more micro-esque — `helplinkpick` now groups links into Docs/Files/External sections in the TUI, and external-link follow gives an explicit `cap.open-url` enable hint.

Rev83 note: docs navigation now recognizes **reference-style links** (`[text][id]` + `[id]: target`) and **autolinks** (`<https://...>`), so docs pages can use more idiomatic Markdown forms.

Rev90 note: picker-style prompts (buffer/doc/help pickers, palette, etc.) now support **Up/Down selection** without mutating the typed query, and `Ctrl-y` copies the selected row (for links: copies the target).

Rev91 note: picker-style prompts now also support **PageUp/PageDown selection jumps** (option: `prompt.page`, default 8), which makes long pickers (palette, docs link lists) feel much closer to a real command palette.

Rev92 note: picker-style prompts gain a `prompt.wrap` option (wrap vs clamp), support `Ctrl-Home`/`Ctrl-End` to jump to first/last selection, and the TUI repeats the current section header as a sticky header while paging through long mixed sections.

Rev93 note: picker-style prompts now support `Alt-Up`/`Alt-Down` section jumps (jump between section headers; `Alt-Up` also jumps to the start of the current section when used inside it), implemented in the headless core and used by the minimal TUI.

Rev94 note: the docs browser now understands **shortcut reference links** (`[id]` when a matching `[id]: target` definition exists), and the minimal TUI underlines inline/reference/shortcut/autolinks consistently so help pages feel more like a real in-editor browser.

Rev97 note: docs link pickers (`helplinkpick`) can optionally group links by nearest markdown heading (option: `help.linksections heading`), the host adds a capability-gated `ed.fs-stat` helper for portable path metadata, and the repo includes `tools/mkrevzip.py` to build standard-named offline archives.

Rev95 note: small repo + picker UX polish — the `Makefile` now runs scripts via `bash` (so `make test` works even when executable bits are lost in an archive), and the minimal TUI now highlights query-token substring matches in picker suggestion rows for faster scanning.

Rev84 note: docs navigation gained a combined picker (`helpnavpick`) that merges **Headings** + **Links** into one navigator, and the host now exposes grouped navigator sections via `ed.helpnav-section-rows`.

Rev85 note: the minimal curses TUI now interprets **Alt/Meta chords** (ESC-prefixed sequences) so default `Alt-*` bindings work, and maps **Ctrl-Space** (NUL) to `Ctrl-Space` for command palette muscle memory. Core defaults now include `Ctrl-b` buffer picker, `Ctrl-o` open (prefilled), `Ctrl-r` replace (prefilled), and `Alt-g` binding discovery.

Rev86 note: added an interactive **query-replace** loop (`qreplace` / `queryreplace`) that confirms each replacement with a tiny y/n/a/q keymode (capture mode so global bindings can't accidentally fire). Also unified Cursor<->offset conversion helpers (`micromax_editor.textpos`) used by search + replace.
Rev87 note: `replace` / `replaceall` and `qreplace` now respect the editor's `ignorecase` option (like `find`), and `qreplace` shows a small `match i/N` progress hint when it can pre-count matches.
Rev88 note: docs buffers gained `helplinkcopy` (and `y`) to copy the markdown link target under cursor, and external links now confirm by default when `cap.open-url` is enabled (capture keymode: y/open, n/cancel, c/copy).

Rev89 note: added `urlopen` / `urlcopy` (and default `Alt-o`/`Alt-y` bindings) to open/copy URLs under cursor in any buffer, reusing the same capability gate (`cap.open-url`) and confirmation keymode (`openurl`).

## What is already real

### Language / VM
- Python reference VM with wordlists, quotations, deferred words, hooks, maps, locals, and hostcalls
- two-tier execution path: token interpreter + optional bytecode/compiler scaffolding
- provenance/debug surfaces such as spans, `see`, `help`, `where`, and hook/keybinding inspection
- pure micromax stdlib loaded from `src/micromax/stdlib/core.mx`

### Editor substrate
- headless `Editor` core with buffers, cursors, selections, undo, and action chaining
- command bar + shell-ish parsing + prompt history
- searchable command/action palette, topic/help prompt, and current-binding prompt built on shared headless row metadata
- command palette now has a small MRU/recent section and grouped palette-section rows for future UIs/scripts
- incremental search (`ignorecase`, `incsearch`), replace, and jump list
- multi-cursor primitives, macros, clipboard model, and statusline/infobar data model
- keybinding modes, one-shot/transient keymodes, `whichkey`-style discovery, binding docs, and prefix helpers
- micromax-defined commands, completion hooks, plugin lifecycle hooks, and grouped reload cleanup

### Archive ergonomics
- docs aimed at humans **and future LLMs** (`docs/01-llm-start-here.md`, `docs/02-repo-map.md`)
- `make context` for a curated snapshot
- `make doctor` for archive hygiene
- `make pack` for a clean zip archive

## Repository layout

- `docs/` — research notes, design docs, roadmap, decisions log, portability ledger
- `src/micromax/` — reference VM, core words, REPL, stdlib
- `src/micromax_editor/` — headless editor substrate + VM bridge
- `plugins/` — micromax plugins
- `examples/` — small language examples
- `tests/` — headless unit tests
- `tools/` + `scripts/` + `Makefile` — bootstrap/lint/test/context/pack helpers

## Quick start

Run the micromax REPL:

```bash
python -m micromax.repl
```

Run the headless editor prototype (REPL UI):

```bash
python -m micromax_editor
python -m micromax_editor path/to/file.txt
```

Run the minimal curses TUI:

```bash
python -m micromax_editor --tui
python -m micromax_editor --tui path/to/file.txt
```

## Development workflow

```bash
make bootstrap
make test
make doctor
make context
```

Optional local git bootstrap (no remote required):

```bash
make init-git
```

Build a clean archive zip:

```bash
make pack
```

## Good entry points

Read these first:

1. `TODO.md` + `docs/43-worklist.md`
2. `docs/00-vision.md`
3. `docs/01-llm-start-here.md`
4. `docs/42-portability-ledger.md`
5. `docs/22-two-tier-execution.md`
6. `docs/50-editor-behaviors.md`
7. `docs/64-editor-prompt-completion.md`
8. `docs/71-cookbook.md`

## Portability contract

The Python implementation is the **reference implementation** and **test oracle** for future ports
(such as Rust/WASM). If you add VM surface area, update `docs/42-portability-ledger.md`.
