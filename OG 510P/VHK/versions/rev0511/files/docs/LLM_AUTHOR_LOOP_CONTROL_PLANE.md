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
That checked gate is now intentionally coupled to resident-runtime latency attention as well as recorder/replay debt, so a reachable-but-sluggish warm daemon is treated as a runtime-health blocker, not a green light with a footnote.

The generated stack-level helpers deliberately collapse that flow:

- `next_action_json.sh` follows the author queue first, then reuses `primary_macro_work_ticket_json.sh` when the selected macro already has a better one-read handoff (for example a bounded live probe sample), then checks for current latest-dispatch evidence for that same selected macro before falling through to the selected macro's checked gate. Revision 0436 makes that selected-macro receipt read explicitly macro-scoped via `macro_latest_dispatch_json.sh <macro>`, so the selected lane stays correct even when some other macro emitted more recently. Revision 0442 adds the next fallback: when the narrower selected-macro gate/work-ticket lane is unavailable or only a generic `dispatch_or_run` answer, `next_action_json.sh` now reuses the bounded `runtime_handoff` already carried by `macro_runtime_board_json.sh`, and `stack_state_json.sh` now mirrors that same selected-macro runtime handoff explicitly.
Revision 0437 closes the next selected-lane leak: macro-scoped receipt evidence now keeps that same helper in its followup chain instead of drifting back to `latest_dispatch_json.sh`, and the dispatch-history board now names the project-global vs macro-scoped receipt lanes explicitly.
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
- `primary_macro_work_ticket`
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

`primary_macro_work_ticket` is the selected-macro traffic director layered above those sibling tickets. It keeps one bounded answer to *what lane comes next for this macro?* explicit: recorder first, cleanup before replay, replay before trust, durable signoff, resident-runtime repair, live probe inspection when the gate already knows the current desktop mismatch, or execute now. The point is not to hide the underlying tickets; it is to stop a private LLM from reopening five siblings and re-deriving the same priority order on every turn. The fused stack still carries the detailed tickets, but `primary_macro_work_ticket` turns them into one machine-readable handoff with one stage id, one source ticket id, one recommended command, and compact evidence/followup commands. Revision 0419 adds `bin/primary_macro_work_ticket_json.sh` as the direct extraction surface for that handoff, plus `bin/warm_runtime_ticket_json.sh` for the resident-runtime side of the same loop. Revision 0429 tightens the execute side of that promise again: the same ticket now also carries `latest_dispatch_handoff`, so the selected-macro loop can see whether the newest receipt is still current warm-runtime evidence for this macro. When that receipt is current and clean, the work ticket now points back to `latest_dispatch_json.sh` before suggesting another emit, which is a better fit for a warm resident service than reflexively dispatching again just because the gate is still green. Revision 0430 carries the same rule one layer higher: `next_action_json.sh` now also uses `latest_dispatch_json.sh` as part of its selected-macro execute triage, so the top-level helper can prefer `inspect_current_dispatch_evidence` over `ready_to_dispatch` when the newest receipt is already current resident evidence for the chosen macro. Revision 0431 finishes the same alignment on the per-macro gate itself: `macro_dispatch_gate_json.sh <macro>` now emits `inspect_current_dispatch_evidence` when the lane is still ready *and* the newest receipt for that macro is already current clean warm-runtime evidence, so the private-LLM/operator path no longer has to ignore a green gate just to avoid a redundant re-emit. Revision 0432 closes the next one-read gap on the blocked side: the work ticket now also carries `probe_handoff`, and when the checked gate is blocked on `desktop_state_mismatch` with a bounded live sample already available, it prefers that probe surface before generic execution triage. Revision 0433 carries the same rule one layer higher again: `next_action_json.sh` now consumes `primary_macro_work_ticket_json.sh`, so the top-level warm-runtime helper can also choose `inspect_live_probe_observation` instead of flattening the same macro back into a generic gate or execution recommendation. Revision 0434 adds the stale-receipt sibling of that same idea: when the newest same-macro receipt is still the most relevant artifact but is no longer current warm-runtime evidence, the selected-macro work ticket now routes to `latest_dispatch_json.sh` before falling back into generic execution repair, and `next_action_json.sh` reuses that handoff directly. Revision 0435 completes the remaining fallback path: `macro_dispatch_gate_json.sh <macro>` now also emits `inspect_stale_dispatch_evidence` on that branch, and the top-level helper can reuse that gate-level stale-receipt recommendation when the smaller selected-macro work-ticket helper is unavailable.

