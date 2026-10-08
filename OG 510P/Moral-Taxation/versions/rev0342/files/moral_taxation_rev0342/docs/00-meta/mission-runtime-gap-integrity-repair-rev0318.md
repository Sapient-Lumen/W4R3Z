# Mission, runtime gap, and integrity repair — rev0318

## Judgment in one sentence

**The archive's heart is an anti-category-error constitution for public burdens:** identify the real person, controller, beneficiary, rent recipient, burden bearer, protected floor, remedy, and review trigger before choosing a tax, fee, mandate, ban, public option, compensation rule, or other instrument.

That is more valuable—and broader—than the title *Moral Taxation* suggests. The project is becoming a **moral-fiscal routing constitution** or **public-burden compiler**. Its central achievement is not a list of preferred taxes; it is a disciplined refusal to tax whatever is easiest to see while responsibility, rent, harm, or capacity sits elsewhere.

## What the mission is really doing

The founding charter says the archive must separate persons from tools, ability-to-pay from throughput, effort from rent, public finance from punishment, and legibility from ornament. The mature route system adds five operational questions:

1. **Who or what is the subject?** A human person, a legal remitter, a controller group, a public body, a current model that is not a person, or a future rights-bearing artificial person.
2. **What is the morally relevant base?** Capacity, rent, land, inheritance, pollution, scarce infrastructure, public subsidy, risk creation, or a different source of burden—not mere technical visibility.
3. **Who actually bears the burden?** Incidence after prices, wages, rents, fees, bargaining power, denial, delay, and claim friction.
4. **What cannot be bought?** Protected floors, standing, due process, privacy, and catastrophic or irreversible harms that require duty, gating, repair, or refusal rather than a price.
5. **How does the rule learn and unwind?** Evidence, currentness, contest, evaluation, triggers, sunsets, and a named fallback duty.

This is a coherent constitutional core. It should remain the project's invariant even if the implementation is radically simplified.

## What is already strong

- The archive has a clear normative ordering: shield subsistence; distinguish subject from base; reach rents, harms, and concentrated capacity before ordinary labor; test incidence; protect standing and remedy; make review architecture part of justice.
- It refuses false AI personhood while still routing controller-side rents, harms, infrastructure burdens, and public-input reciprocity.
- It treats administration as substance: explanation, correction, access, take-up, timing, fallback channels, and claim friction are constitutional design questions rather than afterthoughts.
- It has unusually strong release integrity for a knowledge archive: source IDs, currentness records, schemas, manifest hashes, package receipts, route coverage, and semantic audits.
- The profile layers preserve distinctions commonly lost in tax debate: legal remitter versus burden bearer, title holder versus controller, compensation recipient versus real harmed class, and money remedy versus no-go duty.

## Hard correctness failures found and repaired in rev0318

### 1. The canonical scorecard contradicted its generated scorecard

`scorecard-template.json` contains 98 criteria scored from -2 to +2. Its true extrema are therefore ±196, but the canonical JSON still said ±186. The rendered markdown happened to compute ±196 correctly. All checks passed because the checker validated only the markdown result, not the JSON interpretation.

**Repair:** the JSON now says ±196, and `tools/check_archive.py` independently verifies both extrema against the live criterion count.

### 2. Repository-maintenance events leaked into policy-world escalation logic

Live remedy profiles contained 52 `new_calibration_file` triggers, and policy-action profiles contained 79. A file being added to the repository is not a change in incidence, law, evidence, harm, access, or market structure. This was a direct category error inside the system built to prevent category errors.

**Repair:** all 131 leaks were replaced by each route's substantive `review_trigger` values. Both profile audits now reject this process placeholder, and the cube records zero remaining leaks.

### 3. Packaging did not itself run semantic audits

`make package` rendered the scorecard, built a manifest, ran structural checks, and zipped the release, but did not invoke `make audit`. A package could therefore be declared ready without the semantic gates that the public instructions treated as mandatory.

**Repair:** `package` now depends on `audit`. One command is again sufficient to enforce the release contract.

### 4. “Executable answer contracts” overstated the implementation

