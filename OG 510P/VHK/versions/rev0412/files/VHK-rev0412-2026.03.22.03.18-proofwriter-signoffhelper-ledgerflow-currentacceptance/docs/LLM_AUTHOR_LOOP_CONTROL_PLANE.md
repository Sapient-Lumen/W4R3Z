# LLM author-loop control plane

## Scope

This spec is only about the flagship VHK lane:

- i3 on X11
- thin emit/dispatch paths
- a session-bound warm runtime
- recorder -> cleanup -> replay -> inspect
- a private LLM editing checked-in macro source

It is not a broad Linux-native control-plane promise.

## Decision

The canonical project-wide triage handoff for a private LLM is:

```bash
macro_author_queue_json.sh
macro_replay_board_json.sh
macro_runtime_board_json.sh
macro_acceptance_ledger_json.sh
macro_dispatch_catalog_json.sh
```

Then use `macro_dispatch_gate_json.sh <macro>` or `dispatch_macro_checked.sh <macro>` when one macro is about to emit through the resident runtime.

The generated stack-level helpers deliberately collapse that flow:

- `next_action_json.sh` follows the author queue first, then the selected macro's checked gate.
- `stack_state_json.sh` is the one-read selected-macro handoff for the warm i3/X11 lane.

That fused stack now carries these selected-macro surfaces directly:

- `primary_macro_command_palette`
- `primary_macro_execution_brief`
- `primary_macro_consistency`
- `primary_macro_repair_recipe`
- `primary_macro_probe_observation`
- `primary_macro_execution_ticket`
- `primary_macro_recording_ticket`
- `primary_macro_cleanup_ticket`
- `primary_macro_replay_ticket`
- `primary_macro_acceptance_ticket`
- `warm_runtime_ticket`
- `startup_handoff_witness`
- `startup_handoff_repair_ticket`
- `primary_macro_latest_dispatch`
- `primary_macro_review_queue`
- `primary_macro_latest_run`
- `primary_macro_contract`
- `primary_macro_recording`
- `primary_macro_entrypoints`
- `primary_macro_replay_board`
- `primary_macro_runtime_board`
- `primary_macro_dispatch_history`
- `primary_macro_dispatch_catalog`

`primary_macro_repair_recipe` is intentionally small and bounded. It now also carries `focus_id`, `source_blocker_class_id`, and `evidence_commands`, so the private LLM can tell whether the selected macro is primarily a recorder-contract problem, a live desktop-target mismatch, a run-proof gap, a direct-run macro, or a ready warm-dispatch candidate without reopening helpers. It still stays short enough to avoid turning the resident control plane into a planner.

`primary_macro_probe_observation` is the companion observability surface. When the selected macro already has a bounded live-probe sample, the fused stack now carries the probe id, wait kind, observation summary, observed X11/i3 facts, expected desktop target, and the first inspect command to run. That keeps the warm lane one-read even when the real question is not *what command next?* but *what did the failing live wait actually see?*

`primary_macro_execution_ticket` is the execute-handoff surface layered on top of that diagnosis lane. It keeps the selected macro's actual execution route explicit: checked warm dispatch, direct run, inspect first, or repair first. It stays bounded by carrying one recommended command plus compact preflight commands, verify commands, and the warm-lane route contract when dispatch is the honest path.

`primary_macro_recording_ticket` is the recorder-side companion surface. It keeps the selected macro's honest recording route explicit too: record first, re-record after source edits, inspect recorder/source drift, or review exact/title/workspace segments before cleanup or warm dispatch claims. It stays bounded by carrying one recommended recorder command plus compact evidence and followup commands.

`primary_macro_cleanup_ticket` is the source-mutation companion surface between recorder and replay truth. It keeps the selected macro's honest cleanup route explicit: record before cleanup when recorder truth is stale, reconcile recorder/source drift before touching YAML again, review cleanup diffs when exact/title/workspace pressure is still present, or skip cleanup because the selected macro is already clear enough to move on. It stays bounded by carrying one recommended cleanup-or-proceed command plus compact evidence and verification commands.

`primary_macro_replay_ticket` is the replay-proof companion surface between cleanup and execute handoff. It keeps one bounded answer to the selected macro's replay question explicit: record before trusting replay again, review recorder drift before reusing a healthy run, rerun after an X11/i3 session change when the latest healthy proof was captured on a different `DISPLAY`/`I3SOCK`, inspect the newest warned or failed matching run, mint fresh proof with a direct run, or proceed to the execute ticket because replay proof is still verified. It stays bounded by carrying one recommended replay command plus compact evidence and verification commands.

