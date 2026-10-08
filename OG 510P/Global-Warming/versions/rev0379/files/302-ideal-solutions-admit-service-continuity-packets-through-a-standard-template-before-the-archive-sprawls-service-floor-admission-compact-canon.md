---
id: '302'
revision_added: rev0269
status: canon
object_type: router
domain_tags:
- service_floors
- admission_rule
- template
- archive_governance
service_floor:
- service_floor_admission
hazard_tags:
- archive_sprawl
- missing_service_floor
- duplicated_pattern
clock_tags:
- learning_clock
actor_tags:
- archive_operator
- reviewer
- service_owner
instrument_tags:
- screen
- admit
- route
- template
- reject
- merge
routes_to:
- '90'
- '91'
- '92'
- '301'
- '308'
- '322'
source_ids:
- S603
- S605
- S607
- S608
- S612
- S614
- S616
- S618
- S698
- S699
- S712
upstream_dependencies:
- admission_rule
- cube_schema
- source_register
- reviewer_discipline
downstream_consequences:
- sprawl
- weak_service_packets
- router_confusion
equity_lenses:
- missed_users
- invisible_dependencies
degraded_modes:
- route_to_existing_file
- add_index_row_without_new_note
- quarantine_draft
evidence_grade: design_judgment
speculation_level: medium
bottlenecks:
- hidden_template
- unowned_service_floor
- weak_ledgers
- unclear_routes
failure_modes:
- new_note_for_existing_pattern
- missing_owner
- no_degraded_mode
- no_proof_ledger
proof_ledgers:
- admission_decision
- service_continuity_template
- cube_index
restoration_conflicts:
- coverage_depth_vs_archive_size
assurance_tests:
- net_new_screen_test
- dependency_test
- degraded_mode_test
---
# 302 — Ideal Solutions: Admit service-continuity packets through a standard template before the archive sprawls

## Claim

The late archive discovered a powerful pattern: climate shocks do not only damage sectors.
They interrupt services.
People are harmed when water, health care, schools, care, food, transport, power, communications, housing, legal help, cash, labour protection, waste, and public safety stop working at the same time.

That discovery is correct.
But it creates a new risk: every new service floor can become two more long notes, plus addenda everywhere, until the archive becomes a service encyclopedia.

The answer is not to stop admitting service floors.
The answer is to standardize admission.

## Fast rule

**A new service-continuity note should be admitted only if it names a minimum service floor, the shock cascades around that floor, the owners, the degraded modes, the equity / rights layer, the proof ledger, and the correction path. Otherwise it belongs inside an existing file or the cube index.**

## The service-continuity card

Every service floor should be expressible on one card before it becomes prose.

| Field | Required answer |
|---|---|
| Service floor | What minimum service must remain available under degraded conditions? |
| Users | Who depends on it, including people normally missed by formal systems? |
| Hazards | Which shocks disrupt it? |
| Dependencies | Which other services must work first? |
| Owners | Who owns readiness, live operation, recovery, and correction? |
| Triggers | What warning, threshold, outage, price, injury, denial, or complaint opens the packet? |
| Degraded mode | What is the safe fallback when full service cannot operate? |
| Allocation rule | Who gets priority when capacity is scarce? |
| Access rule | How do people get the service without impossible proof, money, language, mobility, digital, or legal barriers? |
| Worker rule | How are workers protected while maintaining service? |
| Data rule | What is measured, what is protected, and what is published? |
| Finance rule | Who pays for readiness, live response, recovery, and remedy? |
| Integrity rule | What prevents fraud, capture, exclusion, dumping, coercion, or false closure? |
| After-action rule | What must change before the next shock? |

A packet that cannot fill this card is not ready.

## Service floor versus shock absorber

The archive should keep the distinction sharp.

A **service-continuity note** says what minimum service must remain true.
A **shock-absorber note** says how to keep failure from cascading when the service is strained.

Examples:

- `277` names the WASH service floor; `278` governs drought, groundwater, allocation, and water-quality cascades.
- `279` names climate-health continuity; `280` governs disease-ecology cascades.
- `297` names energy continuity; `298` governs outages, shutoffs, backup power, and energy burden.
- `299` names waste continuity; `300` governs debris, mold, contaminated sites, temporary debris sites, and environmental-health closure.
- `303` names public-safety continuity; `304` governs response overload, search and rescue, mass casualty, mortality, missing persons, and family reunification.

