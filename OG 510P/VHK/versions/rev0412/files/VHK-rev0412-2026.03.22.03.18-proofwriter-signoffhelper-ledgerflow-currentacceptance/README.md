# VHK — VisualHotKey for i3/X11-first desktop automation

VHK is an **AHK-shaped automation engine** and the runtime core for a future
**Pulover-style Linux macro studio**.

## Current product stance

VHK is deliberately optimized for one flagship lane:

- **Primary desktop target:** i3 on X11
- **Primary runtime:** a **session-bound long-lived user service** that stays warm while the user is logged in
- **Primary authoring loop:** **record -> cleanup -> replay -> inspect -> refine**
- **Primary advanced use case:** a **private LLM** that can author, revise, inspect, and execute VHK macros against a live desktop
- **Secondary lane:** ad hoc `vhk ...` CLI runs for development, debugging, and one-shot execution

Broad Linux-native positioning, Wayland, portals, and app-native adapters are
kept only when they honestly support the X11/i3 core. Otherwise they are
secondary or vaulted.

## What matters most right now

- fast warm dispatch from i3 bindings and generated wrappers
- queue surfaces that already expose the right execute/inspect entrypoints
- reliable X11 window/focus/workspace control
- recorder fidelity and cleanup quality
- replay discipline, waits, and failure evidence
- one-read control-plane surfaces for humans and a private LLM

Contract-bound replay proof now matters in the same way recorder freshness does: a once-healthy run is not current proof anymore after macro edits, recorder-sidecar drift, or a desktop-session change that moves the current shell onto a different `DISPLAY`/`I3SOCK` than the run was proven on. The selected-macro lane now surfaces that state explicitly as rerun debt instead of over-trusting old logs. Legacy runs without the session witness remain readable, but once a run captures that witness VHK treats session drift as replay drift.

Warm dispatch receipts now follow the same honesty rule in three dimensions: they are bound to the current macro/dispatch contract, they are tied to the resident daemon epoch that emitted them, and they now remember the X11/i3 desktop session they were emitted under. A clean receipt from an older `vhk busd` instance or from a different `DISPLAY`/`I3SOCK` session no longer counts as current warm-runtime evidence after the daemon reloads, restarts, or the shell moves to a different desktop session.

Durable runtime acceptance now follows the same rule too: a posture-only signoff in `review/macro_acceptance.yaml` no longer counts as current without a matching runtime-acceptance proof contract. The ledger can still carry older operator signoff, but the runtime board and author loop now mark that signoff stale until it matches the current replay posture, macro proof contract, dispatch proof contract, and the current resident-runtime witness from the warm busd cache. The next tightening is X11/i3-specific too: the proof contract now also carries the current desktop-session digest, so a signoff minted on one `DISPLAY`/`I3SOCK` pair stops counting as current after the shell moves to a different desktop session even before a fresh replay or dispatch receipt is written.

## Control-plane center of gravity

The generated i3/X11 stack is the repo's current operational center.

Start with:

- `bin/next_action_json.sh`
- `bin/stack_state_json.sh`
- `bin/macro_author_loop_json.sh <macro>`
- `bin/macro_dispatch_gate_json.sh <macro>`

`stack_state_json.sh` is intentionally opinionated around the
**author-queue-selected macro**. The companion `control-plane.json` now makes the flagship product lane, the preferred private-LLM authoring loop, and the X11 session-activation contract explicit in machine-readable form. `stack_state_json.sh` keeps the live selected-macro/runtime handoff equally compact, in one read:

