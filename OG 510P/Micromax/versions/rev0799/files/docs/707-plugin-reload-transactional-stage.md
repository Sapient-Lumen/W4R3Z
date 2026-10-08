# Rev763 — transactional plugin reload staging

## Why this was the risky lane

Rev762 fixed the obvious recovery case: a plugin that failed to reload could be repaired and loaded again without restarting the editor. The remaining failure mode was worse. A currently working plugin could still be disturbed by a bad replacement because source evaluation, startup lifecycle words, grouped command registration, grouped keybindings, hook handlers, timers, module lookup, search order, and old-plugin `deinit` all live on the same reload path.

The waste was not CPU waste this time. It was trust waste: a failed reload could force a human or script to rebuild runtime state that should never have been dropped.

## What changed

`src/micromax_editor/plugins.py` now stages replacement plugins under a temporary reload group instead of unloading the old plugin first. A reload now follows this shape:

1. read fresh metadata and dependency state from disk;
2. build the replacement wordlist under a staged group such as `plugin:alpha#reload1`;
3. run replacement `preinit`/`init`/`postinit` while the old plugin is still committed;
4. run old `deinit` with `use alpha` still resolving to the old wordlist;
5. clean the old stable group;
6. retag staged hooks, commands, keybindings, and timers to the stable `plugin:alpha` group;
7. promote the staged plugin, module mapping, and search-order entry.

If metadata reread, source evaluation, or staged startup lifecycle fails, the old plugin remains loaded. If the replacement overwrote an existing command or keybinding before failing, the pre-reload registration snapshot is restored. If old `deinit` fails after a replacement has staged successfully, the staged runtime is removed, editor registrations are restored, and the old plugin remains the committed plugin.

Initial plugin load now uses the same build path: if a startup lifecycle word registers commands, keybindings, hooks, or timers and then fails, those side effects are removed before the plugin can appear loaded.

## Supporting seams

Three small runtime registries now support group retagging:

- `CommandDispatcher.retag_group(old, new)` updates command provenance without rebuilding command functions.
- `Keymap.retag_group(old, new)` updates keybinding provenance across modes.
- `TimerQueue.retag_group(old, new)` updates pending timer ownership.

The hook path retags `HookHandler.group` directly across loaded hook words. Reload failure paths snapshot and restore command, keymap, hook, and timer stores because a staged plugin can overwrite stable command/key names before later failing.

## User-visible correction

`plugin reload NAME` now distinguishes a failed reload that kept the previous version alive from a failed reload of an unloaded candidate. The loaded failure path reports `previous version still loaded` in the second detail line instead of implying the plugin is simply not loaded.

## Archive hygiene correction

The rev762 archive contained a stray compiled bytecode artifact under `__pycache__`. `tools/mkrevzip.py` already skipped cache directories, but the safer rule is explicit: skip `.pyc` and `.pyo` files anywhere in the tree. The archive should represent source, tests, docs, and revision evidence, not whichever validation artifacts happened to exist in the cloudtainer.

## Regression coverage

New and expanded tests in `tests/test_plugin_reload_recovery.py` cover:

- failed source reload keeps the old plugin wordlist and old `use alpha aword` result;
- invalid replacement metadata keeps the previous plugin live and reports that the previous version is still loaded;
- staged init failure cleans staged command/key/hook/timer side effects;
- staged command/key overwrites are rolled back after failure;
- successful staging retags command/key/hook/timer ownership back to `plugin:NAME`;
- old `deinit` sees the old module mapping until promotion;
- old `deinit` failure restores overwritten registrations and keeps the old plugin active;
- failed old `deinit` drops the uncommitted staged wordlist;
- lifecycle failure during initial plugin load does not leave leaked command/key/hook/timer runtime.

`tests/test_mkrevzip.py` now checks that both plain `.pyc` files and nested `__pycache__` bytecode files are skipped.

## Remaining risk

This is a transactional reload for plugin runtime registration surfaces, not for arbitrary editor side effects. A plugin lifecycle word can still intentionally mutate buffers, messages, files, or other host state before raising. Rolling back arbitrary host effects would need a narrower lifecycle contract or a broader editor transaction model, likely reusing and generalizing the macro replay snapshot machinery.

Committed historical plugin wordlists are also still retained by design. Live module/search surfaces are cleaned or replaced, but retained wordlists remain available for provenance and avoid surprising references.

The next high-value plugin hardening pass is therefore either a lifecycle host-effect boundary for `init`/`deinit`, a plugin reload dry-run/introspection lane that validates metadata and parses source without running lifecycle side effects, or a graph-level staged reload for dependency trees after single-plugin staging remains stable.

## Validation notes

Focused validation in this cloudtainer:

- `python -m py_compile src/micromax_editor/plugins.py src/micromax_editor/command_dispatcher.py src/micromax_editor/keymap.py src/micromax_editor/timers.py src/micromax_editor/editor.py tools/mkrevzip.py tests/test_plugin_reload_recovery.py tests/test_mkrevzip.py` passed.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_plugin_reload_recovery.py tests/test_plugin_load_errors.py tests/test_plugin_hostcalls.py tests/test_editor_pluginpick.py tests/test_editor_registration_groups.py tests/test_editor_keymap_modes.py tests/test_hook_groups.py tests/test_editor_highlight_and_timers.py tests/test_mkrevzip.py --durations=30` passed: 70 tests in 9.88 seconds.
- `python tools/mxdoctor.py` passed: `mxlint` ok and 218 bounded preflight tests in 6.90 seconds.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_revision_index.py tests/test_mxcontext.py tests/test_mkrevzip.py --durations=15` passed: 8 tests in 8.28 seconds.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_packaging_stdlib.py --durations=10` passed: 1 test in 17.53 seconds.
- `python tools/mxtest.py --plan --chunks 8 --strategy segment --json /mnt/data/micromax_rev0763_mxtest_plan.json` collected 1589 tests into segment chunks of 199, 199, 199, 199, 199, 198, 198, and 198 tests.

This revision still does not claim a full-suite pass; full evidence remains the explicit chunked `mxtest` lane.