House rule: **the floor says what must stay true; the absorber says what happens when it starts to fail.**

## The minimum service-floor test

A candidate service floor deserves admission when all five conditions hold.

### 1. Failure causes harm beyond inconvenience

The service must protect life, health, rights, shelter, livelihood, mobility, communication, food, water, care, safety, or recovery.

A service may be mundane and still critical.
Solid waste, document recovery, and cash access are good examples.

### 2. Climate shocks predictably disrupt it

The service must have identifiable failure modes under heat, flood, wildfire, smoke, drought, storm, outage, disease, displacement, price shock, supply-chain shock, or compound stress.

### 3. It depends on other services

A service floor belongs in the archive when it is interdependent.
Schools need water, power, meals, safe routes, teachers, records, cooling, and protection.
Waste cleanup needs transport, workers, legal authority, landfills, information, health guidance, and public finance.

### 4. The market will not protect the floor by default

If normal market incentives, household resources, or fragmented institutional duties routinely leave people out, the service needs a public rule.

### 5. It has a measurable readiness ledger

If the floor cannot be measured, inspected, drilled, or corrected, the file risks becoming moral aspiration rather than operating doctrine.

## The shock-absorber admission test

A candidate shock absorber deserves admission when the cascade is distinct enough to need its own routing.

The file should name:

- triggers;
- scarce-capacity allocation;
- degraded modes;
- unsafe shortcuts;
- fraud / capture / exclusion risks;
- worker risks;
- environmental or public-health externalities;
- after-action metrics;
- correction duties.

If the cascade is merely a subcase of an existing absorber, add it to that absorber and update the cube tags instead of creating a new numbered file.

## The rights and proof screen

Every service floor must answer these proof questions.

1. Can people use it without title, lease, standard ID, bank account, smartphone, fixed address, immigration safety, car ownership, English literacy, or normal working hours?
2. Does the packet protect children, older adults, disabled people, medically dependent people, renters, informal workers, migrants, Indigenous Peoples, unhoused people, prisoners, and people in institutions where relevant?
3. Are denials appealable?
4. Are deadlines tolled during shock conditions?
5. Are records portable?
6. Can people complain safely?
7. Does a missed service trigger remedy or only explanation?

House rule: **a service floor that only reaches the administratively legible is not a service floor.**

## The worker screen

Every service floor must ask who is expected to keep working while others shelter, evacuate, cool, recover, or wait.

The packet should include:

- heat, smoke, flood, disease, violence, and fatigue controls;
- paid safety and stop-work authority;
- childcare, family-care, transport, water, sanitation, rest, and PPE;
- wage and contract protections;
- migrant and informal-worker safety;
- post-exposure health follow-up;
- after-action injury and retaliation data.

House rule: **continuity that consumes workers is not continuity.**

## The degraded-mode screen

A service packet should not pretend full service will always survive.
It should name safe degradation.

Examples:

- paper fallback for digital benefit systems;
- water distribution when piped service fails;
- safe learning day alternatives when schools close;
- cooling refuge when homes are unsafe;
- paratransit evacuation when ordinary transit fails;
- manual dispatch when cloud systems fail;
- mobile clinics when facilities are damaged;
- public pickup when household debris removal is impossible;
- cash fallback when digital payments fail.

House rule: **failure to name a degraded mode is a plan to improvise.**

## The correction ledger

Each service floor should leave behind an after-action ledger with four columns.

| Missed floor | Who was affected | Why it failed | Funded correction |
|---|---|---|---|
| Example: cooling centre unreachable | older adults without cars | no paratransit trigger | accessible transport contract and route-status integration |
| Example: debris pickup missed informal settlement | households without title or standard address | address proof rule | no-document set-out protocol and community pickup map |
| Example: benefit cash-out failed | people without bank access | digital-only payment design | cash / voucher fallback and mobile agent contract |

A correction ledger is not a blame exercise.
It is how service continuity becomes better after every event.

## How to use the template

When a proposed new climate file appears, run this sequence:

