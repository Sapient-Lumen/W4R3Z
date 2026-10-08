---
id: '297'
revision_added: rev0267
status: canon
object_type: service_continuity
domain_tags:
- energy
- electricity
- critical_loads
- thermal_safety
- utility
- nuclear_energy
- clean_firm_power
- nuclear_integrated_energy_systems
- nuclear_cogeneration
- nuclear_desalination
- nuclear_hydrogen
- nuclear_data_centers
- nuclear_system_benefit
- counterfactual_dispatch
- avoided_harm_accounting
- nuclear_cyber_digital_assurance
service_floor:
- energy_continuity
- critical_load_continuity
- thermal_safety
hazard_tags:
- outage
- heat
- cold
- storm
- wildfire
- flood
- cyber
- fuel_disruption
clock_tags:
- emergency_clock
- seasonal_clock
- recovery_clock
- learning_clock
actor_tags:
- utility
- regulator
- emergency_manager
- local_government
- building_operator
- household
instrument_tags:
- prioritize
- island
- store
- reconnect
- protect
- subsidize
- disclose
routes_to:
- '252'
- '253'
- '279'
- '283'
- '284'
- '289'
- '293'
- '295'
- '298'
- '306'
- '311'
- '429'
- '434'
- '436'
- '437'
- '438'
- '442'
- '443'
- '454'
- '455'
- '456'
- '457'
- '458'
- '464'
- '465'
- '466'
- '467'
- '468'
- '497'
source_ids:
- S502
- S503
- S504
- S505
- S510
- S511
- S512
- S513
- S514
- S515
- S516
- S517
- S518
- S532
- S822
- S823
- S824
- S825
- S826
- S827
- S828
- S829
- S830
- S831
upstream_dependencies:
- generation
- transmission
- distribution
- storage
- fuel_or_charging
- staff
- telecoms
- cyber
- affordability
downstream_consequences:
- water_failure
- health_device_failure
- payment_failure
- clean_air_failure
- cooling_failure
- communications_failure
equity_lenses:
- low_income_households
- medically_dependent_people
- renters
- rural_households
- informal_settlements
- older_adults
degraded_modes:
- islanded_microgrid
- resilience_hub
- prioritized_restoration
- load_shed_protection
- emergency_bill_relief
evidence_grade: synthesis
speculation_level: medium
bottlenecks:
- grid_capacity
- backup_power
- fuel_supply
- critical_load_registry
- utility_shutoffs
- affordability
failure_modes:
- asset_ready_people_unserved
- diesel_lock_in
- shutoff_cascade
- critical_load_omission
proof_ledgers:
- critical_load_list
- restoration_log
- backup_power_log
- utility_affordability_log
- outage_duration_log
restoration_conflicts:
- hospital_vs_water_pumps
- data_centre_vs_neighborhood_load
- fuel_for_generators_vs_evacuation
assurance_tests:
- critical_load_blackstart_drill
- medically_dependent_power_test
- shutoff_protection_audit
---

# 297 — Ideal Solutions: Protect electricity, thermal safety, and critical loads as climate-critical services, not utility background

## Claim

A climate programme is not ready if it can electrify vehicles, buildings, pumps, clinics, payment systems, shelters, schools, and communications, but cannot keep their **critical service loads** available through heat, cold, smoke, flood, storm, wildfire, drought, fuel disruption, cyber disruption, or compound outage.

Clean energy is a mitigation backbone. **Energy continuity** is the protection spine that keeps that backbone useful under stress. It has to be planned as a public service floor: safe indoor temperature, medically dependent power, health facilities, water and wastewater, communications, payments, transport charging / fuel, food cold chain, shelters, elevators, refrigeration, lighting, cooling centers, repair depots, and trusted public information. Climate shocks do not wait for the grid to finish the transition, and they do not respect sector boundaries. [S502] [S503] [S504] [S505]

## Fast rule

Every delivery packet that depends on electricity, heating, cooling, fuel, batteries, communications, pumps, digital payments, elevators, refrigeration, transit, care, clinics, schools, shelters, or legal / benefit access must include an **energy-continuity proof**:

> What critical load must keep operating, for whom, for how long, at what degraded-service level, from which grid / distributed / backup / fuel / storage / demand-reduction sources, under which outage scenarios, with which equity guardrails, and with what after-action correction?

If that proof is missing, the packet is still a concept note, not a climate service plan.

## Why this belongs in the archive

