---
id: '331'
revision_added: rev0273
status: canon
object_type: integrity_gate
domain_tags:
- scarcity
- priority
- rationing
- critical_customers
- restoration
- ethics
- service_floors
service_floor:
- fair_restoration_priority
- critical_customer_continuity
- rationing_appeal
hazard_tags:
- compound_shock
- outage
- heat
- smoke
- flood
- drought
- cyber
- disease
- fuel_shortage
- staff_shortage
clock_tags:
- emergency_clock
- recovery_clock
- learning_clock
actor_tags:
- emergency_manager
- utility
- health_authority
- regulator
- public_health_agency
- community_reviewer
- ombud
- service_operator
instrument_tags:
- prioritize
- ration
- triage
- register
- appeal
- publish
- demote
- audit
routes_to:
- '29'
- '39'
- '108'
- '245'
- '252'
- '253'
- '289'
- '297'
- '303'
- '316'
- '318'
- '322'
- '323'
- '325'
source_ids:
- S536
- S587
- S588
- S589
upstream_dependencies:
- service_consequence_map
- critical_customer_registry
- operator_data
- public_authority
- appeals_channel
- communications
- records
- trusted_intermediaries
downstream_consequences:
- avoidable_death
- silent_exclusion
- trust_loss
- service_floor_collapse
- politicized_recovery
- lawsuit_without_correction
- violence_at_distribution_points
equity_lenses:
- medically_dependent_people
- disabled_people
- older_adults
- children
- pregnant_people
- low_income_households
- renters
- rural_communities
- people_without_documents
- people_without_smartphones
degraded_modes:
- published_priority_classes
- manual_queue
- community_verified_exception
- temporary_service_credit
- rotating_service
- appeal_by_phone_radio_or_in_person
evidence_grade: synthesis
speculation_level: medium
bottlenecks:
- scarce_crew
- scarce_fuel
- scarce_bed
- scarce_generator
- scarce_cash
- scarce_inspector
- scarce_route
- scarce_lab_capacity
- opaque_priority
failure_modes:
- first_loudest_served_first
- political_priority_disguised_as_lifeline
- critical_customer_registry_stale
- rationing_without_appeal
- equity_claim_without_service_test
- restoration_priority_hides_exclusion
proof_ledgers:
- priority_rule_register
- critical_customer_registry
- rationing_decision_log
- appeal_log
- exception_log
- service_restoration_queue
- after_action_priority_audit
restoration_conflicts:
- life_safety_vs_economic_reopening
- hospital_vs_home_medical_dependency
- fuel_for_generators_vs_fuel_for_transport
- fast_restoration_vs_equitable_restoration
- data_privacy_vs_priority_registry
assurance_tests:
- priority_tabletop_with_real_resource_limits
- excluded_user_appeal_test
- critical_customer_registry_refresh
- manual_rationing_log_drill
- post_restoration_equity_audit
priority_class: life_safety_first_then_service_cascade_then_recovery_throughput
scarcity_rule: publish_the_rule_before_shortage_and_log_every_exception
---

# 331 — Ideal Solutions: Govern restoration priority, critical-customer registries, and rationing appeals before service floors compete

## Claim

The service-floor archive now needs a scarcity rule: **a service floor is not governed until the programme can say who receives scarce restoration first, why, how exceptions are logged, and how excluded people appeal.**

Climate shocks create simultaneous claims on the same crews, fuel, generators, transformers, beds, cash, routes, inspectors, labs, cooling spaces, police escorts, pharmacies, and communications channels. If priority is not explicit, rationing still happens — it just happens through queue order, political pressure, institutional habit, ability to travel, ability to fill out forms, ability to pay, and ability to be visible.

FEMA's lifelines frame already puts incident stabilization around essential functions [S536]. Crisis-standards and ethics guidance add the missing integrity point: scarce-resource allocation needs prior planning, transparent principles, triggers, public engagement, and reviewable decision rules [S587][S588]. Energy-security practice adds a practical fuel-and-restoration example: priority deliveries and state coordination matter when energy inputs are constrained [S589].

## Compact rule

**When service floors compete, priority should be governed by service consequence, not institutional prestige.**

The first class is immediate life safety and irreversible harm. The second is service-cascade prevention: power to water, oxygen, dialysis, telecoms, cooling, public safety, and fuel nodes that keep many other floors alive. The third is recovery throughput: repairs, inspectors, payments, route clearance, local markets, labs, and records that let many households return safely. The fourth is ordinary restoration and economic reopening.

This order is not absolute. It needs exception channels. A single medically dependent household can outrank a large commercial load. A water pump can outrank a general hospital wing if the pump preserves service for the hospital, shelter, and neighborhood. A pharmacy, cash-out point, or small repair shop can outrank a symbolic reopening if it unlocks real recovery for many people.

## Minimum packet

A serious priority packet has seven records:

1. a **priority-class table** tied to service consequence;
2. a **critical-customer registry** with consent, privacy, refresh, and substitute-proof rules;
3. a **scarce-resource map** for crews, fuel, cash, beds, transformers, lab slots, transport, and communication channels;
4. a **public trigger** for moving from routine restoration to scarcity mode;
5. an **exception and appeal path** that works without broadband or legal sophistication;
6. an **equity audit** comparing restoration order with actual harm and exclusion;
7. a **de-escalation rule** so emergency priority does not become permanent privilege.

## Failure modes

The bad versions are common. A utility protects large accounts because it knows them. A hospital gets priority while home oxygen, dialysis transport, and pharmacies fail. A cooling centre exists but no paratransit or safe route is restored. An insurer, aid office, or permit counter treats missing documents as noncompliance. A fuel plan says "critical facilities" but does not define whose generator is critical or when fossil backup must be replaced.

The archive's rule is stricter: **scarcity must leave a trail.** If a community cannot reconstruct who was served, who waited, who was denied, and why, then the programme cannot learn whether it protected life or merely protected the easiest service users.

## Cube routing

Route this file whenever a continuity packet uses words like priority, critical, essential, scarce, triage, ration, emergency delivery, critical load, critical customer, registry, fuel allocation, shelter capacity, bed capacity, service queue, or restoration order. It pairs especially with `245`, `252`, `253`, `297`, `316`, `318`, `322`, `323`, and `325`.

---
Citations point to `sources/register.md`.
