[rev0511] `latest_runtime_repair*` now carries the current runtime-instance receipt too, so repair-history triage can be checked against the same warm user-service identity as live runtime witness and the dedicated instance receipt.
[rev0510] `runtime_witness*` now carries the concrete `runtime_instance_receipt` too, so one live resident read can prove both warm-lane posture and the actual user-service instance behind it.
[rev0509] `runtime_instance_receipt*` now exposes one compact proof of the concrete warm user-service instance from runtime-state cache + user-unit state, tightening resident observability around the actual daemon being queried.
[rev0508] warm ticket, runtime witness, next-action, and one-read LLM ticket now prove they share one fused repair-witness + review-loop snapshot, tightening resident triage around both repair and replay truth.
[rev0507] warm-runtime ticket, runtime witness, and one-read LLM ticket now prove they share one compact recorder/cleanup/replay digest from a single resident snapshot, tightening review-loop observability across the warm X11/i3 lane.
[rev0506] 'warm_runtime_ticket*' now carries the same compact recorder/cleanup/replay digest as the runtime witness, fused stack, next-action lane, selected-macro ticket, and one-read LLM ticket.
[rev0505] 'runtime_witness*', 'stack_state*', and 'next_action*' now share the compact recorder/cleanup/replay digest, fixing a real generated runtime-witness bug and keeping live resident truth aligned with bounded triage.
[rev0503] 'primary_macro_work_ticket*' and 'llm_session_ticket*' now carry the same compact recorder/cleanup/replay receipt digest, so the selected-macro lane and the one-read private-LLM lane agree on the freshest review/apply/replay commands without reopening larger author-loop surfaces.
[rev0502] `llm_session_ticket_json.sh` now carries the newest post-repair runtime witness context, and `llm_session_ticket.sh` prints that digest inline, so a private LLM can recover live warm-lane truth, bounded edit/execute surfaces, and latest repair posture from one read.
[rev0501] `runtime_witness_json.sh` and `warm_runtime_ticket_json.sh` now preserve the newest post-repair runtime witness directly, and their human summaries print that digest inline, so live readiness, repair history, and bounded next action stay on one resident-runtime contract.
[rev0500] `next_action_json.sh` now carries the newest repair-history runtime witness directly on `primary_action.latest_runtime_repair_context` and in `recommendation_trace`, so bounded next-step selection can cite the same post-repair warm-lane truth as repair receipts, status, and fused stack.
[rev0499] `latest_runtime_repair_json.sh` now preserves the newest repair receipt's compact post-repair runtime witness, and `latest_runtime_repair.sh` prints that witness inline, so repair-history triage can compare the same warm-lane truth as reload/restart/status/stack.
- rev0498: repair receipts now persist a compact post-repair runtime witness so reload/restart outputs can be compared against the same warm-lane truth as status_runtime and stack_state.
# VHK — VisualHotKey for i3/X11-first desktop automation

VHK is an **AHK-shaped automation runtime** and the execution core for a future
**Pulover-style Linux macro studio**.

## Current product lane

VHK is deliberately optimized for one flagship lane:

- **desktop target:** i3 on X11
- **runtime target:** a **session-bound long-lived user service** with thin emit/dispatch paths
- **authoring target:** **record -> cleanup -> replay -> inspect -> refine**
- **advanced use case:** a **private LLM** that can author, revise, inspect, and execute VHK macros against a live desktop
- **secondary lane:** ad hoc `vhk ...` CLI runs for debugging, proof, and one-shot execution

Broad Linux-native ambitions, Wayland, portals, and app-native adapters are kept
only when they materially strengthen the X11/i3 core. Otherwise they are
secondary or vaulted. The shortest current repo-wide statement of that boundary
is `docs/FLAGSHIP_DATACUBE_2026.03.23.md`.

## Read this first

- `docs/ACTIVE_PRODUCT_CONTRACT_2026.03.22.md`
- `docs/FLAGSHIP_DATACUBE_2026.03.23.md`
- `docs/DATACUBE_2026.03.19_X11_FIRST.md`
- `docs/FLAGSHIP_RUNTIME_SPEC_2026.03.21.md`
- `docs/ARCHITECTURE.md`
- `docs/DECISION_2026.03.23_X11_I3_SHIPROOM_AND_LLM_BOUNDARIES.md`
- `docs/LLM_ONE_READ_SESSION_TICKET_2026.03.28.md`


