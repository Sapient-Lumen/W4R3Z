# Macro dispatch history board

`vhk macro-dispatch-history-board-json <project>` and generated `bin/macro_dispatch_history_board_json.sh` expose a project-wide, receipt-backed dispatch observability surface for the resident i3/X11 runtime.

## Why this exists

`latest-dispatch-json` is useful but too narrow on its own. A warm resident runtime and a private LLM also need to know whether a macro:

- has been blocked repeatedly by the checked-dispatch gate
- is still living on a forced override without a newer clean emit
- has dispatch history that is simply stale
- has no dispatch history at all yet

This board answers that at project scope without reopening `build/dispatch_receipts/history/` by hand.

## Postures

- `blocked_repeated_recently`
- `forced_override_pending_review`
- `forced_override_stale`
- `mixed_recent_dispatch`
- `dispatch_history_stale`
- `dispatch_receipt_runtime_probe_refresh_stale`
- `dispatch_receipt_runtime_latency_stale`
- `dispatch_receipt_runtime_probe_status_stale`
- `clean_recent_dispatch`
- `no_dispatch_history`

## Contract shape

Each macro item includes:

- `dispatch_history`: recent counts, streaks, latest receipt summary, latest clean emit, latest forced override, unresolved-force truth, blocked-receipt class counts (`contract_debt`, `desktop_state_mismatch`, `run_proof_gap`), the latest blocked receipt's preserved X11/i3 desktop-target hint when one was present, and `latest_receipt_warm_runtime_evidence` so the board speaks the same receipt-currentness language as `latest_dispatch_json.sh`
- `dispatch_history_posture`: posture id, rank, summary, reason, a direct `command`, and `command_scope_id` so the board tells callers whether the best next surface is the per-macro checked gate or the macro-scoped latest-dispatch helper
- `llm_workbench`: a bounded receipt/history edit-inspect-execute contract for that macro. It tells a private LLM whether the next receipt move is “inspect current receipt”, “inspect stale receipt”, or “produce first dispatch receipt”, and it keeps the receipt lane, author loop, checked-dispatch gate, and source edit target on one read.
- `receipt_observability`: explicit per-macro receipt-lane metadata, including the macro-scoped latest-dispatch helper command
- `preferred_entrypoints`: stable generated wrappers for history-board, project-global latest-dispatch, macro-scoped latest-dispatch, dispatch-gate, and checked-dispatch inspection

At the board root, `receipt_surfaces` now makes the two receipt scopes explicit: `project_latest_dispatch` is project-global newest-receipt truth, while `primary_macro_latest_dispatch` is the board primary macro's macro-scoped receipt lane. Revision 0449 also adds `primary_macro_llm_workbench`, so callers who open the board root do not need to rediscover the selected macro's receipt lane by scanning posture fields manually.

## Resident-runtime use

This surface is observability-first. It does not by itself block dispatch. Instead it makes repeated blocks and unresolved forced overrides visible in the same control plane as the runtime board, dispatch catalog, checked gate, latest-dispatch receipt, and per-macro author loop. Revision 0426 also makes receipt/runtime drift more specific: when the daemon's current bounded probe posture no longer matches the newest receipt, the board now distinguishes stale fresh-proof, latency drift, and probe-result drift instead of only saying that some runtime instance changed. Revision 0427 tightens `probe-result drift` again so it fires on any comparable bounded-probe result change, not only a flip between success and failure classes. A receipt captured during `ack_timeout` should not keep looking current once the same daemon is now answering `invalid_ack`, even though both states are failures.
