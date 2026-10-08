# Kanata integration

VHK intentionally does **not** implement global key interception itself.

On modern Linux desktops (especially Wayland), the most reliable pattern is:

1. Let a compositor / daemon own global hotkey capture.
2. Have that tool launch VHK macros for the “real work”.

Kanata is a popular choice because it works at the input-device level and can
run commands via its `cmd` action.

## Generate a config

From a VHK project folder:

```bash
vhk gen-kanata-config /path/to/project > ~/.config/kanata/vhk.kbd
```

If your VHK binary is not on PATH for Kanata:

```bash
vhk gen-kanata-config /path/to/project --vhk-cmd /usr/local/bin/vhk > ~/.config/kanata/vhk.kbd
```

By default VHK triggers macros **on key release**, which helps avoid repeated
firing from key-repeat.

## Why `danger-enable-cmd` is required

Kanata deliberately ships with the ability to execute external commands turned
off by default, and requires enabling it in the config:

```lisp
(defcfg
  danger-enable-cmd yes
)
```

This is also why VHK’s generator always emits `danger-enable-cmd yes`.
See Kanata’s configuration guide for details.

## Window scoping

Kanata does not have native “only when focused window matches X” scoping.
If you use `when:` selectors in VHK bindings, the generated Kanata config calls:

```bash
vhk run ... --require-window '{"class":"Firefox"}'
```

VHK then checks the active window via i3/sway IPC or Hyprland `hyprctl`.

## Practical tips

- Prefer running Kanata **as your user** if your macros depend on user-session
  services (Wayland portals, notification daemons, etc.).
- If you intercept only a few keys, ensure `process-unmapped-keys yes` is set so
  modifier state is tracked correctly for Kanata’s `switch` / `unmod` logic.
- If you run multiple keyboards, Kanata can target specific devices with
  `linux-dev`.

## See also

- `docs/WINDOW_WATCHERS.md` for event-driven automations.
- `docs/HOTSTRINGS.md` for text expansion via Espanso.