## What is active right now

The repo's center of gravity is:

Revision 0485 makes the private-LLM lane itself one-read by default: the generated stack now exports `bin/llm_session_ticket_json.sh` and `bin/llm_session_ticket.sh`, a compact session ticket/digest that fuses resident-runtime readiness, selected-macro context, authoring boundary, and bounded next commands so the flagship X11/i3 loop no longer has to reopen `stack_state_json.sh`, `next_action_json.sh`, and the selected-macro surfaces just to recover the same edit/inspect/actuate contract.

Revision 0487 locks that one-read lane with executable generated-helper coverage: the repo now tests `bin/llm_session_ticket_json.sh` and `bin/llm_session_ticket.sh` against a stubbed fused stack snapshot, so the fast resident X11/i3 author loop is verified as an actual runnable surface instead of only a manifest contract.

Revision 0488 extends that executable-helper discipline to the other compact resident surfaces too: the repo now tests `warm_runtime_ticket_json.sh` / `warm_runtime_ticket.sh` and `primary_macro_work_ticket_json.sh` / `primary_macro_work_ticket.sh` against a stubbed fused stack snapshot, so the operator-facing warm-runtime and selected-macro tickets stay locked as runnable contracts beside the one-read LLM ticket.

Revision 0489 ties those compact ticket summaries back to the generated control plane itself: the repo now loads `control-plane.json`, seeds the stubbed fused stack from the manifest helper-surface contracts, and proves that `warm_runtime_ticket.sh` and `primary_macro_work_ticket.sh` print the same field-path/rule/digest contract that the resident control plane advertises.

Revision 0490 closes the same manifest/runtime drift on the one-read LLM lane: `llm_session_ticket.sh` now actually emits the `llm_session_`-prefixed digest that the manifest already declared, and the repo now proves that the generated LLM ticket helpers reflect the same entry-flow and digest contract that `control-plane.json` advertises.

Revision 0491 makes the selected-macro work ticket more honest about recorder/cleanup authoring: `primary_macro_work_ticket.sh` now prints an explicit `authoring_boundary_` digest for canonical source, recording review, cleanup review, cleanup apply, warm checked dispatch, direct run, and runtime acceptance, and the repo now proves those recorder/cleanup entrypoints stay aligned with the generated helper contract.

Revision 0492 aligns the one-read LLM ticket with the real selected-macro authoring boundary shape: it now reads `canonical_edit_surface`, `inspect_surfaces`, and `actuation_surfaces` instead of depending on the older `authoritative_inputs` shape, and its manifest-backed digest now carries recorder review, cleanup review, cleanup apply, direct run, and runtime-acceptance surfaces alongside the warm checked-dispatch lane.

Revision 0469 also makes two previously too-implicit rules explicit in-machine: `control-plane.json` now carries a flagship keep-vs-demote `change_filter`, plus a project-wide `surface_authority_contract` and named `entry_flows` so a private LLM can tell what is editable source, what is inspect-only, and which bounded lane to open next without scraping long prose docs.
Revision 0481 closes the adjacent startup gap in the flagship stack itself: `gen-i3-busd-stack` now exports the thin session/startup bridge helpers (`sync_session_activation_env.sh`, `verify_session_readiness.sh`, `verify_session_targets.sh`, `verify_startup_handoff.sh`, `start_user_session.sh`, and the fallback autostart desktop) and classifies them in `control-plane.json`, so the resident i3/X11 lane can actually perform the startup repair/bridge moves it already knew how to describe.

- fast warm dispatch from i3 bindings and generated wrappers
- reliable X11 window, focus, cursor, and workspace control
- recorder sidecars that preserve usable window/session context
- cleanup and replay proof that stay honest after source edits
- resident-runtime truth that stays honest after daemon reloads, restarts, desktop-session drift, and the subtler case where the live daemon answers but is still bound to the wrong X11/i3 desktop witness
- persisted bounded reload/restart receipts so the control plane can remember what repair was already attempted and whether it actually repaired the live session
- compact machine-readable control-plane surfaces for humans and a private LLM

Warm-runtime proof is intentionally multi-part:

- **live probe truth** proves that `vhk-emit -> socket -> resident busd` is reachable now
- **runtime-state cache truth** records the daemon epoch, watcher set, project contract digest, and the daemon's own desktop-session contract
- **dispatch receipts** are bound to both the macro/dispatch contract and the resident runtime witness they were emitted under
- **replay proof** and **durable acceptance** also go stale when the desktop session or resident runtime drifts

