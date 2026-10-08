# Rev 827 — command family extraction

Rev0827 continues the command-dispatcher reduction started in rev0826. The goal was to move behavior families with strong existing tests out of `install_default_commands` without changing command names, docs, prompt metadata, or user-visible messages.

## Changed

Extracted from `src/micromax_editor/command_dispatcher.py`:

- `src/micromax_editor/show_commands.py` — exact `show*`/inspection commands for commands, actions, VM words, docs, topics, options, key bindings/modes, hooks, plugins, macros, status, and current help headings/links/navigation.
- `src/micromax_editor/plugin_commands.py` — `plugin list|reload|info|errors`.
- `src/micromax_editor/macro_commands.py` — `macro record|stop|cancel|play|list|status`.
- `src/micromax_editor/replace_commands.py` — `replace`, `replaceall`, `replacepreview`, `qreplace` and their local planning/preview helpers.
- `src/micromax_editor/command_authority.py` — shared script-origin guard for code-loading commands, reused by `reload` and `plugin reload`.

The dispatcher now keeps the registration table and the still-inline command families: help/navigation, URL open/copy, binding mutation, rawkeys/keymode mutation, prompt pickers, jump/apropos summaries, undo/redo, quit, options, and reload.

## Audit corrections

The extraction exposed two dead dispatcher-local replacement helpers:

- `_convert_template`
- `_validate_replacement_template`

They were no longer called by the command handlers; current replacement validation is centralized through `replace_plan.py` and query-replace handling in `editor.py`. Rev0827 removes those dead helpers from the dispatcher path rather than moving them forward as false surface area.

The command-dispatcher hygiene test now also guards against the extracted `show`, `plugin`, `macro`, and `replace` families sliding back into `install_default_commands`.

## Size effect

After the rev0826 split, `command_dispatcher.py` was about 1,956 lines. Rev0827 reduces it to about 1,139 lines and moves the extracted behavior into focused modules:

```text
src/micromax_editor/show_commands.py       434 lines
src/micromax_editor/plugin_commands.py     232 lines
src/micromax_editor/replace_commands.py    157 lines
src/micromax_editor/macro_commands.py      100 lines
src/micromax_editor/command_authority.py    14 lines
```

## Validation lanes

Focused lanes run during the revision:

```bash
python tools/mxlint.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python -m pytest -q tests/test_command_dispatcher_hygiene.py tests/test_editor_mx_commands_and_completion.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python -m pytest -q tests/test_editor_core.py tests/test_editor_macro_authority.py tests/test_editor_deferred_authority.py tests/test_editor_mx_commands_and_completion.py tests/test_command_dispatcher_hygiene.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python -m pytest -q tests/test_editor_pluginpick.py tests/test_editor_plugin_authority.py tests/test_editor_hostcall_boundary.py tests/test_editor_prompt_completion_hostcalls.py tests/test_command_dispatcher_hygiene.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python -m pytest -q tests/test_editor_help_docs_buffers.py tests/test_editor_interaction_authority.py
```

A full aggregate suite manifest remains pending; rev0827 claims focused coverage for the moved command families, not a full-suite pass.

## Next cut

The next safest dispatcher extraction is the remaining keybinding/help/options family split:

- binding mutation commands: `bind`, `bindmode`, `binddoc`, `unbind`, prefixes;
- help/navigation commands: `help`, `helppick`, `helpjump`, `helpback`, `helpforward`, link/outline/nav pickers;
- option mutation commands: `set`, `setlocal`, `show`, `toggle`, `togglelocal`.
