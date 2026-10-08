# Service-continuity packet template — rev0269

Use this template before admitting a new service-continuity note.

```yaml
id:
revision_added:
status: draft
object_type: service_continuity
domain_tags: []
service_floor: []
hazard_tags: []
clock_tags: [emergency_clock, recovery_clock, learning_clock]
actor_tags: []
instrument_tags: []
bottlenecks: []
failure_modes: []
proof_ledgers: []
routes_to: []
source_ids: []
forecast_trigger_rule:
impact_based_decision_support:
anticipatory_finance_rule:
protective_action_authority:
heat_action_threshold:
smoke_air_quality_action_threshold:
alert_interoperability_state:
false_alarm_learning:
prepositioning_state:
shock_responsive_cash:
evidence_grade: design_judgment
speculation_level: medium
```

## 1. Claim

What service floor is missing from the climate programme?

## 2. Fast rule

One sentence beginning: **Every climate packet that...**

## 3. Minimum service floor

List the service elements that must continue.

## 4. Users and exclusions

Name who depends on the service and who normal systems miss.

## 5. Hazard and dependency map

Which shocks disrupt the service, and which other services must work first?

## 6. Owners

Who owns readiness, live operation, recovery, data, finance, and remedy?

## 7. Degraded mode

What remains safe when full service fails?

## 8. Allocation and access rules

Who gets priority, and how do people access the service without impossible proof or technology?

## 9. Worker protection

Who must work, and how are they protected?

## 10. Data and privacy

What is measured, published, protected, and corrected?

## 11. Finance and procurement

How readiness, live response, recovery, and after-action correction are paid for.

## 12. Integrity risks

Fraud, capture, discrimination, coercion, dumping, price gouging, paper compliance, and false closure.

## 13. Ledger

| Question | Evidence required |
|---|---|
| What service was maintained? |  |
| Who was missed? |  |
| What failed first? |  |
| What degraded mode worked? |  |
| What harms occurred? |  |
| What correction is funded? |  |

## 14. Routing

Name first-use prompts and pair files.

## 15. Compression rule

One bold sentence that can survive inside a router.


## rev0270 dependency-graph addendum

Every service-continuity packet should now add these fields before it is marked ready:

- `upstream_dependencies`: the services, inputs, records, assets, authorities, and workers the floor depends on.
- `downstream_consequences`: the second-order harms if the floor fails.
- `equity_lenses`: the people for whom nominal access is not enough.
- `degraded_modes`: the fallback that still works during outage, displacement, staff shortage, cyber disruption, smoke, heat, or access loss.

Minimum ready test: **five dependencies, five consequences, one restoration-conflict rule, one degraded mode, and one proof ledger.**


## rev0271 assurance addendum

Every packet should now include these fields where applicable:

- `bottlenecks`: the practical capacity, authority, supply, data, staffing, or trust constraints that make the service fail.
- `failure_modes`: the characteristic ways this floor becomes paper compliance, exclusion, capture, or false closure.
- `proof_ledgers`: the records that show whether the floor worked for actual users.
- `restoration_conflicts`: the priority conflicts that cannot all be solved first during live response.
- `assurance_tests`: drills, audits, red-team tests, and excluded-user tests that can promote, condition, demote, or quarantine readiness status.

Minimum rev0271 ready test: **one degraded mode, one excluded-user test, one restoration-conflict rule, one proof ledger, and one assurance test.**
## Rev0272 recovery-rail extension

Add this block to every new or materially revised service-continuity packet:

- **Recovery rail:** what restores the service after failure?
- **Proof rail:** what sampling, inspection, claim, record, or audit proves safety or completion?
- **Local-market bridge:** which local enterprises, contractors, suppliers, or cash-out points make the service usable?
- **Community bridge:** which trusted organizations, caseworkers, translators, or volunteers reach people official channels miss?
- **Restoration conflict:** what scarce rail is likely to be claimed by multiple services at once?
- **Degraded mode:** what lower-service but safe mode operates while the full rail is unavailable?

## Rev0273 required bad-day fields

Every new service-continuity packet should now answer these additional fields:

- `priority_class` — who gets scarce restoration first and why
- `scarcity_rule` — trigger, exception, appeal, and de-escalation logic
- `mutual_aid_status` — agreement, resource typing, credentialing, fuel, reimbursement, and drill evidence
- `inventory_posture` — critical spares, consumables, substitutes, storage, and release priority
- `maintenance_state` — asset condition, deferred maintenance, lifecycle budget, and repair / retirement path
- `civic_legitimacy_check` — whether public decisions, elections, participation, notice, and audit survive degraded operation
- `exercise_load_case` — which compound scenario can demote readiness if failed

## Rev0279 impact-to-intake fields

For post-impact or live-response service floors, the packet should also state:

