# Rev762 — action seams, plugin reload recovery, and macro input isolation

Rev762 is a code-first cut aimed at the pieces most likely to stay risky if the session drifted back into registry maintenance: the giant editor default-installation block, the hot command-completion application path, plugin reload recovery, and macro replay state isolation.

## What changed

- `src/micromax_editor/actions_default.py` now owns default action installation. `Editor._install_default_actions()` is a compatibility delegate.
- `src/micromax_editor/options_default.py` now owns default option installation. `Editor._install_default_options()` is a compatibility delegate.
- `src/micromax_editor/prompt_completion.py` now owns `PromptCompletionPlan`, `plan_prompt_completion_application(...)`, `MergedCompletionCandidates`, and `merge_completion_candidates(...)`.
- `Editor.prompt_complete(...)` still gathers live editor facts, but it delegates final completion edit/session policy and builtin/path/plugin merge policy to pure helpers.
- `src/micromax_editor/plugins.py` now treats load errors as current-state evidence rather than an append-only scar. Successful reload/load clears stale per-plugin errors.
- `PluginManager.reload(...)` rereads `plugin.json` and entry paths before unloading a currently loaded plugin, and a not-loaded but known candidate can be reloaded after the user fixes its source or metadata.
- `Editor.play_macro(...)` restores the caller's live `editor.input` snapshot after successful replay, so recorded action payloads do not leak into the next live action.
- `tools/mxdoctor.py` now includes macro, plugin reload, and command/completion integration regressions in the bounded default preflight.

## Correctness fixed

### Prompt completion escaped-prefix continuation

Rev761 made generated path completions parser-safe for names containing single quotes and backslashes. Rev762 fixes the next edge: after the first Tab inserts an escaped, double-quoted directory prefix, the second Tab must complete against the real filesystem name, not the escaped command spelling. `prompt_token_context(...)` now exposes the unescaped token body for completion lookup while preserving the command-bar spelling for parser-safe display.

Covered examples include directories named `alpha\dir` and `alpha"dir`: the command bar keeps escaped double-quoted text, but the next completion lookup sees the actual path component and can complete the child file.

### Plugin-added completion rows no longer inherit false path metadata

Command completion can combine builtin path candidates with Micromax plugin completion hooks. Before this cut, additive plugin candidates during a path-completion pass could be treated as path rows simply because `path_mode=True` was global. `merge_completion_candidates(...)` now returns a path-provenance set: builtin path candidates keep filesystem rows; plugin-added candidates remain generic unless the plugin supplied aligned metadata; replace mode clears builtin path provenance entirely.

### Plugin reload can recover repaired candidates

A failed plugin reload used to leave a repaired plugin awkward to recover without a broader rescan/restart. The manager now keeps known candidates, rereads metadata on reload, can load a not-loaded known candidate, clears stale errors after a successful repair, and refuses to drop a currently working plugin when the new `plugin.json` is invalid before unload.

One risk remains explicit: if source loading fails after a currently loaded plugin is unloaded, the old plugin is still gone. Fully atomic source reload would require staging VM words, hooks, commands, and lifecycle side effects behind a transaction-like boundary.

### Macro replay restores live input

Action macros replay recorded `editor.input` payloads so actions such as `InsertText` can reproduce their original arguments. Before this cut, a successful macro replay could leave the last recorded payload in `editor.input`, causing a later live action to reuse stale macro data. `play_macro(...)` now restores the pre-replay input snapshot in the normal cleanup path.

## Refactor/audit note

This revision moves 1,735 lines of default installer code out of `editor.py` (`editor.py` dropped from 25,994 to 24,259 lines in this cloudtainer). That is meaningful because the editor class was carrying unrelated action/option registration closures at the same level as runtime editing, prompt completion, plugins, macros, display, and command execution. The extraction is not yet beautiful: `actions_default.py` is still a large installer module with many closures. It is, however, a real seam. Future work can split action families into editing, movement, selection, prompt, macro, multicursor, and clipboard installers without rewriting the whole editor class in one jump.

The prompt-completion work follows the same rule: do not build a new registry until the risky policy has a pure function and tests. Candidate discovery still belongs to the editor for now because it needs live commands, options, buffers, plugins, docs, and filesystem state. Application/merge policy no longer needs the whole editor object.

## Remaining risk

- `actions_default.py` should be split again by action family; otherwise it becomes a second monolith.
- Command-specific prompt row decoration still lives in a long `editor.py` cascade and should be the next prompt seam.
- Plugin source reload is safer around metadata, but not fully atomic around VM/plugin side effects.
- `editor.py` remains much too large even after the installer extraction.
- Full-suite validation is still the explicit chunked `mxtest` lane, not a claim made by default doctor.

## Validation notes

Focused validation in this cloudtainer:

- `python -m py_compile src/micromax_editor/editor.py src/micromax_editor/actions_default.py src/micromax_editor/options_default.py src/micromax_editor/prompt_completion.py src/micromax_editor/plugins.py tools/mxdoctor.py tests/test_prompt_completion.py tests/test_editor_prompt_path_completion.py tests/test_editor_mx_commands_and_completion.py tests/test_editor_macros_named.py tests/test_plugin_reload_recovery.py tests/test_editor_pluginpick.py tests/test_mxdoctor.py` passed.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_editor_core.py tests/test_editor_default_keybindings_core.py tests/test_editor_prompt_picker_navigation.py tests/test_editor_macros_named.py tests/test_editor_registration_groups.py tests/test_prompt_completion.py tests/test_editor_prompt_path_completion.py --durations=20` passed: 153 tests in 2.98 seconds.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_editor_prompt_completion_hostcalls.py tests/test_editor_mx_commands_and_completion.py tests/test_command_palette_path_completion.py tests/test_prompt_grouping_sections.py --durations=20` passed: 351 tests in 13.18 seconds.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_plugin_reload_recovery.py tests/test_plugin_load_errors.py tests/test_plugin_hostcalls.py tests/test_plugin_json_schema.py tests/test_editor_pluginpick.py tests/test_editor_registration_groups.py --durations=20` passed: 55 tests in 0.83 seconds.
- `python tools/mxdoctor.py` passed: `mxlint` ok and 211 bounded preflight tests in 8.61 seconds.
- `bash scripts/lint.sh` passed: `mxlint: ok`.
- `python tools/mxcontext.py --check` passed.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_revision_index.py tests/test_mxcontext.py tests/test_mkrevzip.py tests/test_packaging_stdlib.py --durations=10` passed: 9 tests in 21.77 seconds.
- `python tools/mxtest.py --plan --chunks 8 --strategy segment --json /mnt/data/micromax_rev0762_mxtest_plan.json` collected 1,582 tests into eight segment chunks (198, 198, 198, 198, 198, 198, 197, 197) with source digest `803fc2435b3f`.

Full-suite validation is not claimed here; use the chunked `mxtest` manifest path for aggregate evidence.
