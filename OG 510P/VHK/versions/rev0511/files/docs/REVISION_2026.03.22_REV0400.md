# Revision REV0400 — dispatch watcher contract proof

## Summary

REV0400 tightens the warm-runtime control plane around a practical resident-service
question: not just whether `vhk busd` answered an internal round-trip probe, but
whether the daemon that answered is actually running the watcher contract that
the generated i3/X11 stack expects.

## What changed

- extended `src/vhk/project/runtime_dispatch_probe.py` so the summarized probe now compares:
  - expected watcher names from the generated stack
  - watcher names reported by the resident daemon
- generated `check_runtime_json.sh` now threads expected watcher names into the probe summary and reports:
  - `dispatch watcher contract drift` as a blocker when the live daemon is missing expected watcher(s)
  - `runtime.expected_watchers` in the emitted JSON
- `build_warm_runtime_ticket(...)` now has a dedicated bounded repair lane for watcher-contract drift:
  - `status_id: restart_runtime_for_expected_watcher_contract`
  - `route_id: watcher_contract_then_restart`
- fused `stack_state_json.sh` helper metadata now carries watcher-contract fields:
  - `dispatch_watchers_in_sync`
  - `dispatch_missing_expected_watchers`
  - `dispatch_expected_watchers`
  - `dispatch_daemon_watchers`
- `stack_state.sh` now prints watcher-contract summary lines for operator/LLM triage
- docs tightened to call out the watcher-contract proof explicitly

## Why it matters

The resident runtime can now distinguish four different states that used to blur together:

1. shell/session looks graphical
2. activation environment is restart-safe
3. current daemon is attached to the same X11/i3 session
4. current daemon is actually running the expected generated watcher contract

That last distinction matters because thin i3 emitters only stay trustworthy if
the warm daemon is not merely alive, but alive on the correct dispatch lane.
