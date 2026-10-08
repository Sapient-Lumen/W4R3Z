# 35 — MetaLLM End-to-End Control Loop (v0.19)

This doc is the “ladder builder”: the concrete loop MetaLLM runs to improve outcomes over time.

## Loop: Observe → Nudge → Verify → Snapshot
1) OBSERVE
- parse rate (CTRL seen? healed? repair success?)
- time_to_ctrl distribution
- truncation spikes
- WS churn and compaction frequency
- collision/lease violations
- evidence density (E# per cursor)

2) NUDGE (smallest reversible lever)
Typical order:
- shrink budgets (05_view_budget_profiles.md)
- force compaction (28_ws_compaction_policy.md)
- assign integrator lease
- switch mode (Gatekeeper ↔ PatchOnly)
- enable header repair (BCC)
- enable CAP probe for chronic failures
- enable header-only guided decoding if CAP supports

3) VERIFY (one discriminative check)
- run a fast verifier
- attempt one CE certification
- check whether selected patch actually moves evidence

4) SNAPSHOT
- snapshot router state
- write SUM# for what changed
- update bootstrap templates (19_bootstrap_templates.md) if needed

## Principles
- Prefer improving the control plane over inventing new protocols mid-run.
- Never require multi-round protocol elections to make progress.
- Treat “unknown slices” as a permanent property: design for partial success.

See also: 56_slice_telemetry_and_budget_adaptation.md and 55_consensus_collapse_and_drift_detection.md

Bootstrap fork: choose CI vs EK (62_bootstrap_variants_compiled_intent_vs_evidence_kernel.md).
