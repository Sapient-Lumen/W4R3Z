# Rev0776 — Plugin callback failure rollback

## Problem

Rev0775 restored the right plugin wordlist and package-local source root when a plugin-created callback fired later. That fixed namespace leaks for successful lazy helper loads, but the failure path was still too trusting.

A plugin keybinding, timer, hook, macro step, or `ed.cmd-add` command callback could run `"helper.mx" include`; if that helper defined a word or registered a key/command and then failed, the visible callback reported failure while partial VM dictionary and editor runtime registrations survived. That is a bad recovery boundary: a failed deferred callback should not strand half-loaded helper words, temporary commands, keybindings, hooks, or timers.

The bug was easiest to see through a keybinding because `mx:` action specs intentionally catch Micromax evaluation errors and return `False`. No exception escaped `plugin_callback_context(...)`, so exception-only rollback was insufficient.

## Changes

`src/micromax_editor/plugin_runtime.py` now exposes a small callback rollback snapshot:

- `PluginCallbackSnapshot`
- `snapshot_plugin_callback_state(vm)`
- `restore_plugin_callback_state(vm, snapshot)`

The snapshot combines:

- VM dictionary/module/search-order/loaded-path topology;
- editor runtime registrations: command dispatcher, keymap, hook handlers, timers;
- stack-like VM execution state.

`Editor.plugin_callback_context(...)` now restores that state if a live-plugin callback raises.

`Editor.run_script_origin_callback(...)` is the new higher-level deferred-callback runner for editor surfaces that can swallow Micromax exceptions and report failure as a boolean. It runs under the captured script/plugin authority and, when requested, rolls back live-plugin dictionary/runtime changes on `False` as well as on exceptions.

Current call sites using the false-result rollback path:

- plugin/script-origin key dispatch;
- plugin/script-origin macro replay steps;
- Micromax-defined command-bar commands registered through `ed.cmd-add`.

Timer and hook callbacks still rely on exception rollback through `plugin_callback_context(...)`, because those surfaces are notification-style and do not have a meaningful boolean success contract.

## Concrete guarantees

- A failed plugin keybinding helper include does not leave partial helper words in the plugin wordlist or Forth wordlist.
- A failed plugin command callback does not leave temporary command registrations or keybindings created before the failure.
- Successful lazy helper includes still persist in the plugin wordlist, preserving the rev0775 behavior.
- The rollback is topological/runtime-registration rollback only; it does not pretend to undo arbitrary buffer edits or external host side effects.

## Validation

Focused validation during the rev0776 turn:

```text
26 passed: tests/test_plugin_containment_and_caps.py
120 passed: plugin containment, hostcall/reload, hook provenance/groups, macro, timer/highlight, and deferred-authority regression set
```

The packaged handoff also records compile, lint, default doctor, context, packaging, mxtest-plan, and archive verification evidence.

## Remaining risk

This remains an in-process application boundary, not an OS sandbox or a full transactional VM. The rollback deliberately covers Micromax dictionary topology and editor runtime registrations because those were the persistent shared surfaces affected by failed callback-time code loading. It does not roll back buffer mutations, messages, clipboard activity, shell effects, or arbitrary Python objects captured inside words.

A future hardening lane could add explicit per-callback side-effect policy, but that should be designed as a user-visible plugin contract rather than silently pretending all plugin actions are reversible.
