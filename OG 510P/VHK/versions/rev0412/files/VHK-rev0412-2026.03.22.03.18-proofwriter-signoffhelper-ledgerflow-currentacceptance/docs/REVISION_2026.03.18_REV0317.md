# Revision 0317 — 2026-03-18

This revision teaches the X11 recorder to preserve window transitions inside one
recording instead of flattening them into one selector snapshot plus blind
`Delay` steps.

Shipped
-------

- added recorder-side window segmentation via `--segment-by-window-context`
- inserted `WaitForWindow` guards at recorded active-window boundaries
- long delay spans now split at those boundaries so window guards land near the
  actual transition time
- per-segment selector choice now falls back to `exact` when a broad stable
  selector would collapse distinct recorded windows together
- recorder-side relative mouse authoring now works per window segment, not only
  for one whole recording
- window-context sidecars can now preserve segment timing / selector / anchor
  evidence
- added focused tests for segmented guards, ambiguous same-app windows, and
  multi-window relative-coordinate recording
- updated README / specs / recorder docs / issue tracker
- added a focused research note on WinWait-style recorder segmentation patterns

Intent
------

The product lesson here is that one recording can cross more than one window,
and the recorder should preserve that truth directly. A long sleep is not a
useful explanation for "the user switched to another app here". `WaitForWindow`
segments are still lexical evidence, not full semantics, but they are much
closer to the disciplined Window Spy / WinWaitActive workflow that made AHK and
Pulover practical.

Remaining gaps
--------------

- no Studio/editor review surface yet for recorded segments
- no automatic upgrade from recorded segments into app-native routes yet
- no Wayland-native lexical recorder equivalent yet
- semantic UI capture is still a separate future lane; window guards are more
  honest than raw delays, but they are not the same as structured accessibility
  or app-native control
