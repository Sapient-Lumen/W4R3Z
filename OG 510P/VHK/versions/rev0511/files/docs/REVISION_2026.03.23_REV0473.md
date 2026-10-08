# Revision 0473 — replay target proof and unproven healthy posture

This revision carries X11/i3 target-authority proof into replay-time surfaces instead of leaving that proof only on checked-dispatch gates and receipts.

## What changed

- added replay-time `target_authority` classification to `macro_latest_run_json.sh <macro>` and `latest_run_health_json.sh`
- distinguished `current_replay_target_authority`, `weak_replay_target_authority`, `replay_target_mismatch_observed`, `stale_replay_target_authority`, and `no_explicit_target_authority_contract`
- added replay-board posture `verified_recent_target_unproven` for healthy runs that still lack current target proof for an explicit selector contract
- updated `macro_latest_run_json.sh <macro>` so the suggested next step prefers target-proof inspection when the newest healthy run is still target-unproven
- mirrored latest-run target-authority quick fields into `macro_runtime_board_json.sh` latest-run context
- added focused tests for current replay target proof and target-unproven healthy replay posture

## Why this matters

The flagship VHK lane is not just "a run succeeded recently"; it is "the resident i3/X11 system recently proved the correct target and is still safe to reuse that proof." This revision moves the replay surfaces closer to that standard without widening scope into secondary Linux-native lanes.
