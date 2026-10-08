# Control-plane surface classes

The generated i3/X11 warm-runtime stack now classifies every helper in `control-plane.json` so a shell caller or private LLM can tell **what kind of truth** each surface exposes before it acts.

## Classes

- `canonical_project_source` — checked-in editable project truth; change the source here, then re-render, lint, validate, or replay through generated helpers
- `generated_review_surface` — generated review wrappers and recorder evidence surfaces; inspect or compare here, but do not treat them as the canonical source of truth unless the helper explicitly writes back into source
- `runtime_snapshot` — read-only live state such as readiness, health, inventory, recommended next actions, or fused stack truth; refresh by running the helper again
- `runtime_actuation` — execution/control entrypoints that run macros, dispatch to the warm runtime, record, reload, stop, or otherwise mutate runtime or source
- `runtime_observability` — read-only operator/forensics surfaces for latest runs, artifacts, traces, history, and logs

## Non-claims

The control plane now also carries explicit `non_claims` so callers do not overread generated surfaces:

- generated review helpers and runtime snapshots are **not** canonical editable project source
- recorder review warnings are advisory triage signals, **not** automatic proof that a macro cannot run
- recommended next actions are prioritized guidance, **not** exclusive authority to mutate source

## Why this matters

This prevents a private LLM from collapsing unlike surfaces into one bucket. `macro_source_json.sh` is the place to find and edit project truth, `macro_author_queue_json.sh` is the place to decide which macro should enter the author loop next, `macro_runtime_board_json.sh` is the place to decide what is fit for warm dispatch now, `macro_acceptance_ledger_json.sh` is the place to inspect explicit operator signoff, `optimize_macro.sh` is the place to inspect a generated cleanup proposal, `stack_state_json.sh` is the place to inspect live fused truth, and `dispatch_macro.sh` is the place to execute.

That distinction is part of the flagship product shape: the warm runtime is useful because it exposes **bounded, typed, reviewable surfaces** instead of forcing every caller to rediscover authority and mutability from raw files or ad hoc shell grammar.

Revision 0456 threads that same distinction directly into the selected-macro machine surfaces. `macro_author_loop_json.sh <macro>` and `primary_macro_work_ticket_json.sh` now both project an `authoring_boundary` object that names the canonical editable surface (`macro_source_json.sh <macro>` / checked-in YAML), the inspect-only review/runtime/receipt surfaces, the allowed actuation surfaces, and the default `do_not_edit` globs for generated wrappers, receipts, logs, and runtime caches.

Revision 0457 adds `lane_transition` beside that boundary. This is the machine-readable answer to *when do I stop editing and what lane comes next?* For the active macro it keeps the current lane (`capture_recording`, `edit_source`, `inspect_evidence`, `repair_runtime`, `execute_macro`, `record_signoff`) separate from the next actuation kind/command, plus barrier ids and inspect/verify command bundles. That keeps the X11/i3 resident-runtime path explicit instead of forcing a private LLM to reconstruct the switch point from prose stop conditions.

Revision 0458 adds the sibling answer to *when is the current lane complete enough to stop?* `stage_completion` now rides on the same two helpers and turns fuzzy stop-condition prose into one bounded contract: completion id, completion summary, concrete `complete_when` / `still_open_when` clauses, inspect-to-confirm commands, verify-after-completion commands, and the command most likely to close the lane honestly. The current-receipt and durable-signoff lanes are the highest-value examples: a current warm receipt is no longer treated as generic proof that more emit/re-emit is required, and replay-proof-plus-current-receipt can now route straight to durable signoff.


## Checked dispatch gate

`macro_dispatch_gate_json.sh <macro>` is a runtime snapshot surface. `dispatch_macro_checked.sh [--force] <macro>` is a runtime actuation surface that consults that gate before emitting.
