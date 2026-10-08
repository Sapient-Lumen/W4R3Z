---
id: '251'
revision_added: pre_rev0269
status: canon
object_type: delivery_packet
domain_tags: []
service_floor: []
hazard_tags: []
clock_tags: []
actor_tags: []
instrument_tags: []
routes_to:
- '13'
- '123'
- '230'
- '244'
- '245'
- '246'
- '250'
- '252'
- '253'
- '254'
- '263'
- '264'
- '283'
- '284'
- '285'
- '286'
- '287'
- '288'
- '289'
- '290'
source_ids:
- S40
- S123
- S127
- S203
- S204
- S205
- S206
- S230
- S237
- S261
- S262
- S263
- S264
- S265
- S266
- S267
- S268
- S301
- S303
- S305
- S306
- S307
- S382
- S384
- S386
- S387
- S389
- S391
- S392
- S395
- S397
- S398
- S400
- S401
- S405
- S408
- S409
- S412
- S413
- S415
- S416
- S417
- S419
- S421
- S422
- S424
- S425
- S431
- S434
- S438
- S441
- S444
- S449
- S450
- S453
- S457
- S459
- S461
- S467
- S468
- S474
- S476
- S482
- S487
- S488
- S491
- S494
- S502
- S505
- S508
- S521
- S524
- S531
upstream_dependencies: []
downstream_consequences: []
equity_lenses: []
degraded_modes: []
evidence_grade: design_judgment
speculation_level: mixed
---
# 251 — Ideal Solutions: Stress-Test Delivery Packets Against Compound Shocks Before Calling Them Ready Compact Canon

## Claim

Rev0239 turned the climate answer into a governed work queue.
Rev0240 added overshoot discipline and an implementation ledger.
Rev0241 added scarce-capacity allocation and large-load entry.
Rev0242 added ready project shelves and procurement platforms.
Rev0243 added crews, commissioning, operations, maintenance, and aftercare.

The next missing layer is **bad-day service**.
A packet can be well formed, financed, procured, staffed, commissioned, and maintained in ordinary conditions — and still fail the climate programme if it cannot operate during the shocks that climate change, electrification, geopolitical stress, cyber risk, supply-chain fragility, and infrastructure ageing are making more common.

The archive already says stable clean service is the completion gate.
Rev0244 adds the corollary: **stable clean service has to be tested under stress, not only during normal operation.**

The reason is physical and political.
A heat pump that works in mild weather but fails in a heatwave or cold snap can turn a clean default into a trust failure.
A hospital solar-and-battery system that cannot island, maintain cooling, or power critical equipment during an outage is a ribbon-cutting asset, not resilience.
A water system that depends on an unprotected grid, unmaintained pumps, or a single road corridor can become a cascading-failure amplifier.
A data centre, electrolyser, or charging depot that claims flexibility on paper but cannot actually reduce or shift load during grid stress is not a grid citizen.
A flood, fire, smoke, or heat plan that has never been drilled is not yet civil protection.

Current evidence makes this layer harder to ignore. WMO's 2026 State of the Global Climate 2025 says 2015–2025 were the hottest 11 years on record, 2025 was the second or third warmest year on record at about 1.43 °C above 1850–1900, extreme weather affected millions and cost billions, and the Earth energy imbalance reached the highest level in the 65-year record [S263]. UNDRR's GAR 2025 says direct disaster costs are about USD 202 billion per year, but closer to USD 2.3 trillion per year when cascading and ecosystem costs are counted [S40]. IEA's 2026 energy-system resilience work draws the operating lesson from Ukraine and wider resilience practice: energy security has long-term infrastructure and short-term resilience dimensions, and resilience is the ability to cope with events that exceed standard planning conditions, including cyberattacks, physical attacks, extreme weather, severe weather, and unexpected infrastructure failures [S261]. WHO's summary of the 2025 Lancet Countdown adds the health version: 12 of 20 health-threat indicators reached record levels, heat-related mortality has risen 23% since the 1990s to about 546,000 deaths per year, and heat exposure caused about 640 billion potential labour hours to be lost in 2024 [S262].

So the next discipline is simple: **do not call a climate packet ready until it has a stress-test path.**

