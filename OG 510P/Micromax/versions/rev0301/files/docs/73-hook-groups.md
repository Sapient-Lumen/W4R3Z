# Hook groups (rev33)

Rev33 adds a tiny but practical layer on top of Micromax hooks: **grouped
handler registrations**.

## Why

As soon as hooks are used by plugins/config, reloadability becomes a real issue.
If a plugin adds a handler during `init`, then gets reloaded a few times, stale
handlers can accumulate unless the host or script remembers every exact xt it
installed.

A string group tag is a cheap answer:

- preserve hook execution order
- preserve per-handler provenance
- allow selective cleanup without resetting the VM

This follows the same practical lesson seen in other editor ecosystems: hook
installations are configuration data and should be removable in batches.

## Surface

```forth
hook-group!   ( group|0 -- )
hook-group@   ( -- group|0 )
hook-groups   ( -- groups )   parse hook name
hook-rm-group ( group -- n )  parse hook name
hook-detail   ( -- rows )     parse hook name
```

`hook-detail NAME` returns:

```
[[handler-name group|0 [file line col]|0] ...]
```

This is intentionally row-oriented and portable so tests, tools, and future
LLMs can inspect the live system without scraping formatted text.

## Example

```forth
hook on-save
: trim-space ( -- ) ... ;
: ensure-newline ( -- ) ... ;

"plugin:fmt" hook-group!
' trim-space hook-add on-save
' ensure-newline hook-add on-save
0 hook-group!

hook-detail on-save
"plugin:fmt" hook-rm-group on-save
```

## Plugin loader integration

The reference `PluginManager` now sets:

```
vm.current_hook_group = "plugin:<name>"
```

while evaluating plugin source and lifecycle words. On unload/reload it removes
that group across all hooks. This keeps repeated reloads from stacking duplicate
handlers even though the prototype loader does not yet garbage-collect wordlists.

## Debugging surface

`showhook NAME` now prints handlers as:

```
handler#group@file:line:col
```

when group/provenance are available.

That keeps the friendly human path (`showhook`) aligned with the machine-readable
path (`hook-detail`).
