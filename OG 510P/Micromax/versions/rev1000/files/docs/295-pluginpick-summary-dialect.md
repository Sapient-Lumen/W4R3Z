# Plugin picker summary dialect (rev353)

Micromax-editor's plugin loop had become honest in most places:

- `plugin list` showed compact per-plugin state
- `plugin reload NAME` confirmed the resulting state
- `plugin info NAME` and `plugin errors [NAME]` started with that same summary dialect
- `pluginpick` already routed broken rows to the right detail path

The quiet remaining mismatch was the picker surface itself.

Before this revision, `pluginpick` still rendered row metadata in an older free-form style like:

- `loaded`
- `not loaded deps:missingdep ERROR`

That was enough for rough grouping, but it was not the same dialect the rest of the plugin loop had already settled on. Users and future LLMs could inspect plugin health honestly in `plugin list`, then open `pluginpick` and immediately fall back to a lower-fidelity representation.

## What changed

`pluginpick` row metadata and preview labels now reuse the same compact plugin-state summary vocabulary as the rest of the plugin loop.

Examples:

- picker row: `a [loaded, v1.0.0]`
- picker row: `b [error, deps:missingdep]`
- preview: `Errors: b [error, deps:missingdep] — missing dependency: missingdep`
- preview: `Loaded: a [loaded, v1.0.0] — demo plugin`

This is intentionally small:

- the picker still groups rows into `Errors` / `Loaded` / `Available`
- row shape stays `[insert kind menu info]`
- the change is just that `menu` now carries the same bracketed summary dialect used elsewhere
- plugin previews now compose that summary directly instead of splitting the plugin name and state into two different voices

## Why this matters

This is another trust/flow cleanup, not a new subsystem.

The goal is simple: **searchable plugin inspection should not speak a lower-fidelity dialect than plain plugin inspection.** When someone moves between `plugin list`, `pluginpick`, `plugin reload`, `plugin info`, and `plugin errors`, the editor should make plugin state feel stable and legible rather than slightly different on every surface.

## Files touched

- `src/micromax_editor/editor.py`
- `src/micromax_editor/command_dispatcher.py`
- `tests/test_editor_pluginpick.py`
- `README.md`
- `TODO.md`
- `docs/00-vision.md`
- `docs/01-llm-start-here.md`
- `docs/02-repo-map.md`
- `docs/43-worklist.md`
- `docs/50-editor-behaviors.md`
- `docs/64-editor-prompt-completion.md`
- `docs/95-plugin-json.md`
- `docs/269-editor-goals-taste-trust-flow.md`

## Verification

Focused coverage lives in:

- `tests/test_editor_pluginpick.py`
- `tests/test_editor_main_cli.py`
- `tests/test_editor_mx_commands_and_completion.py`

Manual check:

- `pluginpick` preview now reads `Errors: b [error, deps:missingdep] — missing dependency: missingdep`
