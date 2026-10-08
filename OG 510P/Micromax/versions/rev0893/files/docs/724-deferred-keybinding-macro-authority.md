# Rev0774 — Deferred callback authority and plugin-local roots

## Problem

Rev0772 and rev0773 closed the obvious script-context self-escalation paths: direct capability mutation, nested code loading, `ed.run`, plugin reload, timers, and hooks were no longer supposed to run with more authority than the script that initiated them. The deeper risk was deferred editor automation.

A restricted script or plugin could register a keybinding, save a macro step, schedule a timer, or attach a hook while `Editor.script_context()` was active, then return. Later, an ordinary keypress, timer pump, hook notification, or interactive macro replay could run the stored action as ambient editor/user authority. For keybindings, a payload such as `command:set cap.fs-save true` could therefore be delayed until after the script exited. For plugin callbacks, package-local source loading had a second failure mode: callbacks that later ran `"helper.mx" include` needed the plugin package root that existed at registration time, without granting global `cap.fs-require`.

The first concrete bug found in this turn was half-landed provenance: `ed.bind` passed `plugin_load_root` into `Keymap.bind(...)`, but `Keymap.bind(...)` did not accept or store it. That made the keybinding origin path fail before the deeper authority problem could even be tested.

## Changes

`src/micromax_editor/keymap.py` now records both pieces of delayed-callback provenance on `Binding`:

- `script_context`
- `plugin_load_root`

`Editor.script_callback_origin_kwargs()` is the shared origin seam for delayed callbacks. It captures whether the registration is happening inside script context, and it captures the current plugin load root only for script/plugin-originated callbacks.

The following registration paths now stamp delayed callbacks with that origin:

- command-bar `bind`, `bindmode`, `bindprefix`, and `bindmodeprefix`;
- hostcalls `ed.bind`, `ed.bind-mode`, `ed.bind-prefix`, and `ed.bind-mode-prefix`;
- timer scheduling through `ed.after`;
- core `hook-add` handlers;
- recorded/imported macro steps through `MacroStep` and `Editor.set_macro(...)`.

The following execution paths restore the stored origin before running deferred work:

- `Editor.dispatch_key(...)` through `_run_key_binding(...)`;
- `Editor.pump_timers(...)`;
- `HookWord.execute(...)`;
- `Editor.play_macro(...)` per replayed step.

For script/plugin-originated callbacks, execution re-enters `script_context`. When a callback came from plugin package loading, it also restores `current_plugin_load_root` so package-local `include` / `require` remains available without granting arbitrary script code-load authority.

`Keymap.set_desc(...)` now preserves authority metadata when a description is added later. That closes a subtle version of the same bug: `ed.bind-doc` or prefix-binding helpers must not accidentally strip `script_context` and turn a lower-authority binding into a trusted one.

I also trimmed the default `mxdoctor` lane so it does not run `mxtest` process-group stress probes inside the doctor subprocess. Those tests remain available directly in `tests/test_mxtest.py`; the bounded doctor should stay a reliable handoff gate instead of becoming a nested process-signal stress harness.

## Concrete guarantees

- A script-created keybinding cannot later mutate `cap.*` options by being pressed outside the original script call.
- A script-created command-bar binding has the same lower-authority behavior as a hostcall-created binding.
- Adding a binding description does not drop the lower-authority origin marker.
- Trusted interactive/config-created keybindings still run with user authority.
- Plugin-created keybindings keep plugin package-local load roots and still cannot self-enable capabilities.
- Plugin-created timers and hook handlers keep the package load root they had when registered.
- Script-created saved macro steps re-enter script context when replayed later instead of running as ambient user-authority command/action steps.

## Validation

Focused validation during the rev0774 turn:

```text
121 passed: keybinding provenance, keybinding docs, script-context capability, named macro, and plugin containment regressions
85 passed: timers, keymap modes/discovery, prefix maps, hook groups, lifecycle hooks, plugin reload/picker/json regressions
15 passed: deferred-authority and doctor-selector regressions
```

Default doctor, context, archive, and packaging verification are recorded in the handoff for the packaged revision.

## Remaining risk

This is application-level provenance, not an OS sandbox. Trusted direct user commands and trusted init/config evaluation can still grant capabilities by design.

The next risky lane is plugin dictionary cleanliness: plugin package-local `include` during a callback is now rooted, but a future audit should decide whether callback-time included definitions should always land in the plugin wordlist instead of whichever wordlist is current when the callback fires. Macro serialization/import should be audited at the same time if portable macro storage starts carrying more than the current optional script marker.
