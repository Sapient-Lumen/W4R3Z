# UI Accessibility Doctor Kit fixtures

These fixtures exist to make **P-0087 UI Accessibility Doctor Kit** look implementable instead of merely aspirational.

The receiver-facing question is:

> what files should another maintainer, reviewer, or CI job receive in order to understand whether a toolkit/app emitted coherent semantics and whether a release should be blocked?

## Minimal pack for 0.1

- `toolkit-profile.schema.json` — toolkit/app identity, backend assumptions, rule-pack identity, and baseline metadata.
- `a11ydoctor.report.schema.json` — findings with node ids, severities, rule ids, evidence refs, and suggested next actions.
- `a11ygate.result.schema.json` — release/CI verdict with severity counts, diff summary, waiver usage, and manual-review status.

## Design rules

- Stay **authoring-side**: emitted semantics, doctor findings, and release gating.
- Reuse **AccessKit-shaped** node identity and semantics where possible.
- Preserve `manual-review-required` as an honest output.
- Do not pretend this fixture pack is the same thing as platform capture or legal compliance.

## Intended first scenarios

1. `missing_accessible_name_in_dialog` — a button inside a modal dialog lacks a name and should fail the doctor/gate.
2. `focus_order_regression` — a rerender changes keyboard traversal order and should produce a semantic diff and a warning/fail depending on policy.


## Added 2026-03-19

This pass promotes three more first-class review objects for **P-0087**:

- `semantic-contract.report.schema.json` — what authoring-side tree the toolkit/app is actually claiming
- `rule-authority.policy.schema.json` — which findings are structural, standards-inspired, toolkit-specific, or manual-review-only
- `baseline-drift.report.schema.json` — how names/roles/states/focus/node identity changed across snapshots

New scenario families:

1. `virtualized_list_recycles_node_identity_and_breaks_diff` — diff quality collapses when semantic node ids churn
2. `icon_only_button_name_comes_from_tooltip_requires_manual_review` — name derivation that should remain semi-automatic/manual-review territory
3. `canvas_textbox_reports_focus_but_not_value_or_selection` — text controls that exist and focus correctly while still under-reporting value/selection semantics