- selected-macro gate, latest run, recorder, contract, and entrypoints
- selected-macro replay/runtime/dispatch board rows
- selected-macro acceptance, signoff handoff, and review-queue slices
- selected-macro latest dispatch receipt
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
- `session_attachment`
- `dispatch_path_probe`
- `dispatch_path_summary`
- `dispatch watcher contract proof` (expected watcher(s) vs the live daemon's loaded watcher list)
- `dispatch runtime contract proof` (disk project digest vs the live daemon's loaded project digest)
- `startup_handoff_witness`
- `startup_handoff_repair_ticket`
- `latest dispatch runtime witness` (receipt daemon epoch vs current cached daemon epoch)

`primary_macro_repair_recipe` is now blocker-aware: it carries a bounded repair
focus, blocker class, evidence commands, and a short next sequence for the
author-queue-selected macro.

`warm_runtime_ticket` is the resident-service companion to those selected-macro
surfaces. It compresses session readiness, socket/service activation, helper
health, session-attachment truth, and the selected macro's current execute handoff
into one bounded answer: enter a graphical session first, sync the systemd/D-Bus
activation environment back to the live X11/i3 shell, reactivate the warm
socket/service, restart a daemon that is bound to the wrong watcher contract,
reload a daemon whose loaded project contract drifted behind disk after LLM or
operator edits, verify that reload with a machine-readable receipt, clear remaining runtime blockers, inspect degraded warnings, or
proceed to the selected macro's checked-dispatch/direct-run command.

`session_attachment` now makes that X11/i3 binding explicit in the fused stack.
It distinguishes a merely graphical shell from a warm runtime that can be
restarted safely through socket activation into the same `DISPLAY`,
`XAUTHORITY`, `DBUS_SESSION_BUS_ADDRESS`, `XDG_RUNTIME_DIR`, and `I3SOCK`
context. It now also compares the live shell against the *running* busd
service's startup environment, so the fused stack can tell the difference
between “activation is now fixed” and “the current daemon was already started in
the wrong desktop session and must be restarted there.”

`startup_handoff_witness` now sits beside that live runtime ticket. It keeps the
next login/startup owner question equally bounded: primary user-unit owner,
autostart-only fallback, duplicate-start risk, missing owner, or startup-owner
drift attention. That lets the fused stack warn about graphical-session vs
autostart ownership problems without widening into a full installer or planner.

`startup_handoff_repair_ticket` now sits immediately beside that witness. It keeps one bounded owner-fix answer explicit for the i3/X11 lane: hide a duplicate autostart bridge so the user unit becomes the single owner again, unmask or enable the user-unit owner when startup drifted or disappeared, or skip startup repair entirely because the current owner is already correct.

That lets an operator or private LLM stay on one fused diagnosis lane instead of
reopening helpers just to decide the next repair, execution, or live X11/i3
inspection step. `primary_macro_execution_ticket` now makes the honest execute
handoff explicit too: checked warm dispatch vs direct run vs inspect/repair
first, plus compact preflight and verification commands. `primary_macro_recording_ticket` keeps the recorder-heavy lane equally explicit: record first, re-record after source edits, inspect recording drift, or review exact/title/workspace segments before claiming replay stability. `primary_macro_cleanup_ticket` now sits between recorder and replay truth and answers the source-mutation question directly: record before cleanup, reconcile recorder/source drift, review the cleanup diff, or skip cleanup because the selected macro is already clear. `primary_macro_replay_ticket` now closes the replay-proof hop between cleanup and execute: record before replay when recorder truth drifted, inspect warned/failed matching runs, mint fresh proof with a direct run, or proceed to the checked warm-dispatch lane when replay proof is still healthy. `primary_macro_acceptance_ticket` closes the durable-signoff hop after that: repair before signoff when stack signals still contradict each other, settle cleanup or replay debt first, or review/update the acceptance ledger with a bounded signoff handoff once the selected macro is actually current. That handoff now carries the current runtime-acceptance proof contract too, so a private LLM can refresh durable signoff without guessing which proof state should be written back. Dispatch history now stays equally honest after resident-runtime changes: receipts are compared against a cheap busd-written runtime-state cache so a clean emit from an older daemon epoch is no longer mistaken for proof about the currently loaded warm runtime.

## Repo map

- `src/vhk/core/` — runner, events, watchers, selector helpers
- `src/vhk/system/` — X11/system wrappers and runtime plumbing
- `src/vhk/i3/` — i3 IPC and tree helpers
- `src/vhk/project/` — project format, packs, generated runtime/control-plane surfaces
- `examples/hello_project/` — sample project layout
- `docs/` — active specs, decisions, issues, revisions
- `vault/` — preserved but demoted research and side lanes

## Start here

- `docs/DATACUBE_2026.03.19_X11_FIRST.md`
- `docs/FLAGSHIP_RUNTIME_SPEC_2026.03.21.md`
- `docs/DECISION_2026.03.19_X11_FIRST_PRODUCT.md`
- `docs/DECISION_2026.03.19_RUNTIME_AND_LLM_CONTROL.md`
- `docs/ROADMAP_2026.03.19_X11_FIRST.md`
- `docs/ARCHITECTURE.md`
- `docs/I3_X11_RUNTIME_STACK.md`
- `docs/RECORDER_X11.md`
- `docs/OPTIMIZE_MACROS.md`
- `docs/PERFORMANCE.md`
- `docs/LLM_AUTHORING_LOOP.md`
- `docs/LLM_AUTHOR_LOOP_CONTROL_PLANE.md`
- `docs/ISSUES_2026Q1.md`

## Working principle

VHK does not need to win by pretending Linux automation is one universal stack.
It needs to be **excellent on the environment it actually targets**:
**i3/X11, warm resident runtime, strong recorder cleanup, and honest execution
contracts for shell callers and a private LLM.**


REV0399 adds a first-class resident dispatch witness: the generated stack now carries both a raw internal probe payload and a summarized `vhk-emit -> socket -> resident busd` round-trip status so the warm-runtime lane is judged by live dispatch reachability, not only by units/env looking plausible.

REV0400 tightens that witness into a real generated-stack contract: the probe summary now compares the expected watcher set against the live daemon's loaded watcher list, so VHK can tell the difference between ‘busd answered’ and ‘the busd that answered is actually running the hotkey/dispatch watcher contract this stack depends on’.


REV0401 adds a resident project-contract witness: the internal bus probe now carries a digest of the daemon's loaded project state, `check_runtime_json.sh` compares it against the current project on disk, and `warm_runtime_ticket` now routes project-state drift to a bounded reload repair instead of treating stale resident state as generic dispatch failure.

REV0402 makes that reload repair observable: `bin/reload_runtime_json.sh` emits the reload event, probes the resident daemon before and after, and returns a machine-readable receipt that says whether a new runtime epoch/reload count was observed and whether the daemon now reports the current on-disk project contract.

REV0409 binds durable runtime signoff to warm-dispatch history too: the runtime acceptance contract now carries dispatch-history posture/attention, so an old accepted signoff goes stale when the resident bus lane turns session-stale, runtime-stale, contract-stale, or newly blocked. REV0410 tightens the same signoff around the resident daemon itself: the acceptance proof now also captures the cached busd runtime epoch/runtime-contract witness, so a warm-service reload or restart can stale durable signoff even before a new dispatch receipt is written. REV0411 binds durable signoff to the current X11/i3 desktop session too: the acceptance proof now carries the current desktop-session digest, so a signoff from one `DISPLAY`/`I3SOCK` session cannot silently survive onto another.
