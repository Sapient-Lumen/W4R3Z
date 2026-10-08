# Revision 0316 — 2026-03-18

This revision teaches the X11 recorder to emit relocatable pointer coordinates
through `CoordMode(mouse=window|client)` using captured active-window geometry.

Shipped
-------

- added recorder-side relative mouse authoring via `--coord-mode-mouse screen|window|client`
- window-context capture can now include active-window geometry snapshots
- recorded `MouseMove`, `MouseDrag`, and `MouseClickAt` steps can now be rewritten into window-relative or client-relative coordinates
- recorder output is prefixed with `CoordMode(target=mouse, mode=...)` when relative mode is requested
- relative-anchor details are preserved in the optional window-context sidecar payload
- added focused tests for pointer-step relativization and record-x11 relative-coordinate CLI flows
- updated README / specs / recorder docs / issue tracker
- added a focused research note on CoordMode / relative-recording product patterns

Intent
------

The product lesson here is that relocatable pointer recording should be easier
than hand-subtracting coordinates. VHK already knew how to *run* relative mouse
coordinates; now the recorder can *author* them too when the active window stays
stable enough to justify it.

Remaining gaps
--------------

- no Studio/editor surface yet for reviewing the chosen relative anchor
- no per-step mixed-space editing yet
- no Wayland-native lexical recorder equivalent yet
- semantic UI capture is still a separate future lane; relative coordinates are
  more robust than raw screen points, but they are not the same as structured
  accessibility or app-native control
