---
id: '448'
title: 448 — Nuclear bankability/buildability scorecard and refactor audit
object_type: audit
domain_tags:
- nuclear_energy
- bankability_audit
- buildability_audit
- market_design_audit
- construction_audit
- maturity_caps
- data_quality
- nuclear_system_benefit
- counterfactual_dispatch
- avoided_harm_accounting
- nuclear_liability
- financial_assurance
- decommissioning_trust
- incident_compensation
- public_risk_transfer
service_floor:
- nuclear_finance_buildability_audit
- nuclear_bankability_case
- nuclear_creditworthy_offtake
- nuclear_construction_standardization
- nuclear_ratepayer_protection
hazard_tags:
- false_maturity
- finance_washing
- buildability_washing
- offtake_washing
- unbounded_public_exposure
clock_tags:
- revision_cycle
- portfolio_review_cycle
- pre_fid_review
- construction_readiness_review
- public_challenge_window
actor_tags:
- A_data_steward
- A_public_auditor
- A_red_team_reviewer
- A_ratepayer_advocate
- A_project_controls_office
- A_nuclear_finance_authority
instrument_tags:
- bankability_scorecard
- buildability_scorecard
- propagation_audit
- maturity_cap_execution
- red_team_docket
- data_quality_rule
routes_to:
- '421'
- '422'
- '423'
- '424'
- '425'
- '428'
- '429'
- '431'
- '433'
- '438'
- '443'
- '444'
- '445'
- '446'
- '447'
- '459'
- '460'
- '461'
- '462'
- '463'
- '464'
- '465'
- '466'
- '467'
- '468'
- '479'
- '480'
- '481'
- '482'
- '483'
source_ids:
- S776
- S801
- S802
- S803
- S804
- S805
- S806
- S807
- S808
- S809
- S810
- S811
- S812
- S842
- S843
- S844
- S845
- S850
- S876
- S877
- S878
- S879
- S880
- S881
- S882
- S883
- S884
- S885
- S886
- S887
- S888
upstream_dependencies:
- nuclear_policy_preference_ledger
- nuclear_finance_capital_stack
- nuclear_offtake_market_design
- nuclear_construction_supply_chain_control
- nuclear_public_value_safeguard
downstream_consequences:
- nuclear_preference_becomes_queryable_as_buildability_requirements
- gaps_become_backlog_items
- false_maturity_caps_become_explainable
equity_lenses:
- public_challenge
- ratepayer_protection
- host_community_benefit
- workforce_access
- intergenerational_lifecycle_cost
degraded_modes:
- declared_preference_without_table_propagation
- source_citation_treated_as_project_evidence
- audit_table_not_connected_to_maturity_caps
- sqlite_view_omits_nuclear_finance_gates
evidence_grade: mixed
speculation_level: medium
revision_added: rev0292
status: canon
---
# 448 — Nuclear bankability/buildability scorecard and refactor audit

## Claim

The nuclear-positive cube is now mature enough to audit its own preference.

Rev0289 declared the nuclear orientation. Rev0290 turned it into sequencing, fuel, water and grid routing. Rev0291 added regulatory legitimacy, security, emergency and traceability controls. Rev0292 adds the missing delivery-finance layer: bankability, offtake, market design, construction standardization, long-lead procurement, project controls, ratepayer safeguards and public value.

This file is the refactor audit. It says the nuclear preference must propagate through data structures, not only prose.

## Audit rule

A nuclear preference is considered properly codified only when it appears in:

1. canon files;
2. service floors;
3. policy preference ledger;
4. assurance gates;
5. traceability matrix;
6. evidence backlog;
7. source-quality audit;
8. maturity-cap execution;
9. SQLite query views;
10. exception and red-team ledgers.

Rev0292 therefore adds a finance/buildability propagation audit and query views. The audit asks whether each nuclear-relevant service floor has bankability, offtake, construction, public-value and project-control coverage.

## Scorecard interpretation

The scorecard is pro-nuclear but not credulous.

A service floor can be `favored_with_gates` while still capped at `R2_documented_template_only`. That is not a contradiction. It is the cube saying: build this if the public evidence arrives.

A service floor can also be `favored_but_blocked`. That means the nuclear pathway is preferred on energy-system logic but blocked by missing finance, licensing, water, fuel, waste, security, emergency, workforce or legitimacy evidence.

## Refactor consequence

From this revision forward, nuclearization means more than adding the tag `nuclear_energy`. It means routing relevant service floors into the nuclear assurance engine and giving the maturity engine enough evidence fields to say why nuclear should advance, pause, change procurement form, or fail.