The 84 golden cases and case contracts are machine-readable and schema-checked, but no query engine, route matcher, answer generator, or output comparator is invoked. The tools directory contains audits, rendering, manifest, checking, and packaging—not an answer runtime. A fixture is not an executable test merely because its internal references are valid.

**Repair:** current machine surfaces now state `declarative_only_no_answer_router`. The case audit records route coverage and prevents regression below the present 80-route floor. The project may reclaim the word *executable* when a router is actually called and returned output is compared with expected routes, flags, remedies, and must-not answers.

### 5. Current audit reporting was multiplying files

The active release previously pointed to separate current reports for cube, currentness, remedy, cases, policy action, accountability, axis hygiene, prose bloat, waste, and procurement. Rev0318 points those gates to one consolidated current audit report. Historical reports are retained for now, but the forward release pattern no longer requires ten near-duplicate report files per turn.

## What is missing

### A. An answer runtime

The project needs one deterministic path from a case to an answer object:

`facts -> normalized facts -> candidate routes -> precedence/conflict resolution -> selected routes -> duties/remedies -> citations -> confidence/unknowns`

OpenFisca is a useful comparator because it makes the execution boundary explicit: provide a situation, run coded rules, obtain a calculation, and test the result.[S675] The Moral Taxation runtime need not calculate tax liabilities first; its first executable output can be a structured routing decision. But it must actually run.

### B. A quantitative policy layer

The archive can classify a moral problem, but it generally cannot answer how much revenue a proposal raises, which households or firms gain or lose, how incidence changes under behavior, what administrative cost is plausible, or how uncertainty affects the choice. PolicyEngine exposes the missing categories plainly—rules, parameters, variables, data, calibration, validation, behavioral responses, APIs, and reform models.[S676]

The correct move is not to turn every route memo into a model. Add connectors: route records should declare which external calculator, microsimulation, budget model, distribution table, or empirical estimate can evaluate the instrument. Moral vetoes remain separate from model outputs.

### C. A real policy lifecycle

The scorecard is an appraisal instrument, but 98 criteria mix universal constitutional gates with domain-specific questions. The UK Green Book frames appraisal around objectives and the costs, benefits, and risks of options; the 2026 revision explicitly shortened and simplified the guidance.[S677] The Magenta Book treats evaluation as a lifecycle activity that feeds learning back into continuation, improvement, or stopping decisions.[S678]

The archive should split its scorecard into:

- a compact constitutional kernel applied to every proposal;
- route-specific modules loaded only when relevant;
- an evaluation contract naming outcomes, data, owner, cadence, trigger, and stop/scale rule.

### D. Claim-level provenance

A route usually lists source IDs, but the machine layer does not consistently say which exact claim came from which source location, under what jurisdiction/status, checked when, and with what confidence. W3C PROV-O is a useful reference model because it separates entities, activities, and agents in interoperable provenance records.[S680]

The next provenance object should be small: `claim_id`, `claim_text`, `source_id`, `locator`, `jurisdiction`, `status/effective_date`, `checked_at`, `review_due`, `agent`, and `confidence`.

### E. A clearer data model name

In the W3C model, a data cube centers on observed values organized by dimensions and metadata.[S679] This archive's `cube-index.json` is mainly a route ontology and denormalized profile index. It contains no observation table, measure model, counterfactual, or statistical cube.

Two honest options exist:

1. rename the current object `route-index.json` or `moral-fiscal-route-graph.json`; or
2. keep “datacube” as the project metaphor but add an actual observation layer for rates, revenue, distribution, take-up, administrative cost, harm, and uncertainty.

## Where the system has become wasteful or distorted

### 1. Regression coverage is much thinner than the rhetoric

Case contracts exercise 80 of 155 routes (51.6%). 75 routes have no expected-route case at all.

