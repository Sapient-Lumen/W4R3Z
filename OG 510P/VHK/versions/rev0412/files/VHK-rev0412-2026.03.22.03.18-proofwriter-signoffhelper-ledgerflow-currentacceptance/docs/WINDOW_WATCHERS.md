# Window watchers

Window watchers are VHK’s analogue to the “run a script when focus changes”
workflows people build with i3 IPC subscriptions or Hyprland socket2 listeners.

The goal is intentionally modest:
- keep **trigger policy** in `project.yaml`
- reuse the normal **Runner** for the macro’s actual work
- log “why did this fire?” decisions to JSONL for debugging

## Example

```yaml
window_watchers:
  - name: focus_firefox
    event: focus
    when:
      class: Firefox
    macro: on_focus
    debounce_ms: 50
    # Optional: prevent event loops (milliseconds)
    cooldown_ms: 0
    # Optional: skip repeated signatures in the last N ms
    dedupe_window_ms: 0

  - name: workspace_any
    event: workspace
    macro: on_workspace

  - name: title_changes
    event: title
    when:
      class: Firefox
    macro: on_title

  - name: urgent_any
    event: urgent
    macro: on_urgent
```

Run:

```bash
vhk watch-window /path/to/project focus_firefox
```

## Events

- `focus`: active window changed
- `workspace`: focused workspace changed
- `title`: a window title changed
- `urgent`: a window became urgent or lost urgency
- `new`: a window was created/mapped (i3/sway `window::new`, Hyprland `openwindow`)
- `close`: a window was closed/unmapped (i3/sway `window::close`, Hyprland `closewindow`/`kill`)
- `custom`: compositor custom event (currently Hyprland socket2 `custom>>...`)

### “Which window is this about?”

- For `focus` / `workspace`, VHK typically queries the active window (same
  behavior as `vhk window-spy`).
- For `title` / `urgent` / `new` / `close`, VHK prefers the window identified by the underlying
  event payload:
  - i3/sway: the IPC `window` event includes a `container` object
  - Hyprland: socket2 events include a window address for most window-related
    events. `closewindow` / `kill` only provide the address, so VHK keeps a
    small best-effort address→metadata cache from earlier events (open/title/move/focus)
    and falls back to it when `hyprctl -j clients` no longer lists the window.

## Variables passed into watcher macros

Watcher-triggered macros receive these initial vars:

- `wm`: compositor identifier (`i3`, `sway`, `hyprland`, or `unknown`)
- `wm_event`: one of `focus`, `workspace`, `title`, `urgent`, `new`, `close`, `custom`
- `wm_event_name`: raw WM event name (`window`, `workspace`, `activewindow`, ...)
- `wm_event_data`: raw event payload (dict for i3/sway, string for Hyprland socket2)
- `window`: best-effort window info dict
- Convenience fields:
  - `window_title`
  - `window_class`
  - `workspace`
  - `urgent`
- `prev_window`: previous active window info dict, when `include_prev: true`

## Platform notes

### i3 / sway

VHK uses an IPC **subscribe** connection to receive events, and it follows the
best practice of using a dedicated connection for event delivery.

If the compositor restarts (or IPC socket resets), VHK reconnects with a small
exponential backoff.

### Hyprland

VHK uses Hyprland’s **socket2** event stream (`.socket2.sock`) when available.
If the socket disconnects (for example on config reload), VHK reconnects.

### Unknown / fallback

If the compositor is not recognized, VHK falls back to **polling** the active
window at `--poll-ms` intervals (focus only).

## Logs

Each watcher writes a JSONL log under:

- `logs/window_watcher_<name>.jsonl`

This log intentionally stores metadata (event type, window signature, preview)
and a reference to the macro’s run/event log, rather than full window dumps.

## Avoiding loops

Window-triggered automation can accidentally create loops (e.g. a focus watcher
that refocuses another window).

- `debounce_ms` sleeps briefly after handling an event.
- `cooldown_ms` throttles macro runs; events are still observed and logged.
- `dedupe_window_ms` skips repeated window signatures seen recently.
