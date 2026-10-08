# Rev 828 — command installer flattening

Rev0828 finishes the command-dispatcher extraction lane that started in rev0826. The goal was to remove the remaining nested command handlers from `install_default_commands` while preserving command names, docs, prompt metadata, and user-visible messages.

## Changed

Extracted from `src/micromax_editor/command_dispatcher.py`:

- `src/micromax_editor/help_commands.py` — `help`, docs navigation, help pickers, help link copying, and URL open/copy commands.
- `src/micromax_editor/binding_commands.py` — binding mutation commands: `bind`, `bindmode`, `binddoc`, `bindmodedoc`, `unbind`, `unbindmode`, and prefix-map binding helpers.
- `src/micromax_editor/keymode_commands.py` — `keymode`, keymode stack commands, `prefixmode`, and `rawkeys`.
- `src/micromax_editor/picker_commands.py` — prompt picker entry commands, `jumps`, `apropos`, and `sfmt`.
- `src/micromax_editor/option_commands.py` — `set`, `setlocal`, `show`, `toggle`, and `togglelocal`.
- `src/micromax_editor/session_commands.py` — `undo`, `redo`, `quit`, and `reload`.

`install_default_commands` is now registration-only: no nested `c_*` handlers and no local helper functions remain in the installer closure.

## Audit corrections

The extraction exposed a small argument-validation hole: `showkeymodes EXTRA` silently ignored the extra argument even though the command has no argument form. Rev0828 now returns `False` and reports:

```text
usage: showkeymodes
```

The duplicate `_no_such_binding` helper that existed in the show-command module is now centralized through `binding_commands.py`.

The command-dispatcher hygiene test now has a direct guard that `install_default_commands` remains registration-only.

## Size effect

```text
rev0827 command_dispatcher.py: ~1,139 lines
rev0828 command_dispatcher.py:   ~373 lines
```

New focused command modules:

```text
src/micromax_editor/help_commands.py       235 lines
src/micromax_editor/binding_commands.py    150 lines
src/micromax_editor/keymode_commands.py     88 lines
src/micromax_editor/picker_commands.py      93 lines
src/micromax_editor/option_commands.py      75 lines
src/micromax_editor/session_commands.py     68 lines
```

## Validation lanes

Focused lanes run during the revision:

```bash
python tools/mxlint.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -q tests/test_command_dispatcher_hygiene.py tests/test_editor_keymap_modes.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -q tests/test_editor_mx_commands_and_completion.py tests/test_editor_prompt_completion_hostcalls.py tests/test_editor_help_docs_navigation.py tests/test_editor_keybinding_authority.py tests/test_editor_rawkeys_command.py tests/test_command_cd.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -q tests/test_editor_option_authority.py tests/test_editor_option_words_set_toggle_show.py tests/test_editor_readonly_option.py tests/test_editor_helplinkcopy_and_openurl_confirm.py tests/test_editor_helplinkpick.py tests/test_editor_helplink_section_rows_heading_option.py tests/test_editor_helplink_section_rows_hostcall.py tests/test_editor_undo_authority.py tests/test_editor_with_undo_transaction.py tests/test_editor_command_authority.py tests/test_plugin_reload_recovery.py
```

A full aggregate suite manifest remains pending. An aggregate attempt collected 2,148 tests, but this cloudtainer delivered SIGTERM during the first chunk and left `.artifacts/mxtest-all-rev828.json` partial, so rev0828 claims focused coverage for the moved command families, not a full-suite pass.

## Next cut

With command registration flattened, the next high-value refactor is no longer the dispatcher closure itself. The safest remaining seams are:

- convert the default command registration block into a data table only if it materially helps tests or packaging;
- narrow `prompt_suggestions.py` from broad editor-object access to smaller providers;
- extract another `Editor` behavior cluster, likely help-history/navigation state or command-prompt model state, with focused tests first.
