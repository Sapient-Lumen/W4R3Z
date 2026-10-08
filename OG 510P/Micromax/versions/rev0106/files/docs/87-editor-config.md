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

- `history.persist` (bool) — enable persistence (requires `cap.persist`)
- `history.file` (str) — JSON path (default: `~/.config/micromax/history.json`)
- `history.limit` (int) — max entries per prompt kind (default: 200)

The file format is a simple JSON object: `{kind: ["entry", ...], ...}`.



## Clipboard backends

Micromax-editor keeps an internal clipboard by default (`set clipboard internal`).

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
