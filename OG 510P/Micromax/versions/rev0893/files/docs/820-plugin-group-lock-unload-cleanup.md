# Rev0862 — plugin runtime groups stay locked during plugin execution

Rev0861 gave users `plugin unload NAME` as a restart-free recovery command.  The
next audit found a concrete escape from that cleanup path: plugin code could
clear `ed.group!` / `hook-group!`, or switch to an ordinary diagnostic group,
before registering commands, keybindings, timers, hooks, actions, or marks.
Those callbacks still carried script/plugin authority, but their group no longer
matched the loader-owned `plugin:NAME` cleanup group, so unload could report
success while leaving live surfaces behind.

Rev0862 keeps the fix narrow.  While script-context code is running with a plugin
package root and an active loader-owned `plugin:*` runtime group, attempts to
clear or change that group now fail visibly.  Plain scripts can still use normal
diagnostic groups, and trusted/user code can still group registrations manually.
The stricter rule applies only to plugin-originated source, lifecycle hooks, and
deferred plugin callbacks where the group is part of load/reload/unload
provenance.

## Contract

- Plugin source runs with a loader-owned editor and hook group.
- Plugin code may preserve that current group.
- Plugin code may not clear that group with `0 ed.group!` or `0 hook-group!`.
- Plugin code may not switch that group to an ordinary name such as `"loose"`.
- Plain non-plugin scripts still cannot mint `plugin:*` groups.
- `plugin unload NAME` can continue to rely on group cleanup for plugin-owned
  runtime registrations.

## Why this matters

A surviving callback after unload is worse than a normal plugin load failure: the
operator has asked for recovery and the inventory says the plugin is gone.  The
remaining callback can still run later through a command, key, timer, or hook and
may be hard to attribute.  Denying group escape at registration time is easier to
reason about than trying to discover every possible leaked surface later.

## Residual risk

This is still an in-process policy boundary.  A loaded plugin can run until it is
unloaded, and already-evaluated code is not erased from Python memory.  The rule
protects Micromax runtime-registration cleanup; it is not OS sandboxing or
hostile-code containment.
