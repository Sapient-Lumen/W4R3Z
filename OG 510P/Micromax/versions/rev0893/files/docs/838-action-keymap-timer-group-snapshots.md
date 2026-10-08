# Rev0880 — touched action/keymap/timer rollback

Rev0880 continues the typed-journal migration on the risky plugin cleanup path.
Rev0879 proved the pattern for command registrations: runtime-group cleanup and
retag commit guards should snapshot only the rows owned by the affected group(s),
not a whole registry.  This revision applies the same concrete cut to actions,
keybindings, and pending timers.

`RuntimeGroupStateSnapshot` now carries:

- `RuntimeCommandGroupSnapshot`;
- `RuntimeActionGroupSnapshot`;
- `RuntimeKeymapGroupSnapshot`;
- `RuntimeTimerGroupSnapshot`.

Each helper captures only entries whose group matches the cleanup/retag group
labels passed by the plugin manager.  On restore, rows currently owned by those
groups are removed and the captured rows are put back.  Unrelated trusted rows
are not copied into the snapshot and are not rewound by that restore.

Timers are the subtle case.  Cleanup and retag only cancel or retag pending
tasks.  The touched timer snapshot therefore keeps affected tasks, not the
whole timer queue or next-id counter.  Restore rebuilds the queue heap from the
current pending task table after replacing the affected tasks, so unrelated
timers stay in their current state.

## Why this matters

This is still not the final effect journal, but it moves three more cleanup
surfaces out of surface-wide copying.  The remaining group snapshot still has
broad state for hooks, marks, cursor/navigation/history/clipboard/search/help
sidecars, and interaction state.  Those should be cut only when a test can prove
the narrower behavior preserves the cleanup failure contract.

The useful migration rule remains:

1. keep `RuntimeRegistrationSnapshot` for plugin source/lifecycle/callback paths
   where arbitrary overwrites can happen before failure;
2. narrow only the commit-sweep paths whose mutators are known;
3. test that affected rows are restored and unrelated rows are not captured or
   rewound;
4. enforce the seam in `mxaudit` so future cleanup work cannot silently fall
   back to broad registry copying.

## Non-claims

This is not process isolation, hostile-code containment, a complete typed effect
journal, durable cleanup provenance, or a full release evidence manifest.  It
does not shrink `editor.py`, remove the broad 40-field
`RuntimeRegistrationSnapshot`, or make document edits, file opens, saves, shell
or URL effects, external clipboard exports, blocking hostcalls, memory
exhaustion, native code, or process compromise rollback-safe.
