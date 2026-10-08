# Revision 0423 — warm-path latency now stales durable signoff

This revision closes the gap between live resident-runtime latency attention and durable runtime acceptance on the i3/X11 lane.

## What changed

- `runtime_state_cache` now records the latest bounded dispatch-probe observation, including latency status/budget.
- `check_runtime_json.sh` now persists that probe observation into the runtime-state cache each time it runs.
- `restart_runtime_json.sh` also refreshes the cached probe observation while it verifies the repaired daemon.
- `runtime_acceptance_contract` now carries `warm_runtime_probe_latency_attention_id`.
- The current runtime-acceptance contract now sets that field to `inspect_runtime_latency` when the latest cached probe says the warm path is over budget.
- Durable runtime signoff now goes stale when a previously accepted macro is still proof-current in other ways but the resident warm path has regressed into latency attention.

## Why

VHK's flagship architecture is not just `session-bound and reachable`; it is `session-bound and warm enough to be worth using as the preferred lane`. Once the control plane learned to say `reachable but sluggish`, durable runtime acceptance had to learn the same lesson. Otherwise the repo would keep one fast-path promise in the live ticket and a different, more optimistic promise in the signoff ledger.

## Focused validation

- `tests/test_runtime_state_cache.py::test_runtime_state_cache_records_dispatch_probe_observation`
- `tests/test_runtime_acceptance_contract.py::test_runtime_acceptance_contract_detects_latency_attention_drift`
- `tests/test_macro_runtime_board_json_cli.py::test_macro_runtime_board_json_stales_signoff_when_runtime_probe_latency_goes_over_budget`
- `tests/test_macro_runtime_board_json_cli.py`
- `tests/test_primary_macro_work_ticket_cli.py::test_primary_macro_work_ticket_prefers_acceptance_after_proof_is_current`
