---
id: '475'
title: 475 — Nuclear operator licensing, training, simulator, and requalification assurance
object_type: assurance_case
domain_tags:
- nuclear_energy
- operator_licensing
- training_simulator
- requalification
- operations_assurance
- human_performance
service_floor:
- nuclear_operator_licensing_pipeline
- nuclear_simulator_training_capacity
- nuclear_requalification_program
- nuclear_operator_fatigue_control
- nuclear_control_room_succession
hazard_tags:
- licensed_operator_shortage
- simulator_capacity_gap
- requalification_failure
- operator_fatigue
- knowledge_decay
clock_tags:
- operator_exam_window
- annual_requalification_cycle
- outage_staffing_cycle
- shift_crew_readiness_review
actor_tags:
- A_nrc
- A_nuclear_operator
- A_training_provider
- A_simulator_vendor
- A_operations_manager
- A_public_auditor
instrument_tags:
- operator_licensing_pipeline
- simulator_capacity_ledger
- requalification_audit
- human_performance_control
routes_to:
- '00'
- '01'
- '02'
- '03'
- '05'
- '17'
- '226'
- '247'
- '297'
- '421'
- '422'
- '423'
- '425'
- '426'
- '427'
- '428'
- '429'
- '430'
- '431'
- '432'
- '433'
- '434'
- '435'
- '436'
- '437'
- '438'
- '439'
- '440'
- '441'
- '442'
- '443'
- '444'
- '445'
- '446'
- '447'
- '448'
- '449'
- '450'
- '451'
- '452'
- '453'
- '454'
- '455'
- '456'
- '457'
- '458'
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
- '469'
- '470'
- '471'
- '472'
- '473'
- '474'
- '476'
- '477'
- '478'
source_ids:
- S868
- S869
- S870
- S871
- S872
upstream_dependencies:
- nuclear_policy_preference_ledger
- nuclear_assurance_gate_engine
- workforce_capacity_model
- regulator_capacity_model
downstream_consequences:
- nuclear_preference_is_capped_by_human_capital_evidence
- training_and_regulator_capacity_become_queryable
- quality_culture_and_knowledge_retention_are_maturity_gates
equity_lenses:
- high_road_workforce_development
- host_community_benefit
- public_sector_regulator_capacity
- just_access_to_training_pathways
degraded_modes:
- paper_reactor_without_people
- accelerated_licensing_without_regulator_capacity
- safety_culture_decay
- training_pipeline_greenwash
evidence_grade: mixed
speculation_level: medium
revision_added: rev0298
status: canon
---

# 475 — Nuclear operator licensing, training, simulator, and requalification assurance

## Nuclear-positive rule

Nuclear energy can count as clean firm capacity only if competent licensed people can safely operate the plant across normal, abnormal, outage, emergency, flexible-operation, and degraded-grid conditions.

## Assurance case

Operator licensing, simulator training, requalification, fatigue management, control-room succession, and emergency role depth are now explicit maturity gates. The cube uses NRC operator licensing references as a model for a testable licensing pipeline: facility training, written examination, operating test, simulator performance, and continued requalification.

## Anti-false-maturity rule

No nuclear service floor can rise above documented-template maturity if operator licensing, simulator capacity, requalification, fatigue control, and shift-crew succession evidence are missing or stale.

## Cube products

The main artifacts are `cube/nuclear-operator-licensing-pipeline.csv`, `cube/nuclear-training-credential-crosswalk.csv`, `cube/nuclear-operator-training-qualification.csv`, and `cube/nuclear-human-capital-maturity-cap-execution.csv`.

## Sources

- [S868]
- [S869]
- [S870]
- [S871]
- [S872]
