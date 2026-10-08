# Editor config / init file (rev64)

Micromax-editor loads a **user init file** at startup (best-effort):

- Default: `~/.config/micromax/init.mx`
- Override: `$MICROMAX_INIT` (explicit file path)

Load order:
1. core/editor hostcalls are installed
2. plugins are loaded from the plugin root (`--plugins`)
3. the user init file is evaluated
4. the requested file (if any) is opened

This ordering mirrors the usual expectation that user config can **override**
plugin keybindings/options.

## Common patterns

- Put user keybindings in the init file.
- Put personal helper words/macros in the init file.
- Use `require` to load additional `.mx` files (see `docs/88-require-and-paths.md`).
- Use plain `show` to inspect the active buffer's effective option state; rev424 also makes local overrides explicit as `(local)` so per-buffer drift stops hiding inside ordinary config checks.
- Use `showoptiongroups [QUERY]` when you want the smallest broad answer first — what option families are visible right now, and roughly what lives in each one.
- Use `showoption NAME` when you want the exact value/default/doc view for one option without losing alias spelling like `savehistory`.

## Reloading

There isn't a dedicated `reloadrc` command yet, but you can use:

- `reload "path/to/file.mx"` — loads even if previously `require`d
- `include "path/to/file.mx"` — always loads

(See `docs/88-require-and-paths.md` for path resolution rules.)


## Recent file persistence

By default the recent-file MRU is headless-only and does not persist.

Persistence touches the host filesystem, so it is additionally gated by:
- `cap.persist` (see `docs/32-capabilities.md`)

You can opt in via options:

- `recent.persist` (bool) — enable persistence
- `recent.file` (str) — path to the JSON file (default: `~/.config/micromax/recent.json`)
- `cap.persist-root` (str) — optional sandbox root for persistence files (default: `~/.config/micromax`)

When enabled, the editor loads the file after the user init runs (so the init can toggle it)
and saves on MRU updates (best-effort).

## Prompt history persistence

The editor keeps in-memory prompt histories for commands/find and most picker prompts.
You can optionally persist them (best-effort) via options:

- `history.persist` (bool) — canonical enable/disable option (requires `cap.persist`)
- `savehistory` (bool) — micro-esque alias for `history.persist`
- `history.file` (str) — JSON path (default: `~/.config/micromax/history.json`)
- `history.limit` (int) — max entries per prompt kind (default: 200)

The file format is a simple JSON object: `{kind: ["entry", ...], ...}`.

## Autosave

Micromax can now also autosave dirty path-backed buffers through the shared save path:

- `autosave` (int, default `0`) — save dirty path-backed buffers every N seconds; `0` disables autosave

Current rule:

- autosave only applies to buffers that already have a path
- it reuses the same save path as manual `save`, so save-time options like `rmtrailingws`, `eofnewline`, `mkparents`, `fileformat`, and `encoding` still apply
- it does not invent background threads; the existing host-driven timer pump is still the clock
- `quit` will best-effort autosave eligible dirty buffers before falling back to the ordinary unsaved-changes warning for anything left
- pathless or read-only dirty buffers still require an explicit user decision


## Savecursor persistence

Micromax can also remember the primary cursor position for each file path when
you reopen it later. This is intentionally small and shared-core: it does not
try to restore whole sessions, undo history, or multi-cursor state.

Options:

- `savecursor` (bool) — enable persistence (requires `cap.persist`)
- `savecursor.file` (str) — JSON path (default: `~/.config/micromax/cursor.json`)

When enabled, the editor loads the file after the user init runs and remembers
positions when switching buffers, closing buffers, saving, and on normal REPL/TUI exit.


## Parsecursor open targets

Micromax can optionally parse open targets like `notes.txt:42:7` as “open
`notes.txt` and place the primary cursor there immediately”.

Option:

- `parsecursor` (bool) — enable best-effort `file:line[:col]` parsing for open targets

Current rules:

