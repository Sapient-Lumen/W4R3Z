# i3/X11 runtime stack

The current flagship runtime for VHK is:

**i3 binds -> `vhk-emit` -> socket-activated/session-bound `vhk busd` -> macro execution**

This is the repo's clearest answer to the warm-runtime question:

- keep hotkey activation cheap
- keep one resident VHK process warm while the desktop session is alive
- preserve ad hoc CLI runs for debugging, testing, and one-shots
- give a private LLM one stable control plane for authored scripts and dispatch

## Generate the stack

```bash
vhk gen-i3-busd-stack /path/to/project --watcher hotkeys

# Developer-tree / uninstalled repo use
vhk gen-i3-busd-stack /path/to/project --watcher hotkeys   --vhk-cmd /path/to/vhk-wrapper.sh   --vhk-pythonpath /path/to/repo/src
```

This writes a small handoff tree. The generated `control-plane.json` now makes three repo-wide contracts explicit in machine-readable form too: the flagship product lane, the preferred private-LLM authoring loop, and the X11 session-activation sync contract for the warm runtime.


- `systemd-user/<unit>.socket`
- `systemd-user/<unit>.service`
- `i3/vhk-busd.conf`
- `README.md`
- `control-plane.json`
- `bin/list_macros.sh`, `bin/macro_inventory_json.sh`, `bin/macro_source_json.sh`, `bin/macro_author_queue_json.sh`, `bin/macro_replay_board_json.sh`, `bin/macro_runtime_board_json.sh`, `bin/macro_dispatch_history_board_json.sh`, `bin/macro_acceptance_ledger_json.sh`, `bin/macro_author_loop_json.sh`, `bin/macro_entrypoints_json.sh`, `bin/macro_contract_json.sh`, `bin/render_macro.sh`, `bin/lint_macro.sh`, `bin/validate_project.sh`, `bin/optimize_macro.sh`, `bin/apply_optimize_macro.sh`, `bin/retime_macro.sh`, `bin/run_macro.sh`, `bin/dispatch_macro.sh`, `bin/record_macro.sh`, `bin/report_latest.sh`, `bin/latest_run_json.sh`, `bin/latest_dispatch_json.sh`, `bin/latest_runtime_repair_json.sh`, `bin/latest_run_health_json.sh`, `bin/latest_artifacts.sh`, `bin/trace_latest.sh`, `bin/history_runs.sh`, `bin/reload_runtime.sh`, `bin/reload_runtime_json.sh`, `bin/restart_runtime_json.sh`, `bin/stop_runtime.sh`, `bin/status_runtime.sh`, `bin/status_runtime_json.sh`, `bin/check_runtime_json.sh`, `bin/assert_runtime_ready.sh`, `bin/next_action_json.sh`, `bin/next_action.sh`, `bin/warm_runtime_ticket_json.sh`, `bin/warm_runtime_ticket.sh`, `bin/llm_session_ticket_json.sh`, `bin/llm_session_ticket.sh`, `bin/primary_macro_work_ticket_json.sh`, `bin/primary_macro_work_ticket.sh`, `bin/stack_state_json.sh`

- `stack_state_json.sh` should derive `primary_macro_execution_brief` from the already-loaded selected-macro slices instead of forcing callers to reconcile review queue, acceptance, gate, latest run, and dispatch history themselves.
- `stack_state_json.sh` should also derive `primary_macro_consistency` from those same selected-macro slices so contradictions (review debt vs ready-to-dispatch, acceptance vs blocked receipts, optimistic runtime vs replay posture) are explicit in the one-read warm-runtime snapshot.
- `stack_state_json.sh` should also keep one bounded cleanup handoff between the recording and replay tickets, so selected-macro source mutation can say record first, reconcile drift, review cleanup diff, or proceed without cleanup from the same one-read snapshot.
- `stack_state_json.sh` should also keep one bounded replay handoff beside the execute and recording tickets, so selected-macro replay proof can say record first, inspect warnings/failures, mint fresh proof, or proceed to checked dispatch without another helper hop.
- `stack_state_json.sh` should also keep one bounded acceptance/signoff handoff after replay and execute, so selected-macro durable-ledger work can say repair first, cleanup first, replay first, or ready-to-update-ledger without another helper hop.
- `stack_state_json.sh` should derive a `primary_macro_command_palette` for the author-queue-selected macro from already-loaded review queue, checked gate, latest run, author loop, and entrypoint data.
- This keeps the fused warm-runtime snapshot actionable in one read without adding another helper hop just to recover the right shell command.

