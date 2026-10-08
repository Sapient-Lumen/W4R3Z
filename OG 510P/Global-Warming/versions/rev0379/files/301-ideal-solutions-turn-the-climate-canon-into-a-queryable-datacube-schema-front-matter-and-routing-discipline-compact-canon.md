---
id: '301'
revision_added: rev0269
status: canon
object_type: router
domain_tags:
- datacube
- schema
- routing
- metadata
- archive_governance
service_floor:
- queryable_archive
hazard_tags:
- archive_sprawl
- evidence_drift
- routing_failure
clock_tags:
- learning_clock
actor_tags:
- archive_operator
- reviewer
- policy_designer
instrument_tags:
- schema
- index
- front_matter
- validate
- route
- audit
routes_to:
- '302'
- '308'
- '322'
source_ids:
- S519
- S523
- S530
- S603
- S607
- S610
- S612
- S618
- S653
- S666
upstream_dependencies:
- stable_ids
- consistent_h1
- source_register
- cube_schema
- validation
downstream_consequences:
- hard_to_query_archive
- duplicate_notes
- missing_service_floors
- stale_claims
equity_lenses:
- plain_language_access
- reviewer_burden
degraded_modes:
- external_index_before_full_frontmatter
- structural_audit
- conservative_admission_rule
evidence_grade: design_judgment
speculation_level: medium
bottlenecks:
- untyped_notes
- missing_metadata
- broken_routes
- stale_sources
- addenda_sprawl
failure_modes:
- prose_canon_without_query_layer
- hidden_duplicate_claims
- evidence_not_routed
- service_floor_sprawl
proof_ledgers:
- cube_index
- schema_validation
- source_register_audit
- structural_audit
restoration_conflicts:
- legacy_readability_vs_machine_readability
assurance_tests:
- index_row_completeness_check
- route_resolution_check
- source_resolution_check
---
# 301 — Ideal Solutions: Turn the climate canon into a queryable datacube

## Claim

The archive has outgrown a purely sequential note stack.
It is still compact compared with an encyclopedia, but it now contains enough service-continuity packets, routers, ledgers, shock absorbers, proof gates, and addenda that readers can miss the underlying machine.
The next discipline is not simply to add more notes.
It is to make every note queryable.

A climate datacube is the smallest structure that lets the archive answer questions such as:

- which services fail when power, water, transport, communications, or workers fail;
- which notes are mitigation lanes, which are civil-protection lanes, and which are proof / governance layers;
- which hazards each packet has actually stress-tested;
- which actors own the packet;
- which clocks apply before, during, and after a shock;
- which evidence is hard fact, trend signal, design judgment, or speculation;
- which source IDs support the claim;
- which file should route first when the prompt is messy.

The cube does not replace prose.
It keeps prose from becoming unsearchable doctrine.

## Fast rule

**Every archive object should carry enough structured metadata that a person or machine can route it by service, hazard, actor, clock, instrument, evidence grade, and failure mode before reading the whole note.**

## Minimum cube schema

The archive should treat each numbered note as a row with these fields.

| Field | Purpose | Example |
|---|---|---|
| `id` | stable archive number | `299` |
| `title` | human title | `Protect solid waste...` |
| `object_type` | what kind of object this is | `service_continuity`, `shock_absorber`, `router`, `ledger`, `doctrine`, `integrity_gate` |
| `domain_tags` | what the note is about | `waste`, `health`, `housing`, `grid`, `finance` |
| `service_floor` | minimum service that must remain true | `debris clearance`, `medical waste`, `mold-safe return` |
| `hazard_tags` | stressors tested | `heat`, `flood`, `wildfire`, `outage`, `smoke`, `displacement`, `price_shock` |
| `clock_tags` | when it governs | `pre_shock`, `live_shock`, `recovery`, `after_action`, `stock_turnover`, `residuals` |
| `actor_tags` | who must act | `utility`, `city`, `regulator`, `emergency_manager`, `school`, `health_system`, `court` |
| `instrument_tags` | governing tools | `build`, `ban`, `fund`, `procure`, `insure`, `disclose`, `route`, `ration`, `remedy` |
| `bottlenecks` | scarce things to release | `crews`, `permits`, `grid capacity`, `trucks`, `cash-out points` |
| `failure_modes` | what goes wrong if absent | `paper compliance`, `capture`, `unsafe return`, `silent exclusion`, `fossil fallback lock-in` |
| `proof_ledgers` | what must be measured | `load tickets`, `indoor temperature`, `route uptime`, `benefit denial`, `worker injury` |
| `routes_to` | next files to open | `252`, `253`, `299`, `300` |
| `source_ids` | bracket sources used | `[S519]`, `[S523]`, `[S530]` |
| `evidence_grade` | evidentiary posture | `constraint`, `trend`, `synthesis`, `design_judgment`, `speculative_watch` |
| `speculation_level` | how far the note reaches beyond evidence | `low`, `medium`, `high` |
| `revision_added` | archive revision that admitted it | `rev0268` |
| `status` | active / superseded / quarantine | `active` |

