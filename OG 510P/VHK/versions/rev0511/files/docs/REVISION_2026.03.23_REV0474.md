# Revision 0474 — replay ticket target-authority handoff

This revision keeps the replay lane aligned with the i3/X11-first target-authority story.

What changed:
- `primary_macro_replay_ticket` now carries `target_handoff` from the newest run's replay-time `target_authority`
- healthy-but-target-unproven replay proof now routes to `inspect_replay_target_authority` instead of generic replay-history review
- `macro_replay_board_json.sh` now points `verified_recent_target_unproven` at the bounded target-proof command itself
- fused helper metadata and `stack_state.sh` now mirror replay-ticket target status / command / match verdict

Why it matters:
- a private LLM or operator can now stay on the compact selected-macro replay lane and still get a precise answer to `what X11/i3 target proof is missing before I trust this replay again?`
