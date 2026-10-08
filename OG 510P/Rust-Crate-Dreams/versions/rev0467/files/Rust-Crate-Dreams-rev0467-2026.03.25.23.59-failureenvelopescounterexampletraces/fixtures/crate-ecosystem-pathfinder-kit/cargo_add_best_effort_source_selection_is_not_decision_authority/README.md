# Scenario — `cargo_add_best_effort_source_selection_is_not_decision_authority`

This fixture exists to prove that **P-0509** should not treat Cargo’s convenient package-selection behavior as recommendation authority.

The review question is not “can Cargo find or add this crate?”
It is “what does that source-selection behavior actually prove for this task lane?”

## What the scenario should force

- `candidate-basis.receipt.json` should record Cargo `add` / `info` as **official tooling input**, not task-fit authority.
- `decision-axis.report.json` should keep task fit, interop fit, and lock-in cost separate from package discoverability.
- `decision-pack.report.json` should still be able to conclude `manual_review_required` even when Cargo can select a package cleanly.

## Why it matters

Cargo’s current docs explicitly say a best-effort source may come from an existing dependency, a workspace member, or the latest registry release.
That is useful ergonomics.
It is not the same thing as “this is the right starter-set choice.”
