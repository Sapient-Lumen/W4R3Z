# Editor integration plan (more concrete)

We want “Emacs-like” extensibility without the sprawl:
- every editor action is a word or quotation
- keymaps bind to quotations
- config is micromax code, not JSON

See also: `docs/50-editor-behaviors.md` for the UX wishlist.

## Why “Forth as the plugin system” can be right

Pros:
- one language for config + commands + macros + plugins
- live development cycle (redefine words, reload files)
- extremely small runtime footprint (good for terminal apps)

Risks:
- plugins can crash or hang the editor
- global namespace pollution
- unsafe host access

Mitigations (design commitments):
- **wordlists + search order** for isolation
- **capability-based host calls** (allowlisted)
- **structured errors + trace**
- later: step/time limits, per-plugin VMs, safe schedulers

## Architectural sketch

- `Editor` owns:
  - `Buffer` objects
  - `Window` / `Pane` layout
  - `Keymap` stack (global, mode, transient)
  - one or more `MicromaxVM` instances (starting with 1)

- `MicromaxVM` exposes a small host API via `hostcall` words, e.g.:
  - `"editor.current-buffer" hostcall   ( -- buf )`
  - `"buf.insert" hostcall              ( s buf -- )`
  - `"cursor.move" hostcall             ( dx dy -- )`
  - `"key.bind" hostcall                ( key q -- )`
  - `"command.register" hostcall         ( "name" q -- )`

In early iterations, “buf” and other editor objects can be opaque Python objects.
Later we should wrap them with safe micromax-visible proxies.

## Modes

Modes are wordlists + keymap overlays:
- `mode.text`
- `mode.python`
- `mode.forth`

Activating a mode does:
- push mode keymap onto keymap stack
- (optional) push mode wordlist onto the micromax search order

## Sane plugin packaging

A plugin is a directory:
- `plugin.json` metadata (optional; rev7 uses JSON for simplicity)
- `init.mx` (or `init.mmx` / `init.mf` during the transition)
- optional assets / themes

Loading algorithm (implemented in rev7, minimal):
1. create a dedicated plugin wordlist `wid`
2. set CURRENT to `wid`
3. optionally push `wid` onto the search order during plugin init
4. evaluate `init.mx`
5. pop `wid` from the search order (unless plugin explicitly opts into global)

Additionally, if a plugin defines lifecycle words, the host calls them:
- `preinit` → `init` → `postinit` during load
- `deinit` during unload

This yields “isolated by default” while still allowing cooperative extensions.

## Keymaps + quotations

Keybindings want code values:

    "Ctrl-S" [ "file.save" hostcall ] "key.bind" hostcall

Macros want recorded quotations:

    "macro.start" hostcall  ...  "macro.end" hostcall

Prompts want callbacks:

    [ "prompt.read-line" hostcall "buf.insert" hostcall ] "editor.with-prompt" hostcall

So quotations are not optional—they’re an editor integration primitive.

## Guardrail checklist (rev3 additions)

- **Every plugin hook runs under** `catch` (errors reported, editor stays alive).
- **Every hook has a budget** via `with-budget` (prevents accidental infinite loops).
- **Hostcalls are capability-based** (allowlist) and should be split into:
  - read-only editor queries
  - UI-only mutations (only callable on the UI task)