- line numbers are 1-based
- columns are 0-based (`file:42` means line 42, column 0)
- malformed inputs stay literal paths
- literal existing colon-containing paths win over parsing
- explicit parsed targets override `savecursor` for that open
- the same behavior is preserved through interactive open, capability-gated/scripted open, and path-style command-palette opens

## Softwrap + wordwrap

Micromax can also shape long visual rows through two small ordinary options:

- `softwrap` (bool, default `false`)
- `wordwrap` (bool, default `false`)

Current rule:

- `softwrap` wraps long lines to the viewport width and disables horizontal scrolling
- `wordwrap` only matters when `softwrap` is enabled
- with `wordwrap=true`, wrapped rows prefer breaking at spaces when one fits on the current row
- long unbroken tokens still fall back to hard wrapping by width
- the same row boundaries drive rendering, cursor mapping, and visual-row movement

## Encoding

Micromax now also treats text encoding as a real per-buffer open/save option:

- `encoding` (str, default `utf-8`)

Current rule:

- ordinary `open` / `ed.open` decode existing files using the configured encoding
- ordinary `save` / `ed.save` encode using the effective buffer encoding
- the buffer-local option spelling stays user-facing (`latin-1` stays `latin-1`) even though Python may normalize aliases internally when doing the actual codec lookup
- docs/help buffers keep using their existing explicit UTF-8 docs path

## Fileformat

Micromax now also treats line endings as a real per-buffer option instead of a
statusline placeholder:

- `fileformat` (enum: `unix` or `dos`, default `unix`)

Current rule:

- existing files are best-effort detected on open (`CRLF` => `dos`, otherwise `unix`)
- in-memory buffer text stays normalized to `\n` regardless of on-disk line endings
- `save` writes `\n` for `unix` and `\r\n` for `dos`
- `setlocal fileformat dos` affects future saves immediately without inventing a richer newline model

## Autoindent

Micromax can now also control its shared newline indentation behavior through an
ordinary option:

- `autoindent` (bool, default `true`)

Current rule:

- with the default `autoindent=true`, `InsertNewline` reuses the current line's leading whitespace
- splitting inside the indent prefix still only keeps the prefix up to the split point
- with `set autoindent false`, Enter inserts a plain newline without copying indentation
- `keepautoindent` only matters when `autoindent` actually inserted indentation for you


## Keepautoindent

Micromax can optionally keep or clear whitespace-only autoindent lines when you
press Enter again on them:

- `keepautoindent` (bool, default `false`)

Current rule:

- by default, if the *original* line was only spaces/tabs and `InsertNewline` autoindents the next line, the previous line is cleared back to empty
- with `set keepautoindent true`, the previous whitespace-only line is kept
- this stays in the shared `InsertNewline` action rather than a save-time cleanup pass


## Readonly

Micromax can also mark ordinary buffers as protected through the normal option
system:

- `readonly` (bool, default `false`)

Current rule:

- mutating editor actions reject edits while `readonly` is enabled
- `save` and capability-gated `ed.save` also refuse to write
- `setlocal readonly true` is the most natural per-buffer form
- `set readonly true` can provide a broader default, and `setlocal readonly false` locally overrides that default for one buffer


## Tabmovement

Micromax can optionally make leading runs of spaces feel more like tabs during
plain left/right cursor motion:

- `tabmovement` (bool, default `false`)

Current rule:

- only applies when `tabstospaces` is also enabled
- `CursorLeft` / `CursorRight` and `SelectLeft` / `SelectRight` treat leading runs of exactly `tabsize` spaces like one tab stop
- outside leading indentation, movement stays character-wise

## Smartpaste

Micromax can optionally apply a tiny micro-esque paste aid in the shared editor core:

- `smartpaste` (bool) — when `Paste` inserts multiple lines at an indentation-only prefix, reuse that existing whitespace prefix for otherwise-unindented continuation lines

This is intentionally conservative and headless-first:

