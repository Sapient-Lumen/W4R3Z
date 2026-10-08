# Rev0776 — Plugin group provenance guard

## Problem

Rev0775 and the first rev0776 callback rollback pass made deferred plugin callbacks much safer, but the provenance lookup still treated a raw `plugin:*` runtime group as enough evidence to recover plugin callback authority.

That was too trusting. Runtime groups are useful for cleanup, diagnostics, and reload retagging, but lower-authority script code can create registrations too. If a script-created keybinding, hook, timer, command callback, or macro could carry `group = "plugin:victim"` without also carrying a captured package root owned by the loaded plugin, the later callback could borrow the victim plugin's wordlist and package-local include root.

That is an integrity bug, even though the callback still ran under script authority. It would let a lower-authority script write helper definitions into another plugin's namespace or load package-local source that it should not have been able to name.

## Changes

`Editor._plugin_callback_candidate(...)` now treats the captured package root as the callback authority token when a plugin manager is installed.

Rules now used by deferred callback restoration:

- a captured root must resolve to a currently loaded plugin root;
- a raw `plugin:*` group without a matching captured root is only cleanup/provenance metadata;
- when both root and `plugin:*` group are present, they must identify the same loaded plugin;
- stale roots from unloaded plugins still fail closed;
- embeddings without a plugin manager retain the older explicit `plugin_load_root_context(...)` low-level behavior for tests and simple hosts.

`Editor.set_runtime_group_value(...)` is the new shared group-mutation policy seam. It lets trusted user/init code set any group, but refuses script-context attempts to mint reserved `plugin:*` groups. The policy now covers:

- `ed.group!` / `ed.group@` editor registration groups;
- core `hook-group!` / `hook-group@` hook registration groups.

Ordinary non-reserved script groups such as `cfg` remain allowed.

## Concrete guarantees

- A script-created callback with `group = "plugin:victim"` but no captured package root cannot regain the victim plugin's include root or dictionary context.
- A mismatched captured root plus `plugin:other` group does not borrow either plugin's context.
- Script-context code cannot assign `plugin:*` through `ed.group!` or `hook-group!` unless it is merely preserving the same already-active plugin lifecycle group.
- Plugin load/reload code can still register its own grouped commands, keys, hooks, and timers because the plugin manager establishes the lifecycle group before evaluating plugin source.
- Callback failure rollback from `docs/726-plugin-callback-failure-rollback.md` remains active for loaded-plugin callbacks that carry valid root provenance.

## Validation

Focused validation during this turn included:

```text
26 passed: tests/test_plugin_containment_and_caps.py
120 passed: plugin containment, hostcall/reload, hook provenance/groups, macro, timer/highlight, and deferred-authority regression set
139 passed: script filesystem/recovery capability set
```

The packaged handoff also records compile, lint, default doctor, context, packaging, mxtest-plan, and archive verification evidence.

## Remaining risk

Runtime groups are still string metadata rather than first-class signed provenance objects. The important correction is that reserved `plugin:*` strings no longer grant plugin authority on their own. A future cleanup could replace group-string authority checks with an explicit immutable `PluginCallbackOrigin(plugin_name, root, generation)` record, which would make reload and stale-callback reasoning even clearer.