This file is not a duplicate of clean-power deployment. Files `17` and `226` ask how to build, connect, operate, and balance clean power fast enough. File `235` asks how flexible demand, storage, and smart charging reduce peak stress. File `239` asks how efficiency and passive demand reduction reduce the size and cost of the system. File `252` asks whether critical services remain available under stress.

This file adds the missing public-service question: **what happens to people, care, water, transport, housing, cash, warnings, and rights when energy supply is interrupted, rationed, unaffordable, or unsafe?**

## Compact canon

1. **Measure service-hours, not just megawatts.** The minimum energy metric is not installed capacity. It is the number of critical service-hours protected for named people and functions during degraded conditions.

2. **Map critical loads before the shock.** Every jurisdiction needs a maintained critical-load register: medically dependent homes, clinics, pharmacies, shelters, cooling / warming centers, water and wastewater assets, telecom nodes, payment points, transport depots, charging hubs, fuel depots, food cold-chain nodes, elevators in high-rise housing, accessible equipment, and repair logistics.

3. **Start with passive survivability.** Insulation, shading, ventilation, cool roofs, weatherization, efficient appliances, thermal storage, water storage, and passive design reduce the load that must be protected. A building that stays safer without power is a better emergency asset than one that requires heroic backup.

4. **Use a critical-load ladder.** Separate life-safety loads, public-health loads, water / sanitation loads, communication loads, mobility / logistics loads, food loads, housing loads, household finance / payment loads, and comfort / ordinary-service loads. Load-shedding must not treat these as equivalent.

5. **Treat backup power as an operated system, not a gadget.** Backup generators, batteries, microgrids, fuel contracts, portable chargers, transfer switches, maintenance crews, spares, test schedules, cybersecurity, manual operation, and fuel / battery logistics must be funded and drilled. Untested backup is decoration.

6. **Make resilience hubs real service nodes.** Libraries, schools, community centers, faith facilities, clinics, and shelters can become energy-backed hubs only if they have operating envelopes, staffing, accessibility, communications, water, cooling / heating, device charging, medical-device accommodation, transport access, and trusted local governance. [S510] [S511] [S518]

7. **Protect medically dependent people at home.** Electricity-dependent medical devices, refrigeration for medicines, oxygen, mobility equipment, communications, and caregiver access must be visible in planning without exposing people to stigma or surveillance. The power floor must include opt-in registries, privacy controls, outreach, backup-device support, transport, restoration priority, and shelter alternatives. [S512]

8. **Make health-facility energy a care-continuity requirement.** Clinics, hospitals, pharmacies, laboratories, cold chains, dialysis, maternity care, emergency departments, and long-term-care facilities must prove reliable energy for black-sky operation, not just nominal backup generation. [S513]

9. **Plan water and wastewater as electricity-dependent services.** Pumping, pressure, treatment, monitoring, wastewater conveyance, and laboratory functions need electricity continuity and electric-provider coordination before an outage becomes a WASH failure. [S514]

10. **Name telecom, payment, and transport dependencies.** Public alerts, cell towers, broadband, ATMs, point-of-sale terminals, benefit access, traffic signals, EV charging, fuel pumping, rail operations, port cranes, depot operations, and route-status data need their own energy-continuity assumptions.

11. **Treat affordability and shutoff as continuity risks.** A household that cannot afford power, cooling, heating, refrigeration, charging, or reconnection does not have service continuity. Energy-burden, arrears, disconnection, prepayment, reconnection fees, and inefficient housing must sit inside the energy-continuity ledger. [S515]

12. **Use demand response with equity guardrails.** Flexible demand, managed charging, thermal pre-cooling, battery dispatch, and load reduction are essential, but emergency curtailment must not invisibly cut medically necessary, disability, care, refrigeration, communications, or livelihood-critical uses.

13. **Restore by service consequence, not only customer count.** Restoration sequencing should account for people whose outage consequences are severe, not merely feeders with the largest number of customers. That means combining grid topology with health, WASH, housing, transport, care, and social-protection data under strict privacy and accountability rules.

14. **Require regulators to value resilience.** Utility commissions and energy regulators need a public method for deciding which resilience investments, undergrounding, vegetation management, microgrids, sectionalizing, storage, efficiency, redundancy, cyber controls, and affordability protections are prudent because they protect public service continuity. [S517]

