# Window event waits

`WaitForWindowEvent` gives VHK a one-shot, event-driven synchronization
primitive for WM/compositor transitions.

It is the runtime analogue of:
- `xdotool behave` on X11-style workflows
- `i3-msg -t subscribe` / `swaymsg -t subscribe`
- Hyprland `socket2`

## Why this exists

Linux automation often becomes much more reliable when a macro waits for a
**focus/title/new/close/urgent/workspace** transition instead of guessing with a
fixed sleep.

Examples:
- wait for a browser window to be created after launching a URL
- wait for a dialog title change before typing into it
- wait for an urgent event before surfacing a notification or mode switch
- wait for a workspace transition emitted by the compositor itself

## Step shape

```yaml
- type: WaitForWindowEvent
  event: new          # focus | workspace | title | urgent | new | close | custom
  selector:
    class: Firefox
  raw_name: window    # optional raw backend event name filter
  condition: 'wm_event["workspace"] == "2"'   # optional expression filter
  timeout_ms: 5000
  out_event: wm_event_payload
  out_window: wm_window
  out_workspace: wm_workspace
  out_wm: wm_name
```

## Output shape

`out_event` receives a payload like:

```yaml
wm: sway
kind: new
name: window
data: ...raw backend payload...
window: ...best-effort window snapshot or null...
workspace: "2"
```

`out_window` gets the best-effort window snapshot, and `out_workspace` /
`out_wm` expose the common convenience fields directly.

## Honest backend expectations

`WaitForWindowEvent` intentionally follows the same honesty rule as the rest of
VHK’s window lane:
- i3/sway: first-class focus/workspace/title/urgent/new/close via IPC
- Hyprland: first-class focus/workspace/title/urgent/new/close/custom via
  socket2
- generic X11 / other desktops: do **not** claim a universal rich event stream;
  VHK currently only treats focus-style waits as generally safe there unless a
  compositor-specific bridge is involved

That is why planner/validator/doctor now include WM **event-kind** support in
addition to selector/state/geometry/pointer-window contracts.

## When to use this vs `WaitForWindow`

Use `WaitForWindow` when you want to prove **current state** and succeed
immediately if the matching window already exists.

Use `WaitForWindowEvent` when you want to synchronize against a **future WM
transition**.
