---
id: '308'
revision_added: rev0270
status: canon
object_type: router
domain_tags:
- datacube
- critical_services
- interdependency
- cascading_risk
service_floor:
- cross_service_continuity
hazard_tags:
- compound_shock
- outage
- flood
- heat
- smoke
- drought
- cyber
- supply_chain
clock_tags:
- emergency_clock
- recovery_clock
- learning_clock
actor_tags:
- city
- emergency_manager
- utility
- public_health_agency
- regulator
- service_operator
instrument_tags:
- map
- stress_test
- route
- rehearse
- ledger
- after_action
routes_to:
- '252'
- '253'
- '261'
- '263'
- '301'
- '302'
source_ids:
- S536
- S563
- S603
- S607
- S608
- S612
- S614
- S616
evidence_grade: design_judgment
speculation_level: medium
bottlenecks:
- hidden_dependencies
- simultaneous_failure
- ownership_gap
- data_gap
- restoration_conflict
failure_modes:
- single_sector_readiness
- lifeline_cascade
- restoration_blindness
- duplicate_claims
- unowned_hand_offs
proof_ledgers:
- interdependency_matrix
- service_floor_checklist
- outage_cascade_log
- after_action_corrections
---

# 308 — Ideal Solutions: Map critical-service interdependencies before cascades hide inside single-sector notes

## Claim

rev0269 made service floors explicit.
rev0270 adds the next cube discipline: **no service floor should be marked ready until its dependencies and downstream consequences are mapped.**

A water packet depends on power, staff, chemicals, access roads, telecoms, payment, procurement, security, public information, and legal authority.
A cooling-refuge packet depends on buildings, power, water, transport, staff, communications, disability access, public trust, and indoor-air quality.
A food packet depends on ports, roads, fuel or charging, cold chain, workers, payments, refrigeration, public order, and waste.
A health packet depends on all of the above, plus oxygen, medicines, triage, records, waste, backup water, and family contact.

The archive should therefore stop asking only, “Does this service have a continuity plan?”
It should also ask: **what must remain true around it for the plan to work?**

FEMA's Community Lifelines already frames incident stabilization around cross-cutting lifelines rather than agency silos [S536]. UNDRR's local-resilience work likewise treats cities and municipalities as front-line systems where risk reduction depends on local governance, capacity, and inclusion [S563]. The archive should internalize the same lesson as a cube rule: **service floors are nodes in a dependency graph, not isolated topics.**

## Fast rule

**Every service-continuity packet must name at least five dependencies, five downstream consequences, and one restoration-conflict rule before being marked ready.**

## The compact canon

### 1. Separate service floor from dependency

A service floor is the minimum public function that must remain true.
A dependency is something that service needs in order to remain true.

Examples:

| Service floor | Dependencies that must be tested |
|---|---|
| safe drinking water | electricity, chemicals, staff, telecoms, roads, lab testing, public notice, payment authority |
| heat-safe shelter | cooling, ventilation, water, toilets, transport, staff, registration, security, clean air |
| medicine access | pharmacies, cold chain, payment rails, prescriptions, transport, supplier stock, records |
| school continuity | buildings, teachers, meals, WASH, transport, telecoms, child protection, records |
| debris clearance | trucks, transfer sites, disposal capacity, PPE, worker pay, road access, monitoring tickets |
| emergency cash | identity, payment rails, cash-out points, telecoms, fraud controls, appeals, legal authority |

House rule: **a dependency that is assumed but not named is a hidden failure mode.**

### 2. Map downstream consequences

Each service also protects other services.
When it fails, it creates secondary failures.

Examples:

- power failure creates water, cooling, communications, medical-device, payment, and food-cold-chain failure;
- transport failure creates evacuation, dialysis, school, food, medicine, worker, and debris-clearance failure;
- telecom failure creates warning, payment, family-reunification, benefits, claims, and rumor failure;
- waste failure creates health, housing, worker-safety, environmental-health, and recovery-delay failure;
- legal-access failure creates eviction, benefit denial, debt, family-safety, insurance, and relocation failure.

House rule: **the first failed service is rarely the last harmed population.**

### 3. Declare restoration conflicts in advance

Restoration is not neutral.
A utility, road crew, health agency, telecom provider, debris contractor, fuel supplier, police force, or emergency manager may face simultaneous demands that cannot all be satisfied first.

The packet should state how conflicts are resolved:

- hospital power vs water pumps;
- debris clearance for arterial roads vs low-income neighborhoods;
- telecom restoration for emergency operations vs household benefit access;
- fuel for generators vs fuel for evacuation transport;
- shelters for tourists vs residents;
- road access for supply chains vs accessible evacuation;
- rebuilding speed vs mold-safe and contamination-safe return.