`primary_macro_acceptance_ticket` is the durable-signoff companion surface layered after cleanup, replay, and execution. It keeps one bounded answer to the selected macro's acceptance question explicit: repair before signoff when stack signals still contradict each other, settle cleanup debt first, mint or refresh replay proof first, or treat the macro as ready for signoff and carry a compact ledger-update handoff with the current runtime posture, current proof-contract digest, the current resident-runtime epoch/runtime-contract witness, the current desktop-session digest, and a suggested acceptance entry. That keeps a private LLM from reopening the acceptance ledger just to recover the obvious next signoff move. The warm stack now also carries `record_runtime_acceptance.sh`, so the model can write the current proof-bound runtime signoff explicitly instead of only getting a ledger-update sketch.

`warm_runtime_ticket` is the resident-service companion surface above all of those selected-macro tickets. It keeps one bounded answer to the stack-level runtime question explicit: helper health broken, session not attached, socket/service activation debt, watcher-contract drift, resident project-contract drift after macro edits, degraded-but-running warnings, or runtime ready with a selected-macro handoff already available. When the issue is stale resident project state, the generated stack now also exposes `reload_runtime_json.sh` so the private LLM can ask for a reload receipt instead of trusting a blind `reload && check` shell chain. That keeps the warm lane itself honestly observable without reopening `status_runtime_json.sh`, `check_runtime_json.sh`, and `next_action_json.sh` separately just to recover whether the resident daemon really reloaded current source.

`startup_handoff_witness` keeps the next-login owner question equally bounded, and `startup_handoff_repair_ticket` turns that witness into one honest owner-fix handoff for the same stack: hide the duplicate autostart bridge when the user unit should stay primary, unmask/enable the user-unit owner when startup drifted or disappeared, or skip startup repair because ownership is already current. That keeps the private-LLM lane on one fused i3/X11 service story instead of bouncing between install docs and helper output.

Use that set first when the question is either *which macro should I open next?* or *what can the resident runtime emit right now without reopening per-macro contracts?*

Once one macro is under review, jump to its own latest-run surfaces before falling back to project history:

```bash
macro_latest_run_json.sh <macro>
macro_report_latest.sh <macro>
macro_trace_latest.sh <macro> [out.json]
```

The canonical per-macro handoff is still:

```bash
macro_author_loop_json.sh <macro>
```

Use that once one macro is actually under review.

Those helpers are intentionally fused. Together they carry the pieces that were previously spread across several helpers:

- project-wide queue rank plus preferred author-loop, run, dispatch-gate, and latest-run diagnostics entrypoints
- project-wide runtime posture and accepted-vs-active debt
- one project-wide replay board with per-macro latest-run posture so replay truth stops depending on the project's single latest run
- one project-wide thin-dispatch catalog with current bus event, minimal payloads, wrapper commands, and dispatch blockers
- editable source metadata and review commands
- recorder-side evidence and freshness
- per-macro review debt
- invocation and dispatch contract
- latest-run scope and health when the newest run belongs to the same macro
- direct per-macro report/trace jump points for that macro's newest matching run
- one recommended next step
- queue-visible dispatch pressure for repeated checked-dispatch blocks and unresolved forced overrides, now split by contract debt vs live desktop-state mismatch vs missing clean run proof when receipts make that clear

## Why this exists

The flagship lane already had strong building blocks, but the project-level and per-macro LLM story was still too fragmented. A private LLM often needed to reopen:

- `macro_source_json.sh`
- `macro_recording_json.sh`
- `macro_contract_json.sh`
- `latest_run_json.sh`
- `latest_run_health_json.sh`

just to answer two simple questions: *which macro should I open next?* and *what should I do next for that macro?*

The fused queue + loop pair keeps the checked-in source authoritative while reducing control-plane churn.

## Non-claims

- The fused helper is advisory. It does not mutate source by itself.
- Recorder review debt is not automatic proof that replay must fail.
- Latest-run health is only treated as macro-specific when the newest run belongs to the same macro.

## Next-step policy

The helper chooses one recommended next step in this order:

1. record first when recorder evidence is missing
2. review or refresh recorder evidence when freshness drift exists
3. review brittle exact/title-bound segments before widening scope
4. inspect the newest failing or warning-bearing run when it belongs to the same macro
5. otherwise execute the current macro so latest-run truth actually applies to it

## Execution preference

- interactive macros prefer direct run
- non-interactive macros prefer warm-runtime dispatch

That keeps interactive prompting honest while still favoring the resident runtime for cheap non-interactive dispatch.

## Queue policy

`macro_author_queue_json.sh` ranks macros by the same next-step policy used inside the per-macro author loop, then applies dispatch-pressure escalation for warm-runtime macros whose checked-dispatch history is repeatedly blocked or still depends on an unresolved forced override. Repeated blocks now carry a more specific attention id when receipts say the dominant cause is contract debt, live desktop-state mismatch, or missing clean run proof. Revision 0369 also makes that queue more actionable by reusing the gate-level `repair_action` command instead of bouncing attention back to a generic author-loop read. That keeps execute-lane triage honest without letting dispatch observability outrank missing recorder evidence or active cleanup debt. It remains advisory triage, not a lock or scheduler.

