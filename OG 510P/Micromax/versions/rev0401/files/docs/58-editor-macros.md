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

Hostcalls (portable surface; lists/ints/strings only):

- `ed.macro-names` ( -- names )
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
- Inventory should be explicit too: `macro list` now stays count-aware as `macros: N macro(s), ...`, says `macros: 0 macro(s)` before anything real is saved, and later shows `name (N step[s])` entries instead of raw names.
- Command typos should be explicit too: unknown `macro` subcommands now fail as `macro: no such subcommand: NAME` instead of a context-free parser message.
- Each action step stores a shallow snapshot of `editor.input` so insertion and
  other parameterized actions replay correctly.
- Recording is disabled while playing back to avoid runaway recursion.
- "last macro" semantics match micro, but named macros make it easy to keep a
  small library of tiny automations (similar spirit to Vim/Emacs macro naming).