## Current operator / LLM entrypoints

Start with the generated i3/X11 stack surfaces:

- `bin/llm_session_ticket_json.sh`
- `bin/llm_session_ticket.sh`
- `bin/stack_state_json.sh`
- `bin/next_action_json.sh`
  - the top-level resident recommendation now also projects the chosen selected-macro handoff plus `stage_completion` / `execution_cutover` directly on `primary_action`, so callers that only consume the live next step do not have to rejoin sibling trace fields just to know whether receipt inspection, runtime repair, or durable signoff is the sharper move; revision 0463 also lets `primary_action` adopt the sharper cutover identity itself when the underlying gate answer is still a generic `dispatch_now` / `ready_to_dispatch` / `use_direct_run` wrapper, and revision 0464 mirrors that projected top-level action identity into `stack_state_json.sh` helper metadata and `stack_state.sh` so the fused resident snapshot itself preserves the same receipt/signoff/repair truth. Revision 0465 makes the helper-surface contract explicit too: `control_plane.helper_surface_contracts.next_action_json.contract.top_level_projection` now declares that projection rule and `control_plane.helper_surface_contracts.stack_state_json.contract.mirrored_next_action_projection` declares that the fused snapshot preserves the same projected identity in both `next_action` and `sources.helpers.next_action_json`. Revision 0466 extends that same self-description to the smaller resident tickets: `warm_runtime_ticket_json.sh` and `primary_macro_work_ticket_json.sh` now advertise explicit `selected_handoff_projection` contracts, so callers can discover from one control-plane read that those compact ticket surfaces already preserve receipt disposition, runtime repair, signoff readiness, and fallback execution-ticket context. Revision 0467 pushes that charter into the live ticket payloads too: `warm_runtime_ticket` and `primary_macro_work_ticket` now each carry an inline `contract.selected_handoff_projection`, so compact callers that only open those JSON tickets still get the same machine-readable handoff rules without reopening `control_plane.helper_surface_contracts` first. Revision 0468 carries that same charter into the compact human summaries: `warm_runtime_ticket.sh` and `primary_macro_work_ticket.sh` now print a one-line `selected_handoff_projection_*` digest, and the helper manifest advertises that inline-summary contract so operators and private-LLM loops can confirm the chosen receipt/repair/signoff semantics without reopening JSON. Revision 0470 makes the resident-runtime half equally explicit: `warm_runtime_ticket` now carries a bounded `runtime_repair_recipe` with repair family, scope, action bias, retry guard, and startup-owner secondary attention, so a private LLM can tell from one read whether to repair now, inspect a failed retry first, or follow the selected macro. Revision 0472 makes the newest checked-dispatch receipt equally explicit about X11/i3 target proof after the fact: receipt comparison now canonicalizes selector defaults instead of treating omitted vs explicit `false` selector flags as drift, `latest_dispatch_json.sh` now classifies `target_authority_evidence`, and `primary_macro_work_ticket` mirrors that receipt-scoped target handoff so an operator or private LLM can inspect the last observed target proof before re-emitting.