The cube files in `/cube/` provide a first-pass schema, index, and service-continuity template.
They are deliberately plain text, CSV, and JSON so the archive can be inspected without a special platform.

## Object types

### 1. Doctrine note

A doctrine note states a durable rule.
Examples include the canonical thesis, ranked stack, minimum sufficient solution, and fossil-decline doctrine.

Doctrine notes should be few.
They should change only when the archive's center of gravity changes.

### 2. Delivery packet

A delivery packet turns a doctrine into owned work.
It names bottlenecks, owners, finance, procurement, workforce, timing, and proof.

Delivery packets should answer: **who has to do what by when, using which authority and budget, with which verification?**

### 3. Service-continuity packet

A service-continuity packet names a minimum service floor under degraded climate conditions.
Examples now include food, water, health, school, care, worker, housing, finance, legal, information, transport, energy, waste, and public safety.

Service-continuity packets should answer: **what must still work when the shock arrives?**

### 4. Shock absorber

A shock absorber governs the cascade around a service floor.
It names triggers, allocation rules, degraded modes, temporary measures, correction ledgers, and after-action duties.

Shock absorbers should answer: **what prevents the first failure from becoming a social, health, financial, or governance cascade?**

### 5. Router

A router helps a user choose the first file.
Routers should not become encyclopedias.
They should preserve the shortest route to an answer.

### 6. Integrity gate

An integrity gate blocks false climate progress.
Examples include carbon-market quarantine, offset boundaries, procurement integrity, methane measurement, and claims discipline.

Integrity gates should answer: **what proof is required before a claim is allowed to count?**

### 7. Ledger

A ledger defines what must be recorded.
Ledgers should be short, inspectable, and connected to remedies.

A ledger that records failure without triggering correction is merely documentation.

## Evidence grades

The archive should distinguish five grades.

1. **Constraint** — a hard boundary condition, such as observed warming, remaining carbon budget, physical infrastructure dependence, or legally binding accounting rule.
2. **Trend** — a directional signal, such as rising heat exposure, growing adaptation finance needs, or increasing data-center loads.
3. **Synthesis** — a conclusion drawn across authoritative reports and archive doctrine.
4. **Design judgment** — an operational rule inferred from evidence but not itself a directly measured global fact.
5. **Speculative watch** — an emerging risk, design possibility, or institutional failure mode that should be tracked but not overclaimed.

House rule: **the cube should let readers see when the archive is stating fact, interpreting trend, designing governance, or speculating.**

## Clocks

Most climate mistakes come from using the wrong clock.
The cube should tag at least these:

- `emergency_clock`: hours to weeks; warnings, evacuation, response, outage, rescue, cooling, medical continuity;
- `seasonal_clock`: heat season, fire season, monsoon, drought year, school year, budget cycle;
- `stock_turnover_clock`: buildings, vehicles, appliances, industrial equipment, grid assets, ports, landfills;
- `finance_clock`: capital budget, insurance renewal, bond issuance, concessional window, debt refinancing;
- `recovery_clock`: debris, repair, claims, housing, benefits, legal deadlines, school catch-up, worker recovery;
- `residuals_clock`: long-lived hard-to-abate emissions, removals, contaminated sites, closure duties;
- `learning_clock`: after-action review, correction, drill, standard update, source refresh.

