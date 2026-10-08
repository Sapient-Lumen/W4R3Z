# Revision 0315 — 2026-03-18

This revision teaches the X11 recorder to capture window context alongside
lexical input, which moves VHK a little closer to the AutoHotkey / Pulover
"Window Spy + scoped macro" authoring feel while staying conservative about
what should be auto-applied.

Shipped
-------

- added recorder-side window-context capture plumbing
- `vhk record-x11` now supports:
  - `--capture-window-context`
  - `--apply-window-context`
  - `--window-context-out`
  - `--window-context-poll-ms`
- recorder context capture emits reviewable `stable` and `exact` selector
  suggestions derived from sampled active-window snapshots
- project recording can now write the conservative `stable` selector into the
  recorded macro's top-level `when:` field
- macro-file writing now supports setting/preserving top-level `when:` during
  generated writes
- added focused tests for macro writing and recorder context capture flows
- updated README / specs / project-format / recorder docs / issue tracker
- added a focused research note on Window Spy and recorder-adjacent selector
  capture patterns

Intent
------

The product lesson here is simple: app scope should be easier to keep than to
lose. Recorder output can stay lexical, but authors should not have to run a
second unrelated workflow just to reattach honest window scope to the macro.

Remaining gaps
--------------

- no semantic UI capture yet; this is still window-level scoping, not control-
  level automation
- no Wayland-native recorder equivalent yet
- future Studio/editor flows should surface the same stable/exact selector
  evidence without requiring CLI review
