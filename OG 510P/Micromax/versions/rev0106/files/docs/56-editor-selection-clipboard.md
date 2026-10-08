# Selection, clipboard, and indentation (micro-inspired)

This doc captures "low-hanging fruit" editor behavior that is surprisingly
foundational: selection + copy/cut/paste, plus indentation of selected lines.

## What micro does (reference behavior)

Micro's default keys include:

* **Shift + arrows**: "Move and select text".
* **Ctrl-c / Ctrl-x / Ctrl-v**: Copy / Cut / Paste selection.
* **Ctrl-k**: Cut current line.
* **Ctrl-d**: Duplicate current line.
* **Ctrl-a**: Select all.
* **Tab**: `Autocomplete|IndentSelection|InsertTab` action chain.
* **Shift-Tab**: Unindent selection.

Source: micro `runtime/help/defaultkeys.md` (raw):
  https://raw.githubusercontent.com/micro-editor/micro/master/runtime/help/defaultkeys.md

Micro also documents a special detail about `CutLine`: it appends additional
cut lines to the clipboard until the next paste.

Source: micro `runtime/help/keybindings.md` (raw):
  https://raw.githubusercontent.com/micro-editor/micro/master/runtime/help/keybindings.md

Micro has a `clipboard` option with backends (`external`, `terminal`, `internal`).
The docs note that `terminal` uses OSC 52 and can work over SSH.

Sources:

* https://raw.githubusercontent.com/micro-editor/micro/master/runtime/help/options.md
* https://raw.githubusercontent.com/micro-editor/micro/master/runtime/help/copypaste.md

## What micromax-editor does (v16)

We implement:

* **Per-cursor selections** (each cursor has its own anchor).
* `Copy`, `Cut`, `Paste`, `CutLine`, `DuplicateLine` actions.
* Selection movement actions: `SelectLeft/Right/Up/Down`.
* `SelectAll` collapses to a single cursor and selects the whole buffer.
* `IndentSelection` / `UnindentSelection` operate on the union of selected lines.
* Clipboard is stored as **items** (selection chunks) or **lines** (cut-line blocks).
* `CutLine` accumulates until the next paste (micro-esque).
* Selection endpoints are stored as **directed anchor+cursor** pairs (Kakoune/Helix-ish).
* Selection direction helpers exist as actions (`FlipSelections`, `EnsureSelectionsForward`).
* Scripting convenience: `ed.selection-range` / `ed.set-selection-range` provide a
  directionless range view for the primary selection.

### Design notes

* Typed insert/backspace replace/delete selections.
* Multi-cursor edits apply bottom-to-top to avoid coordinate shift issues.
* Clipboard is internal for now, but we keep micro's `clipboard` option surface
  so external/terminal backends can be added later.


## Terminal clipboard (OSC 52) (rev103)

Micromax keeps an internal clipboard by default.

When running the **curses TUI**, you can opt into a micro-esque terminal clipboard
backend:

- `set clipboard terminal`
- `set clipboard.osc52 true` (default)
- `set clipboard.osc52.max 100000` (bytes; 0 = unlimited)

In this mode, interactive copy/cut operations will **best-effort export** the
clipboard to the system clipboard via an OSC 52 escape sequence.

Notes:

- This is **copy-only** for now. Pasting is usually done via your terminal's paste
  keybinding (it reads the system clipboard and sends text to the app).
- Terminal emulator support varies; many terminals support writing but not reading.
- Script-driven clipboard exports are **disabled by default**; enable
  `cap.clipboard-write` if you want scripts/plugins to trigger OSC 52 exports.



## External clipboard (rev105)

When `clipboard=external`, Micromax can interact with the *system* clipboard via
platform tools (mirroring micro’s expectations: pbcopy/pbpaste on macOS,
xclip/xsel on Linux, and friends).

Best-effort detection order:

**Write (export on copy/cut):**

- Wayland: `wl-copy`
- X11: `xclip` or `xsel`
- macOS: `pbcopy`
- Windows: `clip` / `clip.exe`

**Read (import on Paste):**

- Wayland: `wl-paste -n`
- X11: `xclip -o` or `xsel --output`
- macOS: `pbpaste`
- Windows: `powershell Get-Clipboard -Raw`

Overrides (write):

- `set clipboard.external.cmd ...`
- `set clipboard.external.args ...`
- `set clipboard.external.timeout 1.0`

Overrides (read):

- `set clipboard.external.readcmd ...`
- `set clipboard.external.readargs ...`
- `set clipboard.external.readtimeout 1.0`

Paste behavior:

- When `clipboard=external` and `clipboard.external.import=true` (default), the
  `Paste` action (Ctrl-v in the core plugin) will **best-effort import** the
  system clipboard and paste it.
- If external clipboard tools are unavailable, Micromax falls back to its
  internal clipboard.

Safety note:

- Script-driven clipboard **exports** remain disabled by default; enable
  `set cap.clipboard-write true` if you want plugins/scripts to trigger system
  clipboard writes.
- Script-driven clipboard **imports** are also disabled by default; enable
  `set cap.clipboard-read true` if you want scripts/plugins to read the system
  clipboard (via `ed.clipboard-import` or scripted Paste).

References: micro clipboard docs + common clipboard tools.

## Bracketed paste and the `paste` option (rev104)

Terminal pastes can arrive in two broad ways:

1. **Bracketed paste**: the terminal wraps pasted text in
   `ESC[200~ ... ESC[201~`. Editors can treat the payload as a single paste
   event and avoid autoindent/autopairs corruption.
2. **Key-burst paste**: some terminals send the pasted characters as a rapid
   burst of key events. Editors may mistakenly treat them as typed input and
   apply per-key features (autoindent, autopairs, etc.).

Micromax’s curses TUI now enables bracketed paste mode on startup (and disables
it on exit) and inserts bracketed pastes as a single `InsertText` chunk.

For terminals that *don't* support bracketed paste, Micromax also ships a
micro-esque escape hatch: the `paste` option. When enabled, the TUI aggregates
rapid character bursts into a single insert. This is meant to be toggled
*temporarily* while pasting, just like micro’s recommendation.
