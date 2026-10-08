# Rev349: plugin info should begin with the same state dialect as plugin list

Rev347 made plain `plugin list` legible, and rev348 made successful `plugin reload NAME`
report the resulting plugin state in that same compact dialect.

That still left one quiet mismatch in the ordinary plugin loop.

When a person wants more than inventory, they do not usually run `plugin list` again; they run
`plugin info NAME` (or select an unloaded plugin from `pluginpick`). Before this revision, that
detail path opened with a different, older header:

- `plugin a: loaded`
- `plugin b: not loaded`

That was not wrong, but it was lower-fidelity than the surrounding plugin surfaces. It also made
unknown plugin names awkward: a truly missing plugin could look too much like a real candidate
that simply was not loaded yet.

This revision keeps the implementation tiny and just aligns plugin detail with the surrounding
plugin inventory/reload language.

## What changed

`plugin info NAME` now starts with the same small inspectable entry shape used by `plugin list`
and `plugin reload`:

- `plugin info: a [loaded, v1.0.0]`
- `plugin info: fmt [loaded, v2.1.0, deps:core,theme]`
- `plugin info: b [error, deps:missingdep]`

The richer detail lines still follow after that summary when metadata exists:

- `version:`
- `entry:`
- `root:`
- `desc:`
- `requires:`
- `errors:`

Unknown names are now explicit instead of pretending to be a generic unloaded plugin:

- `plugin info: no such plugin: missing`

Picker-driven info inherits the same first-line summary automatically, because it already routes
through the same command path.

## Why this matters

This is a small trust/flow follow-up, not a new subsystem.

The repo has been tightening one simple rule across ordinary editor behavior:

- inventory should say what state exists
- recovery should say what state it returned to
- detail views should begin by stating the same truth the inventory sees

Plugin detail belongs in that same family. The first line of `plugin info NAME` should not force a
user or future LLM to translate from one state dialect into another before the rest of the detail
starts making sense.

That makes the tiny plugin loop more coherent:

1. inspect plugin health with `plugin list`
2. refresh with `plugin reload NAME`
3. inspect one plugin with `plugin info NAME`
4. get back the same state summary shape each time

## Files

- `src/micromax_editor/command_dispatcher.py`
- `tests/test_editor_pluginpick.py`
- `docs/50-editor-behaviors.md`
- `docs/95-plugin-json.md`
## Rev390 follow-up

When the plugin subsystem itself is absent, `plugin info NAME` now fails as `plugin info: no plugin manager` instead of a context-free `no plugin manager` line. That keeps the info surface self-identifying even in stripped-down harnesses.
