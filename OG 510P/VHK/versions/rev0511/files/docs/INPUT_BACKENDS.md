# Input backends (keyboard + pointer)

Desktop automation lives or dies on its input injection story.

VHK tries to be pragmatic:

- **Prefer compositor APIs** when they exist (sway IPC, Hyprland `hyprctl`, etc.).
- Otherwise use the best available helper **for the current session**.
- Provide escape hatches (environment overrides) so users can pin a backend when auto-choice is wrong.

## The current landscape

### X11

- **`xdotool`** is the classic choice (XTEST-based injection).

Pros: simple; supports window focus and absolute pointer motion.

Cons: X11-only.

### Wayland

Wayland intentionally restricts global input injection. The ecosystem has a few common workarounds:

- **`wtype`**: uses the Wayland *virtual keyboard* protocol.
  - Works well on wlroots compositors.
  - Often fails on GNOME/Mutter with "Compositor does not support the virtual keyboard protocol".
- **`ydotool`**: uses the Linux **uinput** subsystem.
  - Requires `ydotoold` daemon + `/dev/uinput` permissions.
  - Socket defaults vary; some distros run the daemon as root with `/tmp/.ydotool_socket`, others as a user service under `$XDG_RUNTIME_DIR`.
- **`dotool`**: also uses **uinput**, but reads commands from stdin.
  - One-shot `dotool` can have an initial "device registration" delay.
  - `dotoold` + `dotoolc` keeps devices alive for snappy hotkey usage.
  - Useful command vocabulary (stdin protocol):
    - `key CHORD...`, `keydown CHORD...`, `keyup CHORD...`, `type TEXT`
    - `click left|middle|right`, `buttondown ...`, `buttonup ...`
    - `wheel AMOUNT`, `hwheel AMOUNT`
    - `mouseto X Y` (normalized 0..1), `mousemove X Y` (relative)

## VHK selection + overrides

Default selection (Wayland):

- Keyboard (wlroots-ish): `wtype` → `dotoolc` → `dotool` → `ydotool`
- Keyboard (GNOME/Mutter-ish): `dotoolc` → `dotool` → `ydotool` → `wtype`
- Pointer: `dotoolc` → `dotool` → `ydotool`

Those are preference orders, not blind promises: `dotoolc` only really shines when `dotoold` is already alive. VHK now keeps that distinction visible in doctor/readiness output **and** in the live runtime chooser, so a lane that is explicitly known broken does not keep getting auto-selected just because a helper binary is on `PATH`.

Override with environment variables:

- `VHK_INPUT_BACKEND=...` (affects both)
- `VHK_KEYBOARD_BACKEND=...`
- `VHK_POINTER_BACKEND=...`

Supported values: `auto|xdotool|wtype|ydotool|dotool|dotoolc|xvkbd`

Doctor note:

- `vhk doctor --json` now distinguishes **one-shot `dotool` presence** from a truly **daemon-ready `dotoold` + `dotoolc` lane**.
- In other words: seeing `dotoolc` on `PATH` is no longer treated as proof that the low-latency helper path is actually ready.

## Practical setup recipes

### 1) Wayland + ydotool

1. Fix `/dev/uinput` permissions (`vhk doctor --json` + `vhk gen-udev-uinput`).
2. Start the daemon:

```bash
vhk gen-ydotoold-service --out-dir ~/.config/systemd/user
systemctl --user daemon-reload
systemctl --user enable --now ydotoold-vhk.service
```

Notes:

- Some ydotool releases/setups have a broken `mousemove --absolute X Y` (moves
  to the top-left regardless of coordinates). VHK defaults to a conservative
  workaround: reset to (0,0) using `--absolute 0 0`, then move relatively.
  You can force native absolute moves with:

  ```bash
  export VHK_YDOTOOL_ABSOLUTE_METHOD=native
  ```

- If your ydotool virtual device has coordinate scaling issues (eg "10px moves
  20px"), set a pixel scale factor:

  ```bash
  export VHK_YDOTOOL_PIXEL_SCALE=0.5
  ```

### 2) Wayland + dotool (simple stdin protocol)

1. Fix `/dev/uinput` permissions (same as above).
2. Start the daemon for low-latency hotkeys:

```bash
vhk gen-dotoold-service --out-dir ~/.config/systemd/user
systemctl --user daemon-reload
systemctl --user enable --now dotoold-vhk.service
```

Then prefer the client:

```bash
export VHK_KEYBOARD_BACKEND=dotoolc
export VHK_POINTER_BACKEND=dotoolc
```

Notes:
- VHK macros use **pixel** coordinates. When driving dotool's `mouseto`, VHK
  converts pixels into dotool's normalized 0..1 space using compositor
  geometry probes (Hyprland `hyprctl monitors -j` or i3/sway IPC outputs).

## Looking forward: libei / EIS

The most promising cross-compositor answer is **libei** (Emulated Input) + an **EIS** server in the compositor.

VHK does not integrate with libei yet, but it’s the clearest path to reducing per-compositor hacks over time.
