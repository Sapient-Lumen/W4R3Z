# REV0353 — runtime board for resident dispatch triage

- added `vhk macro-runtime-board-json <project>` as a project-wide execution-posture surface for the resident i3/X11 lane
- generated `bin/macro_runtime_board_json.sh` in the flagship warm-runtime stack
- fused runtime-board summary, primary macro, and macro list into `stack_state_json.sh` / `stack_state.sh`
- made runtime posture explicit as `warm_dispatch_ready`, `warm_dispatch_candidate`, `direct_run_only`, or `stabilize_first`
- tightened docs so the private-LLM loop is now: author queue for triage, runtime board for execution posture, author loop for one macro
- backfilled `next_action_trace.selected_action_id` when the next-action helper only returns `primary_action`, so fused state stays self-describing