Revision 0471 does the same for checked X11/i3 targeting: `macro_dispatch_gate_json.sh <macro>` now carries a bounded `target_authority` witness that names the selector authority, the latest observed match/mismatch verdict, and the next inspect/verify command, and `primary_macro_work_ticket_json.sh` mirrors that as `target_handoff` with an explicit inline projection contract so the resident control plane can say not just *which macro next*, but *which focused X11/i3 target proof is in play before replay*. Revision 0473 carries that same X11/i3 target-proof discipline into replay-time surfaces: `macro_latest_run_json.sh <macro>` and `latest_run_health_json.sh` now classify `target_authority` for the newest run itself, `macro_replay_board_json.sh` now distinguishes a healthy run with weak target proof from a fully current replay proof, and the runtime board mirrors the same target-authority quick fields in `latest_run_context` so the resident control plane can tell whether the last replay actually proved the intended window/workspace contract before another checked dispatch.
Revision 0474 turns that replay-time target proof into an actual selected-macro handoff: when the newest replay is healthy but still target-unproven, `primary_macro_replay_ticket` now routes to `inspect_replay_target_authority` instead of generic history review, and the replay board itself now points at the bounded target-proof command so the resident lane keeps saying *prove the intended X11/i3 target first* instead of flattening back into broad replay advice.
Revision 0475 closes the adjacent acceptance gap: the macro author/runtime surfaces now expose `runtime_signoff_readiness`, durable runtime signoff is only treated as ready when replay proof is truly `verified_recent` *and* the newest checked-dispatch receipt is current, and `macro-runtime-accept` now refuses to write by default when the newest healthy replay still lacks current X11/i3 target proof unless the caller uses `--force`. That keeps “healthy replay” from drifting into misleading signoff on selector-bound macros while preserving an explicit override for deliberate operator judgment.
Revision 0476 closes the auditability gap that remained after that override was introduced: a runtime signoff written with `--force` now stays visible as `forced_review` until a clean non-forced replacement is recorded. The acceptance ledger, author loop, and runtime board now preserve `force_override`, the blocked readiness that was bypassed, and a clear `force_review_required` signal so a private LLM or operator cannot confuse an override-backed signoff with a fully current clean acceptance.
Revision 0477 makes the adjacent receipt lane equally honest: the newest checked-dispatch receipt can now be classified as `current_forced_dispatch_evidence`, which means the receipt is still current enough to inspect but was recorded with `--force` and still needs a clean checked-dispatch replacement before durable runtime signoff is honest. `macro_author_loop_json.sh <macro>`, the selected-macro work ticket, and runtime-signoff readiness now preserve that distinction instead of flattening it back into generic current receipt truth.
Revision 0478 tightens that same receipt lane one step further: current forced checked-dispatch evidence is no longer allowed to masquerade as a generic current-receipt *workflow* either. `macro_latest_dispatch_json.sh <macro>`, the author loop, and the selected-macro work ticket now give that case its own receipt-stage completion/cutover/handoff (`forced_receipt_disposition_and_clean_replacement_explicit` / `inspect_forced_receipt_before_clean_replacement`), so a private LLM can see from one resident snapshot that the receipt is current enough to inspect but still not clean enough to reuse or sign off.
Revision 0479 closes the remaining top-level projection gap above that lane: `next_action_json.sh`, `stack_state_json.sh`, and their compact text summaries now preserve `clean_replacement_required` and the dedicated `inspect_forced_receipt_before_clean_replacement` cutover directly on the projected primary action and selected-macro handoff trace, so the resident control plane no longer falls back to a generic dispatch wrapper when the honest next move is still *inspect forced receipt, then replace it cleanly*.
- `bin/macro_author_loop_json.sh <macro>`
- `bin/macro_dispatch_gate_json.sh <macro>`
- `bin/check_runtime_json.sh`
- `bin/reload_runtime_json.sh`
- `bin/restart_runtime_json.sh`
- `bin/latest_runtime_repair_json.sh`
- `bin/warm_runtime_ticket_json.sh`
- `bin/primary_macro_work_ticket_json.sh`
- `bin/macro_latest_dispatch_json.sh <macro>`