| Family | Covered | Routes | Coverage |
|---|---:|---:|---:|
| `controller_ai` | 3 | 21 | 14.3% |
| `cross_border_reporting` | 5 | 6 | 83.3% |
| `environment_climate_commons` | 9 | 10 | 90.0% |
| `financial_system_risk` | 6 | 8 | 75.0% |
| `labor_care_benefits` | 7 | 11 | 63.6% |
| `legal_enforcement_penalty` | 4 | 11 | 36.4% |
| `public_finance_core` | 17 | 44 | 38.6% |
| `public_procurement_industrial_policy` | 5 | 5 | 100.0% |
| `regulated_networks_platforms` | 4 | 4 | 100.0% |
| `release_integrity_currentness` | 4 | 4 | 100.0% |
| `social_floor_public_services` | 6 | 8 | 75.0% |
| `tax_administration_access` | 7 | 17 | 41.2% |
| `wealth_property_rent` | 3 | 6 | 50.0% |

The weakest families are controller AI (3/21), legal enforcement (4/11), public finance core (17/44), and tax administration access (7/17). The next case work should be risk-weighted, not numerically uniform: start with routes whose wrong answer can remove standing, shift a burden onto a protected floor, price non-compensable harm, or misassign controller liability.

### 2. The axis taxonomy is overfit

The cube declares 2031 axis values across 23 axes for only 155 routes. Several high-cardinality axes are dominated by one-off labels:

| Axis | Declared | Used by routes | Singleton values | Singleton share |
|---|---:|---:|---:|---:|
| `subject` | 225 | 225 | 157 | 69.8% |
| `incidence` | 162 | 162 | 112 | 69.1% |
| `stage` | 135 | 135 | 82 | 60.7% |
| `floor_risk` | 132 | 132 | 74 | 56.1% |
| `proceeds_route` | 124 | 124 | 88 | 71.0% |
| `anti_pattern` | 214 | 164 | 113 | 68.9% |
| `review_trigger` | 163 | 125 | 98 | 78.4% |
| `market_structure` | 56 | 56 | 30 | 53.6% |
| `delivery_channel` | 135 | 135 | 112 | 83.0% |
| `burden_mechanic` | 167 | 167 | 124 | 74.3% |
| `remedy_type` | 163 | 163 | 118 | 72.4% |

This looks precise but weakens reuse, comparison, and routing. Meanwhile low-information axes are nearly constant: `legal_status=unknown` on 126 routes, `evidence_state=authoritative_source` on 152, `severity=medium` on 145, `confidence=medium` on 147, and `review_cadence=event_triggered` on 145.

The likely correction is a two-level vocabulary:

- **small canonical route dimensions** for matching and comparison;
- **route-local facts/tags** for specific actors, failures, records, and triggers.

### 3. Raw case facts and canonical route outputs share one vocabulary registry

There are 239 declared values used by case inputs but by no live route record: `anti_pattern` 50, `base` 84, `instrument` 16, `proof_posture` 51, `review_trigger` 38. This is why a case can say `base=information_reporting` while its expected route uses a broader normalized base. The distinction may be intentional, but the schema does not name it clearly.

Split `input_fact_vocabulary` from `canonical_route_axes`, then add an explicit normalization map. Do not force raw facts and normalized outputs to masquerade as one taxonomy.

### 4. Release machinery has become an institution of its own

`docs/00-meta/` contains 276 files, including 209 revision-stamped audit reports. The archive is only a few megabytes, so storage is not the main problem; attention, search noise, re-entry cost, and synchronization are. Rev0318 stops adding ten current reports, but historical pruning should be a separate verified migration: retain a compact revision ledger and the latest full reports, then move or collapse old per-audit notes only after checking inbound links.

### 5. Denormalized profiles create synchronization debt

Each of 155 routes has a route record plus remedy, policy-action, and actor-accountability profiles. In the accountability file, all 155 primary-accountable-actor strings are unique, all 155 beneficiary strings are unique, all 474 responsibility-basis entries are unique, and all 755 evidence-required entries are unique. Some uniqueness is substantively valuable; all-unique prose also means the system cannot cheaply distinguish reusable concepts from handcrafted wording.

The durable architecture is one canonical route graph plus generated views. Store reusable actors, duties, evidence types, channels, and remedies as entities; store route-specific relationships as edges; render profile documents for humans and compatibility.

### 6. Source volume is not yet claim assurance

