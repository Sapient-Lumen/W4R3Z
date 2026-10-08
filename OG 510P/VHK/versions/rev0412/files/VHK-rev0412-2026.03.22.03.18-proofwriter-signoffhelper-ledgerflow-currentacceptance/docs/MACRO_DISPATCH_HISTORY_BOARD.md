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
- `clean_recent_dispatch`
- `no_dispatch_history`

## Contract shape

Each macro item includes:

- `dispatch_history`: recent counts, streaks, latest receipt summary, latest clean emit, latest forced override, unresolved-force truth, blocked-receipt class counts (`contract_debt`, `desktop_state_mismatch`, `run_proof_gap`), and the latest blocked receipt's preserved X11/i3 desktop-target hint when one was present
- `dispatch_history_posture`: posture id, rank, summary, reason, suggested followup entrypoints, and a more specific `attention_id` when repeated blocks are mostly contract debt vs mostly live desktop-state mismatch vs mostly missing clean run proof
- `preferred_entrypoints`: stable generated wrappers for history-board, latest-dispatch, dispatch-gate, and checked-dispatch inspection

## Resident-runtime use

This surface is observability-first. It does not by itself block dispatch. Instead it makes repeated blocks and unresolved forced overrides visible in the same control plane as the runtime board, dispatch catalog, checked gate, latest-dispatch receipt, and per-macro author loop.