Rev0250 adds a digital-stress corollary: the stress test should include cyber incidents, data-system outages, model failure, platform lockout, vendor failure, false automation, and loss of remote control, because climate packets increasingly depend on connected records, devices, and platforms; see `263` and `264` [S301][S303][S305][S306][S307].

## Fast rule

**Every serious delivery packet should carry two readiness claims: routine-service readiness and stress-service readiness. The stress-service claim should name the compound shocks it is tested against, the critical dependencies that might fail, the minimum service floor during degradation, the people or assets protected first, the clean backup or fallback path, the drill / exercise cadence, the recovery-time target, and the correction trigger if the packet fails under stress.** [S40][S123][S203][S204][S205][S206][S230][S237][S261][S262][S263]

## Why this note is not redundant

- `13` says **adaptation is civil protection**.
- `123` compresses the **off-normal state machine**.
- `230` says **protection speed and resilience throughput help determine programme durability**.
- `244` says **queue items must become owner-led delivery packets**.
- `250` says **stable clean service, not first installation, is the completion gate**.
- this note says **the delivery packet must also say how the clean or protective service behaves under compound stress**.

The distinction matters.
Normal-operation success can hide climate failure.
A clean service that only works under benign conditions may become brittle exactly when people most need it.

House rule: **a packet is not ready for a hotter world if it has only been designed for a normal day.**

## The compact canon

### 1. Separate routine, peak, degraded, emergency, and recovery states
Every packet should define at least five operating states:

| State | Meaning | Example question |
|---|---|---|
| Routine | ordinary operation | does the clean service work and displace the dirty default? |
| Peak | high demand, but system intact | does the service still work during peak heat, cold, traffic, water, or load? |
| Degraded | one or more dependencies partially fail | what happens if grid, road, staff, water, telecom, fuel, data, or supplier access is constrained? |
| Emergency | life safety, essential continuity, or major exposure risk is active | who gets protected first and what minimum service must continue? |
| Recovery | restoration, learning, compensation, and rebuilding decisions | does the system return cleaner and safer, or rebuild the same vulnerability? |

House rule: **one completion claim cannot cover all operating states.**

### 2. Test compound shocks, not single-hazard averages
The stress test should not ask only whether the asset survives one design event in isolation.
It should ask what happens when hazards stack:
- heatwave plus grid outage
- flood plus telecom failure
- drought plus hydropower shortage plus cooling demand
- wildfire smoke plus hospital surge plus transport disruption
- storm damage plus supply-chain delay
- cyberattack plus public-communications failure
- platform outage plus support-payment failure
- model error plus automated denial of critical support
- DER control failure plus feeder stress
- fuel-price shock plus household arrears
- displacement plus school, clinic, or shelter load
- transformer shortage plus new large-load connection pressure

House rule: **single-hazard design can understate real climate risk when systems fail together.**

### 3. Map dependencies before they fail
A stress-tested packet should map the dependencies that make the service real:
- electricity
- water
- telecoms and data
- roads and transport
- fuel and backup supply
- staff availability
- cooling, heating, and ventilation
- spare parts
- finance and payment systems
- emergency communications
- vendor support
- public authority
- social support and access

For each dependency, the packet should say whether it is hard, redundant, islandable, substitutable, or a single point of failure.

House rule: **unmapped dependencies become invisible tripwires.**

### 4. Define the minimum service floor
Not every service can remain perfect in a shock.
But serious governance should state the minimum acceptable service before the shock arrives.

Examples:
- a clinic keeps critical care, refrigeration, communications, and safe indoor temperatures
- a school or cooling centre remains safe for specified hours or days
- a water system maintains minimum potable supply and sewage safety
- a transit agency keeps lifeline routes operating
- a distribution feeder protects critical customers and restoration priorities
- a retrofit keeps indoor temperatures within a survivable range during outage
- a data centre or industrial load curtails without destabilising the grid

House rule: **degraded service should still be governed service, not improvisation.**

### 5. Put vulnerable people and critical services into the first test case
Do not begin with the median customer, median asset, or average weather file.
Begin with the people and services for whom failure is most dangerous:
- older adults
- infants and children
- people with disabilities
- medically dependent people
- outdoor workers
- tenants and low-income households
- informal settlements
- care facilities
- hospitals, clinics, schools, shelters, and water systems
- evacuation routes, telecom nodes, grid-control rooms, and food / medicine cold chains

