# Crate Runtime Handoff Pack Kit fixtures

This fixture pack is a draft substrate for **P-0513 Crate Runtime Handoff Pack Kit**.
It is intentionally small and focused on receiver-facing runtime support surfaces rather than general logging or hosted crash collection.

## Included schema drafts

- `runtime-handoff.pack.schema.json`
- `runtime-context.receipt.schema.json`
- `panic-handoff.receipt.schema.json`
- `redaction-profile.schema.json`
- `runtime-handoff-check.report.schema.json`
- `failure-shape-diff.report.schema.json`
- `capture-exactness.policy.schema.json`
- `share-safety.receipt.schema.json`
- `handoff-fidelity.report.schema.json`

## Scenario families

- `error_chain_runtime_context/` — a public runtime error crosses abstraction boundaries and exports a safe receipt
- `async_span_handoff/` — an async failure exports logical span context with explicit `captured` / `empty` / `unsupported` status
- `panic_report_redaction/` — a panic hook emits a user-submittable crash report that honors redaction classes
- `error_stack_attachment_secret_needs_hash_redaction/` — exact attachment capture still needs hashed or omitted support export
- `spantrace_declared_but_error_layer_missing/` — declared async context support is weaker when `SpanTrace` ends up unsupported or empty
- `panic_hook_present_but_report_bundle_path_missing/` — custom panic hooks are weaker than a witnessed support-bundle path


## 2026-03-17 productization note

This family now treats three runtime-support review objects as first-class:

- **capture exactness** (`exact_capture`, `exact_capture_with_redaction`, `maintainer_summary`, `inferred_summary`)
- **share safety** (`safe_by_default`, `hashed_for_support`, `omitted_by_default`, `manual_review_required`)
- **handoff fidelity** (how complete a post-failure bundle really is across error, panic, backtrace, span context, and recovery-step linkage)

Future revisions should avoid collapsing those into one fake “the crate gives useful crash reports” verdict.