- `bin/stack_state_json.sh` now also carries `primary_macro_latest_dispatch`, lifted directly from the selected macro's dispatch-history row. That keeps the one-read resident-runtime handoff aware of the selected macro's own newest blocked/emitted/forced receipt even when `latest_dispatch_json.sh` points at some other macro.
- `bin/stack_state_json.sh` now also carries `primary_macro_review_queue`, lifted directly from the selected macro's active review-queue buckets. That keeps the one-read resident-runtime handoff aware of whether the selected macro is still queued for recorder/segment cleanup and which review command should be used next.
`, `bin/stack_state.sh`, `bin/logs_runtime.sh`


## Stable operator + authoring + observability surface

The generated `bin/` scripts plus `control-plane.json` are now the preferred handoff surface once the warm
runtime exists. They now also carry an explicit `runtime_repair_recipe` on the warm-runtime ticket itself: one bounded object for repair family, repair scope, action bias, retry guard, and startup-owner secondary attention. That keeps resident-runtime repair honest for both operators and a private LLM when reload/restart has already failed recently. They make the flagship lane easier to drive from shell, i3, or a
private LLM without reconstructing raw `vhk` / `systemctl` / `journalctl` command
lines. `reload_runtime_json.sh` and `restart_runtime_json.sh` now persist bounded receipts under `build/runtime_control_receipts/`, `latest_runtime_repair_json.sh` surfaces the newest one-read repair outcome, and `stack_state_json.sh` carries that latest repair forward so the warm-runtime ticket can prefer inspect-first after a recent failed reload/restart instead of thrashing the resident lane with blind repeats. The fused stack now also carries `primary_macro_work_ticket`, which compresses the selected macro's recorder/cleanup/replay/acceptance/runtime/execute priority into one bounded handoff for the private-LLM/operator loop. Revision 0419 also adds `warm_runtime_ticket_json.sh` and `primary_macro_work_ticket_json.sh` so callers can read those two top tickets directly without reparsing the entire fused stack payload. Revision 0486 now makes `llm_session_ticket_json.sh` / `llm_session_ticket.sh` the declared first-entrypoint pair in the fused control plane too, so the private-LLM lane and the resident stack-state lane stop disagreeing about which surface should be opened first.
grammar on every turn.

- `bin/list_macros.sh` lists macros in the project through a stable project-pinned wrapper
- `bin/macro_source_json.sh <macro>` emits the editable source path plus preferred render/lint/validate commands for one macro, including recorder-side freshness/drift status
- `bin/macro_author_queue_json.sh` emits a ranked project-wide queue of which macro should enter the author loop next, including preferred entrypoints, next-step posture, and dispatch-pressure escalation when warm-runtime receipts show repeated blocks or unresolved forced overrides; that escalation now reuses the per-macro gate `repair_action` command instead of only pointing back at generic review surfaces
- `bin/macro_replay_board_json.sh` emits a project-wide replay-proof board keyed by each macro's own newest matching run
- `bin/macro_latest_run_json.sh <macro>` emits the newest matching run plus health for one macro so replay inspection can stay macro-scoped
- `bin/macro_report_latest.sh <macro> [extra report args...]` summarizes that macro's newest matching run directly
- `bin/macro_trace_latest.sh <macro> [out.json] [extra trace args...]` exports that macro's newest matching run directly into trace-viewer JSON
- `bin/macro_runtime_board_json.sh` emits a project-wide execution-posture board for the resident lane and now mirrors both project-global newest-receipt truth and the primary macro's macro-scoped newest receipt lane, plus a bounded `runtime_handoff` per item so callers do not have to infer the next checked-dispatch/direct-run/stabilize action from posture alone
- `bin/warm_runtime_ticket_json.sh` and `bin/warm_runtime_ticket.sh` now reuse that same bounded `runtime_handoff` when runtime is healthy but the selected macro's execution ticket is only generic, so the smaller resident-runtime ticket stays as action-specific as the runtime board
- `bin/macro_acceptance_ledger_json.sh` emits the durable project signoff ledger for recorder/runtime debt that has been explicitly accepted
- `bin/macro_dispatch_catalog_json.sh` emits the project-wide thin-dispatch catalog: current bus event, minimal payloads, generated wrapper commands, and explicit dispatch blockers
- `bin/macro_author_loop_json.sh <macro>` emits one fused author/review/execute contract for a single macro, including source, recorder evidence, per-macro review debt, latest-run context, runtime posture, dispatch-history posture, and a recommended next step
- `bin/macro_recording_json.sh <macro>` emits recorder sidecar paths, selector/segment summaries, and whether that recorder evidence is aligned with or stale relative to the macro source
- `bin/macro_entrypoints_json.sh` emits a machine-readable project-wide map of preferred author/review/run/dispatch/contract entrypoints so a private LLM can discover the safest route without scraping YAML
- `bin/macro_contract_json.sh <macro> [extra args...]` emits a machine-readable invocation contract for one macro so a private LLM can see presets, prompt forms, source metadata, and preferred run/dispatch shapes
- `bin/render_macro.sh <macro>` renders a readable review view for one macro
- `bin/lint_macro.sh <macro> [extra args...]` lints one macro through its resolved source path and emits JSON by default
- `bin/validate_project.sh [extra args...]` runs project-level lint/validation as JSON
- `bin/optimize_macro.sh <macro> [extra args...]` reviews cleanup/normalization changes for one macro with the recommended diff-oriented cleanup defaults
- `bin/apply_optimize_macro.sh <macro> [extra args...]` applies those recommended cleanup defaults back into the macro in place
- `bin/retime_macro.sh <macro> [retime args...]` exposes focused replay-speed retiming for one macro through the generated stack
- `bin/run_macro.sh <macro> [extra run args...]` runs a macro directly through the ad hoc CLI path while pinning the project root; it fails fast on unknown macro names
- `bin/dispatch_macro.sh <macro>` emits the configured hotkey dispatch event with a macro payload and fails fast on unknown macro names
- `bin/dispatch_macro_checked.sh [--force] <macro> [json-payload]` validates one macro against the current checked-dispatch gate, records an explicit receipt, and only emits when the resident-runtime lane says it is acceptable
- `bin/record_macro.sh <macro> [duration-ms]` records a new macro into the project using the recommended X11 cleanup / segmentation defaults
- `bin/report_latest.sh` summarizes the newest run event log for the project
- `bin/latest_run_json.sh` emits a machine-readable snapshot of the newest run plus its main artifact paths
- `bin/latest_dispatch_json.sh` emits the newest warm-runtime dispatch receipt so blocked, forced, and emitted thin-dispatch attempts stay observable without reopening logs

- Revision 0476 tightens durable signoff observability on the flagship lane: if `macro-runtime-accept --force` is used, the acceptance ledger, author loop, and runtime board now keep that row visible as `forced_review` with the blocked readiness that was bypassed. A forced signoff can still be a deliberate operator action, but it no longer masquerades as a clean current runtime acceptance after the contract matches again.
- Revision 0477 tightens the newer checked-dispatch override story on the same flagship lane: the newest receipt can now be `current_forced_dispatch_evidence`, which means the receipt is still current for inspection but still owes a clean checked-dispatch replacement before durable signoff is honest. The author loop, selected-macro work ticket, and runtime-signoff readiness now all preserve that distinction as `blocked_by_forced_dispatch_receipt` instead of flattening it back into generic current receipt truth.
- Revision 0478 finishes the next missing step in that same lane: current forced checked-dispatch evidence now gets its own receipt-stage disposition surfaces too. `macro_latest_dispatch_json.sh <macro>`, the author loop, and the selected-macro work ticket now expose `forced_receipt_disposition_and_clean_replacement_explicit` plus `inspect_forced_receipt_before_clean_replacement`, so the resident control plane no longer flattens a forced current receipt back into generic current-receipt review.
- blocked checked-dispatch receipts now preserve the exact refusal text returned by the checked wrapper, so the warm lane can be triaged from receipt truth instead of wrapper stderr
- blocked checked-dispatch receipts and `latest_dispatch_json.sh` now also preserve a likely failed live X11/i3 probe hint when the newest matching run already points at a concrete window/event/focus/i3 mismatch, plus one bounded snapshot of the actual failed live observation when it is cheaply available
- `bin/latest_run_health_json.sh` emits a machine-readable health verdict for the newest run so callers can tell whether it looks safe to build on
- `bin/latest_artifacts.sh` prints a compact artifact-oriented view of the newest run for human operators and shell tooling
- `bin/trace_latest.sh [out.json]` exports the newest run into trace-viewer JSON (default: `build/traces/latest.trace.json`)
- `bin/history_runs.sh` shows recent run history for the project
- `bin/reload_runtime.sh` sends the live-reload control event
- `bin/stop_runtime.sh` sends the clean-stop control event
- `bin/status_runtime.sh` prints enablement + compact user-unit state
- `bin/check_runtime_json.sh` emits a focused X11/i3 prerequisite snapshot with blockers and warnings for the flagship stack
- `bin/assert_runtime_ready.sh` exits nonzero when the flagship stack is not ready to use
- `bin/next_action_json.sh` emits a machine-readable recommended-next-step summary that combines prerequisite/runtime truth with latest-run health and a recorder-review queue derived from macro inventory drift/brittleness; it now lifts the primary macro from `bin/macro_author_queue_json.sh` and, when that macro is already in the execute lane, reuses `bin/macro_dispatch_gate_json.sh <macro>` so stack-level next actions can surface `ready_to_dispatch`, `use_direct_run`, or a more specific repair command instead of falling back to generic review heuristics. The live `primary_action` payload now also mirrors the chosen selected-macro handoff plus `stage_completion` / `execution_cutover`, so the top-level resident recommendation itself carries receipt-disposition, runtime-repair, and signoff truth instead of leaving that only in sibling trace fields.
- `bin/stack_state_json.sh` now also opens `bin/macro_dispatch_gate_json.sh <primary-macro>` when the author queue already names a primary macro, then carries that gate under `macro_dispatch_gate` plus helper diagnostics under `sources.helpers.macro_dispatch_gate_json` so the fused stack snapshot is a true one-read warm-lane handoff.
- `bin/stack_state_json.sh` now also opens `bin/macro_latest_run_json.sh <primary-macro>` when the author queue already names a primary macro, then carries that under `primary_macro_latest_run` plus helper diagnostics under `sources.helpers.macro_latest_run_json` so the same fused stack snapshot includes the selected macro's freshest replay truth and next-step health.
- `bin/stack_state_json.sh` now also opens `bin/macro_contract_json.sh <primary-macro>` when the author queue already names a primary macro, then carries that under `primary_macro_contract` plus helper diagnostics under `sources.helpers.macro_contract_json` so the same fused snapshot includes the selected macro's desktop target, invocation shape, and generated wrappers.
- `bin/stack_state_json.sh` now also opens `bin/macro_recording_json.sh <primary-macro>` when the author queue already names a primary macro, then carries that under `primary_macro_recording` plus helper diagnostics under `sources.helpers.macro_recording_json` so the fused snapshot includes selector/segment freshness truth for the exact macro the warm lane is about to inspect or execute. That recorder helper now also emits `recording.selector_summary`, so explicit top-level `when:` selectors and recorder-derived stable selectors share one bounded X11/i3 target summary.
- `bin/stack_state_json.sh` now also mirrors the selected macro's project-scoped entrypoints under `primary_macro_entrypoints` plus helper diagnostics under `sources.helpers.macro_entrypoints_json`, so the same fused snapshot carries concrete author-loop, direct-run, and warm-runtime commands for the macro the author queue chose.
- The fused stack helper now runs subordinate helpers with stdin closed (`DEVNULL`) so broken or half-configured environments are less likely to stall the resident control plane by accidentally prompting for input.
- `bin/next_action.sh` prints the same recommendation in a concise human/operator format
- `bin/logs_runtime.sh` tails recent user-journal entries for the stack

That split is deliberate: ad hoc `vhk ...` still exists, but the generated stack
now includes a **stable control + authoring surface** for the resident runtime.

`control-plane.json` makes that surface explicit for tools and for a private LLM, and now classifies each generated helper as canonical editable source, generated review surface, runtime snapshot, runtime actuation, or runtime observability so callers know which surfaces are authoritative to edit, which must be regenerated, and which must be refreshed from the live stack. `bin/status_runtime_json.sh` gives that same caller a stable JSON runtime-state snapshot, `bin/check_runtime_json.sh` gives it a focused X11/i3 prerequisite snapshot with blockers and warnings, `bin/latest_run_json.sh` gives it a machine-readable latest-run artifact snapshot, `bin/latest_dispatch_json.sh` gives it a machine-readable snapshot of the newest checked/raw dispatch attempt and the stored receipt path under `build/dispatch_receipts/`, `bin/latest_run_health_json.sh` gives it a machine-readable verdict about whether the newest run looks healthy enough to iterate on, `bin/macro_inventory_json.sh` gives it machine-readable macro/preset inventory plus rolled-up recorder-drift counts, `bin/macro_recording_json.sh <macro>` gives it recorder-side selector/segment evidence plus source-freshness truth for one macro, `bin/macro_entrypoints_json.sh` gives it a project-wide preferred run/dispatch/contract map, `bin/macro_author_queue_json.sh` gives it a ranked answer to which macro should enter the author loop next and now already carries the right run/dispatch-gate/latest-run entrypoints to act on that choice, `bin/macro_replay_board_json.sh` makes per-macro replay proof explicit, `bin/macro_latest_run_json.sh <macro>` plus `bin/macro_report_latest.sh <macro>` / `bin/macro_trace_latest.sh <macro>` keep replay inspection on one macro's own newest matching log, `bin/macro_runtime_board_json.sh` makes project-wide execution posture explicit, `bin/macro_dispatch_history_board_json.sh` keeps recent dispatch receipt truth explicit at project scope, `bin/macro_acceptance_ledger_json.sh` separates active debt from accepted debt, `bin/macro_dispatch_catalog_json.sh` makes thin-dispatch contract truth explicit at project scope, `bin/reload_runtime_json.sh` now proves both project-contract sync and post-reload daemon desktop-session sync, `bin/restart_runtime_json.sh` now proves whether a service restart really brought the daemon back on the current X11/i3 session with the expected watcher/runtime contract, and `bin/macro_author_loop_json.sh <macro>` now carries `execution.dispatch_gate` so the per-macro lane includes the same checked-dispatch verdict, contract, and force-override guidance instead of merely pointing back out to `bin/macro_dispatch_gate_json.sh`. `bin/stack_state_json.sh` now fuses the primary macro's checked gate, latest run, macro contract, per-macro author loop, and recorder-side review truth together, which keeps the private-LLM lane closer to a true one-read inspect → decide → execute handoff. `bin/macro_contract_json.sh <macro>` gives it the invocation contract for one specific macro, `bin/optimize_macro.sh <macro>` / `bin/apply_optimize_macro.sh <macro>` / `bin/retime_macro.sh <macro> ...` make cleanup and replay-speed revision first-class generated surfaces, `bin/next_action_json.sh` turns runtime/prereq truth, latest-run health, and recorder-review debt into a small recommended-next-step contract with `macro_review_queue` buckets (`stale_recording_sidecars`, `recording_newer_than_source`, `exact_segment_macros`, `title_segment_macros`), and that queue now includes stable issue taxonomy (`issue_code`, `status_label`, `severity`, `action_lane`) plus per-item evidence strings so triage can be automated without losing provenance. `bin/stack_state_json.sh` fuses those surfaces into one higher-level state snapshot that now carries both macro/preset/group/tag inventory and recorder-side drift counts plus the latest dispatch receipt, the project-wide preferred macro run/dispatch/contract routes, the ranked macro author queue, the replay board, the runtime board, the primary macro's checked-dispatch gate, the thin-dispatch catalog, per-helper diagnostics, and the projected top-level `next_action` identity (selected handoff, stage completion, execution cutover, and underlying generic gate) instead of forcing callers to merge those helper surfaces themselves. The selected-macro repair recipe inside that fused stack is now blocker-aware: it keeps a bounded repair focus, blocker class, evidence commands, and short next-step sequence instead of a single generic repair step. `bin/check_runtime_json.sh` now also distinguishes generic dispatch-path env drift from `dispatch daemon desktop session drift`, and `warm_runtime_ticket` can answer with `restart_runtime_for_daemon_desktop_session` when the resident daemon replies but its own X11/i3 desktop witness no longer matches the current shell. The same fused stack now also carries `primary_macro_probe_observation`, a compact selected-macro X11/i3 live-probe sample that preserves the freshest observed workspace/event/selector mismatch plus the first inspect command to run. It now also carries `primary_macro_execution_ticket`, a compact selected-macro execute handoff that makes checked warm dispatch vs direct run vs inspect/repair first explicit and keeps compact preflight + verification commands next to the recommended action. It also now carries `primary_macro_recording_ticket`, a compact selected-macro recorder handoff that makes record first vs re-record vs inspect drift vs review segments explicit and keeps compact recorder evidence/followup commands beside that recommendation. It now also carries `primary_macro_cleanup_ticket`, a compact selected-macro cleanup handoff that makes record-before-cleanup vs reconcile-drift vs review-cleanup-diff vs proceed-without-cleanup explicit and keeps compact cleanup evidence/verification commands beside that recommendation. It now also carries `primary_macro_acceptance_ticket`, a compact selected-macro signoff handoff that makes repair-before-signoff vs cleanup-before-signoff vs replay-before-signoff vs ready-for-signoff explicit and carries a bounded ledger-update handoff beside that recommendation. It also now carries `warm_runtime_ticket`, the stack-level resident-service handoff that compresses helper health, session readiness, socket/service activation debt, degraded warnings, and the selected macro's current execute handoff into one bounded runtime answer. The same fused stack now also carries `startup_handoff_witness`, a bounded startup-owner companion that keeps duplicate-start risk, autostart-only fallback, missing-owner states, and startup-owner drift visible beside the live runtime ticket instead of burying them in install docs or journal archaeology. It now also carries `startup_handoff_repair_ticket`, a bounded owner-fix companion that makes hide-autostart-bridge vs unmask/enable-user-unit-owner vs no-startup-repair-needed explicit without widening into a general installer. `bin/startup_handoff_status_json.sh` and `bin/startup_handoff_drift_json.sh` are the machine-readable helper surfaces behind those startup-owner tickets. `bin/assert_runtime_ready.sh` is the shell-friendly fail-fast gate for the live-session contract, `bin/latest_artifacts.sh` is the concise artifact-oriented human view, `bin/next_action.sh` is the concise human/operator next-step view and prints queue summaries for those review buckets, and `bin/stack_state_json.sh` / `bin/stack_state.sh` provide a one-shot fused stack-state snapshot for operators and a private LLM.

## Why this lane is preferred

Cold-starting the full `vhk` CLI on every hotkey is convenient but not the right
latency story for the main product. The stack above moves startup and watcher
ownership into one resident runtime while keeping bindings themselves simple.

`xdotool` can still be a useful X11 execution backend inside that runtime, but it
no longer has to compensate for avoidable startup overhead.

## Session binding

The generated units are **session-bound by default**. That means they install
under `graphical-session.target` and are meant to follow live desktop lifetime,
not pretend that every user login is the same thing as an active graphical
session.

Use `--no-session-bound` only when you intentionally want the older generic
user-service posture.

## Related commands

- `vhk gen-i3-config /path/to/project --via-bus`
- `vhk gen-vhk-busd-service /path/to/project`
- `vhk gen-vhk-busd-socket-units /path/to/project`
- `vhk emit-bus /path/to/project hotkey --data '{"macro": "name"}'`
- `vhk bus-reload /path/to/project`
- `vhk record-x11 --project /path/to/project --macro example --optimize`
- `vhk report --project /path/to/project --latest`
- `vhk trace --project /path/to/project --latest --out build/traces/latest.trace.json`


## Developer-tree bootstrap

When the stack is generated from an uninstalled repo checkout, pass `--vhk-pythonpath /path/to/repo/src`. The generated `bin/` wrappers and resident busd unit will export that path before invoking `vhk`, which keeps the flagship i3/X11 stack usable from a local `python -m vhk.cli` wrapper instead of requiring a prior installation step. `control-plane.json` records this under `runtime.vhk_cmd`, `runtime.vhk_pythonpath`, and `runtime.developer_tree_mode`.

- `stack_state_json.sh` should expose direct primary-macro slices from the already-loaded replay board, runtime board, dispatch-history board, and dispatch catalog. The fused state should not make LLM/operators rescan project-wide arrays once the author queue already chose the macro.

- `stack_state_json.sh` should lift the selected macro's acceptance ledger row directly out of `macro_acceptance_ledger_json.sh`, so the fused warm-runtime snapshot can distinguish active debt from explicit review/runtime signoff without rescanning the ledger. That fused stack should also keep one compact signoff ticket beside the raw acceptance row so a private LLM can tell whether the selected macro is still repairing or is ready to update the durable ledger.

- `control_plane.helper_surface_contracts` should describe the resident-runtime projection rules, not only helper paths and purposes. `next_action_json.sh` now declares its `primary_action` projection contract there, and `stack_state_json.sh` now declares that the fused snapshot mirrors the same projected top-level action identity into both `next_action` and `sources.helpers.next_action_json`.
- Revision 0466 extends that same machine-readable charter to the compact resident tickets: `warm_runtime_ticket_json.sh` and `primary_macro_work_ticket_json.sh` now declare `selected_handoff_projection` contracts so downstream tools can discover, from one control-plane read, that those smaller tickets already preserve selected-macro receipt disposition, runtime-repair, signoff, and fallback execution-handoff context. Revision 0467 carries the same charter inline on the live `warm_runtime_ticket` and `primary_macro_work_ticket` payloads themselves, so compact consumers do not have to reopen `control_plane.helper_surface_contracts` before trusting those handoff fields. Revision 0468 mirrors that charter into the compact human summaries and helper manifest too: `warm_runtime_ticket.sh` and `primary_macro_work_ticket.sh` now print `selected_handoff_projection_*` digest lines, and the helper-surface contracts advertise that inline-summary digest so the fused resident stack stays self-describing in both JSON and shell summary form.


## Checked dispatch target-authority lane

Revision 0471 adds one more compact resident-runtime surface: the checked dispatch gate now emits `target_authority`, a bounded X11/i3 target-proof witness derived from the macro's selector contract plus the freshest preserved live probe hint/observation.

It answers four operator/LLM questions directly:

- which selector authority is in force (`macro_when` vs recorder-derived selector)
- whether the latest preserved live proof matched or mismatched that selector
- whether the next action should be inspect-first, capture-live-proof, or gate-then-dispatch
- which bounded command is the sharpest next reopen for that target lane

The selected-macro work ticket mirrors the same witness as `target_handoff` and carries an inline `target_handoff_projection` contract so compact callers do not have to reopen the larger gate payload just to recover target proof, observed workspace/event context, or the next inspect command.


## Revision 0472: receipt-scoped target-authority evidence

The checked-dispatch lane now preserves X11/i3 target proof not just at gate time but also on the latest receipt surfaces. `latest_dispatch_json.sh` classifies `target_authority_evidence` from the stored gate snapshot, and `primary_macro_work_ticket` mirrors that as part of `latest_dispatch_handoff`. Selector comparison on dispatch receipts now canonicalizes omitted-vs-explicit false selector flags so the resident lane does not falsely mark a matched target receipt stale just because a selector serializer changed shape.


## Revision 0473: replay-time target-authority proof

The resident X11/i3 lane now keeps target-authority truth on replay-time surfaces too, not only on checked-dispatch gates and receipts. `macro_latest_run_json.sh <macro>` and `latest_run_health_json.sh` now classify `target_authority` for the newest run itself, including whether the run preserved a matched selector witness, only weak target proof, or no explicit target contract at all. `macro_replay_board_json.sh` now uses that signal to split a healthy-but-target-unproven replay from a fully current replay proof under `verified_recent_target_unproven`, and `macro_runtime_board_json.sh` mirrors quick target-authority fields beside the selected macro's latest-run context so compact resident callers can see whether the last replay actually proved the intended X11/i3 target before they ask the warm runtime to touch it again.


## Revision 0474: replay-ticket target-authority handoff

Revision 0473 taught the replay board and latest-run surfaces how to *describe* healthy-but-target-unproven runs, but the selected-macro replay ticket still tended to flatten that case into generic replay-history advice. Revision 0474 closes that remaining handoff gap. `primary_macro_replay_ticket` now preserves a compact `target_handoff` from the newest run's replay-time `target_authority`, routes to `inspect_replay_target_authority` when the newest healthy replay still lacks current selector proof, and mirrors that handoff through fused helper metadata and the compact `stack_state.sh` summary. `macro_replay_board_json.sh` now also points its `verified_recent_target_unproven` posture at the bounded target-proof command itself instead of defaulting back to history review.

## Revision 0475: durable signoff now requires explicit signoff readiness

The replay/receipt surfaces were already honest about target-proof debt by revision 0474, but durable runtime signoff still lacked one explicit boundary: a healthy replay plus a current receipt could still *look* signoff-ready on selector-bound macros even when the newest replay had only weak X11/i3 target proof. Revision 0475 closes that last acceptance gap. `macro_author_loop_json.sh <macro>` and `macro_runtime_board_json.sh` now carry `acceptance.runtime_signoff_readiness`, which names the exact blocker family (`blocked_by_replay_target_authority`, `blocked_by_dispatch_receipt`, `blocked_by_replay_proof`, and similar), the bounded next command, and whether signoff is actually ready now. `macro-runtime-accept` now respects that same readiness contract by default and refuses to write unless proof is ready, while still preserving an explicit `--force` escape hatch for deliberate operator overrides.


## Revision 0479: top-level next-action now preserves forced-receipt clean-replacement debt

The resident control plane could already distinguish a clean current checked-dispatch receipt from a forced current one on macro-scoped surfaces, but the top-level `next_action_json.sh` / `stack_state_json.sh` projection could still flatten that debt back into a generic execute wrapper. That was too soft for the flagship i3/X11 lane because a private LLM opening only the fused stack could still miss that the newest receipt was current enough to inspect yet still required a clean replacement before honest reuse or durable signoff.

Revision 0479 closes that gap by mirroring `clean_replacement_required` and the dedicated `inspect_forced_receipt_before_clean_replacement` cutover onto the projected top-level primary action, helper metadata, and compact shell summaries. Concrete win: one-read resident triage now stays explicit about *inspect forced receipt first, then mint a clean replacement* instead of bouncing back toward a generic warm dispatch suggestion.
