# Scenario — `docsrs_default_target_shift_changes_visible_support_story`

This fixture exists to prove that **P-0509** should not treat docs visibility on docs.rs as identical to real support scope.

The review question is not “did the docs render?”
It is “did the visible documentation surface change for reasons that should or should not alter a starter-set recommendation?”

## What the scenario should force

- `evidence-origin.report.json` should separate **official docs.rs policy** from crate-authored support claims.
- `freshness-window.policy.json` should treat a docs-surface change as something worth importing and reviewing, but not automatically as task-fit truth.
- `starter-set-scope.report.json` should say whether a target-specific starter set was actually intended.
- `decision-pack.report.json` should avoid overreacting when target visibility changes but the underlying task scope did not.

## Why it matters

docs.rs changed its default target list in October 2025.
That affects what users see by default, but not every visible change should rewrite the ecosystem’s boring default recommendations.
