# Revision 0450 — selected-macro handoff chooses receipt truth when that is the sharper lane

## Decision

Small resident-runtime helper surfaces must not hide receipt-first triage behind generic execution or signoff language.

## Implemented

- added `build_selected_macro_handoff(...)` to centralize the selected-macro next-hop choice
- `primary_macro_work_ticket` now carries both `dispatch_history_workbench` and `selected_macro_handoff`
- `warm_runtime_ticket` now mirrors that same chosen handoff instead of flattening back to execution-only when the daemon itself is healthy
- stale selected-macro dispatch evidence now outranks generic acceptance repair in the selected-macro work ticket
- stack/helper summaries now print the selected handoff source/mode/surface/command
- generated-stack regression coverage now includes dispatch-history handoff projection on stack summaries

## Why it matters

The resident i3/X11 control plane is supposed to be one-read for a private LLM. When the newest receipt is already telling us the warm lane drifted, the system should say `open the receipt lane` directly instead of forcing the caller to infer that from acceptance debt plus runtime posture.

## Touched

- `src/vhk/cli.py`
- `tests/test_primary_macro_work_ticket_cli.py`
- `tests/test_i3_busd_stack_cli.py`
- `README.md`
- `docs/ACTIVE_PRODUCT_CONTRACT_2026.03.22.md`
- `docs/LLM_AUTHOR_LOOP_CONTROL_PLANE.md`
- `docs/ISSUES_2026Q1.md`