Revision 0458 adds one more rule that had still been implicit: `macro_author_loop_json.sh <macro>` and `primary_macro_work_ticket_json.sh` now also project `stage_completion`, a machine-readable answer to *when is this lane actually done?* That keeps the warm resident-runtime lane honest about when to stop editing, when to stop re-emitting, and when the sharper move is durable runtime signoff instead of another redundant checked dispatch. `stack_state_json.sh` now also carries `primary_macro_work_ticket`, a selected-macro handoff that collapses recorder/cleanup/replay/acceptance/runtime/execute priority into one bounded machine-readable ticket. Revision 0456 also makes the selected-macro source/inspection/actuation boundary explicit: `macro_author_loop_json.sh <macro>` and `primary_macro_work_ticket_json.sh` now carry `authoring_boundary`, a machine-readable rule that says edit checked-in macro YAML only, inspect generated review/receipt/snapshot surfaces read-only, and use explicit actuation helpers for cleanup apply, checked dispatch, direct run, or runtime signoff. `warm_runtime_ticket_json.sh` and `primary_macro_work_ticket_json.sh` extract the two highest-leverage tickets into smaller machine-readable surfaces when a caller does not need the full fused stack. The selected-macro work ticket now also carries the editable source path, desktop-target summary, the smallest useful source/author/review entrypoints, the minimal checked-dispatch/direct-run/runtime-signoff handoff, the newest receipt-evidence handoff, the freshest bounded live-probe handoff, and a stage-aware `llm_workbench` object with inspect-first, edit-loop, execute-when-clear, verify-after-change, and stop-condition guidance, so a private LLM can move directly from triage to edit/review/execute without reopening the whole stack. `macro_author_loop_json.sh <macro>` now carries that same bounded contract on the per-macro lane: it mirrors `execution.runtime_handoff`, `execution.latest_dispatch_handoff`, and a top-level `llm_workbench`, so opening one macro directly no longer requires bouncing back to the selected-macro ticket just to recover the same edit/review/execute loop. The project-wide runtime board now also mirrors macro-scoped receipt observability and a bounded per-macro `runtime_handoff`, so posture, newest selected-macro receipt evidence, and the next checked-dispatch/direct-run/stabilize action stay on one surface instead of forcing a hop back into the dispatch-history board just to inspect the right warm-lane receipt or infer the next move. Revision 0448 closes the last smaller-surface readability gap on that resident lane: `macro_runtime_board_json.sh` now also projects a per-macro `llm_workbench` copied from the direct author loop, and `warm_runtime_ticket_json.sh` / `warm_runtime_ticket.sh` now mirror the fused stack's chosen `primary_macro_llm_workbench`, so runtime posture, runtime handoff, and the bounded LLM edit/inspect/execute lane stay visible from the same resident-runtime surfaces. Revision 0449 carries the same bounded contract into the receipt-history lane itself: `macro_dispatch_history_board_json.sh` now projects a per-macro `llm_workbench`, `stack_state_json.sh` mirrors `primary_macro_dispatch_history_workbench`, and the warm-runtime ticket helpers carry that receipt-scoped workbench too, so the resident-runtime/control-plane surfaces can reopen the selected macro's newest receipt lane without making the caller rediscover it from posture fields alone. Revision 0450 makes the smaller selected-macro tickets explicit about which lane is actually sharper next: `primary_macro_work_ticket_json.sh` and `warm_runtime_ticket_json.sh` now carry a chosen `selected_macro_handoff` that can point at the receipt-history workbench, not just the execution or runtime surfaces. When stale resident evidence is the real blocker, receipt inspection now outranks generic durable-signoff repair. Revision 0451 carries that same chosen handoff up into `next_action_json.sh`, `next_action.sh`, `stack_state_json.sh`, and `stack_state.sh`: the top-level resident-runtime surfaces now project `primary_macro_selected_handoff` and trace when receipt/runtime inspection is the sharper thing to reopen than the generic macro `llm_workbench`. Revision 0452 closes the checked-dispatch sibling of that gap: `macro_dispatch_gate_json.sh`, `primary_macro_execution_ticket`, and the fused `stack_state_json.sh` gate snapshot now reuse the same receipt-first selected handoff and latest-receipt truth, so the checked dispatch lane no longer drifts back to a generic `dispatch_now` answer when the sharper move is to inspect the newest receipt first. Revision 0453 closes the smaller-ticket fallback that still remained above that lane: `primary_macro_work_ticket` now carries an explicit `execution_ticket_handoff`, and `next_action_json.sh` / `next_action.sh` now prefer that checked-dispatch handoff when the visible selected-macro ticket is only generic, so the resident control plane keeps reopening the newest receipt/runtime truth instead of flattening back into a generic dispatch answer. Revision 0454 closes the remaining divergence on the resident-runtime side of that same lane: `warm_runtime_ticket_json.sh` / `warm_runtime_ticket.sh` now also fall back to the checked-dispatch `execution_ticket_handoff` when their directly visible selected-macro handoff is only generic, and they expose both the chosen handoff basis and the execution-ticket fallback explicitly for observability. Revision 0442 now threads that same bounded handoff back into `next_action_json.sh` and `stack_state_json.sh` whenever the narrower selected-macro gate/work-ticket surfaces are missing or only generic, so the top-level resident-runtime lane can still stay selected-macro specific instead of falling back to a vague `dispatch_or_run` answer. Revision 0444 closes the remaining smaller-surface gap on the resident lane: `warm_runtime_ticket_json.sh` and `warm_runtime_ticket.sh` now prefer the runtime board's bounded selected-macro handoff when the execution ticket is only generic, and they expose whether that chosen handoff came from the runtime board or the execution ticket. The warm-runtime ticket now also treats `reachable but over-budget` as its own resident-service health state instead of folding it into generic readiness, and the latest bounded probe observation is now persisted into the runtime-state cache so durable runtime signoff can go stale when the resident fast path slows down. They answer:
The checked per-macro dispatch gate now honors that same latency attention state instead of only macro-local replay debt, so `dispatch_macro_checked.sh` and `macro_dispatch_gate_json.sh` stop claiming the warm path is ready when the resident daemon is reachable but too slow for the fast-path promise. Revision 0425 closes the next honesty gap: if the runtime-state cache only has an old successful probe, checked dispatch and durable signoff now treat that as `refresh runtime probe first` instead of pretending an old warm-path sample is still current. Revision 0426 extends that same honesty to dispatch receipts and history: the latest dispatch surfaces now stale when the current resident probe result, freshness, or latency posture no longer matches the witness captured with the newest receipt, so a private LLM does not mistake an old clean emit for current fast-path health. Revision 0427 tightens the probe-result part again: receipt currentness now tracks any comparable bounded-probe result change, not only a flip between success and failure families. Revision 0428 makes `latest_dispatch_json.sh` act on that truth instead of only describing it: the newest receipt now carries a compact `warm_runtime_evidence` verdict with `current`, `status_id`, and a concrete next command, so a private LLM can tell whether the receipt is still current resident evidence or whether it should reopen the warm-runtime ticket or current checked-dispatch gate first. Revision 0429 pulls that same receipt truth into `primary_macro_work_ticket`: when the selected macro already has a current clean warm-runtime receipt on the current resident lane, the work ticket now carries the receipt-evidence handoff directly and points to `latest_dispatch_json.sh` before recommending another emit, so the author loop stops defaulting to blind re-dispatch. Revision 0430 closes the remaining top-level helper drift: `next_action_json.sh` now also opens `latest_dispatch_json.sh` before trusting a green checked gate, so the global operator/LLM surface can recommend inspecting the current receipt instead of redundantly re-emitting on an already-proven warm lane. Revision 0431 closes the same drift on the per-macro execution surface itself: `macro_dispatch_gate_json.sh <macro>` now switches from `dispatch_now` to `inspect_current_dispatch_evidence` when the newest receipt for that macro is still current warm-runtime evidence, so the gate no longer asks the resident service to prove the same clean warm-path state twice in a row. Revision 0432 closes the next one-read gap on the selected-macro lane: when the checked gate is blocked on `desktop_state_mismatch` and a bounded live probe sample already exists, `primary_macro_work_ticket` now carries that `probe_handoff` directly and routes to probe inspection before generic execution triage. Revision 0433 carries the same decision up to `next_action_json.sh`: the top-level helper now reuses `primary_macro_work_ticket_json.sh` and prefers `inspect_live_probe_observation` over the generic checked-gate path when the selected macro is blocked on a live desktop mismatch that already has bounded probe evidence. Revision 0434 closes the adjacent stale-receipt gap: when the selected macro already has the newest warm-runtime receipt for this lane but that receipt is no longer current, `primary_macro_work_ticket` now routes to `latest_dispatch_json.sh` first instead of flattening back into a generic execution handoff, and `next_action_json.sh` now reuses that selected-macro stale-receipt handoff before falling through to the checked gate. Revision 0435 finishes the same alignment on the per-macro gate and the top-level fallback path: `macro_dispatch_gate_json.sh <macro>` now emits `inspect_stale_dispatch_evidence` when the newest receipt for that macro is stale resident evidence, and `next_action_json.sh` can now still reuse that receipt-first recommendation from the checked gate even if the smaller selected-macro work-ticket helper is unavailable. Revision 0436 closes the remaining selected-macro correctness gap: the generated stack, selected-macro work ticket, and stack-state projection now use `macro_latest_dispatch_json.sh <macro>` as the selected-macro receipt surface instead of accidentally consulting the project-global newest receipt when another macro emitted more recently.
Revision 0437 closes the followup-path sibling of that bug and makes the project-wide history board speak more plainly: macro-scoped receipt evidence now keeps pointing at `macro_latest_dispatch_json.sh <macro>` instead of drifting back to `latest_dispatch_json.sh`, and `macro_dispatch_history_board_json.sh` now exposes project-global newest-receipt truth separately from the board primary macro's macro-scoped receipt lane.

