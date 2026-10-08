# Rev348: plugin reload should confirm resulting state

Rev347 made plain `plugin list` legible: one concise line, one inspectable entry per
plugin, with visible `loaded` / `available` / `error` state plus version/dependency
hints.

That still left one quiet mismatch in the ordinary plugin loop.

The command a person naturally uses after editing a plugin is not `plugin list`; it is
`plugin reload NAME` (or a reload chosen from `pluginpick`). Before this revision,
successful reload only said:

- `reloaded NAME`

That confirmed the action ran, but it did **not** confirm the resulting state. If you
wanted to know whether you had reloaded the right plugin, which version/dependencies
were now in play, or whether the resulting loaded state still matched what the editor
thought it had, you had to run a second command.

This revision keeps the implementation tiny and simply aligns the success feedback with
rev347's inventory dialect.

## What changed

Successful reload now reports the same small inspectable entry shape used by
`plugin list`:

- `plugin reload: core [loaded]`
- `plugin reload: a [loaded, v1.0.0]`
- `plugin reload: fmt [loaded, v2.1.0, deps:core,theme]`

The same message shape now appears whether reload came from:

- explicit command-bar use: `plugin reload NAME`
- picker-driven reload from `pluginpick`

Reload failures remain explicit and unchanged:

- `plugin reload error: NAME: ...`

## Why this matters

This is a small trust/flow follow-up, not a new subsystem.

The repo has been tightening a consistent rule across ordinary editor behavior:

- movement should say where it landed
- inventory should say what state exists
- text-changing commands should say what they changed

Plugin refresh belongs in that same family. A successful reload is not just an event;
it is a state transition. The editor should confirm the resulting state directly.

That makes the tiny plugin loop more coherent:

1. inspect plugin health with `plugin list`
2. reload a plugin with `plugin reload NAME`
3. get back feedback in the **same dialect**

## Files

- `src/micromax_editor/command_dispatcher.py`
- `tests/test_editor_pluginpick.py`
- `docs/50-editor-behaviors.md`
- `docs/95-plugin-json.md`