House rule: **a system that protects the average while abandoning the exposed is not climate protection.**

### 6. Prefer passive survivability before active rescue
Stress tests should reward designs that reduce dependence on perfect active systems:
- insulation, shade, reflective surfaces, ventilation, and passive cooling
- floodable or sacrificial ground floors where appropriate
- water storage and leakage reduction
- efficient equipment that lowers peak load
- thermal storage and pre-cooling where safe
- safe walkable access to shelters and care
- redundant communications and manual override
- distributed storage and islanding where justified

House rule: **the best backup is often lower demand and higher passive tolerance before the emergency.**

### 7. Keep fallback narrow, clean, and temporary
Some emergency fallback may be unavoidable.
But fallback should not become a permanent fossil loophole.
The packet should specify:
- what fallback is allowed
- how long it can run
- which emissions, pollution, or fuel risks it creates
- which cleaner alternative will replace or narrow it
- what evidence must be published
- what exit test closes the fallback

House rule: **bad-day fallback must not quietly become routine dirty service.**

### 8. Drill the handoff chain
Stress readiness is not proven by a document alone.
The actors who must perform should rehearse:
- trigger detection
- alerting
- authority transfer
- dispatch or curtailment
- emergency procurement
- shelter or cooling-centre operation
- restoration priority
- public communication
- grievance and remedy
- after-action correction

House rule: **a plan that has never been exercised is still a theory.**

### 9. Add stress-test results to allocation and procurement
A scarce-capacity system should prefer packets that remain useful under stress.
Procurement and allocation should therefore ask:
- does this packet reduce stress on other systems?
- does it protect critical services?
- does it add flexible capacity?
- does it have passive survivability?
- does it avoid dirty fallback?
- does it have tested O&M and staffing?
- does it create a replicable resilience archetype?

House rule: **brittle packets should not outrank resilient packets merely because they look cheaper on a normal day.**

### 10. Turn every failed stress test into a design update
A failed drill, outage, heat event, flood, smoke episode, or user-support breakdown should update:
- reference designs
- commissioning tests
- procurement specifications
- tariff and payment rules
- staff and training plans
- spare-parts rules
- siting and land-use rules
- fallback limits
- public communication
- compensation and remedy

House rule: **stress failure should harden the archetype, not merely explain the incident.**

### 11. Test the recovery path, not only the emergency moment
Rev0245 adds the post-event stress case. A packet is not fully stress-tested if it preserves service during the first shock but leaves people to rebuild the same exposure, absorb uninsured losses silently, or wait for improvised recovery finance. Stress tests should therefore include recovery finance, safer-rebuild gates, clean replacement defaults, residual-loss ledgers, and retreat / buyout options where repeated protection is no longer credible [S264][S265][S266][S267][S268].

House rule: **the bad-day test includes what the system does the week, month, and year after the bad day.**

## Stress-test ledger in one view

| Packet type | Normal completion claim | Stress-test question | First stress proof |
|---|---|---|---|
| Clean heat / retrofit | installed and commissioned | does the home remain safe and affordable in heat, cold, outage, or tenant turnover? | 12–24 month performance plus outage / peak-temperature protocol |
| Efficient cooling | appliance or district system works | does cooling protect health without breaking the peak or leaking refrigerants? | indoor-temperature, peak-load, and refrigerant records |
| Grid upgrade | capacity connected | does the feeder or substation operate through heat, storm, fire, cyber, or restoration stress? | reliability, restoration, and critical-load continuity data |
| Bus / charging depot | buses and chargers operating | what happens during outage, heat, traffic disruption, or route surge? | route continuity and depot backup test |
| Hospital / clinic resilience | equipment installed | can critical care, refrigeration, cooling, water, telecoms, and staff access continue? | drill and real-event continuity record |
| Water packet | infrastructure built | what happens during drought, outage, flood contamination, or pump failure? | minimum-service and water-quality continuity record |
| Large-load entry | load approved with clean supply | can the load curtail, shift, island, or provide grid services when stress hits? | tested flexibility and public stress-event performance |
| Retreat / safer rebuilding | plan approved | does recovery reduce exposure or rebuild the same loss loop? | repeat-loss reduction and protected continuity |

