# Revision 0401 — resident project-contract drift is now first-class

Date: 2026-03-22

## What changed

- added `src/vhk/project/runtime_contract.py`
- the internal `vhk.runtime.probe` acknowledgment now carries a digest of the
  daemon's loaded project contract
- `check_runtime_json.sh` now computes the expected project contract digest from
  disk and compares it against the live daemon's digest
- `dispatch_path_summary` now exposes:
  - `runtime_contract_in_sync`
  - `expected_runtime_contract_digest`
  - `daemon_runtime_contract_digest`
- `warm_runtime_ticket` now routes project-contract drift to a bounded reload
  handoff:
  - `status_id = reload_runtime_for_project_contract`
  - `route_id = runtime_contract_then_reload`
- `stack_state.sh` and fused helper metadata now surface that drift directly
- added targeted tests for the probe summary and stack routing

## Why it matters

The resident daemon can stay alive across macro edits. That is good for latency,
but it means “daemon answered” is still not enough proof for an LLM-driven edit
loop. The warm stack now proves whether the daemon that answered is actually
serving the same project contract that is on disk right now.

That keeps the i3/X11-first lane honest:

- restart when the daemon is attached to the wrong session
- restart when the watcher contract is wrong
- reload when the daemon is healthy but stale relative to current macro source

## Result

The resident runtime is now easier to trust after local or LLM-authored edits,
and the fused stack can recommend a narrower repair than a full restart when the
live service simply needs to reload current project state.
