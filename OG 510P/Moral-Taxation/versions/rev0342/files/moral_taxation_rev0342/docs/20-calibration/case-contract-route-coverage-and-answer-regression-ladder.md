# Case-contract, route-coverage, and answer-regression ladder

## Question in one sentence

How should golden cases become executable answer contracts rather than prose examples that can drift away from the cube?[S21][S27][S59][S594]

## Companion routes

Use this memo with:

- [`../10-framework/case-contract-and-route-test-harness-routing.md`](../10-framework/case-contract-and-route-test-harness-routing.md)
- [`../10-framework/release-integrity-source-bijection-and-regression-harness-routing.md`](../10-framework/release-integrity-source-bijection-and-regression-harness-routing.md)
- [`../10-framework/remedy-traceability-and-escalation-routing.md`](../10-framework/remedy-traceability-and-escalation-routing.md)
- [`../10-framework/source-hierarchy-conflict-refresh-and-current-law-routing.md`](../10-framework/source-hierarchy-conflict-refresh-and-current-law-routing.md)

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — prose-only case | the case is readable but has no machine obligation | Insufficient once the cube is used for routing. |
| B — route-only case | the case names expected routes but not axes, flags, remedies, or bad-answer blocks | Useful but incomplete; it catches broken IDs, not wrong answers. |
| C — answer contract | the case names expected routes, route-backed flags, raw axes, remedy-profile obligations, sources, and must-not answers | Default for all new golden cases. |
| D — negative regression case | the case is written specifically to catch a tempting wrong shortcut | Required for release-integrity, currentness, private-rail, and remedy-spine failures. |
| E — retirement test | the case proves a route is now redundant or stale | Use when route pruning is proposed. |

## Eight-gate ladder

1. **case identity gate** — every golden case has a stable `GC-###` identifier and continuous numeric order.
2. **route existence gate** — each expected route ID exists in `cube-index.json`.
3. **axis validity gate** — each raw case axis uses a cube axis and each raw value exists in that axis vocabulary.
4. **flag normalization gate** — expected flags use route-backed terms where possible, not generic placeholders such as `ai_error` when the route has a more precise anti-pattern.
5. **remedy-profile gate** — every expected route has a remedy profile.
6. **source gate** — each source cited by the case exists in `SOURCES.json` and, if used as currentness, is also in the currentness registry.
7. **negative-answer gate** — every case has at least one prohibited shortcut.
8. **coverage-report gate** — the release records how many routes are exercised by cases and which high-risk families lack cases.

## Defaults

| Parameter | Default | Redesign trigger |
|---|---|---|
| contract count | one contract per golden case | mismatch between `golden-cases.json` and `case-contracts.json` |
| expected flags | route-backed terms | flag is not found in route axes or remedy profile text |
| raw axes | validated against cube schema | case contains ad hoc values outside the cube vocabulary |
| remedy obligation | every expected route has a profile | route can classify but not state the corrective move |
| release action | fail the checker | contract drift, unknown route, invalid axis, missing remedy profile, or stale report |

## Anti-pattern definitions

- **orphan golden case** — the case survives in prose but no machine contract tests it.
- **decorative expected flag** — a flag appears in the case but not in the expected route, remedy profile, or axis vocabulary.
- **nearby-route substitution** — an answer chooses a related route while missing the route the case exists to test.
- **must-not evaporation** — the case’s prohibited shortcut disappears during summarization or answer generation.
- **axisless moral fact** — a morally decisive fact cannot be expressed in the cube vocabulary.

## Machine checkpoint

Run `tools/audit_case_contracts.py` before release. The audit must confirm one contract per case, valid route IDs, valid raw axes, route-backed flags, remedy-profile coverage, and a fresh case-route coverage report.

## Accountability capsule

Authoritative assignment: route `case_contract_route_coverage_answer_regression` in [`actor-accountability-profiles.json`](../00-meta/actor-accountability-profiles.json).

- Duty owner: `case_contract_maintainer_golden_case_owner_or_answer_regression_reviewer_with_expected_route_and_must_not_control`.
- Rent/benefit trace: `archive_user_policy_evaluator_or_public_body_saved_from_nearby_route_substitution_must_not_evaporation_and_axisless_moral_fact_regression`.
- Bottleneck/evidence: `golden_case_expected_route_and_flag_record; case_contract_required_profile_and_must_not_answer_channel +2 more`; evidence starts with `golden_case_expected_route_expected_flag_source_and_must_not_record; case_contract_required_remedy_policy_action_actor_profile_map +4 more`.
- Fallback duty: `archive_maintainer_must_preserve_fallback_explicit_case_contracts_route_redirects_and_failure_reports_when route coverage or answer obligations change`.


## Source IDs only

[S21][S27][S59][S594]

[S21]: ../../SOURCES.md#S21
[S27]: ../../SOURCES.md#S27
[S59]: ../../SOURCES.md#S59
[S594]: ../../SOURCES.md#S594
