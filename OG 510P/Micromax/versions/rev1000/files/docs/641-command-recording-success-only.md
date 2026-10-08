# Rev700 - command recording keeps only successful non-inspector commands

## What changed

- `exec_command_line(...)` now decides whether a command *could* be recorded before dispatch
- the actual `MacroStep(kind='command', name='command', payload={'cmdline': ...})` is appended only after dispatch returns success
- failed command lines stay out of the recording buffer
- read-only `show*` commands still stay out of the recording buffer entirely

## Why

Micromax already had the right headline rule in the docstring: only successful command lines should become recorded macro steps. But the old implementation appended the command step before dispatch finished, which meant failed commands could still sneak into the saved macro.

That was a trust problem because the recorded automation could include things that did not actually run successfully.

## New contract

While recording a macro:

- failed command lines like `nope` do **not** become recorded steps
- read-only inspector commands like `showstatus` do **not** become recorded steps
- successful ordinary command lines like `goto 1:1` **do** become recorded steps

## Directly pinned

Starting from an empty recording:

- `nope` leaves the macro buffer at `0`
- `showstatus` still leaves the macro buffer at `0`
- `goto 1:1` raises the buffer length to `1` with one command step
- stopping the macro saves `demo` at `1 step`

## Trust impact

This is a trust-first cleanup. Recorded automation should reflect what actually ran, not failed attempts or observational probes.