## What this note demotes

This note demotes:
- normal-weather commissioning as the only proof of readiness
- single-hazard resilience plans for compound-risk systems
- resilience assets with no drills, staff, O&M, or restoration priority
- backup systems that increase long-run fossil lock-in
- flexibility claims that are not tested during actual or simulated grid stress
- adaptation plans that do not state minimum service floors
- procurement that buys cheap normal-day performance and ignores bad-day brittleness
- after-action reports that do not change standards, contracts, or designs

## Preferred use

Open this note first when the live question is any of the following:
- how do we know whether a climate packet works under compound stress
- how should stable clean service be tested beyond normal commissioning
- what should be in a resilience stress test for buildings, grids, water systems, hospitals, schools, cooling, transit, or large loads
- how to prevent emergency fallback from becoming fossil lock-in
- how to connect adaptation, reliability, O&M, and procurement into one readiness test

Then reopen:
- `250` for stable-service completion
- `252` for critical-service continuity packages
- `253` for recovery discipline
- `254` for protection-gap governance
- `123` for the off-normal state machine
- `230` for protection-speed doctrine
- `245` for scarce-capacity allocation
- `246` for large-load entry

## Compression rule

**Do not call a delivery packet ready just because it works on a normal day. A serious packet should be stress-tested against compound shocks, dependency failures, degraded-service states, vulnerable-user needs, backup limits, drills, recovery finance, protection-gap ledgers, and correction triggers — so clean service and protection survive the bad days that are now part of the climate operating environment.**

## Rev0258 addendum — stress tests must include health signals and disease ecology

Rev0258 adds a health stress-test. A packet is not compound-shock ready if it can keep assets running but loses the health signal, the care floor, the medicine cold chain, the health workforce, the vector-control route, the WASH outbreak-prevention route, or the One Health coordination needed to stop a climate shock from becoming an avoidable disease or care-continuity crisis.

Minimum stress-test additions: heat plus outage plus clinic surge; flood plus sewage plus diarrhoeal disease; drought plus water storage plus dengue risk; displacement plus shelter crowding plus vaccination / WASH / ventilation gaps; smoke plus respiratory care and clean-air access; road outage plus medicines and cold chain; animal / land-use change plus zoonotic surveillance; and post-shock mental-health and chronic-care continuity [S382][S384][S386][S387][S389][S391][S392].

The test is not whether someone wrote “public health” in the risk register. It is whether a signal triggers a funded action before caseloads, deaths, stigma, or emergency improvisation prove the packet was incomplete.

## Rev0259 addendum — stress-test child service continuity explicitly

Compound-shock stress tests should now include child-service continuity. Test whether a heatwave plus outage closes schools, whether flood plus displacement breaks enrollment and WASH, whether smoke plus disease surge interrupts childcare and care work, whether food-price spikes break school meals, whether shelters create child-protection risks, and whether remote learning excludes children without power, devices, internet, disability support, or safe homes.

A packet is not ready if its failure mode is "children wait until adults recover the assets." Stress tests should prove that schools, childcare, meals, records, teacher capacity, child protection, psychosocial support, and youth communication have fallback modes [S395][S397][S398][S400][S401][S405].

## Rev0260 addendum — stress tests must include functional dependencies

Rev0260 adds a functional-dependency stress test. A packet that survives an asset-level stress test can still fail if older adults, disabled people, medically dependent people, home-care users, and long-term-care residents cannot receive warnings, keep oxygen powered, keep medicines cold, reach cooling, use toilets, travel with devices, communicate, receive personal assistance, or return to an accessible home.

Every compound-shock test should therefore include at least one access-and-care scenario: heat plus outage for powered medical-device users; smoke plus care-worker absence; flood plus paratransit failure; water contamination plus care-home staffing shortage; evacuation plus lost assistive devices; recovery portal failure plus inaccessible documentation. See `283` and `284` [S408][S409][S412][S413][S415][S416][S417].

## Rev0261 addendum — stress tests must include labour shock and paid safety

Compound-shock stress tests now include a labour layer. A packet is not ready if it assumes that workers can keep building, repairing, cleaning, teaching, caring, driving, distributing, inspecting, and restoring through heat, smoke, flood, outage, disease exposure, school closure, or care disruption without safe schedules, paid safety, backup staffing, transport, childcare, or stop-work authority.

