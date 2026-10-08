# Revision 0437 — macro-scoped receipt followups and explicit history-board receipt scopes

Revision 0436 made selected-macro receipt lookup macro-scoped, but one quieter correctness leak remained in the shared receipt-evidence classifier: `macro_latest_dispatch_json.sh <macro>` could still emit `warm_runtime_evidence.followup` commands that pointed back at the project-global `latest_dispatch_json.sh`.

This revision closes that leak and tightens the project-wide dispatch-history board so it states, instead of implying, which receipt lane is project-global and which is macro-scoped.

## What changed

- fixed `_classify_latest_dispatch_warm_runtime_evidence(...)` so it preserves the caller-supplied latest-dispatch command instead of overwriting it with `latest_dispatch_json.sh`
- `macro_latest_dispatch_json.sh <macro>` now keeps `macro_latest_dispatch_json.sh <macro>` in its receipt-evidence followup chain for both current and stale/repair states
- `macro_dispatch_history_board_json.sh` now exposes:
  - `receipt_surfaces.project_latest_dispatch`
  - `receipt_surfaces.primary_macro_latest_dispatch`
  - `receipt_surfaces.macro_latest_dispatch_template`
- each dispatch-history macro item now carries:
  - `dispatch_history.latest_receipt_warm_runtime_evidence`
  - `dispatch_history_posture.command_scope_id`
  - `receipt_observability.macro_latest_dispatch`
  - explicit `preferred_entrypoints.project_latest_dispatch` and `preferred_entrypoints.macro_latest_dispatch`
- dispatch-history posture commands now route more directly:
  - `no_dispatch_history` and `blocked_repeated_recently` point at the checked gate
  - receipt-centric postures point at the macro-scoped latest-dispatch helper

## Why it matters

The flagship VHK lane is a resident i3/X11 service plus a thin control plane for a private LLM. That only works if the control plane stays selected-macro correct all the way through the next recommended command, not just through the initial payload load.

After this revision:

- project-global newest-receipt truth remains available for project observability
- selected-macro receipt truth stays on the chosen macro
- the dispatch-history board is explicit about which lane a command belongs to
- receipt-first author/repair/execute loops are less likely to bounce back into the wrong macro's newest receipt

## Validation

- `python -m py_compile src/vhk/cli.py tests/test_macro_latest_dispatch_json_cli.py tests/test_macro_dispatch_history_board_json_cli.py`
- `pytest -q tests/test_macro_latest_dispatch_json_cli.py`
- `pytest -q tests/test_macro_dispatch_history_board_json_cli.py::test_macro_dispatch_history_board_json_reports_attention_and_clean_history`
- `pytest -q tests/test_macro_dispatch_history_board_json_cli.py::test_macro_dispatch_history_board_json_marks_receipt_stale_after_macro_change`
- `pytest -q tests/test_macro_dispatch_history_board_json_cli.py::test_macro_dispatch_history_board_json_marks_receipt_stale_after_runtime_epoch_change`
- `pytest -q tests/test_macro_dispatch_history_board_json_cli.py::test_macro_dispatch_history_board_json_marks_receipt_stale_after_desktop_session_change`
- `pytest -q tests/test_macro_dispatch_history_board_json_cli.py::test_macro_dispatch_history_board_json_marks_receipt_stale_after_runtime_probe_latency_change`
- `pytest -q tests/test_macro_dispatch_history_board_json_cli.py::test_macro_dispatch_history_board_marks_probe_result_variant_drift_within_failures`
- `pytest -q tests/test_macro_dispatch_history_board_json_cli.py::test_macro_dispatch_history_board_json_separates_project_global_and_primary_macro_receipt_lanes`
