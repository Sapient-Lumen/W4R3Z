# Revision 0424 — checked dispatch now honors warm-path latency attention

This revision closes the last warm-path inconsistency between resident-runtime observability and the actual checked dispatch gate on the flagship i3/X11 lane.

## What changed

- `macro_dispatch_gate_json` now consults the cached resident-runtime probe witness, not only macro-local replay/cleanup posture.
- When the latest bounded probe reports `latency_status=over_budget`, checked dispatch now adds a dedicated blocker:
  - `warm_runtime_probe_latency_attention`
  - `primary_blocker_class_id=runtime_latency_attention`
- The checked gate now routes that state to:
  - `decision.id = inspect_runtime_latency_before_dispatch`
  - `repair_action.id = inspect_runtime_latency`
- `dispatch_readiness` now carries the resident probe latency fields directly:
  - `latency_attention_required`
  - `warm_runtime_probe_latency_status`
  - `warm_runtime_probe_latency_ms`
  - `warm_runtime_probe_latency_budget_ms`
- `dispatch_contract` now carries `warm_runtime_ticket_command` so thin per-macro gate consumers can jump back to the resident runtime ticket without reopening the full stack.
- The generated per-macro stack contract now includes lightweight runtime-helper wrappers (`warm_runtime_ticket`, `check_runtime`, `status_runtime_json`) because those are now part of the honest checked-dispatch repair loop.

## Why it matters

Before this cut, VHK could simultaneously say:

- durable runtime signoff is stale because the warm path is over budget, and
- checked dispatch is still ready now for the same macro.

That was too optimistic for a resident fast-path product. After this revision, the actual checked gate used by operators and a private LLM now shares the same latency-attention truth as the warm-runtime ticket and runtime-acceptance contract.

## Focused validation

- `python -m py_compile src/vhk/cli.py tests/test_macro_dispatch_gate_json_cli.py`
- `pytest -q tests/test_macro_dispatch_gate_json_cli.py`
- `pytest -q tests/test_macro_runtime_board_json_cli.py::test_macro_runtime_board_json_stales_signoff_when_runtime_probe_latency_goes_over_budget`
- `pytest -q tests/test_primary_macro_work_ticket_cli.py::test_primary_macro_work_ticket_prefers_runtime_latency_attention_before_checked_dispatch`
