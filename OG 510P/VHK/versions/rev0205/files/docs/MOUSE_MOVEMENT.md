# Mouse movement: smoothing and drag paths

VHK is primarily a *headless* runner, so the default `MouseMove` behavior is an
instantaneous jump (or a single relative delta). That mirrors tools like
`xdotool`.

In practice, some apps ignore or mishandle instantaneous cursor teleports, and
some macro authors prefer more "human-like" motion.

## MouseMove

`MouseMove` supports optional smoothing parameters:

- `duration_ms`: total duration for the movement.
- `smooth_steps`: number of intermediate segments.
- `easing`: `linear` (default) or `ease_in_out`.

Example:

```yaml
- type: MouseMove
  x: 1200
  y: 640
  duration_ms: 200
  smooth_steps: 10
  easing: ease_in_out
```

Notes:

- If you set `duration_ms` but omit `smooth_steps`, VHK picks a step count based
  on a ~60Hz cadence (`duration_ms / 16`).
- `smooth_steps` is capped to keep macros from accidentally generating thousands
  of pointer events.
- For absolute smoothing, VHK needs the **current cursor position**. On some
  Wayland desktops that is not available (by design). When VHK cannot read the
  cursor position, it falls back to a single direct move.

## MouseDrag

`MouseDrag` gained the same smoothing options:

```yaml
- type: MouseDrag
  x1: 400
  y1: 400
  x2: 1200
  y2: 400
  duration_ms: 250
  smooth_steps: 12
```

Behavior:

1. Move to `(x1,y1)`
2. Press the button down
3. Move through intermediate points toward `(x2,y2)`
4. Release the button

## Backend considerations

- X11 (`xdotool`) generally handles many intermediate moves well.
- Wayland uinput backends (`dotoolc`, `ydotool`) can also handle smooth paths,
  but it is **strongly** recommended to use `dotoolc` with the `dotoold` daemon
  if you do a lot of tiny segments (to avoid the per-invocation device setup
  overhead).
