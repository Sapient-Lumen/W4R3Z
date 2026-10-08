# Rev0876 — narrow runtime-group rollback snapshot

Rev0876 is the first practical cut toward typed effect journaling without
removing the broad transaction snapshot.  Runtime-group cleanup and retag commit
guards now snapshot only the surfaces their sweep can mutate, rather than taking
another full `RuntimeRegistrationSnapshot` plus VM dictionary snapshot before the
sweep.

## Why this mattered

Rev0875 correctly made cleanup and retag failures commit-critical: unload/reload
no longer reported success when one cleanup surface failed.  The guard still used
the same broad runtime snapshot built for plugin source/lifecycle transactions.
That was safe but wasteful and easy to entangle with unrelated state.

For a cleanup sweep, the rollback target is not arbitrary option state, macro
recording state, message logs, or VM modules.  It is the finite set of grouped
runtime surfaces:

- VM hook handlers;
- command/action/key/timer registries;
- marks and authority sidecars;
- active interaction state;
- recovery/jumplist/selection rows;
- recent files, saved cursors, palette MRU, prompt history;
- active search, internal clipboard, and help history.

Rev0876 introduces `RuntimeGroupStateSnapshot` for exactly that boundary.

## Behavior

`PluginManager._group_operation_or_restore()` now uses
`snapshot_runtime_group_state()` before cleanup/retag and
`restore_runtime_group_state()` if the report contains failed surfaces.

That means a failed cleanup still restores commands, keys, hooks, timers, and
other group-sweep surfaces that may have been partially removed before the
failure, but it no longer deep-copies unrelated option state just to enter the
cleanup guard.

The broader `RuntimeRegistrationSnapshot` remains in use around plugin source,
lifecycle callbacks, deinit, and deferred callbacks where arbitrary hostcall
families can run.

## Tests added

The focused regression proves a force-unload cleanup failure restores a command
removed earlier in the sweep even when `_snapshot_option_state()` is patched to
raise.  Under rev0875 that unrelated option snapshot would have blocked the
cleanup guard before it could even collect a cleanup report.

The `mxaudit` policy lane now checks that:

- `RuntimeGroupStateSnapshot` and its capture/restore helpers exist;
- the commit guard uses the narrow group snapshot;
- `_group_operation_or_restore()` does not call the full registration snapshot.

## Non-claims

This is not the full typed journal.  It is a narrow, named effect-boundary
snapshot for one hot path.  The 40-field `RuntimeRegistrationSnapshot` remains
available as the broader oracle for plugin code execution.  This revision also
adds no process isolation, hostile-code containment, dependency lock, CI
workflow, or complete aggregate test manifest.
