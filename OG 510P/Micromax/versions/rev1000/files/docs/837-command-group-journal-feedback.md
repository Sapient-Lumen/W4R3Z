# Rev0879 — touched command-group rollback and cleanup hints

Rev0879 keeps the work on the risky plugin cleanup path concrete.  The prior
cleanup guards restored runtime-group sweeps with a narrower snapshot, but the
command slice of that snapshot still copied the entire command table.  That was
safe, but it kept one of the old broad-snapshot habits alive inside the new
cleanup boundary.

This revision adds `RuntimeCommandGroupSnapshot` plus
`snapshot_command_group_state()` / `restore_command_group_state()`.  Runtime
cleanup and retag commit guards now pass the affected runtime group labels, so
command rollback captures only commands owned by those group(s):

- unload cleanup captures the stable plugin group;
- staged reload promotion captures both staged and stable groups;
- loaded-plugin cleanup captures the committed plugin group before combining
  runtime-group and generation cleanup.

The broad `RuntimeRegistrationSnapshot` remains intact for plugin source,
lifecycle, callback, and deinit transactions.  Those paths can still involve
arbitrary command overwrites before failure.  Rev0879 only narrows the commit
sweep path where the effect boundary is already known.

The second small operational change makes retained diagnostics easier to find.
When `plugin unload NAME` or `plugin reload NAME` fails and retained cleanup
rows exist, the feedback line now appends `see plugin cleanup NAME`.  The full
failed-surface rows remain in `plugin cleanup [NAME]` and the headless hostcall;
the ordinary failure message just points to them.

## Why this matters

The project goal is not to create more registries.  The useful migration pattern
is:

1. keep the broad snapshot as an oracle where plugin code can mutate too much;
2. identify a path whose effect class is actually smaller;
3. snapshot or journal only that path's touched state;
4. pin the narrower boundary with tests and audit checks.

Commands are now the first runtime-group surface cut this way.  The remaining
group-sweep surfaces—actions, keymaps, timers, marks, and delayed state
sidecars—still use broader captures inside `RuntimeGroupStateSnapshot`.

## Non-claims

This is not hostile-code containment, process isolation, Wasm isolation, durable
provenance, or a complete touched-effect journal.  It does not shrink
`editor.py`, remove the 40-field broad registration snapshot, or make document
edits, external I/O, file opens, saves, shell/URL effects, blocking hostcalls,
memory exhaustion, native code, or process compromise rollback-safe.