1. Is it a new service floor? If not, test whether it is a router, integrity gate, or subcase.
2. Does the service floor have a named shock cascade? If yes, decide whether the absorber is distinct enough for a paired file.
3. Fill the service-continuity card.
4. Add cube tags before adding prose.
5. Add only the smallest prose note needed to preserve the rule.
6. Update `95`, `129`, `252`, and the cube index.
7. Add sources only if they materially support a new fact, trend, or design constraint.

## What this rules out

It rules out service notes that are merely empathy categories.
It rules out generic “vulnerable groups” files that do not name a service floor.
It rules out standalone disaster examples with no transferable rule.
It rules out adding a new note because a topic is important when it can be represented as a tag, dependency, or ledger in an existing packet.

## Compression rule

**Admit service-continuity files by card, not enthusiasm: service floor, users, hazards, dependencies, owners, triggers, degraded mode, allocation, access, worker protection, data, finance, integrity, and correction. If the card is empty, the new file is not ready.**


## rev0271 admission addendum — hidden-rail test

Before admitting a new service-continuity packet, ask whether the problem is really one of the hidden rails now named in `316`–`322`: medical products, telecom / cloud / cyber, payments, humanitarian logistics, displacement reception, conflict sensitivity, or readiness assurance. If yes, route to those files and add a cube row before creating another prose island.

Admission now requires at least one `assurance_test` as well as a degraded mode. A service floor without a drillable assertion is not yet ready for canon status.

## Rev0272 admission update — require recovery-rail fields

A new service-continuity packet should now answer four additional admission questions:

1. Which recovery rail restores it after failure?
2. Which proof rail verifies that it is safe or complete?
3. Which local-market or community bridge makes it usable by excluded users?
4. Which restoration conflict becomes acute when several rails fail together?

If those answers are missing, the packet may still be useful, but it is not cube-ready.

## Rev0273 admission patch — every new service packet must answer the scarcity question

A service-continuity packet now fails admission if it cannot answer: what scarce resource limits the service, what priority rule governs shortage, what mutual-aid path exists, what spares or consumables are critical, what maintenance debt is hidden, what mental-health or civic legitimacy consequences follow, what reentry / credentialing conditions matter, and what compound loadcase can demote readiness.

## Rev0274 admission test — harmful interface

A new continuity packet is admissible when it reveals a harmful interface that otherwise hides across sectors. Shelters, registries, aid queues, contractor markets, pets / service animals, fatality management, safeguarding, remote access, and cultural anchors qualify because many existing packets depend on them but none owned the combined failure mode [S603][S605][S607][S608][S612][S614][S616][S618].


## Rev0275 admission rule — require rebuild-authority answers when recovery is claimed

Any future packet that claims recovery, repair, relocation, rebuilding, reopening, or restoration should answer the rev0275 gate questions: proof of right or occupancy, risk-exit decision, contracting path, reimbursement path, code / permit / inspection state, worker sustainment, shared-asset governance, and unmet-needs closure.

## Rev0276 admission rule

Future service-continuity packets should not be admitted as mature unless they include an R0-R4 readiness posture, an owner-of-record table, a freshness class for implementation claims, a financing path, and at least one excluded-user path. If cross-border aid, shared water, insurance, credit, tax base, informal housing, or worker-camp access matter, those constraints must be explicit at admission rather than discovered after failure.

## Rev0279 admission update — require an impact-to-intake path

A new service-continuity packet should now declare how it enters the post-impact operating loop: incident-management owner, rapid-assessment method, lifeline stabilization clock, safe-return gate where relevant, intake / grievance channel, commodity or volunteer dependency where relevant, and emergency-powers guardrail where authority restricts movement, access, property, or care.

## Rev0280 addition — stabilization-to-recovery pathways

rev0280 adds the rule that impact-to-intake is not recovery. A person can be registered, sheltered, assessed, or referred and still remain stranded. Climate service floors therefore need stabilization pathways: interim-to-durable housing, displaced-student stability, chronic-care continuity, nutrition-benefit continuity, utility-arrears protection, deadline tolling, and no-wrong-door benefit sequencing [S698][S699][S712].

The cube should now ask not only whether a service exists, but whether a household can move from first contact to a durable outcome without losing school, medicine, food, utilities, legal rights, or case status along the way.

---
Citations point to `sources/register.md`.