- what the selected macro is
- where editable source lives
- whether recorder/cleanup/replay debt is active
- whether checked warm dispatch is currently honest
- whether the resident daemon is attached to the right X11/i3 session
- whether a bounded live reload actually kept the daemon on the current X11/i3 session instead of only refreshing project state
- whether a bounded live restart actually brought the daemon back on the current X11/i3 session with the expected watcher/runtime contract
- which bounded reload/restart helper was tried most recently, when it ran, and whether it actually repaired the resident session
- whether the live daemon is serving the current project contract from disk
- which single selected-macro lane is active right now: recorder, cleanup, replay, acceptance, runtime repair, or execute
- what the next bounded repair or execution step should be, including the inspect-first path after a recent failed repair

## Repo map

- `src/vhk/core/` — runner, events, watchers, control flow, run logging
- `src/vhk/system/` — X11/system wrappers, runtime plumbing, session probes, recorder support
- `src/vhk/i3/` — i3 IPC and tree helpers
- `src/vhk/project/` — project schema, generated runtime/control-plane surfaces, proof contracts, packs
- `src/vhk/vision/` — image match, OCR, pixel helpers
- `examples/hello_project/` — sample project layout
- `docs/` — active specs, decisions, issues, revision notes
- `vault/` — preserved but demoted research and side lanes