The archive now has 666 sources, but only 51 are in the separate volatile-source registry. That ratio is not automatically a defect—the registry is intended for volatile dependencies—but the criteria for inclusion should be explicit and claim-based. The OECD's Tax Administration 3.0 vision is useful here: operational transformation aims toward more seamless and frictionless processes, not merely a larger reference library.[S674]

## Recommended change sequence

### Now — completed in rev0318

- Correct scorecard extrema and guard the canonical JSON.
- Purge 131 process placeholders from live escalation semantics and add release-blocking checks.
- Make semantic audits part of `make package`.
- Record the truthful declarative-only case status and a non-regression coverage floor.
- Consolidate current audit reporting.
- Add authoritative external comparators for the next architecture pass.

### Next — build the minimum runtime

Create one command such as:

```text
python tools/route_case.py --case-id GC-001 --json
```

It should return candidate routes, selected routes, matched facts, precedence decisions, duties/remedies, sources, unknowns, and confidence. `audit_case_contracts.py` should invoke it for a small, high-risk subset first. A test fails when returned output differs—not merely when the fixture is self-consistent.

### Then — normalize and generate

- Split raw input facts from canonical route axes.
- Collapse high-singleton axes into reusable dimensions plus route-local tags.
- Define one canonical route object and generate remedy/policy/accountability views.
- Split the 98-item scorecard into a constitutional kernel and conditional modules.

### After that — connect evidence and models

- Add claim-level provenance and locators.
- Attach route-specific model interfaces for distribution, revenue, behavior, administrative cost, and uncertainty.
- Add evaluation contracts and decision logs: continue, scale, amend, suspend, or retire.

### Finally — prune history safely

- Generate one compact release ledger from receipts.
- Keep current reports plus milestone reports in the active root.
- Move superseded per-revision audit notes to a historical bundle only after link and manifest checks.
- Measure re-entry time and file-touch count, not only bytes saved.

## Speculative reframing

My strongest inference is that the project outgrew its name. Tax remains the founding domain, but the archive now routes fees, mandates, bans, public options, procurement, insurance, environmental no-go rules, infrastructure, standards, compensation, and administrative remedies. Calling all of that “taxation” obscures the achievement.

A conservative change would keep the project name and add a subtitle:

> **Moral Taxation: a constitutional router for public burdens, rents, harms, remedies, and fiscal governance.**

A stronger architectural change would name the machine layer **Moral Fiscal Router** and retain **Moral Taxation** for the constitutional essays and tax-ordering doctrine.

My second inference is organizational: the archive has been optimized by repeatedly hardening whatever failed last. That is rational locally, but it produced audit accretion, profile duplication, and taxonomy overfitting. The next phase should optimize for **end-to-end answer behavior, generated canonical views, and measured policy consequences**, even if that means deleting or merging surfaces that individually look well defended.

## Full uncovered-route baseline

### `controller_ai` — 18 uncovered

- `artificial_personhood_threshold`
- `automation_dividend_trigger`
- `controller_boundary_and_co_controller_ranking`
- `controller_map_confidence_unknowns_and_bounded_imputation`
- `controller_map_contest_window_counter_map_and_finality`
- `controller_map_event_log_retention_and_preservation`
- `controller_map_evidence_presumption_and_burden_shifting`
- `controller_map_field_severability_partial_acceptance_and_issue_scoped_correction`
- `controller_map_integrity_correction_safe_harbor_and_sanction`
- `controller_map_minimum_contents_attestation_and_update_cadence`
- `controller_map_packet_identity_canonical_fields_and_supersession`
- `controller_map_reuse_portability_and_cross_regime_reliance`
- `controller_map_signer_authority_delegation_and_joint_attestation`
- `controller_map_verification_sampling_and_review_intensity`
- `controller_map_visibility_redaction_and_audience_tier`
- `frontier_ai_host_market_controller_jurisdiction`
- `model_assisted_enforcement_red_team`
- `public_input_reciprocity_contribution`

### `cross_border_reporting` — 1 uncovered

- `international_coordination_claim_split`

### `environment_climate_commons` — 1 uncovered