`warm_runtime_ticket` is the resident-service companion surface above all of those selected-macro tickets. It keeps one bounded answer to the stack-level runtime question explicit: helper health broken, session not attached, socket/service activation debt, watcher-contract drift, resident project-contract drift after macro edits, bounded probe latency over the fast-path budget, degraded-but-running warnings, or runtime ready with a selected-macro handoff already available. When the issue is stale resident project state, the generated stack now also exposes `reload_runtime_json.sh` so the private LLM can ask for a reload receipt instead of trusting a blind `reload && check` shell chain. When the issue is `reachable but slow`, the same ticket now makes that explicit instead of hiding it behind generic readiness, which keeps the warm lane honestly observable without reopening `status_runtime_json.sh`, `check_runtime_json.sh`, and `next_action_json.sh` separately just to recover whether the resident daemon is merely alive or actually fast enough for checked dispatch. The latest bounded probe observation is now also persisted into the runtime-state cache so durable runtime acceptance can stale on warm-path latency regressions instead of only on outright dispatch/session/contract drift. Revision 0425 makes that cache honesty stricter still: an *old* successful probe is no longer treated as enough proof for checked dispatch or durable signoff. The resident lane now distinguishes `fresh bounded proof`, `current latency attention`, and `stale probe -> refresh first`, which is a better fit for a warm session service that a private LLM is expected to trust without rereading raw helper output. Revision 0427 tightens the receipt side of the same promise: durable dispatch-history surfaces now treat *any* comparable bounded-probe result change as drift, so `ack_timeout -> invalid_ack` is no longer flattened into `same failure bucket, probably still current`.

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

Use that once one macro is actually under review. Revision 0446 makes that per-macro handoff structurally match the selected-macro work ticket on the parts that matter most for a private LLM: `execution.runtime_handoff`, `execution.latest_dispatch_handoff`, and a top-level `llm_workbench` now stay on the same macro-scoped read. That means “open this macro directly” and “open the currently selected macro” now share one bounded inspect/edit/review/execute contract instead of forcing the model to translate between two similar-but-not-identical surfaces.

Revision 0456 makes the mutation boundary explicit on both lanes too. `macro_author_loop_json.sh <macro>` and `primary_macro_work_ticket_json.sh` now project `authoring_boundary`, which names the checked-in macro YAML as the only canonical edit surface, classifies recorder review / runtime snapshots / receipt history as inspect-first surfaces, and keeps cleanup-apply / checked dispatch / direct run / runtime signoff on explicit actuation surfaces. That stops the private-LLM lane from drifting into hand-edits of generated wrappers, receipts, logs, or runtime cache artifacts just because they were the most recent files opened.

Revision 0457 adds the sibling rule that was still implicit: `lane_transition`. The same two helpers now also say when the model should leave the edit loop and what class of action comes next — capture recording, keep editing YAML, inspect probe/receipt evidence, repair the resident runtime, emit checked warm dispatch, use direct run, or record durable signoff. Each transition carries the current lane id, the likely next actuation kind/command, barrier ids, inspect-before-actuation commands, and verify-after-actuation commands so the private-LLM path can stop guessing when to switch from authoring into resident-runtime execution.

Revision 0458 adds `stage_completion`, the missing answer to *when is the current lane actually done?* The per-macro author loop and the selected-macro resident ticket now both project completion ids, completion summaries, `complete_when` / `still_open_when` lists, inspect-to-confirm commands, verify-after-completion commands, and the most honest completion command for the active lane. This matters most on the warm-receipt path: once replay proof is current and the newest resident receipt is current, the private-LLM lane can now stop treating `inspect_current_receipt_before_reemit` as the default forever-loop and switch to durable runtime signoff when that is the real bounded finish line.

