# Revision 0348 — macro review queue surface and fused stack visibility

Revision 0348 turns recorder/cleanup debt into a first-class resident-runtime surface instead of leaving it buried inside inventory rollups or ad hoc helper logic:

- added `vhk macro-review-queue-json <project>` as a project-level recorder/cleanup review queue with macro-specific review, cleanup, retime, and record commands
- generated warm-stack exports now include `bin/macro_review_queue_json.sh` as a stable control-plane helper for operators and a private LLM
- `next_action_json.sh` now consumes that queue directly, while preserving inventory-derived fallback logic so the resident stack remains robust if one helper is unavailable
- `stack_state_json.sh` now carries both `review_counts` and the full `macro_review_queue`, so one fused call can answer what recorder evidence is stale, missing, or brittle
- `stack_state.sh` now prints review-queue summary counts for humans without forcing them to inspect raw JSON
- tightened generated README/control-plane story so the recorder review queue is explicit flagship product truth for the i3/X11 warm-runtime lane
- added focused tests for the new queue command and for generated warm-stack helpers that consume and surface the queue