15. **Build clean backup with an emergency fossil exit path.** Diesel generators can be necessary in transitional emergency plans, but climate strategy should shift backup toward efficiency, solar-plus-storage, thermal storage, batteries, clean fuels where credible, and shared community assets while retaining reliability proof.

16. **Write an outage after-action ledger.** Every outage should leave a public record: who lost power, for how long, which critical loads failed, which backups worked, which households were excluded, which restoration decisions were made, which communications failed, which costs landed on whom, and which upgrades are now mandatory.

## Minimum energy-continuity packet

| Field | Minimum requirement |
|---|---|
| Critical-load inventory | Named facilities, home-dependent users, network nodes, and service functions with load profiles and priority class. |
| Outage scenarios | Heat, cold, wildfire smoke, flood, storm, drought, fuel disruption, cyber disruption, and compound events by duration and geography. |
| Degraded-service floor | What service must continue at 4 hours, 24 hours, 72 hours, 7 days, and longer. |
| Power sources | Grid path, distributed energy, microgrid, batteries, fuel, generators, mobile assets, load reduction, and mutual-aid assets. |
| Passive reduction | Efficiency, weatherization, shading, thermal safety, storage, and operational changes that reduce emergency load. |
| Equity guardrails | Medically dependent people, disabled people, older adults, children, low-income households, renters, informal settlements, rural users, no-car households, and people without digital access. |
| Affordability safeguards | Arrears, shutoff, reconnection, emergency credits, bill relief, appliance / retrofit support, and benefit access. |
| Restoration doctrine | Priority method, privacy rules, public explanation, appeals, and after-action correction. |
| Operations proof | Staffing, fuel / battery logistics, spares, transfer switches, cybersecurity, manual fallback, drills, and maintenance budget. |
| Public accountability | Metrics, outage-duration distribution, service-failure log, complaint / remedy channel, and funded correction list. |

## What this file routes to

- use `298` for blackout, brownout, backup-power, microgrid, shutoff, energy-burden, and restoration shock-absorber design
- use `17`, `226`, `235`, and `239` for clean power, grid connection speed, flexibility, storage, smart charging, efficiency, and passive demand reduction
- use `252` and `253` for critical-service continuity and risk-reducing recovery
- use `277` / `278` for WASH power dependencies
- use `279` / `280`, `283` / `284`, and `281` / `282` for health, care, disability, medically dependent people, schools, childcare, and child protection
- use `287` / `288` for housing, habitability, shelter, rent, repair, and homelessness energy risks
- use `289` / `290` for bill payment, emergency cash, benefits, debt, and payment-rail continuity
- use `293` / `294` for warning, connectivity, public information, rumor, telecom, and feedback dependencies
- use `295` / `296` for transport, charging, fuel, logistics, evacuation, depots, and last-mile access

## What this rules out

It rules out climate plans that count electrification success while ignoring outage survival. It rules out resilience plans that buy generators but do not test transfer switches, fuel, staffing, accessibility, or restoration doctrine. It rules out emergency plans that identify critical facilities but not critical homes. It rules out utility plans that protect average reliability while hiding distributional outage harm. It rules out affordability plans that treat shutoff, arrears, and inefficient housing as private problems rather than service-continuity risks.

## Compression rule

**Do not ask whether the grid is clean only. Ask whether critical services stay powered, affordable, safe, and accountable when the climate-stressed grid is degraded.**

## Rev0268 energy-continuity bridge — outages create waste and cleanup risk

Energy continuity now includes waste-system loads: transfer stations, landfill pumps / controls, scale houses, compactors, medical-waste storage, refrigeration, organics processing, charging / fuel for cleanup fleets, public communication, and mold-drying support. Outages can create spoiled food, unsafe generators, and waste-facility failure. Pair with `299` and `300`. [S532]


## rev0271 global-access note

Energy continuity is not only about advanced grids under stress. It also has a global access floor: hundreds of millions of people still lack electricity, many more face unreliable supply, and distributed renewable energy can be part of both access and resilience if maintenance, affordability, and service design are handled explicitly [S516].

---
Citations point to `sources/register.md`.


## Rev0294 nuclear integrated-energy propagation note

Rev0294 extends the nuclear-positive preference into cogeneration, district heating, process heat, desalination, hydrogen and clean molecules, data-center/AI infrastructure, critical loads, and co-product public-value scorecards. These additions are explicitly bounded by new gates NG_53–NG_66 and by sector-coupling exception rules; preference is not treated as maturity without local evidence.