Revision 0462 closes the remaining top-level recommendation gap on that same lane: `next_action_json.sh` still computed the right selected-macro handoff, receipt disposition, runtime repair, and signoff truth, but only exposed it clearly in sibling trace sections. The live `primary_action` recommendation now mirrors `selected_macro_handoff`, `stage_completion`, and `execution_cutover` directly, so a caller that only consumes the current recommended step still gets the same bounded inspect/repair/signoff contract the lower selected-macro surfaces already carry.
Revision 0463 tightens the identity of that same top-level answer. When the lower selected-macro contract already says the bounded state is `inspect_current_receipt_before_reemit`, `inspect_stale_receipt_before_runtime_reuse`, `repair_runtime_before_resident_dispatch`, or `signoff_from_current_proof`, `primary_action` now projects that cutover id/summary/command directly instead of sounding like a generic `dispatch_now` wrapper with the sharper truth hidden in sibling fields. Revision 0464 mirrors that projected top-level action identity into `stack_state_json.sh` helper metadata and `stack_state.sh`, so the fused resident snapshot keeps the same receipt/signoff/repair truth without making the caller reopen `next_action_json.sh` just to recover it.
Revision 0465 closes the discoverability gap on that same contract. `control_plane.helper_surface_contracts.next_action_json.contract.top_level_projection` now states the projection rule and the mirrored field families explicitly, while `control_plane.helper_surface_contracts.stack_state_json.contract.mirrored_next_action_projection` declares that the fused resident snapshot preserves the same projected top-level action identity in both the live `next_action` payload and `sources.helpers.next_action_json`. Downstream tools can now discover the projection contract from one control-plane read instead of reverse-engineering helper payloads or docs first. Revision 0466 gives the smaller resident tickets the same self-description: `warm_runtime_ticket_json.sh` and `primary_macro_work_ticket_json.sh` now publish `selected_handoff_projection` contracts that declare the chosen handoff field path plus the preserved stage-completion and execution-cutover families. Practical effect: the private LLM can trust those compact ticket surfaces directly when the warm resident lane is already narrowed to receipt inspection, runtime repair, signoff, or execution fallback. Revision 0468 makes the compact human summaries match that same contract: `warm_runtime_ticket.sh` and `primary_macro_work_ticket.sh` now print a `selected_handoff_projection_*` digest and the helper-surface contract declares that digest too, so a private LLM or operator can sanity-check the chosen handoff charter from the small human summary without reopening JSON first.

Revision 0447 lifts that same choice into the top-level resident control plane. `next_action_json.sh` and `stack_state_json.sh` now project a chosen `primary_macro_llm_workbench`, so the top-level answer tells the private LLM whether to reopen `primary_macro_work_ticket_json.sh` or `macro_author_loop_json.sh <macro>` next. During review-heavy stages the chosen workbench stays on the selected-macro ticket; during execution-stage work it switches to the direct macro author loop, where receipt/runtime handoffs already carry the sharper truth.

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

`macro_runtime_board_json.sh` answers a different question: which macros are actually fit for the resident runtime now, which are only warm-runtime candidates, which still require direct-run because they prompt, and which still need recorder stabilization first. It now also mirrors the macro-scoped newest receipt lane for each item plus explicit project-global vs primary-macro receipt surfaces, and revision 0441 adds `runtime_handoff` so the same board can answer one bounded *what next?* question per macro: inspect the receipt lane, run checked dispatch, refresh replay proof, direct-run, or stabilize first. Revision 0444 carries that same bounded handoff into `warm_runtime_ticket_json.sh` / `warm_runtime_ticket.sh` when the resident runtime itself is healthy but the selected macro's execution ticket is still generic, so a private LLM can stay on the smaller resident-runtime surface without reopening the whole runtime board just to recover the sharper selected-macro action.

`macro_acceptance_ledger_json.sh` is the durable signoff lane. It does not hide raw review debt; it records which recorder/runtime concerns were intentionally reviewed and accepted so project-wide triage can separate active debt from tolerated debt.

`macro_dispatch_catalog_json.sh` answers the thin-dispatch question the other helpers only implied: for each macro, what is the current bus event, what is the minimal payload worth emitting, which generated wrapper should the resident stack call, and what explicit blocker explains why that macro is not dispatch-ready yet. `macro_author_loop_json.sh <macro>` now embeds that same checked-dispatch projection under `execution.dispatch_gate`, so once a private LLM has already focused on one macro it can decide `dispatch_now` / `direct_run_only` / `inspect_before_dispatch` / `stabilize_before_dispatch` without a second helper read. That embedded gate now also carries `dispatch_readiness.desktop_target`, which keeps the expected X11/i3 selector/workspace/title hint on the same per-macro execution lane instead of forcing another helper lookup when the blocker class is `desktop_state_mismatch`. Revision 0367 adds `dispatch_readiness.live_probe_hint` as the sibling run-truth surface: when the newest matching run already points at a likely failed live window/event/focus/i3 probe, the author loop can see that on the same per-macro execution read. Revision 0368 extends that hint with `observation`, so the LLM can inspect one bounded sample of what the failed wait/error actually observed before deciding whether to re-run, stabilize, or revise. Revision 0369 adds `repair_action`, so the same per-macro execution surface now also says which single command best advances the lane next instead of forcing the LLM to infer a repair command from blocker class plus followups. Revision 0446 closes the remaining parity gap between the selected-macro and direct-macro lanes: the per-macro author loop now also mirrors the newest receipt-evidence handoff, the current checked-dispatch/direct-run runtime handoff, and the same top-level `llm_workbench` guidance shape. In practice that means the private LLM can stay on one macro-scoped surface from first inspection through source edits, recorder review, checked dispatch, latest-receipt inspection, direct run, and durable runtime signoff.