## Start here

- `docs/DATACUBE_2026.03.19_X11_FIRST.md`
- `docs/FLAGSHIP_RUNTIME_SPEC_2026.03.21.md`
- `docs/ARCHITECTURE.md`
- `docs/DECISION_2026.03.23_X11_I3_SHIPROOM_AND_LLM_BOUNDARIES.md`
- `docs/I3_X11_RUNTIME_STACK.md`
- `docs/RECORDER_X11.md`
- `docs/LLM_AUTHORING_LOOP.md`
- `docs/LLM_AUTHOR_LOOP_CONTROL_PLANE.md`
- `docs/ROADMAP_2026.03.19_X11_FIRST.md`
- `docs/ISSUES_2026Q1.md`

## Development

Run focused tests while iterating:

```bash
python -m pytest -q tests/test_runtime_state_cache.py
python -m pytest -q tests/test_latest_dispatch_json_cli.py
python -m pytest -q tests/test_i3_busd_stack_cli.py
```

Run the broader suite when changing shared runtime/control-plane behavior:

```bash
python -m pytest -q
```

## Working principle

VHK does not need to win by pretending Linux automation is one universal stack.
It needs to be **excellent on the environment it actually targets**:
**i3/X11, warm resident runtime, thin dispatch, strong recorder cleanup, and
honest execution contracts for shell callers and a private LLM.**


[rev0438] `next_action_json.sh` now carries both `latest_dispatch_json.sh` (project-global newest receipt) and `macro_latest_dispatch_json.sh <macro>` (selected-macro newest receipt) as explicit receipt scopes.
[rev0439] Receipt evidence now carries its own explicit scope metadata (`project_global_latest_dispatch` vs `selected_macro_latest_dispatch`) plus the scope command that produced it, so selected-macro work tickets and next-action recommendations stop relying on helper names alone to explain which receipt lane they are following.


[rev0440] `macro_runtime_board_json.sh` now mirrors macro-scoped receipt observability and explicit project-global vs selected-macro receipt surfaces, so the project-wide execution board can point directly at `macro_latest_dispatch_json.sh <macro>` instead of only describing dispatch posture.


[rev0441] `macro_runtime_board_json.sh` now carries a bounded `runtime_handoff` per macro plus primary-handoff summary fields, so the execution board can say not only which lane is preferred but also whether the next move is checked dispatch, receipt inspection, replay-proof refresh, direct run, or recorder stabilization.
[rev0442] `next_action_json.sh` now reuses that selected-macro `runtime_handoff` when the per-macro gate/work-ticket path is unavailable or only generic, and `stack_state_json.sh` now mirrors the same handoff explicitly so the top-level resident-runtime control plane stays action-specific.

