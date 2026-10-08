# KMonad integration

VHK can export `bindings:` from `project.yaml` into a **KMonad** config that runs
macros as shell commands.

The key idea (copied from how many KMonad users build "macro layers") is:

- choose a **leader key** (default: `caps`)
- holding the leader temporarily activates a `vhk` layer
- inside that layer, selected keys run `vhk run <project> <macro>` via KMonad’s
  `cmd-button`.

This works across X11, Wayland, and even TTY sessions because KMonad hooks the
keyboard at the evdev/uinput layer.

## Generate a config

```bash
vhk gen-kmonad-config /path/to/project --out ~/.config/kmonad/vhk.kbd
```

By default the generated config expects you to set `$KBD_DEV` to the input
device file (typically under `/dev/input/by-id`). KMonad’s FAQ explicitly
recommends the `by-id` directory, and documents an env-var based approach so the
same config can work across different keyboards.

Example (bash):

```bash
export KBD_DEV=/dev/input/by-id/usb-...-event-kbd
kmonad ~/.config/kmonad/vhk.kbd
```

### Collision handling (same trigger key used multiple times)

If multiple VHK bindings share the same final key (e.g. `Mod4+P` and
`Control+P`), KMonad can’t naturally express the same WM-style modifier scoping.

The generator resolves this by:

- mapping the first binding directly in the `vhk` layer
- mapping additional bindings into `vhk_alt1`, `vhk_alt2`, …
- assigning **selector keys** (`1`, `2`, … when available) that perform
  `layer-next` into those alt layers

Workflow: hold the leader → press selector key → press the trigger key.

## Why this design

KMonad configs do not have a native concept equivalent to i3’s “Mod4+Shift+P”
criteria-scoped binds. The quick reference describes `layer-toggle` / `layer-next`
as the intended way to build "modes" and leader-key style flows, and also warns
that command execution is gated behind `allow-cmd` for safety.

So the exporter intentionally produces a **mode/layer** config rather than
trying to guess your preferred remapping strategy.

## Important: permissions and safety

### `/dev/uinput` and `/dev/input`

On Linux, KMonad needs access to both the `input` and `uinput` subsystems.
The FAQ documents the typical setup:

- ensure a `uinput` group exists
- add your user to `input` and `uinput`
- add a udev rule for the `uinput` device
- ensure the `uinput` module is loaded (`modprobe uinput`)

### `allow-cmd`

The generated config sets `allow-cmd true` so `cmd-button` works.
KMonad’s docs explicitly warn this can be dangerous if someone can edit your
config (because it enables arbitrary shell commands as key actions).

Treat your KMonad config like a shell script: keep permissions tight.

## Tips

- Start by running:
  - `kmonad -d <file.kbd>` to validate syntax (dry-run)
  - `kmonad --log-level debug <file.kbd>` if it starts but doesn’t behave
- Prefer using `/dev/input/by-id/...` for stable device paths.
- If you want **WM-style modifier binds**, prefer `vhk gen-kanata-config` or
  `vhk gen-keyd-config` (those tools model modifiers directly).

## References

- KMonad quick reference (configuration options, `allow-cmd`, `cmd-button`, layers):
  - https://raw.githubusercontent.com/kmonad/kmonad/master/doc/quick-reference.md
- KMonad FAQ (Linux permissions, udev rule, device discovery):
  - https://raw.githubusercontent.com/kmonad/kmonad/master/doc/faq.md

## Lint support

`vhk lint-project` now emits:

- `KMONAD_TRIGGER_SHAPE_CHANGE` when a project has bindings, because the export
  is a leader/layer macro surface rather than a direct WM-style hotkey map.
- `KMONAD_SCOPE_RUNTIME_ONLY` when a binding uses `when:` and the selector stays
  VHK-owned at runtime.
- `KMONAD_COLLISION_SELECTOR_LAYER` when multiple bindings share the same final
  trigger key and the exporter will allocate selector sublayers.
