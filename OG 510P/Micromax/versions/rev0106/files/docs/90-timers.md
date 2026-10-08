# Timers / `after` (rev66)

Micromax-editor uses a **host-driven** timer queue: no threads and deterministic
tests.

## Hostcalls

### `ed.after`

Schedule a quotation to run after N milliseconds.

Stack effect:

```
( ms q -- id )
```

- `ms` is clamped to `>= 0`
- `id` is a monotonically increasing integer timer id

Example:

```
: autosave ( -- ) "autosaving" "ed.msg" hostcall ;
5000 [ autosave ] "ed.after" hostcall drop
```

### `ed.cancel-timer`

Cancel a previously scheduled timer.

Stack effect:

```
( id -- ok )
```

Returns 1 if a timer with that id existed (even if it was already due), else 0.

### `ed.pump-timers`

Run all timers that are due *right now*.

Stack effect:

```
( -- ran )
```

Returns how many timers executed.

## Execution semantics

- Timer callbacks run like editor hooks: **stack-isolated** and best-effort.
  Exceptions become editor messages.
- Nothing happens unless the host calls `ed.pump_timers()` (the curses TUI does
  this every tick).

## Plugin unload cleanup

Plugin loaders set `vm.current_editor_group = "plugin:NAME"` during load.
Timers scheduled while that group is active inherit the group tag and are
canceled on plugin unload/reload.

## Implementation

- Queue: `src/micromax_editor/timers.py`
- Execution: `Editor.pump_timers()`
- Hostcalls: `src/micromax_editor/micromax_bridge.py`
