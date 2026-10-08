# Rev693 - showmacro root live action summary

Date: 2026-03-28

## Why

`showmacro NAME` had already become a truthful exact-inspection surface:

- exact rows spoke live recording/playback truth for one chosen slot
- idle no-arg `showmacro` centered the default `last` slot
- the umbrella `macro` root now kept live action detail visible during recording and playback

But the no-arg `showmacro` root still always reused the idle-default helper. That meant recording/playback could flatten back into a broader or even idle-looking summary right before `usage: showmacro NAME`.

## What changed

`_showmacro_root_preview_summary()` now reuses the same live macro root summary as plain `macro`:

- idle: `idle · default=last (0 steps) · 0 macros`
- recording: `recording · demo (1 step) · stop to save, cancel to discard · 0 macros`
- playback: `playing · demo (1 step) · wait for playback · 2 macros · e.g. last (1 step) [default]`

## Result

Plain `showmacro` now previews the real live macro state it is about to summarize instead of flattening recording/playback back into an idle-only exact-inspection story.