- `failure_waterfall_and_ex_ante_security`

### `financial_system_risk` — 2 uncovered

- `creditor_distress_netting_and_retained_surplus`
- `insurance_policyholder_benefit_and_retained_surplus`

### `labor_care_benefits` — 4 uncovered

- `assessment_unit_and_care_load`
- `data_minimization_credential_reuse_and_sensitive_attribute_firewall`
- `pension_pass_through_incidence_and_proceeds`
- `worker_benefit_pay_hours_member_share_and_local_repair`

### `legal_enforcement_penalty` — 7 uncovered

- `burden_salience_disclosure_and_hidden_tax`
- `criminal_tax_referral_civil_criminal_boundary_voluntary_disclosure_and_restitution`
- `culpability_penalty_safe_harbor_and_criminal_referral`
- `summons_third_party_contact_john_doe_and_privilege`
- `transferee_nominee_alter_ego_successor_and_wrongful_levy`
- `trust_fund_recovery_responsible_person_and_willfulness`
- `whistleblower_tip_classification_confidentiality_award_and_accused_taxpayer_protection`

### `public_finance_core` — 27 uncovered

- `automaticity_and_take_up_delivery`
- `base_ordering_overlap_creditability_and_non_substitution`
- `beneficial_ownership_and_controller_chain`
- `beneficiary_composite_netting_and_residual_ordering`
- `beneficiary_home_market_and_local_burden_claim_split`
- `capacity_fragility_and_enforceability`
- `channel_pluralism_access_independence_and_fallback`
- `customer_benefit_price_access_and_retained_surplus`
- `frontier_scarce_capacity_threshold`
- `incidence_evidence_and_protected_burden`
- `interim_liability_stays_escrow_and_hardship_relief`
- `loss_recognition_symmetry`
- `measurement_cadence_and_proxy_graduation`
- `net_fiscal_stack_disclosure_and_substitution`
- `precaution_threshold_gating`
- `proceeds_visibility_local_share_and_earmarking`
- `regressivity_repair_channel_and_delivery_sync`
- `relabeling_dependence_and_category_integrity`
- `reliance_privilege_phase_in_and_grandfathering`
- `reportable_transaction_material_advisor_promoter_and_advisee_list`
- `review_trigger_conversion_and_sunset`
- `same_facts_reuse_portability_and_delta_update`
- `standing_bundle_and_non_conflicted_representation`
- `status_proxy_disparate_impact_and_accessibility_repair`
- `supplier_benefit_net_terms_and_retained_surplus`
- `threshold_cliff_smoothing_and_graduation`
- `verification_sampling_and_review_intensity`

### `social_floor_public_services` — 2 uncovered

- `charitable_public_benefit_transfer_and_retained_surplus`
- `public_service_member_relief_and_local_repair`

### `tax_administration_access` — 10 uncovered

- `administration_explanation_and_appeal_minimum`
- `bounded_contest_issue_scoped_correction_and_period_finality`
- `collection_anchor_choice_and_remittance_chain`
- `compliance_cost_assisted_filing_and_preparer_dependence`
- `official_error_prefill_and_guidance_reliance`
- `provisional_controller_filing_escrow_and_true_up`
- `record_asymmetry_burden_shifting_and_adverse_inference`
- `reinvestment_prefunding_ring_fence_and_retained_surplus`
- `third_party_reporting_correction_and_bounded_recipient_shelter`
- `timing_cashflow_liquidity_deferral_and_prefunding`

### `wealth_property_rent` — 3 uncovered

- `annual_wealth_backstop_visibility_grouping_and_liquidity`
- `land_site_rent_netting_and_retained_surplus`
- `real_value_indexation_and_reset_cadence`

## Source IDs only

[S674][S675][S676][S677][S678][S679][S680]

[S674]: ../../SOURCES.md#S674
[S675]: ../../SOURCES.md#S675
[S676]: ../../SOURCES.md#S676
[S677]: ../../SOURCES.md#S677
[S678]: ../../SOURCES.md#S678
[S679]: ../../SOURCES.md#S679
[S680]: ../../SOURCES.md#S680