- it only affects multi-line pastes
- it does nothing for mid-line pastes inside ordinary text
- it does nothing when the pasted block already has indentation on every non-empty line
- it applies equally to internal clipboard paste, external clipboard import, and per-cursor multi-item paste

## Clipboard backends

Micromax-editor keeps an internal clipboard by default (`set clipboard internal`).

Rev343 note: the ordinary clipboard loop is now more explicit too — `Copy` / `Cut` report selection counts and copied-char totals, successful `Paste` reports cursor count, inserted chars, and the landed target, and an empty internal clipboard now fails as `paste: clipboard empty` instead of disappearing into silence. This is intentionally a trust/flow pass, not a richer kill-ring design.

When running the curses TUI, you can opt into OSC 52 export (system clipboard over
a terminal escape sequence) with:

- `set clipboard terminal`
- `set clipboard.osc52 true` (default)
- `set clipboard.osc52.max 100000` (bytes; 0 = unlimited)

Safety note: script-triggered clipboard export is disabled by default; enable
`cap.clipboard-write` if you want plugins/scripts to drive OSC 52 exports.



## Capability gates (unsafe features)

Some host surfaces are intentionally **disabled by default** (they touch the
host world: browser/processes).

You can enable them via `cap.*` options in your init file:

- `cap.open-url` — allow opening external URLs from docs help
- `cap.shell` — allow running shell commands from scripts

See: `docs/32-capabilities.md`.


### External clipboard (rev104)

If you want micromax-editor to export copied text to your desktop clipboard,
use `clipboard=external`. The curses TUI will best-effort pipe clipboard writes
to a detected clipboard tool:

- Wayland: `wl-copy`
- X11: `xclip` or `xsel`
- macOS: `pbcopy`
- Windows: `clip` / `clip.exe`

Overrides:

- `set clipboard.external.cmd <program>`
- `set clipboard.external.args <args>`
- `set clipboard.external.timeout 1.0`

Safety note: script-triggered external clipboard export is disabled by default;
enable `set cap.clipboard-write true` if you want plugins/scripts to drive
system clipboard writes.


## Basename

Micromax now also exposes the small micro-esque display option:

- `basename` (bool, default `false`)

Current rule:

- with the default `basename=false`, statusline-style filename displays prefer the full buffer path when one exists
- with `set basename true` or `setlocal basename true`, `$(filename)` / `showstatus` prefer the basename instead
- raw structural state still keeps both `path` and `file_name`, while `display_name` is the effective user-facing label

## Fastdirty

Micromax now also exposes the dirty-buffer policy itself as a small ordinary option:

- `fastdirty` (bool, default `false`)

Notes:

- with the default `fastdirty=false`, the buffer compares its current text against the last clean baseline and clears `dirty` again when the content truly matches
- with `set fastdirty true`, the first edit makes the buffer sticky-dirty until the next successful save/open baseline reset
- command-bar `set` / `setlocal`, Micromax `set` / `toggle`, and `ed.opt-set` / `ed.opt-set-local` all resync existing buffers immediately



## Matchbrace style

Micromax now also exposes a tiny renderer-side follow-up for the existing brace cue:

- `matchbracestyle` (enum `underline|highlight`, default `underline`)

Current rule:

- `underline` keeps the earlier bold+underline brace cue
- `highlight` uses a tiny bold+reverse highlight instead
- the setting only affects the visible brace cue in the current curses TUI; it does not change buffer text or add headless brace spans

## Visible invisible characters (`showchars`)

Micromax now also has a tiny renderer-side `showchars` option:

- `showchars` (str, default `""`)

Current rule:

- the current curses TUI recognizes micro-esque `key=value` pairs separated by commas
- supported keys are `space`, `tab`, `ispace`, and `itab`
- `ispace` / `itab` override the ordinary `space` / `tab` glyphs in the leading indent run before the first visible character on a line
- shown characters are display-only and never enter the buffer text
- this first pass keeps every replacement one cell wide, so even `tab` / `itab` currently use only their first configured character
- softwrap continuation-indent prefix spaces stay plain because they are renderer-created, not file content
