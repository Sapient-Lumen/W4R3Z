# Cargo Feature Surface Contract Kit fixtures

This fixture pack freezes a stronger artifact vocabulary for **P-0528 Cargo Feature Surface Contract Kit**.

Artifacts:
- `feature-surface.receipt.schema.json`
- `activation-profile.report.schema.json`
- `conflict-policy.receipt.schema.json`
- `unification-risk.report.schema.json`
- `resolution-scope.receipt.schema.json`
- `hosted-feature-profile.receipt.schema.json`
- `feature-support-bundle.manifest.schema.json`

Scenario families:
- `grouped_optional_deps_hide_internal_switches_from_public_surface/`
- `mutually_exclusive_backends_require_explicit_conflict_policy/`
- `resolver_v2_host_target_split_requires_unification_risk_receipt/`
- `workspace_wide_no_default_features_scope_needs_explicit_receipt/`
- `docsrs_all_features_profile_is_not_runtime_support_contract/`
- `portable_bundle_keeps_scope_hosted_docs_and_contract_separate/`
