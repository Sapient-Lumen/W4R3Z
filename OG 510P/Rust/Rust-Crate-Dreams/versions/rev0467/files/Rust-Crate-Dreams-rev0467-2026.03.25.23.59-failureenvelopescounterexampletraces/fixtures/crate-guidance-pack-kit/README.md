# Crate Guidance Pack Kit fixtures

This fixture pack is a draft substrate for **P-0512 Crate Guidance Pack Kit**.
It is intentionally small and focused on receiver-facing crate support surfaces rather than generic diagnostic rendering.

## Included schema drafts

- `guidance-pack.schema.json`
- `compile-guidance.receipt.schema.json`
- `recovery-recipe.manifest.schema.json`
- `guidance-check.report.schema.json`
- `guidance-diff.report.schema.json`
- `guidance-authority.policy.schema.json`
- `recovery-origin.receipt.schema.json`
- `recipe-fidelity.report.schema.json`
- `message-stability.report.schema.json`
- `guidance-channel.receipt.schema.json`

## Scenario families

- `trait_bound_guidance/` — a trait-heavy crate gives a better error and a smallest good-path recipe
- `runtime_or_feature_mismatch/` — a feature/runtime mismatch points to the supported configuration
- `proc_macro_usage_guidance/` — a proc-macro misuse case has an expected diagnostic and correction path
- `compile_fail_doctest_catches_failure_but_not_message_drift/` — docs prove failure still happens, but not exact guidance fidelity
- `do_not_recommend_hides_blanket_impl_but_recipe_missing/` — a misleading impl is hidden, but the crate still owes users the smallest working path
- `proc_macro_diagnostic_url_points_to_stale_syntax/` — emitted diagnostics and linked examples can drift apart
