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
