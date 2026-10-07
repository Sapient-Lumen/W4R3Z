# Archive Budget and Hygiene Policy

This archive should stay compact enough to remain reviewable and conservative enough to avoid slowly re-accumulating shipped clutter.

Budget rules:

1. The shipped archive should stay below the configured total-byte and total-file budgets in `publishing/archive_budget_policy.json`.
2. Root-level control surfaces are allowed, but root sprawl should stay below the configured root-file budget.
3. Reports and schemas are useful, but their counts should stay below explicit budgets so trust surfaces do not quietly crowd out the archive itself.
4. Review-render directories like `renderNNN/` are build/review artifacts, not canonical moving-paper source. They may live under `build/review_renders/`, but they should not ship inside `series/` trees.
5. If the budget report fails, default to no publication and prune or simplify before trusting the bundle.
