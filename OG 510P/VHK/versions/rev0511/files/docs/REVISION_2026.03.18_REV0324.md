# Revision 0324 — workspace-aware recorder segmentation and guards

## Summary

Revision 0324 closes the next recorder truth seam. Same-window workspace changes are no longer silently treated as generic focus changes: recorder segmentation can now keep them flat by default, or preserve them explicitly with `--segment-on-workspace-change`, including `WaitForWindowEvent(event=workspace, ...)` when event-guard mode is active.

## Code changes

- `src/vhk/cli.py`
  - added `--segment-on-workspace-change` to `vhk record-x11`
  - workspace is no longer implicitly part of every segment identity
  - recorder transition classification now distinguishes `workspace` from `focus`
  - event guard mode can now emit `WaitForWindowEvent(event=workspace, ...)`
  - window-context sidecars now preserve `segment_on_workspace_change`
- `tests/test_record_x11_context_cli.py`
  - added coverage for same-window workspace changes staying flat by default
  - added coverage for opt-in workspace segmentation and workspace event guards
  - added CLI validation coverage for `--segment-on-workspace-change`

## Tests

- `python -m compileall -q src/vhk tests`
- `pytest -q tests/test_record_x11_context_cli.py tests/test_wait_for_window_event_step.py tests/test_wm_events_polling.py tests/test_window_contracts.py`

## Docs

- updated `README.md`
- updated `docs/RECORDER_X11.md`
- updated `docs/SPECS.md`
- updated `docs/ISSUES_2026Q1.md`
- added `docs/RESEARCH_2026.03.18_WORKSPACE_SEGMENTATION_AND_EVENT_GUARDS.md`
