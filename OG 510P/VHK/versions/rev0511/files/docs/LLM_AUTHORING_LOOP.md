# LLM authoring loop

VHK now treats the private-LLM loop as a first-class X11/i3 workflow, not an afterthought on top of `run` and `dispatch`.

## Preferred loop

0. Start with `next_action_json.sh` or `stack_state_json.sh` on the generated warm stack when you need runtime truth plus the current recorder-review queue; use `control-plane.json` to distinguish editable source, generated review surfaces, runtime snapshots, and actuation entrypoints before choosing a command
1. When the question is which macro deserves attention next, open `macro_author_queue_json.sh` first so project-wide triage comes from one ranked surface instead of ad hoc helper merging
2. When the question is which recorded or runtime concerns are already signed off, open `macro_acceptance_ledger_json.sh` before re-raising already-accepted debt
2. Once one macro is chosen, open `macro_author_loop_json.sh <macro>` so source, recorder evidence, review debt, invocation, latest-run posture, runtime posture, and dispatch-history posture stay fused on one lane
3. Discover macro source with `macro_source_json.sh <macro>` or `vhk macro-source-json <project> <macro>`
4. Record or edit the YAML source directly
5. If the macro came from the recorder, inspect `macro_recording_json.sh <macro>` first so selector/segment evidence stays visible and so you know whether that recorder evidence is stale relative to the current macro source
6. When `next_action_json.sh` reports `macro_review_queue`, start with those macros before doing broad cleanup or retime passes; stale sidecars and exact/title-bound segments should be treated as explicit review debt, not hidden trivia, and the queue now carries stable `issue_code`, `status_label`, `action_lane`, and `evidence` fields so an LLM can triage instead of paraphrasing
7. Review the readable form with `render_macro.sh <macro>`
8. Lint the macro with `lint_macro.sh <macro>`
9. Review recorder cleanup changes with `optimize_macro.sh <macro>`
10. Apply cleanup with `apply_optimize_macro.sh <macro>` when the diff looks right
11. Retime replay with `retime_macro.sh <macro> --speed <multiplier> --in-place` when the recording is still too slow or too brittle
12. Validate the whole project with `validate_project.sh`
13. Execute through `run_macro.sh <macro>` for direct review or `dispatch_macro.sh <macro>` for the warm runtime
14. Inspect `latest_run_json.sh`, `latest_run_health_json.sh`, `latest_artifacts.sh`, or `stack_state_json.sh`

## Canonical per-macro handoff

For the flagship i3/X11 warm-runtime lane, `bin/macro_author_queue_json.sh` is now the preferred project-wide triage entrypoint, `bin/macro_runtime_board_json.sh` is the preferred execution-posture entrypoint, `bin/macro_acceptance_ledger_json.sh` is the durable signoff ledger, and `bin/macro_author_loop_json.sh <macro>` remains the preferred per-macro entrypoint. `bin/primary_macro_work_ticket_json.sh` is now the smaller first read when the question is only about the currently selected macro: it carries the chosen lane, editable source path, desktop-target summary, the minimum source/author/review entrypoints, and the minimal execute/signoff handoff (`warm_runtime_checked`, `warm_runtime_gate`, `direct_run`, `record_runtime_acceptance`, plus execution mode/signoff state) needed to move from triage into action. Together these helpers let a private LLM decide which macro to open next, which macro is actually dispatchable now, which concerns are already explicitly accepted, and then stay on one fused source/recording/review/execute lane without rediscovering the same relationships across multiple helpers on every turn. The per-macro author-loop payload now carries `execution.runtime_posture`, `execution.runtime_signoff`, `execution.dispatch_gate`, and `execution.dispatch_history` so the LLM can make the direct-run vs checked-dispatch decision without reopening either the project-wide runtime board or the per-macro gate helper first.
