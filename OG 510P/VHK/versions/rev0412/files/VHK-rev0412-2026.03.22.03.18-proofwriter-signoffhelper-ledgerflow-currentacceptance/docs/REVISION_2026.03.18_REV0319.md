# Revision 0319 — 2026-03-18

This revision tightens segmented recorder guards so they default to the same
foreground truth the recorder actually observed.

Shipped
-------

- segmented `vhk record-x11` output now defaults inserted `WaitForWindow`
  guards to `focused: true`
- added `--window-guard-scope active|present`
- `active` is now the default guard scope; `present` remains available for
  authors who intentionally want broader existence waits
- recorded guard comments now make the chosen scope explicit
- window-context sidecars now preserve `window_guard_scope`
- added focused tests for active-vs-present segmented guard output
- updated README / specs / recorder docs / issues
- added a focused research note on active-window guard truth

Intent
------

The recorder samples the active window, not an arbitrary matching background
window. Its generated guards should preserve that same contract by default.
This makes recorded Linux desktop flows behave more like `WinWaitActive` /
foreground-sync discipline and less like a loose "some matching window exists"
check that can pass too early.

Remaining gaps
--------------

- no Studio/editor review surface yet for active-vs-present segment guards
- no semantic understanding of *why* focus changed beyond recorder evidence
- no Wayland-native lexical recorder equivalent yet
- recorder-side active-window truth still depends on polling snapshots rather
  than toolkit-native app state
