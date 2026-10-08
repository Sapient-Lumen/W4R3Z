# Cargo Fix Campaign Kit fixtures

These fixtures are for **P-0507 Cargo Fix Campaign Kit**.

The point is to freeze the orchestration layer above `cargo fix` and `cargo check`:

- lint selection,
- target batching,
- per-pass receipts,
- and manual-review leftovers.

These fixtures should stay distinct from:

- edition-specific rehearsal bundles,
- future-incompat triage ledgers,
- and generic codemod APIs.

Scenario families in this pass:
- `edition_2024_multi_target_rehearsal/`
- `future_incompat_partial_lint_selection/`
