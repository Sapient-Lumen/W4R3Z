# Rev695 - macro root sample dedup

Date: 2026-03-28

## Why

After rev692/rev693, bare `macro` and `showmacro` root summaries already spoke truthful live action state during playback. But the sample tail could still repeat the same macro a second time:

- `playing · demo (1 step) · wait for playback · 2 macros · e.g. demo (1 step)`

That was technically correct, but visually noisy.

## What changed

Playback-root summaries now skip `e.g.` candidates whose saved name matches the currently playing macro and prefer another saved sample when one exists, for example:

- `playing · demo (1 step) · wait for playback · 2 macros · e.g. last (1 step) [default]`

If no other saved sample exists, the summary simply omits the redundant `e.g.` tail.

## Result

The root macro summaries stay truthful, but they now spend their last few words on new information instead of echoing the same live macro twice.
