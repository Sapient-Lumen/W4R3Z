---
id: '483'
title: 483 — Nuclear financial-assurance scorecard and publication-control audit
object_type: scoring_model
domain_tags:
- nuclear_energy
- financial_assurance_scorecard
- liability_gap_backlog
- decommissioning_publication_control
- source_authority_audit
- sensitive_publication
service_floor:
- nuclear_financial_assurance_source_authority_audit
- nuclear_liability_publication_control
- nuclear_public_risk_transfer_transparency
- nuclear_decommissioning_public_value_scorecard
- nuclear_liability_maturity_cap_execution
hazard_tags:
- financial_assurance_scorecard_greenwash
- source_authority_confusion
- sensitive_fund_or_security_disclosure
- public_backstop_underdisclosure
- liability_gap_backlog_unclosed
clock_tags:
- annual_financial_assurance_scorecard
- pre_fid_liability_maturity_gate
- publication_control_review_cycle
- public_value_scorecard_update
actor_tags:
- A_public_auditor
- A_regulator
- A_nuclear_operator
- A_ratepayer_advocate
- A_civil_rights_office
- A_public_finance_authority
instrument_tags:
- financial_assurance_scorecard
- source_authority_audit
- publication_control_boundary
- liability_gap_backlog
- maturity_cap_execution
routes_to:
- '00'
- '01'
- '02'
- '04'
- '05'
- '421'
- '422'
- '423'
- '424'
- '425'
- '426'
- '428'
- '429'
- '430'
- '431'
- '433'
- '444'
- '447'
- '448'
- '459'
- '463'
- '464'
- '468'
- '473'
- '478'
- '479'
- '480'
- '481'
- '482'
source_ids:
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
- nuclear_liability_financial_assurance
- nuclear_decommissioning_trust_oversight
- nuclear_public_risk_transfer_ledger
- source_authority_audit
downstream_consequences:
- financial_assurance_score_becomes_queryable
- liability_and_decommissioning_evidence_cap_nuclear_maturity
- publication_controls_protect_sensitive_financial_and_security_details
equity_lenses:
- plain_language_public_financial_assurance
- ratepayer_taxpayer_visibility
- host_community_right_to_challenge
- civil_rights_claims_access
degraded_modes:
- public_scorecard_without_evidence
- security_sensitive_disclosure
- underdisclosed_public_backstop
- stale_decommissioning_fund_status
evidence_grade: mixed
speculation_level: medium
revision_added: rev0299
status: canon
---

# 483 — Nuclear financial-assurance scorecard and publication-control audit

## Audit function

This file closes the rev0299 refactor by making nuclear financial assurance queryable. It adds scorecards, maturity caps, source-authority separation, gap backlogs, and publication controls so nuclear can be favored without hiding liability, compensation, cleanup, decommissioning, and public-backstop proof burdens.

## Nuclear-positive rule

The cube remains explicitly pro-nuclear. Rev0299 says that this preference is strongest when the public can see that financial protection, compensation, cleanup, decommissioning, spent-fuel, and long-term stewardship obligations are funded, governed, and challengeable.

## Refactor output

The revision introduces `cube/nuclear-financial-assurance-scorecard.csv`, `cube/nuclear-liability-propagation-audit.csv`, `cube/nuclear-liability-source-authority-audit.csv`, and `cube/nuclear-financial-assurance-maturity-cap-execution.csv`.

## Publication boundary

Public reporting should expose whether financial-protection and decommissioning gates are met. It should not publish exploitable security vulnerabilities, protected insurance-claim personal data, sensitive facility weakness details, or fund-management details that would weaken security or recovery operations.

## Sources

- [S876]
- [S877]
- [S878]
- [S879]
- [S880]
- [S881]
- [S882]
- [S883]
- [S884]
- [S885]
- [S886]
- [S887]
- [S888]
