# Rev699 - keep show commands read-only while recording

## What changed

- macro command recording now excludes the whole `show*` inspector family, not just `showmacro`
- representative read-only inspectors like `showstatus` no longer append themselves to the in-flight macro buffer
- `showmacro` keeps the rev698 exact/root step-count alignment while the same policy now covers the rest of the inspector family too

## Why

Rev698 fixed the most obvious trust seam: `showmacro` should not mutate the macro it is explaining. But the same underlying problem still applied to the rest of Micromax's read-only inspector surface.

Commands like these are meant to observe state:

- `showstatus`
- `showbuffer`
- `showoption`
- `showmark`
- `showjump`
- `showmacro`

If they quietly become recorded macro steps, inspection turns into mutation, which makes live automation harder to reason about.

## New contract

While macro recording is active:

- `macro ...` management commands stay out of the recording buffer
- any command whose name starts with `show` also stays out of the recording buffer
- the recorded macro only grows when the user performs actual edit/action/automation steps, not observational inspection

## Directly pinned

After starting `macro record demo` and recording one `InsertText` step:

- `showstatus` leaves the macro buffer length at `1`
- `showmacro demo` still reports `1 live step`
- stopping the macro saves `demo` at `1 step`

## Trust impact

This is a trust-first cleanup. Inspector commands should observe editor state, not become part of the automation they are inspecting.
