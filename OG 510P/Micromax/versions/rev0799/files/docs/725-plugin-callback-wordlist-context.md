# Rev0775 — Plugin callback wordlist context

## Problem

Rev0774 preserved the **authority** label for deferred callbacks: script-created keybindings, macros, timers, and hooks re-entered `script_context`, and plugin-created callbacks kept a package-local `plugin_load_root` for `include` / `require` without granting global `cap.fs-require`.

That was necessary but not sufficient. The package-local source root only controlled where code could be read from. It did not restore the plugin dictionary context. A callback-time `"helper.mx" include` therefore evaluated under whichever wordlist happened to be current when the keypress, command, timer, hook, or macro fired. In ordinary editor state that is often the global/Forth wordlist. The result was a slow namespace leak: plugin helper definitions could land outside the plugin wordlist, and plugin keybindings either had to spell `use plugin-name ...` in every action string or fail to find their own words.

This is a trust-boundary issue as well as a cleanliness issue. A delayed plugin callback should not turn package-private code into global editor vocabulary just because it ran later.

## Changes

`Editor.plugin_callback_context(plugin_load_root, group)` is now the shared deferred-plugin execution context. It resolves the currently loaded plugin that owns the callback by stable runtime group (`plugin:name`, including staged/reloaded forms) or by package root. While active, it:

- restores the plugin package-local load root;
- puts the plugin wordlist first in the search order;
- sets `CURRENT` to the plugin wordlist;
- restores `current_hook_group` and `current_editor_group` to the live plugin group;
- restores the previous order/current/group state on exit.

The following deferred execution paths now use that context instead of only setting `current_plugin_load_root`:

- key dispatch (`Editor._run_key_binding`);
- timer callbacks (`Editor.pump_timers`);
- hook callbacks (`HookWord.execute`);
- named/last macro replay (`Editor.play_macro`);
- Micromax-defined command-bar commands registered through `ed.cmd-add`.

There is also an intentional stale-root rule: when a plugin manager is installed, a stored plugin root is honored only if a currently loaded plugin still owns it. If the plugin has been unloaded, the callback still runs with script authority, but package-local code-load authority is not retained. Low-level tests/embeddings that use `plugin_load_root_context(...)` without a plugin manager keep their old behavior.

A small refactor removed a duplicate `MacroStep.script_context` annotation that had crept in during the prior provenance work.

## Concrete guarantees

- Plugin keybindings can call plugin words without spelling `use plugin-name` in every action string.
- Callback-time `include`/`require` definitions land in the plugin wordlist, not the global/Forth wordlist.
- Plugin command callbacks, timers, and hooks share the same plugin dictionary context as plugin keybindings.
- Stale callbacks from unloaded plugins do not retain package-local load authority merely because they serialized or captured an old root string.
- Script authority remains intact: plugin callbacks still cannot grant themselves `cap.*` options.

## Validation

Focused validation during the rev0775 turn:

```text
31 passed: plugin containment/capability, deferred authority, keybinding provenance, plugin hostcall regressions
155 passed: plugin containment, script-context fs caps, plugin reload, timers, keybinding docs, and named macro regressions
```

Default doctor, lint, context, archive, and packaging evidence are recorded in the packaged handoff.

## Remaining risk

This is application-level namespace/authority restoration, not an OS sandbox. Plugin callback-time includes are allowed to mutate the plugin wordlist persistently; that is consistent with Micromax `include` semantics, but a future plugin-hardening lane could add optional transactional callback code loading if the project wants callback helpers to be pure/load-once.

Portable macro encoding still exports only the script-origin marker, not absolute plugin roots. That is deliberate for now: exporting absolute package roots would be less portable and could accidentally re-grant code-load authority after import. If macro persistence grows plugin-owned macro packages later, it should use plugin names/package identities rather than raw filesystem roots.
