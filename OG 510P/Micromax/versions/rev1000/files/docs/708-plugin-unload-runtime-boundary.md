# Rev764 — plugin unload runtime boundary and dependency graph guard

## Why this was the next risky lane

Rev763 made plugin reload much safer by staging replacement runtime registrations before promotion. The neighboring `unload()` path was still less safe than reload: it ran `deinit` inside a `finally` cleanup, which meant a failing `deinit` removed the plugin anyway. That is exactly the sort of failure that costs humans trust. A plugin can remove or overwrite commands, keybindings, hooks, and timers during `deinit`, then fail; the old path could leave the plugin gone while the runtime evidence was half-mutated.

The second graph-level risk was dependency honesty. `load_tree()` recorded dependency cycles but still loaded the cyclic plugins in lexical order. That made the live graph claim dependencies had been satisfied when there was no valid order that could satisfy them.

## What changed

`src/micromax_editor/plugin_runtime.py` now owns the registration snapshot/restore and group cleanup/retag mechanics that had grown inside `PluginManager`:

- `snapshot_runtime_registrations(vm)`
- `restore_runtime_registrations(vm, snap)`
- `cleanup_runtime_group(vm, group)`
- `retag_runtime_group(vm, old, new)`
- `retag_hook_group(vm, old, new)`

`src/micromax_editor/plugins.py` now keeps small compatibility wrappers around those helpers while focusing on plugin lifecycle policy.

## Unload correction

`PluginManager.unload(NAME)` now treats a failing `deinit` as a failed transition, not as permission to erase the plugin. On failure it restores the pre-unload command/key/hook/timer snapshot, restores the previous module mapping, leaves the plugin in `plugins`, records the current error witness, and re-raises.

A new explicit escape hatch, `PluginManager.unload(NAME, force=True)`, skips lifecycle and performs grouped cleanup. This is intentionally blunt: it is for the operator case where the committed `deinit` itself is broken and the plugin must be scrubbed without running it again.

## Dependency correction

`PluginManager.loaded_dependents(NAME)` returns the loaded plugins that directly require a plugin. Ordinary `unload(NAME)` now refuses to unload a plugin while direct dependents are loaded; `force=True` can still override this for recovery or tests.

Dependency cycles discovered during `load_tree()` remain visible as candidates and load errors, but cyclic plugins are no longer activated. A cycle such as `a -> b -> a` now reports dependency-cycle errors for both candidates and leaves both unloaded until the metadata graph is repaired.

## Regression coverage

New/expanded tests cover:

- failed `deinit` during unload keeps the plugin loaded;
- failed `deinit` restores overwritten command/key registrations;
- failed `deinit` restores hook/timer registrations;
- failed `deinit` leaves module lookup and search order intact;
- `force=True` unload scrubs a plugin whose committed `deinit` is broken;
- unloading a plugin with loaded dependents is refused by default;
- dependency cycles are reported without activating cyclic plugins.

`tools/mxdoctor.py` now includes `tests/test_plugin_json_schema.py` in the bounded preflight so dependency graph regressions sit next to the reload/unload runtime regressions.

## Remaining risk

This is still a runtime-registration transaction, not a universal editor transaction. Lifecycle code can mutate buffers, files, message history, or other host state before failing. The next plugin-safety step should avoid pretending that arbitrary host side effects are rollback-safe. A better direction is a lifecycle contract or dry-run/introspection lane that validates metadata/source/dependency shape before side-effectful lifecycle words run.

The dependency guard is direct-dependency only. It prevents the most obvious broken unload, but a future graph pass could expose transitive dependents and a staged dependency-tree reload/unload plan.

## Validation notes

Focused validation in this cloudtainer:

- `python -m py_compile src/micromax_editor/plugin_runtime.py src/micromax_editor/plugins.py tools/mxdoctor.py tests/test_plugin_reload_recovery.py tests/test_plugin_json_schema.py` passed.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_plugin_reload_recovery.py tests/test_plugin_json_schema.py --durations=20` passed: 18 tests in 0.74 seconds.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_plugin_reload_recovery.py tests/test_plugin_json_schema.py tests/test_plugin_load_errors.py tests/test_plugin_hostcalls.py tests/test_editor_pluginpick.py tests/test_editor_registration_groups.py tests/test_editor_keymap_modes.py tests/test_hook_groups.py tests/test_editor_highlight_and_timers.py --durations=30` passed: 74 tests in 3.08 seconds.
- A combined plugin/context/doctor regression set passed: 87 tests in 5.15 seconds.
- `python tools/mxdoctor.py` passed: `mxlint` ok and 253 bounded preflight tests in 9.74 seconds.
- `bash scripts/lint.sh` passed.
- `python tools/mxcontext.py --check` passed.
- `python tools/mxtest.py --plan --chunks 8 --strategy segment --json /mnt/data/micromax_rev0764_mxtest_plan.json` collected 1597 tests into segment chunks of 200, 200, 200, 200, 200, 199, 199, and 199 tests.

This revision still does not claim a full-suite pass; full evidence remains the explicit chunked `mxtest` lane.

## Combined rev764 note

This plugin-lifecycle audit landed in the same packaged rev764 as the file-write audit in `docs/709-saveas-transactional-write-boundary.md`. The final combined validation counts for the packaged archive are recorded there; the focused plugin counts above remain the plugin-lifecycle evidence for this seam.
