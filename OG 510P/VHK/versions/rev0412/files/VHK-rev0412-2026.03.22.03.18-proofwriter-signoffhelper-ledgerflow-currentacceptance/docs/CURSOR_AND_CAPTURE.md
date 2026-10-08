# Cursor + capture reliability notes

This revision adds a small but practical X11-oriented reliability slice:

- `CursorHide()` / `CursorShow()` steps
- `ResetModifiers()` step
- project setting `settings.hide_cursor_during_run: true`
- screenshot backend ladder now includes `scrot` and `xwd`+ImageMagick fallback

## Why this matters

Vision automation fails for surprisingly mundane reasons:
- the mouse pointer sits on top of the thing you want to match
- a hotkey-launched macro inherits stuck Ctrl/Alt/Shift state
- one machine has `maim`, another only has `scrot`, and a third only has `xwd` + ImageMagick

This slice does not solve the whole studio UX, but it makes the headless runner noticeably more robust and more diagnosable.

## Current behavior

### Cursor helpers

- VHK currently prefers `unclutter` / `unclutter-xfixes` for explicit hide/show lifecycle control.
- If only `xbanish` is available, VHK can still treat it as a session helper, but it is less precise for explicit “hide now / show now” semantics.
- Cursor management is currently best-effort and X11-only.

### Screenshot helpers

Backend preference is now:
1. Wayland: `grim`
2. X11: `maim`
3. X11 fallback: `scrot`
4. X11 fallback: ImageMagick `import`
5. X11 last resort: `xwd` piped into ImageMagick (`magick` or `convert`)

For PNG outputs on ImageMagick-backed paths, VHK writes to `PNG32:<path>` so alpha is preserved and transparent regions do not silently turn black.

## Doctor output

`vhk doctor` now reports:
- cursor helper availability (`unclutter`, `xbanish`)
- deeper screenshot fallback helpers (`scrot`, `xwd`, `magick`, `convert`)
- the selected screenshot module and cursor module

## Near-term follow-ups

Good next increments from here:
- `CaptureScreenshot(include_cursor=true|false)`
- move-cursor-to-safe-corner before vision steps
- cursor/evidence annotations in the event log
- explicit “touchscreen mode” / `hide-on-touch` doctor guidance
