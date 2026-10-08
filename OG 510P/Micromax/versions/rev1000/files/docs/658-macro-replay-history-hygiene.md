# Rev658 / rev717 — macro replay command-history hygiene

Macro replay now keeps replayed command steps out of command history. Before this change, a macro containing a command-bar step internally called `exec_command_line(...)`, which meant playing the macro could add the replayed command to the same history lane as fresh user command-bar submissions. That is subtle, but it makes command history feel less trustworthy: pressing Up after automation should not look like the user manually typed every command step the macro just replayed.

The fix is intentionally small:

- `Editor.exec_command_line(cmdline, *, record_history=True)` preserves the normal command-bar behavior by default.
- `play_macro()` calls replayed command steps with `record_history=False`.
- A user-typed `macro play NAME` still enters command history; only the internal command steps are suppressed.
- The new history hygiene composes with the rev716 atomic replay path: failed replayed commands still trigger rollback and an abort message without polluting command history.

This is a small flow/taste cleanup rather than a new capability. It keeps automation replay from muddying the user-facing command loop, while preserving the directness of the command-step replay path.
