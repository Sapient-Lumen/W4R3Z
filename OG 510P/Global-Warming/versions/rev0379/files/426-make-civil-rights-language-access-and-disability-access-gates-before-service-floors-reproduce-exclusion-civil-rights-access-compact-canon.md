---
id: '426'
revision_added: rev0284
status: canon
object_type: integrity_gate
domain_tags:
- civil_rights
- language_access
- disability_access
- nondiscrimination
- service_floor_equity
- nuclear_energy
- nuclear_regulatory_legitimacy
service_floor:
- civil_rights_language_access_gate
- meaningful_access
- equal_access_before_readiness
hazard_tags:
- compound_hazard
- displacement
- heat
- flood
- smoke
- outage
clock_tags:
- emergency_clock
- recovery_clock
- learning_clock
actor_tags:
- civil_rights_office
- emergency_manager
- shelter_operator
- benefits_office
- public_information_officer
- contractor
instrument_tags:
- title_vi_review
- language_access_plan
- ada_access_check
- complaint_path
- accessible_notice
- vital_document_translation
routes_to:
- '285'
- '377'
- '385'
- '395'
- '396'
- '424'
- '440'
- '442'
- '443'
source_ids:
- S342
- S695
- S768
- S769
upstream_dependencies:
- alert_interoperability
- intake_navigation
- digital_identity_recovery
- independent_audit_redress
downstream_consequences:
- actual_access
- reduced_denials
- legal_compliance
- trustworthy_readiness
equity_lenses:
- lep_users
- people_with_disabilities
- older_adults
- children
- tribal_communities
- immigrants
- low_literacy_users
- no_smartphone_users
degraded_modes:
- phone_interpretation
- paper_forms
- in_person_navigation
- accessible_transport_dispatch
- community_intermediary
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- english_only_alerts
- forms_require_digital_access
- shelter_not_accessible
- complaints_not_actionable
- contractors_not_bound
failure_modes:
- eligible_people_excluded
- unsafe_shelter
- missed_deadline
- benefit_denial
- civil_rights_violation
- mistrust
proof_ledgers:
- language_access_plan
- translation_inventory
- interpretation_log
- accessibility_checklist
- civil_rights_complaint_register
- corrective_action_record
civil_rights_language_access_gate: readiness requires nondiscrimination, disability access, meaningful language
  access, vital-document translation, complaint path, and corrective-action evidence
---
# 426 — Make civil-rights, language-access, and disability-access gates before service floors reproduce exclusion

## Core claim

A service floor is not a floor if people cannot receive it because of language, disability, race, national origin, digital access, documentation, mobility, age, or fear of retaliation. Civil-rights compliance is therefore a readiness gate, not a legal appendix.

Joint Title VI emergency-preparedness guidance helps recipients of federal financial assistance ensure that disaster-affected people do not face unlawful discrimination based on race, color, national origin, or limited English proficiency [S768]. DOJ/OJP language-access materials say recipients must provide meaningful access to limited-English-proficient individuals, often through oral interpretation and written translation of vital documents [S769]. The archive's existing civil-rights and privacy layers already warn that disaster records, registries, shelters, and benefits can exclude or expose people if access is not designed in advance [S695][S342].

## Access-gate packet

Before a service floor is marked ready, it should prove:

- language-access plan and interpretation capacity;
- translated vital documents and plain-language notices;
- disability-access check for sites, transport, forms, and communications;
- no-smartphone and low-literacy path;
- accessible complaint and appeal route;
- contractor and subrecipient obligations;
- corrective-action process for observed exclusion.

## Equity-is-operational rule

Equity cannot be measured only after service delivery. If excluded-user paths are not tested during exercises, they will fail during shocks.

## Cube rule

The field `civil_rights_language_access_gate` tests whether readiness is access-true. Blank means the service may work only for users who resemble the designers.

---
Citations point to `sources/register.md`.
