# Macros (micro-inspired)

Macros are a deceptively powerful "low-hanging" editor feature because they unlock
automation before you have a full plugin ecosystem.

Micro binds (default keys):

- `Ctrl-u` — toggle macro recording
- `Ctrl-j` — play the latest recorded macro

Reference: micro runtime help/defaultkeys.md.

## What micromax-editor implements (v23)

Actions:

- `ToggleMacro` — start/stop recording the **last** macro (micro-style)
- `PlayMacro` — play the **last** macro
- `CancelMacro` — cancel recording without saving

Command bar:

- `macro record [name]` — start recording into a named slot (default: `last`)
- `macro stop` — stop and save
- `macro cancel` — stop and discard
- `macro play [name] [count]` — play named macro (default: `last`, count default: `1`) and report exactly what ran (`macro: played NAME xN (K step[s])`)
- `macro list` — list saved macros with recorded step counts; stays count-aware as `macros: N macro(s), ...` and reports `macros: 0 macro(s)` until something real is saved
- `macro status` — show the combined live macro runtime state plus the same saved-macro inventory as `macro status: STATE [NAME (N step[s])], M macro(s), ...`

Hostcalls (portable surface; lists/ints/strings only):

- `ed.macro-names` ( -- names )
- `ed.macro-inventory-rows` ( -- rows )
- `ed.macro-status-rows` ( -- rows )
- `ed.macro-get` ( name -- steps )
- `ed.macro-set` ( steps name -- )
- `ed.macro-record` ( name -- ok )
- `ed.macro-stop` ( -- ok )
- `ed.macro-cancel` ( -- ok )
- `ed.macro-play` ( name n -- ok )
- `ed.macro-recording?` ( -- flag )
- `ed.macro-playing?` ( -- flag )

## Macro representation (portable)

A macro is a list of **steps** encoded with simple tags:

- `["a", ACTION, [[key val] ...]]` — run an action with an `editor.input` snapshot
- `["c", CMDLINE]` — run a command-bar line

This is intentionally simple so macros can be inspected, persisted, and replayed
from micromax without needing a map/dict type.

## Design notes

- Recording happens at the **action/command** level (not raw keypresses).
- Playback should be explicit too: successful `macro play` now reports the macro name, repeat count, and recorded step count, while missing named macros fail as `macro play: no such macro: NAME` instead of drifting into an older shorthand.
- Inventory should be explicit too: `macro list` now stays count-aware as `macros: N macro(s), ...`, says `macros: 0 macro(s)` before anything real is saved, later shows `name (N step[s])` entries instead of raw names, and rev420 exposes that same filtered `name/steps` register directly through `macro_inventory_rows()` / `ed.macro-inventory-rows` so scripts and future UIs inherit the same empty-`last` honesty policy instead of rediscovering it.
- Runtime state should be explicit too: rev436 adds `macro status` plus `macro_status_rows()` / `ed.macro-status-rows`, so scripts and future UIs can inspect one tiny combined `idle` / `recording` / `playing` snapshot together with the saved-macro inventory instead of stitching together boolean flags and a separate list walk.
- Command discovery should be explicit too: plain `macro play` / `macro record` / `macro rec` / `macro start` / `macro stop` / `macro cancel` now preview saved inventory, default-slot intent, or active recording guards before Enter, and `macro` completion now offers the real `rec` / `start` aliases instead of hiding them.
- Command typos should be explicit too: unknown `macro` subcommands now fail as `macro: no such subcommand: NAME` instead of a context-free parser message.
- Each action step stores a shallow snapshot of `editor.input` so insertion and
  other parameterized actions replay correctly.
- Recording is disabled while playing back to avoid runaway recursion.
- "last macro" semantics match micro, but named macros make it easy to keep a
  small library of tiny automations (similar spirit to Vim/Emacs macro naming).
