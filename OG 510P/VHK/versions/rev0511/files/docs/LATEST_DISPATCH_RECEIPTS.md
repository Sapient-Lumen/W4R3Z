# Latest dispatch receipts

The warm i3/X11 stack now writes a durable receipt for each generated-stack dispatch attempt under:

- `build/dispatch_receipts/latest.json`
- `build/dispatch_receipts/history/*.json`

This is the resident-runtime answer to: **what did the last thin-dispatch attempt actually do?**

## Why this exists

VHK already had:

- a project-wide dispatch catalog (`macro_dispatch_catalog_json.sh`)
- a per-macro checked dispatch gate (`macro_dispatch_gate_json.sh`)
- a checked dispatch wrapper (`dispatch_macro_checked.sh`)

But those surfaces still left one operational gap: after an emit or refusal, callers had to infer the latest dispatch outcome from stderr or logs. The receipt lane makes the newest decision explicit and durable.

## Receipt shape

Each receipt stores:

- macro name
- bus event
- result (`emitted` or `blocked`)
- route (`dispatch` or `checked_dispatch`)
- whether the checked gate was used
- whether `--force` was used
- raw and parsed payload JSON
- summarized gate data (availability, blockers, blocker classes, reason, preferred execution mode, `repair_action`, the expected X11/i3 desktop target hint when known, and the likely failed live X11/i3 probe when known)
- stderr text when present
- checked-gate `blocked_message` text when the resident dispatcher refused to emit
- timestamp and receipt id

The generated stack also exposes:

- `bin/latest_dispatch_json.sh`

That helper returns one machine-readable snapshot for the latest known dispatch receipt, including the receipt path relative to the project root.

## Intended use

Use this lane when the resident service, shell tooling, or a private LLM needs to answer:

- what macro did we just try to emit?
- was it blocked or emitted?
- did it go through the checked gate?
- was the emit force-overridden?
- what blocker or reason was attached to the decision?
- what X11/i3 target state was the macro expecting when the checked gate said `desktop_state_mismatch`?
- which live X11/i3 probe from the newest matching run most likely failed before the warm lane refused to emit?

This keeps dispatch observability inside the project/runtime control plane instead of pushing it into ad hoc journal scraping.

## Revision 0366 note

Blocked checked-dispatch receipts now preserve the same refusal text the wrapper returned to the caller instead of collapsing that path to a generic placeholder. That makes `latest_dispatch_json.sh` and receipt history good enough for LLM/operator follow-up without reopening wrapper logs.


Revision 0367 adds `gate.live_probe_hint` to the latest-dispatch surface whenever the newest matching run already points at a likely window/event/focus/i3 probe. Revision 0368 extends that same object with `gate.live_probe_hint.observation`, a bounded snapshot of the actual failed wait/error observation when one is cheaply available from the newest matching run. That keeps the resident receipt lane actionable without reopening macro-scoped run history first.


Revision 0369 adds `gate.repair_action` to both durable receipts and `latest_dispatch_json.sh`, so blocked warm-runtime receipts answer not only *what went wrong* but also *which concrete command should repair or advance the lane next*.

Revision 0427 tightens receipt/runtime comparison for the resident fast path: the newest receipt now goes stale whenever the daemon's bounded probe result changes in any comparable way, not only when it flips from success to failure or back. That keeps `latest_dispatch_json.sh` honest when the warm lane drifts between different failure modes such as `ack_timeout` and `invalid_ack`.

Revision 0428 closes the next receipt usability gap for the resident i3/X11 lane: `latest_dispatch_json.sh` now classifies the newest receipt as explicit `warm_runtime_evidence`. That verdict says whether the receipt is still current resident fast-path evidence (`current: true`) or stale evidence that must be refreshed against the current runtime/session/contract state first. It also carries a concrete `recommended.command`, so a private LLM can jump straight to `warm_runtime_ticket.sh` for runtime/session drift or back to `macro_dispatch_gate_json.sh <macro>` when only the macro/dispatch contract changed.

Revision 0429 threads that same receipt-evidence verdict into the selected-macro handoff. `primary_macro_work_ticket` now carries a compact `latest_dispatch_handoff` for the selected macro, and when the newest receipt is still current warm-runtime evidence on the current resident lane, the work ticket recommends inspecting `latest_dispatch_json.sh` before another emit. That keeps the LLM/operator loop from turning a fresh clean receipt into an automatic re-dispatch instruction.


## Revision 0430: receipt truth now feeds the global next-action helper

`latest_dispatch_json.sh` was already the authoritative place to ask whether the newest receipt is still current warm-runtime evidence, but the top-level `next_action_json.sh` helper could still skip that answer and jump straight from author-queue selection to `macro_dispatch_gate_json.sh <macro>`. That was one redundant emit hop too many for the i3/X11 flagship lane.

Revision 0430 closes that gap. When the selected macro already has a current clean warm-runtime receipt, `next_action_json.sh` now returns `inspect_current_dispatch_evidence` with `./bin/latest_dispatch_json.sh` as the recommended command. The checked gate remains the fallback when the newest receipt is stale, belongs to another macro, or cannot be proved current.

Revision 0437 fixes one selected-macro followup leak in that same lane. `macro_latest_dispatch_json.sh <macro>` already chose the right receipt, but its shared `warm_runtime_evidence.followup` list could still end in the project-global `latest_dispatch_json.sh`. The macro-scoped receipt lane now keeps its own helper in those followups, so private-LLM/operator loops stay on the chosen macro instead of bouncing back to project-global newest-receipt truth.


[rev0438] `next_action_json.sh` now carries both `latest_dispatch_json.sh` (project-global newest receipt) and `macro_latest_dispatch_json.sh <macro>` (selected-macro newest receipt) as explicit receipt scopes.
[rev0439] The receipt evidence itself now carries `receipt_scope_id` / `receipt_scope_command`, and `next_action_json.sh` mirrors the chosen selected-macro receipt lane in `recommendation_trace.selected_receipt_scope_id` / `selected_receipt_command`. That makes the warm-lane handoff self-describing even after payloads are fused into stack-state or selected-macro work-ticket summaries.

## Revision 0460: macro-scoped receipts now carry cutover truth

The selected-macro receipt lane now carries `stage_completion` and `execution_cutover` directly on `macro_latest_dispatch_json.sh <macro>`. That means the lower receipt surface can say whether the current task is to inspect receipt disposition, repair runtime before reuse, move to durable signoff, or proceed with checked dispatch, without forcing the LLM or operator to infer that only from higher-level work tickets.