A note may belong to more than one clock.
A strong packet names the clock conflict rather than hiding it.

## Hazard tags

The cube should separate hazard from domain.
A water note can be about drought, flood, disease, outage, affordability, or displacement.
A housing note can be about heat, smoke, flood, mold, rent shock, insurance withdrawal, or homelessness.

Minimum hazard tags:

`heat`, `cold`, `flood`, `coastal_flood`, `storm`, `wind`, `drought`, `wildfire`, `smoke`, `air_pollution`, `outage`, `cyber`, `disease`, `vector`, `water_quality`, `food_price`, `supply_chain`, `displacement`, `violence`, `legal_deadline`, `debt`, `insurance_withdrawal`, `contamination`, `waste_surge`, `compound_shock`.

## Service floors

The service-floor column should be the main new discipline.
A climate packet is incomplete if it describes an asset but not the service that asset protects.

Examples:

- not merely `grid`: **critical load, cooling, water pumps, communications, medicine cold chain**;
- not merely `hospital`: **triage, critical care, medicines, water, cooling, power, waste, worker safety**;
- not merely `school`: **safe learning days, meals, WASH, records, child protection, teacher continuity**;
- not merely `housing`: **safe indoor temperature, clean air, dryness, repair, legal occupancy, rent stability**;
- not merely `waste`: **collection, debris clearance, hazardous separation, medical waste, environmental-health closure**.

House rule: **asset continuity is not service continuity until the service floor is named.**

## Front matter template

Future numbered files should be admitted with front matter like this:

```yaml
id: 301
revision_added: rev0269
status: active
object_type: doctrine
domain_tags: [governance, data_spine, routing]
service_floor: []
hazard_tags: [compound_shock]
clock_tags: [learning_clock, recovery_clock, stock_turnover_clock]
actor_tags: [archive_maintainer, regulator, city, ministry, analyst]
instrument_tags: [index, route, audit, standardize]
bottlenecks: [attention, source_freshness, routing_confusion, prose_sprawl]
failure_modes: [addenda_accretion, hidden_template, stale_sources, duplicate_sources, impossible_router]
proof_ledgers: [cube_index, source_register, changelog, structural_audit]
routes_to: [302, 95, 129, 252]
source_ids: []
evidence_grade: design_judgment
speculation_level: medium
```

Do not require old files to be rewritten immediately.
The first implementation is the external index in `/cube/index.csv`.
Backfill front matter only when a file is next materially revised.

## Admission rule for new notes

Before adding a new numbered file, ask whether the proposed note adds at least one of these:

1. a new service floor;
2. a new shock cascade;
3. a new control point;
4. a new proof ledger;
5. a new integrity gate;
6. a new clock conflict;
7. a compression that makes several existing files easier to use.

If it adds only another example, put it in the cube index or an existing note.

## What this changes

This note changes the archive's operating rule.
The archive is no longer only a list of canon notes.
It is a small knowledge system with:

- prose canon for judgment;
- cube metadata for retrieval;
- source register for evidence;
- changelog for revision memory;
- routers for human use;
- ledgers for implementation;
- quarantine for claims that are too weak or dangerous to count.

## What this rules out

It rules out:

- adding every missing subject as a full note;
- burying new doctrine after citation footers;
- letting addenda replace schema;
- treating sources as references without freshness, use, or duplicate control;
- making routers longer every time the archive grows;
- using the same source tag for fact, trend, and design judgment without saying which job it is doing.

## Compression rule

**A climate datacube lets each archive note be routed by object type, domain, service floor, hazard, clock, actor, instrument, failure mode, evidence grade, and source support. Keep prose for judgment, but make the architecture queryable before the canon becomes too large to govern.**

## Rev0270 cube extension — dependencies and equity / agency lenses

The cube schema now adds four fields that were only implicit in rev0269:

- `upstream_dependencies`: services, inputs, authorities, or systems that must work first;
- `downstream_consequences`: services or populations harmed if the object fails;
- `equity_lenses`: groups, rights, or agency constraints that must be tested;
- `degraded_modes`: what still works under outage, access loss, cyber failure, displacement, staff shortage, or fiscal stress.

This extension reflects the archive's move from service floors as a list to service floors as an interdependent operating graph. The companion artifacts are `cube/interdependency-matrix.csv` and `cube/service-floor-checklist.csv`.


## rev0271 schema extension — assurance and hidden rails

rev0271 extends the cube beyond dependency mapping. Rows should now preserve `bottlenecks`, `failure_modes`, `proof_ledgers`, `restoration_conflicts`, and `assurance_tests` where available. These fields are intentionally operational: they describe the practical reasons a service floor fails, the records that expose failure, the choices that cannot all be optimized during restoration, and the drills that distinguish readiness from paper compliance.

The cube should also recognize hidden-rail packets: medical products (`316`), digital infrastructure (`317`), payments (`318`), humanitarian logistics (`319`), displacement / reception (`320`), climate-conflict integrity (`321`), and service-floor assurance (`322`).

## Rev0272 cube extension — recovery rails

The datacube now distinguishes **service floors** from **recovery rails**. A service floor names what must remain true; a recovery rail names the hidden throughput that makes restoration possible after failure. rev0272 adds energy-input, repair-market, claims, floodwater, local-market, community-bridge, agrifood-input, and proof-rail objects. These should be modeled as dependencies, bottlenecks, assurance tests, and restoration conflicts rather than as generic “resilience” prose.

## Rev0273 schema patch — backfill the old canon and add bad-day operating fields

rev0273 completes the first whole-archive front-matter backfill. Earlier files can now be parsed as cube rows rather than only as prose. The schema also adds bad-day operating fields: `priority_class`, `scarcity_rule`, `mutual_aid_status`, `inventory_posture`, `maintenance_state`, `civic_legitimacy_check`, and `exercise_load_case`. These fields prevent the cube from treating nominal service labels as proof of operability.

## Rev0274 datacube extension — protective interfaces

The cube now gets protective-interface fields: shelter standard, protection risk, privacy posture, wildfire mitigation state, animal continuity, remote access mode, and cultural continuity check. These fields prevent service floors from being falsely marked ready when the access point itself is dangerous, extractive, surveilling, inaccessible, or invisible [S603][S607][S610][S612][S618].


## Rev0275 schema note — rebuild authority fields

The cube now needs fields for property-rights posture, retreat / buyout rule, procurement integrity, reimbursement cash flow, code-upgrade state, essential-worker sustainment, shared-housing governance, and unmet-needs closure. These are not narrative extras; they determine whether a service floor can move from declared need to funded, safe, inspected, occupied recovery.

## Rev0276 schema extension

The datacube now adds a second-order test: not only what a note is about, but whether its service floor is scored, owned, fresh, financeable, and boundary-tested. New fields cover readiness scoring, owner accountability, evidence freshness, market / fiscal signals, cross-border facilitation, basin cooperation, and informal habitation / worker protection.

## Rev0277 query-view extension

The datacube now needs named views, not only fields. Each view should declare its question, filters, returned columns, freshness rule, owner, security boundary, and correction route. Good examples: `service_floors_without_owner`, `R0_R1_before_heat_season`, `dashboards_with_stale_data`, `critical_OT_without_manual_fallback`, `toxic_sites_inside_flood_reentry_zone`, and `disease_surveillance_without_action_threshold`.

The archive should treat a query view as an operating object: it tells the cube what questions must be answerable before readiness can be believed. Route to `364` [S653][S666].

## Rev0278 schema addition — trigger fields

The cube row should now expose forecast-trigger and actionability fields. A service floor should be demoted if it has no trigger rule, no authority, no pre-arranged finance or procurement path, no protective-action matrix, no last-mile alert check, no false-alarm learning, and no pre-positioning or degraded-mode path where the hazard is predictable.

---
Citations point to `sources/register.md`.