- `incident_management_state`: how the service is represented in ICS / EOC operations and resource requests.
- `rapid_assessment_state`: how damage, needs, exclusion, and public-health impacts are assessed and revised.
- `lifeline_stabilization_clock`: how restoration status, degraded mode, hidden pockets, and next update are published.
- `building_safety_placard_state`: how safe return, habitability, utility reconnection, reinspection, and appeal work where buildings matter.
- `survivor_intake_access`: how affected people can enter, track, appeal, and correct service access.
- `commodity_distribution_state`: how supplies move from inventory to reachable points of need.
- `volunteer_donations_management`: how goodwill is turned into safe useful capacity or declined.
- `emergency_powers_guardrail`: how restrictions, waivers, commandeering, quarantine, curfews, and reentry controls remain lawful, supported, reviewable, and sunsetted.


## Rev0281 household-function and closeout fields

For recovery-facing packets, add these fields before claiming success:

- `recovery_outcome_state`: how household function is measured after intake, award, referral, and case closure.
- `household_balance_sheet_repair`: how credit, debt, forbearance, insurance, emergency cash, and asset loss are governed.
- `tenancy_stability_protection`: how renters, right-to-return, affordability, fair housing, and eviction risk are protected.
- `livelihood_return_pathway`: how wage loss, unemployment, payroll, safe work, childcare, transport, and reemployment are connected.
- `recovery_mobility_access`: how people reach jobs, schools, clinics, benefits, repairs, food, and legal help without private-car assumptions.
- `essential_property_device_replacement`: how appliances, DME, assistive technology, communications devices, and basic contents are restored.
- `digital_identity_account_recovery`: how documents, phones, accounts, MFA, portals, fraud controls, and offline alternatives survive disaster.
- `recovery_exit_nonrecurrence`: how closeout proves residual risk, unresolved needs, maintenance finance, mitigation, and lessons applied.

Minimum rev0281 ready test: **one household-function outcome, one excluded-user pathway, one financial/debt guardrail, one document/account fallback, and one nonrecurrence closeout owner.**

## Rev0282 risk-reduction conversion fields

For closeout, mitigation, land-use, infrastructure, and ecosystem-buffer packets, add these fields before claiming nonrecurrence:

- `mitigation_pipeline_state`: how lessons, repeated losses, or residual risk become scoped, owned, financeable mitigation projects or policy actions.
- `repetitive_loss_exposure_register`: how insured and uninsured repeated harm, chronic service failure, and risk-exit decisions are tracked.
- `future_hazard_mapping_disclosure`: how map freshness, future-condition assumptions, design values, and disclosure timing are governed.
- `resilience_finance_stack`: how planning, design, permitting, construction, match, cash flow, debt, affordability, and O&M are financed.
- `benefit_cost_equity_test`: how BCA, avoided service loss, unquantified benefits, distributional screens, and low-capacity assistance guide selection.
- `no_new_risk_land_use`: how siting, zoning, subdivision, utility extension, and rebuild decisions avoid creating new exposure while preserving safe housing supply.
- `nature_based_solution_lifecycle`: how green / blue infrastructure proves protected service, performance, stewardship, maintenance, and adaptive management.
- `post_project_performance_monitoring`: how completed projects prove actual risk reduction, residual-risk transfer, downstream effects, and maintenance.

Minimum rev0282 ready test: **one mitigation-pipeline owner, one repeated-risk register, one future-condition assumption, one finance stack, one equity-aware selection record, one no-new-risk gate, one lifecycle maintenance owner, and one performance-monitoring ledger.**

---
Citations point to `sources/register.md`.

## Rev0283 adaptive-governance fields

Use these fields when a service floor involves long-lived assets, land use, professional design, contracts, or repeated risk:

- `adaptive_pathway_state`: signposts, triggers, switching owner, and preserved options.
- `climate_model_governance`: model inventory, assumptions, uncertainty range, validation, and exception process.
- `real_options_flexibility`: modularity, reversibility, expandability, exit costs, and stage gates.
- `maladaptation_lockin_gate`: induced exposure, risk transfer, inequity, maintenance failure, and foreclosed retreat check.
- `asset_portfolio_stress_test`: asset inventory, criticality, condition, maintenance backlog, and capital-plan crosswalk.
- `resilience_service_level_contract`: measurable service level, acceptance test, maintenance obligation, reporting, and remedy.
- `unsafe_asset_exit_plan`: service replacement, decommissioning budget, stranded-cost treatment, and community transition.
- `professional_duty_standard`: future-condition design basis, residual-risk disclosure, competence, peer review, and exception handling.

## Rev0284 assurance addendum

Before a service-floor packet is marked mature, add an assurance section:

- control objective and service risk;
- preventive and detective controls;
- source-edge evidence and freshness;
- corrective-action status and retest date;
- independent audit / challenge / redress route;
- civil-rights, disability-access, and language-access gate;
- procurement / grant / contractor transparency where money-to-delivery is material;
- workforce competency, backup owner, and succession;
- assurance-case scope, exceptions, expiry, and public-safe summary.

