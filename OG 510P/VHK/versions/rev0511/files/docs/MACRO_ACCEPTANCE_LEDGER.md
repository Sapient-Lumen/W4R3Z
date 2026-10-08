# Macro acceptance ledger

The flagship i3/X11 lane now treats `review/macro_acceptance.yaml` as the durable project signoff ledger for recorder/runtime debt. This is intentionally checked-in project truth, not ephemeral runtime state.

Use it when a macro has recorder debt that is real and understood but intentionally tolerated on the primary desktop, or when a runtime posture has been reviewed and explicitly accepted.

Current generated/CLI surfaces:

- `vhk macro-acceptance-ledger-json <project>`
- `vhk macro-runtime-accept <project> <macro> --accepted-by <name> --note <why>`
- `bin/macro_acceptance_ledger_json.sh` in generated i3/X11 warm-runtime stacks
- `bin/record_runtime_acceptance.sh <macro> --accepted-by <name> --note <why>` in generated i3/X11 warm-runtime stacks

Current shape:

```yaml
macros:
  macro_name:
    review_acceptances:
      - issue_code: stale_recording_sidecar
        accepted_by: operator
        accepted_at: 2026-03-20T22:30:00Z
        note: commentary-only edit
    runtime_acceptance:
      posture_id: warm_dispatch_ready
      accepted_by: operator
      accepted_at: 2026-03-20T22:31:00Z
      note: known-good on primary i3 desktop
```

Only entries with both `accepted_by` and `accepted_at` count as completed signoff. Incomplete entries remain visible but advisory. The raw review queue is not erased; the ledger lets the resident runtime and a private LLM distinguish active debt from explicitly accepted debt.

Runtime acceptance remains explicit and operator-driven, but it no longer requires reconstructing the current proof contract by hand. The write helper records the current posture plus the current proof contract in one bounded step.

Revision 0475 tightens that write path for the flagship lane: `macro-runtime-accept` now checks `runtime_signoff_readiness` first and blocks by default when the current proof is not actually signoff-ready — for example when the newest replay is healthy but still lacks current X11/i3 target proof, or when no current checked-dispatch receipt exists yet. Operators can still use `--force` for a deliberate override, but the default path now treats durable signoff as the *last* bounded step after replay proof, target proof, receipt truth, and warm-runtime posture all agree.

Revision 0476 makes that override visible instead of letting it age into fake normalcy. Forced runtime acceptances now persist `force_override` plus the readiness blocker that was bypassed, and the normalized `runtime_signoff` view reports `forced_review` / `force_review_required` until a clean replacement signoff is recorded from a genuinely ready resident X11/i3 lane.
Revision 0478 sharpens the adjacent receipt-review story too: when the newest checked-dispatch receipt is `current_forced_dispatch_evidence`, the smaller receipt/work-ticket surfaces now advertise a dedicated receipt-stage completion/cutover instead of generic current-receipt reuse. That keeps acceptance debt and receipt debt aligned: a forced current receipt is not just blocked for signoff, it is explicitly routed through clean-replacement inspection first.
Revision 0477 extends the same honesty to checked-dispatch receipts. A newest receipt that is otherwise current but was emitted with `--force` is now classified as `current_forced_dispatch_evidence`, and runtime-signoff readiness blocks that case as `blocked_by_forced_dispatch_receipt` until a newer clean checked-dispatch receipt replaces it. The practical point is simple: a forced receipt can still be useful evidence to inspect, but it is no longer treated as clean reusable proof for durable signoff.