House rule: **priority rules made during panic usually favor the loudest institution; priority rules made before panic can favor service consequence.**

### 4. Build the interdependency matrix as a lightweight artifact

The cube should maintain a small matrix rather than a giant model.
For each service floor, record:

1. upstream dependencies;
2. downstream services harmed by failure;
3. hazard sensitivity;
4. restoration owner;
5. fallback mode;
6. proof ledger;
7. equity / rights lens;
8. first route in the archive.

The first implementation lives in `cube/interdependency-matrix.csv`.
It is not complete; it is the structure that makes incompleteness visible.

House rule: **a partial matrix is better than invisible assumptions.**

### 5. Use degraded-mode tests, not only asset-status tests

A service is not ready just because the asset exists.
Test the degraded mode:

- What happens after 4 hours, 24 hours, 72 hours, 7 days, and 30 days?
- What manual procedure works if the portal fails?
- What public instruction works if mobile service fails?
- What cash / paper / radio fallback works if payment rails fail?
- What service remains for disabled people, children, older adults, undocumented people, renters, informal workers, and people in custody?

House rule: **degraded-mode realism is the difference between continuity and brochureware.**

### 6. Make after-action correction cross-service

After a shock, do not let every agency write its own isolated lesson.
The after-action ledger should ask:

- which dependency failed first;
- which service suffered second-order harm;
- which priority rule was missing;
- which data was unavailable;
- which population was invisible;
- which fallback worked;
- which procurement, staffing, code, tariff, benefit, insurance, or legal rule must change before the next event.

House rule: **a lesson learned only inside one silo is usually not learned by the system.**

## Minimum interdependency ledger

| Field | Question |
|---|---|
| service floor | What minimum public function is protected? |
| upstream dependencies | What other services, inputs, people, and authorities must work first? |
| downstream consequences | What fails if this service fails? |
| degraded modes | What still works under outage, access loss, cyber, displacement, or staffing shortage? |
| restoration conflicts | What cannot all be restored first, and who decides? |
| proof ledger | What records show continuity or failure? |
| correction trigger | What automatically changes after repeated failure? |

## What this routes to

- use `308` when a prompt asks about cascades, dependency mapping, lifelines, critical infrastructure interdependence, compound shocks, resilience prioritization, restoration order, or why a service plan fails despite having assets;
- pair with `252` for critical-service continuity;
- pair with `253` for recovery discipline;
- pair with `261` and `263` for data / cyber fallback;
- pair with the relevant service pair from `275` through `315`.

## Compression rule

**Service continuity is a dependency graph. A packet is not ready until it names what it depends on, what depends on it, what fails second, who prioritizes restoration, what degraded mode survives, and what ledger forces correction.**


## rev0271 extension — hidden rails

The first interdependency matrix named obvious service links such as power-water-health-transport. rev0271 adds hidden rails that fail sideways: medical products, telecoms / cloud / cyber, payment rails, humanitarian logistics, displacement reception, conflict sensitivity, and assurance. These rails should be treated as dependency multipliers: they rarely appear as the headline hazard, but when they fail, many service floors become unusable at once.

## Rev0272 interdependency update — recovery rails are cascade nodes

The interdependency matrix should now include recovery rails as nodes: energy inputs / black-start, repair markets, claims and assistance, floodwater controls, essential local enterprises, community bridges, agrifood inputs, and proof capacity. These are not downstream clean-up details. They are often upstream dependencies for water, health, housing, schools, food, transport, waste, legal access, and public trust.

## Rev0273 interdependency patch — scarcity is the interdependency stress test

A dependency map is incomplete until it states where several services compete for the same limiting resource. Crews, fuel, routes, cash, beds, parts, inspectors, labs, communications channels, trusted intermediaries, and public authority can be shared dependencies. The interdependency matrix should now record not only what depends on what, but what happens when many rows call for the same scarce rail at once.

## Rev0274 interdependency extension — interfaces are nodes

The interdependency graph should treat shelters, registries, verified contractors, animal shelters, fatality-management systems, cultural anchors, and last-mile roads / radios as nodes. These are not merely endpoints. If they fail, they cascade into health, housing, transport, claims, legal records, evacuation compliance, mental health, civic trust, and recovery throughput [S603][S607][S608][S612][S614][S616].


## Rev0275 interdependency note — authority dependencies are dependencies

The interdependency matrix should now include authority dependencies: land records, eligibility proof, grant cash flow, procurement files, permits, inspections, worker lodging, common-element governance, and casework closure. These do not look like pipes or wires, but they can stop water, power, housing, health, schools, waste, and transport from recovering.
---
Citations point to `sources/register.md`.
