# Revision 0318 — 2026-03-18

This revision teaches the X11 recorder to preserve title-driven workflow
transitions inside the same window when authors opt into that extra precision.

Shipped
-------

- added `--segment-on-title-change` to `vhk record-x11`
- recorder segmentation can now split one stable window identity into multiple
  guarded segments when the recorded title changes
- same-window title segments automatically fall back to per-segment `exact`
  selectors when the broad stable selector would collapse them together
- window-context sidecars now preserve whether title-transition segmentation was
  enabled for the recording
- added focused tests for opt-in title segmentation and its validation path
- updated README / specs / recorder docs / issue tracker
- added a focused research note on title-aware wait patterns

Intent
------

A lot of Linux desktop work stays inside one browser/editor/document window
while the meaningful title changes. That is still a real transition, and raw
`Delay` steps are a poor way to preserve it. At the same time, title matching is
more fragile than class/app-id matching, so VHK keeps this lane explicit and
reviewable instead of silently making it the default.

Remaining gaps
--------------

- no Studio/editor review surface yet for recorded title-aware segments
- no semantic understanding of tabs/documents beyond title evidence
- no Wayland-native lexical recorder equivalent yet
- recorder-side title segmentation still depends on polling snapshots rather
  than toolkit-native app state