[rev0443] `primary_macro_work_ticket_json.sh` now also reuses the selected-macro `runtime_handoff` when the execution ticket would otherwise fall back to a generic inspect/author-loop answer.
[rev0444] `warm_runtime_ticket_json.sh` and `warm_runtime_ticket.sh` now do the same on the resident-runtime surface itself: when runtime is healthy but the selected macro's execution ticket is only generic, the warm-runtime ticket now follows the runtime board's bounded selected-macro handoff and prints whether that handoff came from the runtime board or the execution ticket.
[rev0448] `macro_runtime_board_json.sh` now also mirrors the per-macro author-loop `llm_workbench`, and `warm_runtime_ticket_json.sh` / `warm_runtime_ticket.sh` now carry the fused stack's chosen `primary_macro_llm_workbench`, so the resident-runtime surfaces can say both what the daemon should do next and which bounded macro-scoped LLM helper to reopen next.
[rev0449] `macro_dispatch_history_board_json.sh` now also mirrors a bounded per-macro receipt/history `llm_workbench`, and the fused stack / warm-runtime ticket helpers carry `primary_macro_dispatch_history_workbench`, so receipt-first inspection stays visible from the smaller resident-runtime surfaces too.
[rev0454] `warm_runtime_ticket_json.sh` / `warm_runtime_ticket.sh` now also expose `execution_ticket_handoff` and a `selected_macro_handoff_basis`, so the resident-runtime ticket can say when it is reusing the checked-dispatch receipt lane instead of pretending its own generic execution answer is sharp enough.

Revision 0459 adds the next resident-runtime control-plane cut: both `macro_author_loop_json.sh <macro>` and `primary_macro_work_ticket_json.sh` now also carry `execution_cutover`, a machine-readable answer to *what should happen operationally before another execute?* It makes receipt disposition, runtime-repair blockers, redundant warm-dispatch risk, and signoff readiness explicit, and it mirrors into the generated selected-macro helper metadata and summary surfaces so the private LLM can tell when to inspect the newest receipt, when durable signoff is honestly ready, and when the resident lane still needs repair before another checked dispatch.

## Revision 0460: receipt cutover truth reaches the lower resident surfaces

Revision 0460 pushes receipt-disposition and execution-cutover truth down into the lower resident-runtime surfaces themselves. `macro_latest_dispatch_json.sh <macro>` now carries `stage_completion` and `execution_cutover`, the runtime board mirrors those cutover ids on macro-scoped receipt observability and per-macro runtime items, and `runtime_handoff` now echoes the same receipt-disposition, signoff-ready, repair-required, and redundant-dispatch-risk flags so the warm resident lane can inspect or sign off instead of blindly re-emitting.

Revision 0461 closes the remaining bridge above that lane. `selected_macro_handoff` on the selected-macro work ticket and generated resident helpers now preserves the lower receipt/runtime contract instead of flattening it back to a bare command string: higher-level surfaces now carry stage-completion ids, execution-cutover ids, receipt-disposition requirements, signoff readiness, repair requirements, and redundant-dispatch risk. The work-ticket priority also tightens around the warm session service itself, so obvious resident-runtime degradation outranks “inspect the current receipt” when the resident lane is not actually healthy enough to trust reuse.

[rev0493] A new generated-stack consistency test now proves `warm_runtime_ticket*`, `primary_macro_work_ticket*`, and `llm_session_ticket*` stay aligned on one fused selected-macro + checked-dispatch snapshot, so the resident runtime, selected-macro work lane, and one-read private-LLM surface cannot quietly drift onto different macro or dispatch answers.

[rev0494] Added a compact `runtime_witness` helper pair to the generated i3/X11 stack. It fuses watcher/mode truth, warm-lane status, probe freshness/latency, repair recipe, selected-macro handoff, and bounded next action into one resident-runtime witness, and focused generated-stack tests now lock that witness to both the manifest contract and the shared fused snapshot.


[rev0495] `stack_state_json.sh` now mirrors the compact `runtime_witness*` surface explicitly inside its helper metadata and control-plane contract, so one fused resident snapshot can recover watcher/mode truth, warm-lane posture, probe freshness, repair lane, and bounded next action without letting the higher stack drift away from the witness helper.


[rev0496] `stack_state.sh` now mirrors the compact runtime witness as an explicit `stack_runtime_witness_*` digest and advertises that digest in the generated control-plane manifest, so the human/operator one-read summary stays as contract-locked to watcher/mode, warm-lane posture, repair lane, and bounded next action as the JSON resident surfaces.


[rev0497] `status_runtime.sh` now prepends a manifest-backed `status_runtime_witness_*` digest sourced from the compact resident runtime witness before its raw `systemctl` tail, so the shortest daemon-health surface and the fused stack/operator summary stay aligned on watcher/mode truth, warm-lane posture, repair lane, and bounded next action.