`macro_replay_board_json.sh` answers the replay-proof question first: for each macro, what does its own newest matching run say right now? That keeps per-macro truth from drifting toward whichever macro ran most recently.

`macro_runtime_board_json.sh` answers a different question: which macros are actually fit for the resident runtime now, which are only warm-runtime candidates, which still require direct-run because they prompt, and which still need recorder stabilization first.

`macro_acceptance_ledger_json.sh` is the durable signoff lane. It does not hide raw review debt; it records which recorder/runtime concerns were intentionally reviewed and accepted so project-wide triage can separate active debt from tolerated debt.

`macro_dispatch_catalog_json.sh` answers the thin-dispatch question the other helpers only implied: for each macro, what is the current bus event, what is the minimal payload worth emitting, which generated wrapper should the resident stack call, and what explicit blocker explains why that macro is not dispatch-ready yet. `macro_author_loop_json.sh <macro>` now embeds that same checked-dispatch projection under `execution.dispatch_gate`, so once a private LLM has already focused on one macro it can decide `dispatch_now` / `direct_run_only` / `inspect_before_dispatch` / `stabilize_before_dispatch` without a second helper read. That embedded gate now also carries `dispatch_readiness.desktop_target`, which keeps the expected X11/i3 selector/workspace/title hint on the same per-macro execution lane instead of forcing another helper lookup when the blocker class is `desktop_state_mismatch`. Revision 0367 adds `dispatch_readiness.live_probe_hint` as the sibling run-truth surface: when the newest matching run already points at a likely failed live window/event/focus/i3 probe, the author loop can see that on the same per-macro execution read. Revision 0368 extends that hint with `observation`, so the LLM can inspect one bounded sample of what the failed wait/error actually observed before deciding whether to re-run, stabilize, or revise. Revision 0369 adds `repair_action`, so the same per-macro execution surface now also says which single command best advances the lane next instead of forcing the LLM to infer a repair command from blocker class plus followups.


## Revision 0366

The warm-runtime lane now preserves the exact blocked checked-dispatch text in durable receipts and `latest_dispatch_json.sh`. A private LLM no longer has to reopen wrapper stderr or guess from blocker ids alone when the resident service refused an emit.


The stack-level `next_action_json.sh` is no longer only a review-queue helper. It now lifts the primary macro from `macro_author_queue_json.sh` and, when useful, fuses that macro's checked-dispatch repair action from `macro_dispatch_gate_json.sh <macro>`. `stack_state_json.sh` now goes one step further and mirrors the selected macro's full `macro_author_loop_json.sh <macro>` payload beside its gate, latest run, contract, and recorder review truth so the warm resident lane can hand one fused per-macro contract to a private LLM/operator.

- The fused stack snapshot now carries the author-queue-selected macro's project-board rows (`primary_macro_replay_board`, `primary_macro_runtime_board`, `primary_macro_dispatch_history`, `primary_macro_dispatch_catalog`) in addition to its per-macro helpers. That keeps the private-LLM lane closer to a one-read inspect/decide/dispatch loop.

- The fused stack snapshot now carries `primary_macro_acceptance`, letting the private LLM see accepted review issue codes, incomplete acceptance debt, and runtime acceptance posture for the selected macro without a separate ledger read.

- The fused stack snapshot now also carries `primary_macro_acceptance_ticket`, so the same one-read handoff can tell whether the selected macro should repair, clean up, refresh replay proof, or simply review/update the durable acceptance ledger.


## Dispatch runtime witness

When the private LLM reviews warm dispatch history, it must now distinguish
three cases instead of flattening them together:

- the latest receipt is current for the macro/dispatch contract
- the latest receipt is stale because the macro/dispatch contract changed
- the latest receipt is stale because the resident daemon epoch changed

The second case is source debt. The third case is resident-runtime drift. Those
should lead to different next steps even when both are surfaced as "refresh
dispatch proof" work.

Warm-dispatch receipts are also session-bound now: the control plane should treat a receipt from another `DISPLAY`/`I3SOCK` session as stale proof that needs a fresh checked dispatch.


Revision 0409 also tightens durable signoff for the private-LLM lane: `current_runtime_acceptance_contract` now includes warm-dispatch history posture/attention, so the model can see when a once-accepted macro must be re-signed because the resident dispatch lane is now blocked, session-stale, runtime-stale, or contract-stale. Revision 0410 adds the cached resident-runtime witness too, so the model can see when a warm-service reload/restart itself invalidated durable signoff even before another receipt exists. Revision 0411 adds the current desktop-session digest too, so the model can tell that a macro accepted on one `DISPLAY`/`I3SOCK` binding must be re-signed after a desktop-session move even if the resident daemon and dispatch history have not yet been refreshed.