## Revision 0366

The warm-runtime lane now preserves the exact blocked checked-dispatch text in durable receipts and `latest_dispatch_json.sh`. A private LLM no longer has to reopen wrapper stderr or guess from blocker ids alone when the resident service refused an emit. Revision 0426 makes the receipt side more honest too: `latest_dispatch_json.sh` and the dispatch-history board now compare the receipt's captured resident-runtime probe witness against the *current* cached probe posture, so `older epoch`, `probe refresh required`, `probe latency drift`, and `probe result drift` stop collapsing into one vague `runtime changed` bucket. Revision 0428 makes `latest_dispatch_json.sh` actionable as well: the newest receipt now carries `warm_runtime_evidence`, a one-read verdict that says whether the receipt is still current for the resident fast path and which concrete command should refresh runtime proof or reopen the current checked-dispatch gate before reuse.


The stack-level `next_action_json.sh` is no longer only a review-queue helper. It now lifts the primary macro from `macro_author_queue_json.sh` and, when useful, fuses that macro's checked-dispatch repair action from `macro_dispatch_gate_json.sh <macro>`. `stack_state_json.sh` now goes one step further and mirrors the selected macro's full `macro_author_loop_json.sh <macro>` payload beside its gate, latest run, contract, recorder review truth, and the new `primary_macro_work_ticket` so the warm resident lane can hand one fused per-macro contract to a private LLM/operator.

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


[rev0438] `next_action_json.sh` now carries both `latest_dispatch_json.sh` (project-global newest receipt) and `macro_latest_dispatch_json.sh <macro>` (selected-macro newest receipt) as explicit receipt scopes.

## Revision 0448: runtime surfaces now mirror the chosen macro-scoped workbench

The runtime board now carries a per-macro `llm_workbench` copied from the direct author loop, annotated with `source_id=macro_author_loop.llm_workbench` and `source_command=macro_author_loop_json.sh <macro>`. The warm-runtime ticket helpers now also mirror the fused stack's chosen `primary_macro_llm_workbench`.

Revision 0449 closes the remaining receipt-observability gap on that same lane. `macro_dispatch_history_board_json.sh` now carries a bounded per-macro receipt/history `llm_workbench`, the fused stack mirrors `primary_macro_dispatch_history_workbench`, and the warm-runtime ticket helpers print that receipt-scoped workbench next to the chosen runtime/author-loop workbench. Practical effect: a private LLM can open `warm_runtime_ticket_json.sh`, see resident-runtime posture and handoff, and still recover the selected macro's newest receipt-inspection loop without reopening the whole dispatch-history board or inferring it from posture fields alone.

## Revision 0450: one chosen selected-macro handoff, even on the small helpers

The control plane now treats `selected_macro_handoff` as a first-class contract on the smaller resident helpers too.

That handoff can legitimately point at four different surfaces:

- `llm_workbench` when recorder/cleanup/replay/acceptance debt is the real blocking loop
- `dispatch_history_workbench` when the selected macro already has a stale or current receipt that should be inspected before re-emitting
- `runtime_handoff` when the resident daemon is the thing that needs repair or inspection
- `execution_ticket` only when there is no sharper bounded receipt/runtime/review lane

The private LLM should no longer have to infer "receipt first" from posture fields on `warm_runtime_ticket_json.sh` or `primary_macro_work_ticket_json.sh`; the chosen handoff should already say so directly.



Revision 0459 adds `execution_cutover`, the missing operational sibling of `stage_completion`. `stage_completion` answers *when is this lane done?*; `execution_cutover` answers *what should happen before another execute is even attempted?* The per-macro author loop and the selected-macro resident ticket now both project cutover ids, summaries, receipt-disposition requirements, redundant resident-dispatch risk, repair/signoff readiness, and the most honest next command on the current posture. That closes the last major warm-receipt ambiguity: when a current resident receipt already exists, the control plane can now explicitly block another warm emit until that receipt has been dispositioned, and when replay proof plus current resident evidence already suffice, it can elevate straight to durable runtime signoff instead of treating one more checked dispatch as the default answer.

Revision 0461 carries that same contract up into the higher selected-macro bridge. `selected_macro_handoff` on the selected-macro work ticket and generated resident helpers now preserves `stage_completion`, `execution_cutover`, receipt-disposition, signoff, repair, and redundant-dispatch truth from the lower receipt/runtime surfaces. The selected-macro stage chooser also stops letting a merely current receipt outrank obvious resident-runtime degradation: when the warm session service is drifting, repair or refresh of the resident lane wins before receipt reuse or another checked dispatch.
