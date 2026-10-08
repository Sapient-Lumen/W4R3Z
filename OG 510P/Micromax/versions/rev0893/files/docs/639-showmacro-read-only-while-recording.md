# Rev698 - keep showmacro read-only while recording

## What changed

- `exec_command_line(...)` now excludes `showmacro` from command recording, alongside `macro` management commands
- exact `showmacro demo` / `showmacro last` during recording now report the current live step count without mutating the in-flight macro
- plain `showmacro` during recording now keeps the same step count in its runtime summary that the prompt row already previewed

## Why

`showmacro` is an inspector. While Micromax already made that inspector much more truthful, it still had one quiet side effect: if you ran it during recording, the command itself became part of the recorded macro.

That created a subtle trust problem:

- the prompt row could truthfully say `recording · demo (1 step) ...`
- pressing Enter on `showmacro` would then mutate the recording and immediately turn the runtime answer into `2 steps`

That behavior was technically explainable, but it made exact inspection feel less inspectable.

## New contract

While macro recording is active:

- `showmacro NAME` is read-only
- `showmacro` root summaries stay aligned with the current live macro buffer
- `macro stop` saves only the real recorded edit/action steps, not ad hoc exact-inspection commands

`macro` management commands were already exempt from command recording; rev698 extends that same policy to the sibling exact inspector.

## Directly pinned

After starting `macro record demo` and recording one `InsertText` step:

- `showmacro demo` reports `1 live step`
- `showmacro last` reports `1 live step`
- stopping the macro saves `demo` and `last` at `1 step`, not `3 steps`

## Trust impact

This is a trust-first cleanup. Inspection should not secretly rewrite the automation it is trying to explain.