The stress-test question is: when the hazard fires, what changes in the work and who pays for the change? Use `285` for worker-continuity proof and `286` for labour shock absorption [S419][S421][S422][S424][S425].

## Rev0262 stress-test patch — can households stay safely housed?

Add a housing compound-shock test. Assume a heat wave, smoke episode, flood, outage, water contamination, school closure, care disruption, wage interruption, and repair-market surge arrive together. The packet is not ready unless it can show who stays safely housed, who moves temporarily, who pays, who repairs, who protects tenants and informal residents, who serves people without housing, and how receiving places avoid rent spikes and overcrowding.

Failure signals include unsafe indoor heat, smoke-filled homes, moldy returns, inaccessible shelters, unpaid temporary accommodation, eviction filings, rent spikes, repair fraud, contractor shortage, public-housing repair queues, and homelessness inflow. See `287` and `288` [S431][S434][S438][S441].

## Rev0263 addendum — stress-test the payment and debt layer

Compound-shock stress tests now need a household-finance scenario. Ask what happens when heat, smoke, flood, outage, school closure, work stoppage, housing damage, and telecom failure coincide with missed wages, blocked benefits, lost IDs, bank / agent closure, cash-out failure, food-price spikes, rent due dates, utility arrears, insurance deductibles, remittance interruption, and scams.

A packet is not ready if the only safe behaviour assumes spare savings, a working phone, a formal account, a stable address, a clean document set, a patient landlord, no debt collector, and no fraud. Use `289` and `290` [S444][S449][S450][S453][S457].

## Rev0264 stress-test addendum — test legal clocks, proof, and claim routes

Compound-shock stress tests now include legal-continuity failures. A packet should be tested against mailed notices that never arrive, online portals down, legal-aid offices flooded, ID and lease papers destroyed, phones lost, courts closed, deadlines running, agencies understaffed, benefits denied by an automated flag, landlords filing evictions, employers retaliating, insurers disputing coverage, debt collectors accelerating, and displaced people crossing jurisdictional boundaries.

Readiness rule: **if the legal clock keeps running while the life-support system is broken, the packet fails the stress test.** Use `291` and `292` [S459][S461][S467][S468].

## Rev0265 stress-test addendum — break the communication layer on purpose

Compound-shock stress tests now need a communications failure round: cell network down, power out, radio transmitter offline, app unreachable, siren ambiguous, social media rumor spreading, hotline overloaded, local language missing, disabled users excluded, shelter map stale, and official / independent media messages conflicting.

Stress-test rule: **a packet that survives the modelled hazard but fails the communication outage has not survived the hazard.** Use `293` and `294` [S127][S474][S476][S482].

## Rev0266 stress-test addendum — access degradation

Every delivery packet should now be stress-tested against transport degradation: one bridge out, one depot flooded, one transit workforce shortage, one paratransit surge, one fuel / charger outage, one port or warehouse delay, one rural road closure, one route-status data failure, and one no-car evacuation demand spike.

A packet passes only if it can still move the protected people, goods, crews, records, and supplies within the safe window or can support shelter-in-place resupply where movement is unsafe [S487][S488][S491][S494].

## Rev0267 stress-test patch — outage cascade test

Every compound-shock stress test now includes an outage branch: heat + grid stress; storm + telecom outage; flood + substation failure; wildfire + planned shutoff; cold snap + gas / power constraint; cyber + payment outage; drought + hydropower / cooling constraint; and transport disruption + fuel / charging failure. Passing requires proof that critical loads, medically dependent people, WASH, health, warnings, transport, payments, shelters, and care continue at defined degraded-service levels. [S502] [S505] [S508]

## Rev0268 stress-test addition — debris and contamination stress

Stress tests now include debris and environmental-health failure: blocked access, clogged drains, mixed hazardous streams, spoiled-food surges, medical-waste interruption, mold, landfill or transfer-station bottlenecks, worker exposure, temporary debris-site conflict, contaminated-site release, and household cleanup debt. A packet that passes power and transport tests but fails cleanup is not ready. [S521] [S524] [S531]

---
Citations point to `sources/register.md`.
