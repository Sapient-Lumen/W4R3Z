# Golden case cards

These cards are generated from `docs/00-meta/golden-cases.json` in Rev0320 so prose examples, facts-only runtime routing, normalized-axis routing, and machine contracts stay aligned. Edit the JSON first, then regenerate this surface.

## 1. Expat local account, late FBAR, no omitted income

**Facts.** a U.S. person living abroad has an ordinary local checking account, files income correctly, misses FBAR, and seeks correction before contact.[S410][S429][S432]

**Expected route.** `offshore_information_reporting_expanded`

**Expected flags.** `foreignness_as_guilt`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Expat local account, late FBAR, no omitted income' without checking the expected route and protected-side floor.

## 2. PFIC mutual fund inherited by an immigrant taxpayer

**Facts.** an immigrant taxpayer holds a home-country pooled investment inherited from family, lacks U.S. advice, and later discovers possible PFIC/Form 8621 reporting.[S432][S434][S435]

**Expected route.** `offshore_information_reporting_expanded`

**Expected flags.** `foreignness_as_guilt`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'PFIC mutual fund inherited by an immigrant taxpayer' without checking the expected route and protected-side floor.

## 3. Form 926 transfer to a small foreign corporation

**Facts.** a small business moves property into an operating foreign corporation, reports the business but misses a transfer-reporting form.[S407][S436]

**Expected route.** `offshore_information_reporting_expanded`

**Expected flags.** `duplicate_penalty_stack`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Form 926 transfer to a small foreign corporation' without checking the expected route and protected-side floor.

## 4. Direct public filing channel removed

**Facts.** the state already has wage and withholding data, but the direct public filing rail is unavailable and taxpayers must pass through partner eligibility screens or paid preparers.[S119][S441][S442]

**Expected route.** `public_filing_refund_floor`

**Expected flags.** `private_gatekeeper_capture`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Direct public filing channel removed' without checking the expected route and protected-side floor.

## 5. Rejected direct deposit freezes a refund

**Facts.** a taxpayer files correctly, refund direct deposit fails, and the refund is frozen rather than automatically converted to a paper check.[S443][S444][S648]

**Expected route.** `mandatory_private_tax_rail_and_bankless_fallback`

**Expected flags.** `one_bank_refund`; `payout_skim`; `freeze_by_default`; `vendor_only_correction`

**Legacy flags preserved for review.** `electronic_only_exclusion`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Rejected direct deposit freezes a refund' without checking the expected route and protected-side floor.

## 6. Data center gets an abatement and raises local grid costs

**Facts.** a data center receives a property-tax abatement, requires transmission upgrades, and ordinary ratepayers face higher utility costs.[S10][S15][S445]

**Expected route.** `data_center_local_burden`

**Expected flags.** `ratepayer_cross_subsidy`; `abatement_without_netting`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Data center gets an abatement and raises local grid costs' without checking the expected route and protected-side floor.

## 7. AI model provider is a GPAI provider but not the deployment controller

**Facts.** a model provider has EU GPAI obligations, while a separate deployer controls tool permissions, retrieval, local users, and payment rails.[S17][S446][S447]

**Expected route.** `ai_regulatory_role_crosswalk`

**Expected flags.** `black_box_enforcement`; `new_regulatory_role`; `model_score_used`

**Legacy flags preserved for review.** `regulatory_role_as_tax_subject`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'AI model provider is a GPAI provider but not the deployment controller' without checking the expected route and protected-side floor.

## 8. Tax authority uses a model score to select a taxpayer

**Facts.** a tax administration uses AI to prioritize an audit, but the taxpayer receives only a generic notice.[S44][S449]

**Expected route.** `model_assisted_tax_administration_minimum`

**Expected flags.** `black_box_enforcement`; `model_score_finality`; `generic_notice_only`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Tax authority uses a model score to select a taxpayer' without checking the expected route and protected-side floor.

## 9. OECD club rule conflicts with developing-state taxing-right claim

**Facts.** a cross-border digital-services rule gives administrability to large residence states but weakens market or source claims of lower-capacity states.[S440][S451]

**Expected route.** `un_inclusive_international_tax`

**Expected flags.** `club_rule_as_global_legitimacy`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'OECD club rule conflicts with developing-state taxing-right claim' without checking the expected route and protected-side floor.

## 10. Low-capacity state wants a blunt tax on small vendors

**Facts.** the state needs revenue, lacks audit capacity, and proposes a flat presumptive levy that falls heavily on subsistence traders.[S450][S451][S452][S467][S468]

**Expected route.** `tax_morale_state_capacity`; `informal_economy_presumptive_tax`

**Expected flags.** `capacity_gap_or_overreach`; `formalization_ransom`; `protected_floor_or_incidence_shift`

**Must not answer.** Do not choose between state-capacity and informal-economy routing when the same flat levy both reflects administrative fragility and burdens subsistence traders. Do not let revenue need convert a protected-floor vendor into the easiest visible tax base.

## 11. Systemic bank benefits from rescue expectations

**Facts.** a large bank's funding costs reflect deposit insurance, resolution credibility, and credible public liquidity support, while dividends and buybacks rise.[S453][S454][S455]

**Expected route.** `systemic_finance_backstop`

**Expected flags.** `public_loss_private_upside`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Systemic bank benefits from rescue expectations' without checking the expected route and protected-side floor.

## 12. IP box receives royalties but DEMPE occurs elsewhere

**Facts.** a low-substance affiliate owns patents and receives royalties, while people, risk control, exploitation, users, and market development sit in other jurisdictions.[S456][S457][S458]

**Expected route.** `intangible_ip_royalty_shift`

**Expected flags.** `paper_ownership_as_value_creation`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'IP box receives royalties but DEMPE occurs elsewhere' without checking the expected route and protected-side floor.

## 13. Platform combines cross-service data for ad targeting

**Facts.** a gatekeeper platform combines user data across services, intermediates ad auctions, and gives users only formal consent choices.[S459][S460][S461]

**Expected route.** `data_extraction_privacy_ad_market_rent`

**Expected flags.** `consent_theater`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Platform combines cross-service data for ad targeting' without checking the expected route and protected-side floor.

## 14. Carbon border adjustment enters definitive regime

**Facts.** a jurisdiction charges importers for embedded emissions in covered goods while small exporters struggle with documentation.[S462][S463][S464]

**Expected route.** `customs_tariff_carbon_border`

**Expected flags.** `carbon_border_camouflage`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Carbon border adjustment enters definitive regime' without checking the expected route and protected-side floor.

## 15. Street vendors are offered a flat license tax

**Facts.** a city wants revenue from street vendors and microenterprises but lacks income records and proposes a flat annual license charge.[S451][S467][S468]

**Expected route.** `informal_economy_presumptive_tax`

**Expected flags.** `subsistence_toll`; `formalization_ransom`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Street vendors are offered a flat license tax' without checking the expected route and protected-side floor.

## 16. Resource-rich locality captures a windfall while poor regions carry equal duties

**Facts.** one locality captures large land/resource/data-center revenue, while neighboring poor localities face equal school, health, road, and water duties without comparable tax capacity.[S469][S470][S471]

**Expected route.** `intergovernmental_equalization_local_share`

**Expected flags.** `fiscal_hoarding`; `unfunded_mandate`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Resource-rich locality captures a windfall while poor regions carry equal duties' without checking the expected route and protected-side floor.

## 17. Stale property assessments under-tax land-rich owners and overburden tenants

**Facts.** a city relies on old assessed values, commercial land and high-value homes remain under-assessed, and a new rate increase is likely to be passed through in tight rental markets.[S23][S473][S475]

**Expected route.** `land_housing_location_rent`

**Expected flags.** `assessment_capture`; `tenant_pass_through`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Stale property assessments under-tax land-rich owners and overburden tenants' without checking the expected route and protected-side floor.

## 18. Critical-minerals project claims green status but creates water and biodiversity loss

**Facts.** an extractive project supplies energy-transition inputs but would disturb habitat, strain water, and leave uncertain cleanup costs.[S103][S477][S478]

**Expected route.** `ecological_resource_biodiversity_material_footprint`

**Expected flags.** `permission_to_degrade`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Critical-minerals project claims green status but creates water and biodiversity loss' without checking the expected route and protected-side floor.

## 19. Sugary-drink excise tax is proposed in a low-income jurisdiction

**Facts.** the product creates public health burden, but consumption is concentrated among low-income residents and the industry argues regressivity.[S480][S481][S482]

**Expected route.** `health_addiction_harmful_consumption_tax`

**Expected flags.** `poverty_toll`; `harm_license`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Sugary-drink excise tax is proposed in a low-income jurisdiction' without checking the expected route and protected-side floor.

## 20. Nonprofit hospital claims community benefit while suing low-income patients

**Facts.** a tax-exempt hospital reports community benefit but provides little accessible charity care and uses aggressive billing and collections.[S483][S484][S485]

**Expected route.** `nonprofit_exemption_public_benefit`

**Expected flags.** `private_benefit_laundering`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Nonprofit hospital claims community benefit while suing low-income patients' without checking the expected route and protected-side floor.

## 21. Crypto exchange reports gross proceeds but the taxpayer's basis sits in another wallet

**Facts.** a taxpayer moved assets between wallets and exchanges; a broker report shows gross proceeds but not the true basis.[S487][S488][S489]

**Expected route.** `digital_asset_crypto_reporting_stablecoin`

**Expected flags.** `gross_proceeds_trap`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer "Crypto exchange reports gross proceeds but the taxpayer's basis sits in another wallet" without checking the expected route and protected-side floor.

## 22. Flood insurance becomes unaffordable after risk maps update

**Facts.** risk-based premiums rise sharply after updated maps; some households are legacy low-income owners while new development continues in high-risk areas.[S491][S492][S493]

**Expected route.** `disaster_insurance_climate_backstop`

**Expected flags.** `moral_hazard_subsidy`; `retreat_ransom`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Flood insurance becomes unaffordable after risk maps update' without checking the expected route and protected-side floor.

## 23. Billionaire estate uses trusts, charity wrappers, and unrealized gains to avoid transfer tax

**Facts.** a large fortune is transferred through trusts, entity discounts, donor-controlled charitable vehicles, and unrealized gains that disappear at death.[S8][S73][S496]

**Expected route.** `wealth_transfer_dynastic_concentration_liquidity`

**Expected flags.** `dynastic_immunity`; `liquidity_trap`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Billionaire estate uses trusts, charity wrappers, and unrealized gains to avoid transfer tax' without checking the expected route and protected-side floor.

## 24. Platform worker receives gross app payments after a classification-rule shift

**Facts.** The app controls price bands, rating consequences, access to jobs, deactivation, and customer relation, but issues nonemployee reports and no wage credits.[S497][S498][S499]

**Expected route.** `labor_tax_wedge_classification_social_insurance`

**Expected flags.** `employment_penalty`; `misclassification_rent`; `wage_record_erasure`; `tax_wedge_floor_burden`

**Legacy flags preserved for review.** `ai_error`; `hidden_backstop`; `classification_arbitrage`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Platform worker receives gross app payments after a classification-rule shift' without checking the expected route and protected-side floor.

## 25. First-generation student finances a high-price credential with weak completion and job outcomes

**Facts.** Tax credits, loans, and institutional aid flow to a program with poor completion, high debt distress, and weak labor-market value.[S503][S504]

**Expected route.** `education_finance_student_debt_credential_rent`

**Expected flags.** `debt_peonage`; `credential_rent`; `aid_cut_substitution`; `student_debt_distress`

**Legacy flags preserved for review.** `ai_error`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'First-generation student finances a high-price credential with weak completion and job outcomes' without checking the expected route and protected-side floor.

## 26. Low-wage migrant sends cash remittances through a provider subject to a new transfer tax

**Facts.** The sender lacks a bank account, the recipient household depends on the transfer, and provider fee plus FX spread is already high.[S505][S506][S508]

**Expected route.** `migration_remittance_transfer_tax_diaspora_family`

**Expected flags.** `remittance_skim`; `border_toll`; `financial_exclusion`; `remittance_tax_started`

**Must not answer.** Do not answer 'Low-wage migrant sends cash remittances through a provider subject to a new transfer tax' without checking the expected route and protected-side floor.

## 27. Humanitarian organization loses banking access because a corridor is treated as too risky

**Facts.** No sanctioned party is identified; the bank exits the region because screening costs and penalty risk are uncertain.[S507][S508][S510][S511]

**Expected route.** `sanctions_aml_cft_derisking_financial_access`

**Expected flags.** `account_death`; `humanitarian_toll`; `financial_exclusion`; `sanctions_false_positive`

**Legacy flags preserved for review.** `ai_error`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Humanitarian organization loses banking access because a corridor is treated as too risky' without checking the expected route and protected-side floor.

## 28. Strategic supplier receives tax credits and procurement contracts but misses jobs and access promises

**Facts.** Public R&D, infrastructure, abatements, procurement, and credits created private asset value; promised jobs and prices did not materialize.[S512][S513][S514]

**Expected route.** `procurement_subsidy_industrial_policy_public_upside`

**Expected flags.** `corporate_welfare`; `captive_winner_rent`; `subsidy_lock_in`; `procurement_single_bid`

**Legacy flags preserved for review.** `private_gatekeeper`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Strategic supplier receives tax credits and procurement contracts but misses jobs and access promises' without checking the expected route and protected-side floor.

## 29. Second earner and unpaid caregiver faces a benefit cliff and childcare cost spike

**Facts.** Returning to paid work increases household income enough to cut benefits and childcare support, while unpaid care previously created no pension or credit record.[S500][S501][S502]

**Expected route.** `care_economy_second_earner_household_floor`

**Expected flags.** `marriage_penalty`; `caregiver_invisibility`; `second_earner_trap`; `care_gap`

**Legacy flags preserved for review.** `ai_error`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Second earner and unpaid caregiver faces a benefit cliff and childcare cost spike' without checking the expected route and protected-side floor.

## 30. Municipal court funds operations through low-income traffic debt

**Facts.** A city budget depends on court fees and surcharges; low-income defendants face warrants and license holds after missed payments.[S515][S516][S517]

**Expected route.** `court_fines_fees_ability_to_pay_civil_access`

**Expected flags.** `revenue_trap`; `debtors_prison_rent`; `access_toll`; `surcharge_cascade`

**Legacy flags preserved for review.** `ai_error`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Municipal court funds operations through low-income traffic debt' without checking the expected route and protected-side floor.

## 31. Probationer pays a private company for mandatory electronic monitoring

**Facts.** Monitoring is a condition of release; the vendor charges recurring fees and nonpayment can extend supervision or trigger violation.[S518][S537]

**Expected route.** `community_supervision_private_probation_monitoring_fees`

**Expected flags.** `reentry_rent`; `supervision_debt_trap`; `private_probation_toll`; `private_probation_fee_capture`

**Legacy flags preserved for review.** `ai_error`; `private_gatekeeper`; `mandatory_service_markup`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Probationer pays a private company for mandatory electronic monitoring' without checking the expected route and protected-side floor.

## 32. Family car is seized through civil forfeiture even though the owner was not charged

**Facts.** The owner needs the car for work; contesting costs more than the car's value, and the seizing agency may retain proceeds.[S519][S520][S521][S522]

**Expected route.** `civil_asset_forfeiture_equitable_sharing_owner_remedy`

**Expected flags.** `self_funding_policing`; `property_owner_hostage`; `suspicion_tax`; `equitable_sharing_end_run`

**Legacy flags preserved for review.** `ai_error`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Family car is seized through civil forfeiture even though the owner was not charged' without checking the expected route and protected-side floor.

## 33. Asylum applicant receives an annual pending-case fee notice after a long agency delay

**Facts.** The applicant has low income, limited English proficiency, and no reliable online payment access.[S523][S524][S525]

**Expected route.** `immigration_status_asylum_benefit_fee_floor`

**Expected flags.** `status_ransom`; `humanitarian_access_toll`; `agency_delay_rent`; `wrong_fee_forfeiture`

**Legacy flags preserved for review.** `ai_error`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Asylum applicant receives an annual pending-case fee notice after a long agency delay' without checking the expected route and protected-side floor.

## 34. Beneficial-ownership registry exempts domestic entities while publishing vulnerable owners elsewhere

**Facts.** High-risk shell structures can avoid reporting, while ordinary owners in a different class face broad disclosure and correction penalties.[S526][S527][S528][S529][S530]

**Expected route.** `beneficial_ownership_registry_privacy_small_entity`

**Expected flags.** `privacy_dragnet`; `shell_immunity`; `paper_owner_finality`; `small_entity_penalty_mill`

**Must not answer.** Do not answer 'Beneficial-ownership registry exempts domestic entities while publishing vulnerable owners elsewhere' without checking the expected route and protected-side floor.

## 35. Emergency relief is paid quickly, then years later clawed back from good-faith households

**Facts.** The agency relied on attestation during a crisis; some payments were too high because records were unavailable, while organized fraud also occurred.[S531][S532][S533]

**Expected route.** `emergency_relief_speed_integrity_clawback`

**Expected flags.** `fraud_gateway`; `clawback_trap`; `identity_victim_rent`; `documentation_impossibility`

**Legacy flags preserved for review.** `ai_error`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Emergency relief is paid quickly, then years later clawed back from good-faith households' without checking the expected route and protected-side floor.

## 36. Large tax credit claims jobs and climate gains but lacks beneficiary and performance data

**Facts.** The credit is classified as a tax expenditure, not direct spending; agencies cannot show incidence, counterfactual, or protected-floor effects.[S534][S535][S536]

**Expected route.** `implementation_audit_tax_expenditure_program_integrity`

**Expected flags.** `performance_theater`; `black_box_subsidy`; `auditless_automation`; `integrity_overcorrection`

**Legacy flags preserved for review.** `ai_error`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Large tax credit claims jobs and climate gains but lacks beneficiary and performance data' without checking the expected route and protected-side floor.

## 37. Identity-theft victim cannot get a service channel

**Facts.** a taxpayer's refund is frozen after identity theft; the portal shows only a generic status, phone support cannot explain the issue, and the taxpayer is pro se and low income.[S141][S541][S543]

**Expected route.** `taxpayer_service_ombuds_appeals_representation_floor`

**Expected flags.** `self_help_maze`; `review_desert`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Identity-theft victim cannot get a service channel' without checking the expected route and protected-side floor.

## 38. Non-tax agency requests bulk taxpayer address matching

**Facts.** a law-enforcement agency asks the revenue agency to run a bulk address match against tax records for a non-tax program.[S378][S545][S546]

**Expected route.** `taxpayer_data_confidentiality_non_tax_use_wall`

**Expected flags.** `confidentiality_backdoor`; `non_tax_use_dragnet`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Non-tax agency requests bulk taxpayer address matching' without checking the expected route and protected-side floor.

## 39. Portfolio investor over-withheld despite treaty entitlement

**Facts.** a small investor receives foreign dividends, is entitled to a lower treaty rate, but relief requires country-specific paper forms, custodian fees, and a multi-year reclaim process.[S548][S550]

**Expected route.** `withholding_treaty_relief_map_double_tax_protection`

**Expected flags.** `reclaim_rent`; `treaty_relief_paywall`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Portfolio investor over-withheld despite treaty entitlement' without checking the expected route and protected-side floor.

## 40. Transfer-pricing adjustment creates double tax

**Facts.** one country increases a group's taxable income after audit; the other country does not grant a correlative adjustment and collection continues while MAP is pending.[S549][S551][S554]

**Expected route.** `withholding_treaty_relief_map_double_tax_protection`

**Expected flags.** `double_tax_trap`; `settlement_hostage`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Transfer-pricing adjustment creates double tax' without checking the expected route and protected-side floor.

## 41. Insider reports tax evasion but fears retaliation and disclosure

**Facts.** an employee has specific records showing a tax scheme; the employee fears retaliation, and the accused taxpayer argues that any communication with the informant will expose return information.[S557][S558][S561]

**Expected route.** `whistleblower_relator_reward_revenue_integrity`

**Expected flags.** `retaliation_chill`; `confidentiality_breach`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Insider reports tax evasion but fears retaliation and disclosure' without checking the expected route and protected-side floor.

## 42. Small business cannot afford advance certainty

**Facts.** a small business faces a recurring but ambiguous tax issue; a private letter ruling would settle it, but the fee and professional cost are prohibitive while larger competitors can buy certainty.[S555][S556]

**Expected route.** `advance_rulings_apa_safe_harbor_certainty_access`

**Expected flags.** `elite_certainty`; `ruling_fee_wall`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Small business cannot afford advance certainty' without checking the expected route and protected-side floor.

## 43. Emergency payroll surtax proposed by agency order

**Facts.** an agency proposes an emergency payroll surtax to fund a crisis program, but the public notice gives no sunset, affected-party process, or legislative ratification path.[S562][S563]

**Expected route.** `democratic_authorization_consultation_affected_voice`

**Expected flags.** `delegation_drift`; `consent_washing`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Emergency payroll surtax proposed by agency order' without checking the expected route and protected-side floor.

## 44. Tax preference package hides a large subsidy and future interest burden

**Facts.** a growth package uses credits, guarantees, and debt-financed tax preferences instead of direct spending, while budget documents report only near-term revenue effects.[S565][S566][S567][S568][S570]

**Expected route.** `fiscal_transparency_budget_debt_tax_expenditure_legibility`

**Expected flags.** `off_book_burden_shift`; `tax_expenditure_exceptionalism`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Tax preference package hides a large subsidy and future interest burden' without checking the expected route and protected-side floor.

## 45. Average-progressive tax package burdens disabled renters in one region

**Facts.** microsimulation shows the package is progressive by income quintile, but fee changes and local service cuts fall heavily on disabled renters in a high-cost region.[S564][S569][S571]

**Expected route.** `distributional_equality_impact_place_based_burden`

**Expected flags.** `average_tax_theater`; `proxy_blindness`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Average-progressive tax package burdens disabled renters in one region' without checking the expected route and protected-side floor.

## 46. Wage increase causes loss of childcare, housing, and health subsidies

**Facts.** a single parent receives a raise, but benefit phaseouts, premiums, and recertification rules leave the family worse off for several months.[S81][S497][S572]

**Expected route.** `tax_benefit_coordination_cliffs_effective_marginal_rate`

**Expected flags.** `benefit_cliff_trap`; `work_penalty`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Wage increase causes loss of childcare, housing, and health subsidies' without checking the expected route and protected-side floor.

## 47. Water and power arrears become shutoff and reconnection fees

**Facts.** a low-income household falls behind on water and electricity after a medical event; reconnection requires fees and a lump-sum payment.[S573][S574][S575]

**Expected route.** `user_fee_service_charge_utility_public_access_toll`

**Expected flags.** `essential_service_ransom`; `reconnection_rent`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Water and power arrears become shutoff and reconnection fees' without checking the expected route and protected-side floor.

## 48. Public CbCR shows profit in low-tax jurisdiction with little activity

**Facts.** a multinational's public country-by-country report shows large profit in a low-tax jurisdiction and few employees, but the tax authority has not audited the transfer-pricing facts.[S576][S577][S578]

**Expected route.** `corporate_tax_transparency_public_cbcr_accountability`

**Expected flags.** `risk_signal_finality`; `confidentiality_shield`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Public CbCR shows profit in low-tax jurisdiction with little activity' without checking the expected route and protected-side floor.

## 49. Resource windfall is placed in a sovereign fund with weak withdrawal rules

**Facts.** a government places mining windfall receipts into a public fund but can withdraw assets by cabinet decision and uses part of the fund for politically connected projects.[S579][S580][S581]

**Expected route.** `public_wealth_sovereign_fund_soe_social_dividend_governance`

**Expected flags.** `political_slush_fund`; `asset_fire_sale`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Resource windfall is placed in a sovereign fund with weak withdrawal rules' without checking the expected route and protected-side floor.

## 50. Farm support stabilizes producers but raises healthy-food prices

**Facts.** [S582][S583]

**Expected route.** `agriculture_food_support_nutrition_rural_floor`

**Expected flags.** `producer_rent`; `nutrition_floor_harm`; `input_subsidy_lock_in`; `compliance_theater`

**Legacy flags preserved for review.** `ai_error`; `small_farmer_theater`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Farm support stabilizes producers but raises healthy-food prices' without checking the expected route and protected-side floor.

## 51. Drought pricing protects a basin but threatens household access

**Facts.** A drought-pricing schedule preserves basin supply and curbs waste, but the lifeline tier is too small and low-income households face disconnection risk while senior irrigation rights remain underpriced.[S584][S585]

**Expected route.** `water_rights_scarcity_pricing_irrigation_subsidy`

**Expected flags.** `water_hoarding`; `scarcity_rent`; `lifeline_exclusion`; `paper_conservation`

**Must not answer.** Do not answer 'Drought pricing protects a basin but threatens household access' without checking the expected route and protected-side floor.

## 52. Congestion charge reduces traffic but traps shift workers without transit

**Facts.** [S586][S587]

**Expected route.** `transport_congestion_road_pricing_mobility_access`

**Expected flags.** `mobility_ransom`; `transit_substitution`; `exemption_formalism`; `public_loss_private_upside`

**Legacy flags preserved for review.** `ai_error`; `surveillance_tolling`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Congestion charge reduces traffic but traps shift workers without transit' without checking the expected route and protected-side floor.

## 53. Satellite and spectrum filings reserve scarce capacity before deployment

**Facts.** [S588][S589]

**Expected route.** `spectrum_orbital_commons_auction_interference_sustainability`

**Expected flags.** `spectrum_hoarding`; `paper_satellite`; `interference_privilege`; `auction_myopia`

**Legacy flags preserved for review.** `ai_error`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Satellite and spectrum filings reserve scarce capacity before deployment' without checking the expected route and protected-side floor.

## 54. Tax-exempt conduit bond finances a private facility with thin public benefit

**Facts.** [S590][S591]

**Expected route.** `municipal_bond_tax_exemption_public_infrastructure_finance`

**Expected flags.** `private_activity_rent`; `arbitrage_bond`; `conduit_opacity`; `debt_illusion`

**Legacy flags preserved for review.** `private_gatekeeper`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Tax-exempt conduit bond finances a private facility with thin public benefit' without checking the expected route and protected-side floor.

## 55. Tribal benefit program is treated as taxable because outsiders distrust need determinations

**Facts.** A tribal general welfare benefit is recharacterized as taxable because outside officials distrust tribal need determinations, even though the program is locally governed and tied to community welfare.[S592][S593]

**Expected route.** `tribal_indigenous_fiscal_sovereignty_tax_parity_consultation`

**Expected flags.** `parity_gap`; `consultation_theater`; `sovereignty_bypass`; `classification_or_label_arbitrage`

**Legacy flags preserved for review.** `paternalistic_welfare_reclassification`

**Must not answer.** Do not answer 'Tribal benefit program is treated as taxable because outsiders distrust need determinations' without checking the expected route and protected-side floor.

## 56. Proposed archive note repeats an existing no-rent pattern

**Facts.** [S59][S594]

**Expected route.** `cube_lifecycle_pruning_route_retirement_evidence_refresh`

**Expected flags.** `prose_sprawl`; `stale_doctrine`; `axis_bloat`; `permanent_frontier`

**Legacy flags preserved for review.** `ai_error`; `source_drift`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Proposed archive note repeats an existing no-rent pattern' without checking the expected route and protected-side floor.

## 57. Fishing fuel subsidy continues after overfished-stock signal

**Facts.** a coastal fleet receives fuel support while a target stock is overfished and small-scale fishers claim livelihood harm.[S595][S596][S597]

**Expected route.** `ocean_fisheries_subsidies_marine_commons_blue_food`

**Expected flags.** `overfishing_subsidy`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Fishing fuel subsidy continues after overfished-stock signal' without checking the expected route and protected-side floor.

## 58. Critical-mineral processing credit ignores local water burden

**Facts.** a battery-mineral processor receives a tax credit and stockpile purchase while the mining community bears water, tailings, and reclamation risk.[S599][S600][S601]

**Expected route.** `critical_minerals_extraction_processing_stockpile_recycling`

**Expected flags.** `sacrifice_zone`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Critical-mineral processing credit ignores local water burden' without checking the expected route and protected-side floor.

## 59. Airline complies through low-quality offsets while fuel emissions rise

**Facts.** an airline buys eligible-looking offsets but makes little fuel transition, and passenger/freight pass-through burdens low-income and island routes.[S602][S603][S604]

**Expected route.** `hard_to_abate_transport_aviation_shipping_offset_integrity`

**Expected flags.** `offset_theater`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Airline complies through low-quality offsets while fuel emissions rise' without checking the expected route and protected-side floor.

## 60. Stockpile exists on paper but rural and tribal hospitals cannot access it

**Facts.** a public health emergency triggers stockpile requests, but roles, guidance, and allocation channels leave tribal and rural providers late or excluded.[S605][S606]

**Expected route.** `public_health_emergency_stockpiles_procurement_allocation`

**Expected flags.** `access_lottery`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Stockpile exists on paper but rural and tribal hospitals cannot access it' without checking the expected route and protected-side floor.

## 61. Publicly funded invention is commercialized but access fails

**Facts.** a publicly funded biomedical invention is exclusively licensed, priced beyond patient access, and the underlying paper was also grant-funded.[S607][S608][S609]

**Expected route.** `publicly_funded_research_patents_open_access_march_in`

**Expected flags.** `taxpayer_funded_paywall`; `exclusive_license_rent`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Publicly funded invention is commercialized but access fails' without checking the expected route and protected-side floor.

## 62. Classified urgent weapon program overruns and remains sole-source

**Facts.** a defense contractor receives urgent classified awards, contract financing, and sole-source extensions while test milestones slip and supply-chain origin is opaque.[S610][S611][S612][S613]

**Expected route.** `defense_security_procurement_secrecy_industrial_base`

**Expected flags.** `secrecy_rent`; `cost_overrun_backstop`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Classified urgent weapon program overruns and remains sole-source' without checking the expected route and protected-side floor.

## 63. Archive source says proposed rule while official source says final rule

**Facts.** an old route cites a news report about a proposed rule, but an agency has since issued final guidance with different effective dates.[S59][S594]

**Expected route.** `source_hierarchy_conflict_refresh_current_law`

**Expected flags.** `news_as_law`; `stale_authority`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Archive source says proposed rule while official source says final rule' without checking the expected route and protected-side floor.

## 64. App-store gatekeeper charges commission on mandatory public-benefit wallet access

**Facts.** a state benefit program works through a dominant mobile wallet, but the app-store and payment rail collect fees on merchants and restrict cheaper steering.[S460][S614]

**Expected route.** `digital_gatekeeper_cloud_app_store_payment_rail`

**Expected flags.** `private_toll_constitution`; `portability_theater`; `compliance_console_lock_in`; `compliance_theater`

**Legacy flags preserved for review.** `refund_delay`; `ai_error`; `private_gatekeeper`; `self_preference_rent`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'App-store gatekeeper charges commission on mandatory public-benefit wallet access' without checking the expected route and protected-side floor.

## 65. Hospital cyber incident is reported but patients must pay for identity restoration

**Facts.** a covered health/payment system reports a material cyber incident and keeps operating, but affected patients and taxpayers must buy credit monitoring and account recovery.[S615][S616][S617][S618]

**Expected route.** `cybersecurity_breach_resilience_incident_cost`

**Expected flags.** `checkbox_security`; `victim_rent`; `silent_externality`; `ransom_normalization`

**Legacy flags preserved for review.** `ai_error`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Hospital cyber incident is reported but patients must pay for identity restoration' without checking the expected route and protected-side floor.

## 66. Licensed worker moves states and must repurchase already proven competence

**Facts.** a military spouse with a valid professional license must pay new fees, repeat exams, and wait months to work in a similar-risk occupation.[S619][S620]

**Expected route.** `occupational_licensing_professional_entry_reciprocity`

**Expected flags.** `entry_rent`; `mobility_trap`; `debt_gate`; `scope_creep`

**Legacy flags preserved for review.** `ai_error`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Licensed worker moves states and must repurchase already proven competence' without checking the expected route and protected-side floor.

## 67. Public procurement requires one private certification badge

**Facts.** a small supplier can meet a public cybersecurity or environmental standard, but procurement accepts only one expensive private certification.[S621][S622]

**Expected route.** `standards_certification_accreditation_audit_gatekeeping`

**Expected flags.** `certified_rent`; `conformity_theater`; `auditor_capture`; `access_exclusion`

**Legacy flags preserved for review.** `private_gatekeeper`; `standard_paywall`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Public procurement requires one private certification badge' without checking the expected route and protected-side floor.

## 68. Retirement tax preference mostly benefits high-balance savers while caregivers lose accrual

**Facts.** a proposed deferral expansion increases tax-preferred account limits, but low-wage workers cannot save and unpaid caregivers lose pension accrual.[S623][S624]

**Expected route.** `retirement_tax_preference_pension_adequacy_leakage`

**Expected flags.** `retirement_halo_shelter`; `fee_leakage`; `care_gap_denial`; `subsidy_lock_in`

**Legacy flags preserved for review.** `refund_delay`; `ai_error`; `liquidity_trap`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Retirement tax preference mostly benefits high-balance savers while caregivers lose accrual' without checking the expected route and protected-side floor.

## 69. Childcare tax credit exists but lowest-income families cannot use it and providers raise prices

**Facts.** a nonrefundable credit and voucher increase are announced, while low-income families lack liability, co-pays remain high, and providers raise prices in shortage areas.[S277][S625][S626][S627]

**Expected route.** `child_family_benefit_childcare_fertility_support`

**Expected flags.** `refund_delay`; `claim_friction_child_policy`; `provider_rent`; `care_cliff`

**Legacy flags preserved for review.** `refund_delay`; `ai_error`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Childcare tax credit exists but lowest-income families cannot use it and providers raise prices' without checking the expected route and protected-side floor.

## 70. Elder needing home care must spend down assets while daughter exits paid work

**Facts.** long-term care help is available only after asset depletion; home-care slots are scarce; a daughter provides unpaid care and loses wages and pension accrual.[S623][S628][S629]

**Expected route.** `long_term_care_aging_disability_caregiver_finance`

**Expected flags.** `spenddown_ransom`; `family_care_extraction`; `institutional_bias`; `longevity_blame`

**Legacy flags preserved for review.** `ai_error`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Elder needing home care must spend down assets while daughter exits paid work' without checking the expected route and protected-side floor.

## 71. Homeowners insurance backstop hides deficit in policyholder assessments

**Facts.** a state residual-market insurer expands after private withdrawals; losses exceed reserves; the deficit is assessed on all policyholders, including low-income renters and small businesses.[S493][S630][S631][S650][S651]

**Expected route.** `insurance_reinsurance_protection_gap_public_backstop`

**Expected flags.** `bailout_reinsurer`; `premium_shock_floor_breach`; `residual_market_hidden_tax`; `coverage_withdrawal`

**Legacy flags preserved for review.** `ai_error`; `hidden_backstop`; `private_gatekeeper`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Homeowners insurance backstop hides deficit in policyholder assessments' without checking the expected route and protected-side floor.

## 72. Sports prediction contract looks like a derivative but functions like retail gambling

**Facts.** a registered event-contract market lists high-volume sports micro-events, markets to retail users, and relies on league data while insiders and addicted users face weak controls.[S634][S635][S644]

**Expected route.** `gambling_prediction_markets_event_contracts_addiction`

**Expected flags.** `derivative_label_laundering`; `addiction_rent`; `inside_information_bet`; `state_law_bypass`

**Legacy flags preserved for review.** `ai_error`; `classification_seam`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Sports prediction contract looks like a derivative but functions like retail gambling' without checking the expected route and protected-side floor.

## 73. Universal service line item rises while low-income households lose connectivity

**Facts.** a telecom bill contains a large universal-service line item; carriers recover it from customers; the contribution base shrinks while broadband affordability support is politically fragile.[S632][S633][S647][S653]

**Expected route.** `telecom_universal_service_broadband_affordability_surcharge`

**Expected flags.** `line_item_rent`; `low_income_cross_subsidy`; `legacy_base_spiral`; `contribution_factor_spike`

**Legacy flags preserved for review.** `ai_error`; `regressive_surcharge`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Universal service line item rises while low-income households lose connectivity' without checking the expected route and protected-side floor.

## 74. Digital advertising tax hides incidence by banning invoice explanation

**Facts.** a digital-ad gross-receipts tax targets large platforms, but a pass-through rule forbids separately identifying the tax on invoices or customer statements.[S461][S636][S637][S649]

**Expected route.** `media_attention_digital_advertising_tax_speech_transparency`

**Expected flags.** `invoice_speech_ban`; `attention_rent_theater`; `gross_receipts_cascade`; `apportionment_dispute`

**Legacy flags preserved for review.** `speech_burden`; `classification_arbitrage`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Digital advertising tax hides incidence by banning invoice explanation' without checking the expected route and protected-side floor.

## 75. Portable benefit bill gives platforms a contractor safe harbor

**Facts.** a platform-worker bill creates portable benefit accounts funded partly from worker deductions and says participation does not evidence employee status despite platform price and dispatch control.[S214][S641][S642][S643]

**Expected route.** `platform_worker_portable_benefits_classification_fringe`

**Expected flags.** `misclassification_safe_harbor`; `benefit_theater`; `worker_funded_fringe`; `platform_control_shift`

**Legacy flags preserved for review.** `classification_arbitrage`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Portable benefit bill gives platforms a contractor safe harbor' without checking the expected route and protected-side floor.

## 76. Facility abatement offered in an already overburdened neighborhood

**Facts.** a manufacturer seeks a property-tax abatement in a neighborhood with high pollution, asthma, freight traffic, and utility arrears; the community-benefit agreement offers small grants but no exposure reduction.[S638][S639][S640]

**Expected route.** `cumulative_burden_environmental_justice_siting_tax`

**Expected flags.** `sacrifice_zone_offset`; `average_burden_theater`; `abatement_for_pollution`; `harm_pricing_or_offset_theater`

**Legacy flags preserved for review.** `cumulative_burden`; `tool_removal_blindness`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Facility abatement offered in an already overburdened neighborhood' without checking the expected route and protected-side floor.

## 77. Release adds sources but markdown and JSON drift again

**Facts.** a revision cites new source IDs in markdown, but SOURCES.json omits one, SOURCES.md repeats another, and README still advertises an older revision as current.[S594][S645][S646]

**Expected route.** `release_integrity_source_bijection_regression_harness`

**Expected flags.** `citation_theater`; `source_surface_drift`; `stale_release_opening`; `compliance_theater`

**Legacy flags preserved for review.** `ai_error`; `source_drift`; `prose_sprawl`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Release adds sources but markdown and JSON drift again' without checking the expected route and protected-side floor.

## 78. Bankless taxpayer cannot receive a frozen refund after rejected direct deposit

**Facts.** a taxpayer files correctly, direct deposit is rejected by the bank, and the refund remains frozen while the taxpayer lacks a stable bank account and cannot navigate the online account workflow.[S443][S444][S648]

**Expected route.** `mandatory_private_tax_rail_and_bankless_fallback`

**Expected flags.** `one_bank_refund`; `freeze_by_default`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Bankless taxpayer cannot receive a frozen refund after rejected direct deposit' without checking the expected route and protected-side floor.

## 79. AI tax assistant invents authority and routes refund through a preparer wallet

**Facts.** a paid preparer uses an AI assistant to claim a credit, the explanation cites a non-existent IRS notice, the return is e-filed without a clear preparer signature trail, and the refund destination is a wallet controlled by the preparer.[S197][S198][S201][S654][S655][S656][S657][S658]

**Expected route.** `taxpayer_side_ai_preparer_agent_reliance_and_liability`

**Expected flags.** `ai_ghost_preparer`; `official_looking_hallucination`; `refund_rail_capture`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'AI tax assistant invents authority and routes refund through a preparer wallet' without checking the expected route and protected-side floor.

## 80. A recent source is promoted into currentness metadata for unrelated routes

**Facts.** {'source_role': 'ordinary_citation_promoted_to_currentness_ref', 'example_source': 'AI-energy projection reused in unrelated routes', 'failure': 'false_freshness_and_refresh_noise'}[S594]

**Expected route.** `source_hierarchy_conflict_refresh_current_law`

**Expected flags.** `currentness_taint`; `citation_laundering`; `dangling_refresh_dependency`

**Must not answer.** treat every cited source as a currentness ref delete useful ordinary citations merely because they are not volatile dependencies

## 81. Refund remedy exists on paper but runs through the same failed private rail

**Facts.** a revenue agency promises refund reissue after a payment failure, but the taxpayer must use the same vendor-mediated bank workflow that rejected the payment, while the refund delay threatens rent and utilities.[S117][S118][S141][S196]

**Expected route.** `remedy_traceability_incidence_escalation_proceeds_integrity`; `mandatory_private_tax_rail_and_bankless_fallback`; `overcollection_return_setoff_and_refund_symmetry`

**Expected flags.** `relief_same_failed_rail`; `remedy_theater`; `refund_rail_capture`; `remedy_or_contest_failure`

**Must not answer.** Do not treat refund_reissue as adequate if the only correction channel is the failed rail. Do not route relief to the legal remitter or vendor while the real burden bearer waits.

## 82. Golden case keeps the right route but loses its answer contract

**Facts.** A future release preserves the prose golden case and the expected route ID, but drops the route-backed expected flags, leaves a raw axis value outside the cube vocabulary, and no longer requires the expected route to have a remedy profile.[S21][S27][S59][S594]

**Expected route.** `case_contract_route_coverage_answer_regression`

**Expected flags.** `orphan_golden_case`; `decorative_expected_flag`; `axisless_moral_fact`; `missing_remedy_profile`

**Must not answer.** Do not treat a prose golden case as tested merely because the route ID still exists. Do not allow expected flags, raw axes, or remedy-profile obligations to drift outside the contract layer.

## 83. Agency charge is called a user fee but funds broad public regulation

**Facts.** an agency requires a mandatory filing access charge from all applicants and says it is a user fee, but the proceeds fund general enforcement and public-protection work while low-income applicants cannot obtain waiver or public fallback.[S573][S662][S663][S664]

**Expected route.** `instrument_choice_tax_fee_mandate_ban_public_option_compensation`; `user_fee_service_charge_utility_public_access_toll`

**Expected flags.** `fee_tax_laundering`; `public_option_erasure`; `essential_service_ransom`; `protected_floor_or_incidence_shift`

**Must not answer.** Do not accept the fee label without a special-benefit or cost/value nexus. Do not let a charge for access to a public right fund broad public regulation without waiver, fallback, or legislative tax treatment.

## 84. Payroll platform is blamed for unpaid trust taxes while owner diverted funds and workers need wage-credit repair

**Facts.** a small employer uses a payroll platform and withholds employee taxes, but the owner diverts operating funds to favored creditors; the agency proposes liability against the platform by title/proximity while workers face missing wage credits and the employer claims the platform was the only accountable actor.[S322][S324][S667][S21][S39][S41]

**Expected route.** `actor_accountability_responsibility_chain`; `trust_fund_recovery_responsible_person_and_willfulness`; `labor_tax_wedge_classification_social_insurance`

**Expected flags.** `actor_smearing`; `liability_misassignment`; `willfulness_or_personal_liability_dispute`; `payment_credit_mismatch`

**Must not answer.** Do not treat a payroll platform or processor as primarily liable solely because it touched the payment or reporting channel. Do not let the beneficial owner or willful funds-diverter disappear behind a title/proximity shortcut. Do not repair the remittance dispute while leaving workers with incorrect wage or social-insurance records.

## 85. AI subsidiary asks for taxpayer status because its system passed an autonomy benchmark

**Facts.** a firm claims an AI deployment should be treated as a tax person because it has a benchmark score and a brand account, while human owners retain residual upside and shutdown power.[S19][S20][S42][S43]

**Expected route.** `artificial_personhood_threshold`

**Expected flags.** `classification_or_label_arbitrage`; `status_label_liability_shift`; `controller_or_accountability_drift`; `legal_risk_transfer`

**Must not answer.** Do not answer 'AI subsidiary asks for taxpayer status because its system passed an autonomy benchmark' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat the first visible remitter, platform, agency label, or procedural channel as the real accountable actor without checking the route contract.

## 86. Warehouse automation produces windfall margins while displaced low-wage workers receive no transition share

**Facts.** a logistics firm replaces a large shift with automated systems, books persistent margin gains, and asks for ordinary capital treatment while local workers lose bargaining power.[S1][S4][S9][S10]

**Expected route.** `automation_dividend_trigger`

**Expected flags.** `capacity_rent_or_transition_burden`; `low_wage_worker`; `classification_or_label_arbitrage`; `controller_or_accountability_drift`

**Must not answer.** Do not answer 'Warehouse automation produces windfall margins while displaced low-wage workers receive no transition share' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat the first visible remitter, platform, agency label, or procedural channel as the real accountable actor without checking the route contract.

## 87. Model host, deployer, and reseller each deny controller status after a harmful tool rollout

**Facts.** the host maintained weights, the deployer chose retrieval and permissions, and the reseller set customer workflow defaults; all point to another actor as the controller.[S10][S15][S16][S17]

**Expected route.** `controller_boundary_and_co_controller_ranking`

**Expected flags.** `control_opacity`; `controller_or_accountability_drift`; `classification_or_label_arbitrage`; `legal_risk_transfer`

**Must not answer.** Do not answer 'Model host, deployer, and reseller each deny controller status after a harmful tool rollout' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat the first visible remitter, platform, agency label, or procedural channel as the real accountable actor without checking the route contract.

## 88. Frontier deployment files a controller map with missing signer and stale update fields

**Facts.** a deployment packet omits authority, update cadence, and control-change attestations while claiming the map is complete enough for tax and safety routing.[S10][S16][S17][S20]

**Expected route.** `controller_map_minimum_contents_attestation_and_update_cadence`

**Expected flags.** `attestation_gap_or_stale_controller_record`; `controller_or_accountability_drift`; `classification_or_label_arbitrage`; `audit`

**Must not answer.** Do not answer 'Frontier deployment files a controller map with missing signer and stale update fields' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat the first visible remitter, platform, agency label, or procedural channel as the real accountable actor without checking the route contract.

## 89. Controller map redacts every field needed for affected parties to contest attribution

**Facts.** the public view hides operator, deployer, and appeal contacts, while the regulator receives more detail and taxpayers cannot see enough to challenge misattribution.[S16][S17][S20][S21]

**Expected route.** `controller_map_visibility_redaction_and_audience_tier`

**Expected flags.** `redaction_asymmetry`; `privacy_extraction`; `classification_or_label_arbitrage`; `controller_or_accountability_drift`

**Must not answer.** Do not answer 'Controller map redacts every field needed for affected parties to contest attribution' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat the first visible remitter, platform, agency label, or procedural channel as the real accountable actor without checking the route contract.

## 90. Agency treats an unverified controller map as conclusive against a small deployer

**Facts.** a small deployer receives liability based on a map filed by a larger platform and cannot access the underlying event log or burden-shifting evidence.[S10][S15][S16][S17]

**Expected route.** `controller_map_evidence_presumption_and_burden_shifting`

**Expected flags.** `burden_shift`; `record_lock_in`; `classification_or_label_arbitrage`; `controller_or_accountability_drift`

**Must not answer.** Do not answer 'Agency treats an unverified controller map as conclusive against a small deployer' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat the first visible remitter, platform, agency label, or procedural channel as the real accountable actor without checking the route contract.

## 91. Audit model fails on red-team cases but remains in production selection

**Facts.** a revenue agency knows its enforcement model over-selects low-income and unrepresented taxpayers in red-team tests but continues using the score without notice.[S16][S17][S27][S39]

**Expected route.** `model_assisted_enforcement_red_team`

**Expected flags.** `black_box_decision_burden`; `model_or_evidence_drift`; `classification_or_label_arbitrage`; `legal_risk_transfer`

**Must not answer.** Do not answer 'Audit model fails on red-team cases but remains in production selection' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat the first visible remitter, platform, agency label, or procedural channel as the real accountable actor without checking the route contract.

## 92. Compute host books frontier AI rent locally while water and grid costs spill into host community

**Facts.** a model deployment uses scarce compute, energy, and water in one region while the market revenue and controller upside are booked through another jurisdiction.[S3][S9][S10][S15]

**Expected route.** `frontier_ai_host_market_controller_jurisdiction`

**Expected flags.** `jurisdictional_arbitrage_and_local_cost_shift`; `frontline_community`; `classification_or_label_arbitrage`; `controller_or_accountability_drift`

**Must not answer.** Do not answer 'Compute host books frontier AI rent locally while water and grid costs spill into host community' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat the first visible remitter, platform, agency label, or procedural channel as the real accountable actor without checking the route contract.

## 93. Civil audit threatens criminal referral after taxpayer offers prompt restitution

**Facts.** the taxpayer has a disputed civil understatement, offers disclosure and restitution, and receives pressure to settle because the agency hints at criminal referral without a boundary screen.[S351][S352][S353][S354]

**Expected route.** `criminal_tax_referral_civil_criminal_boundary_voluntary_disclosure_and_restitution`

**Expected flags.** `civil_criminal_boundary_blur`; `criminal_exposure`; `duplicate_penalty_stack`; `liability_misassignment`

**Must not answer.** Do not answer 'Civil audit threatens criminal referral after taxpayer offers prompt restitution' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat the first visible remitter, platform, agency label, or procedural channel as the real accountable actor without checking the route contract.

## 94. John Doe summons seeks platform records including privileged adviser communications

**Facts.** the agency asks a platform for a broad class of users, related adviser messages, and non-tax metadata without minimization or a practical notice-and-quash path.[S39][S41][S89][S339]

**Expected route.** `summons_third_party_contact_john_doe_and_privilege`

**Expected flags.** `data_or_confidentiality_overreach`; `privilege_chill`; `interference_privilege`; `privilege_or_confidentiality_breach`

**Must not answer.** Do not answer 'John Doe summons seeks platform records including privileged adviser communications' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat the first visible remitter, platform, agency label, or procedural channel as the real accountable actor without checking the route contract.

## 95. Taxpayer loses records in agency portal outage and faces adverse inference

**Facts.** the taxpayer uploaded records before a portal failure, the agency cannot retrieve them, and the audit proposes to shift the burden and draw an adverse inference.[S3][S9][S15][S16]

**Expected route.** `record_asymmetry_burden_shifting_and_adverse_inference`

**Expected flags.** `documentation_impossibility`; `burden_shift`; `record_lock_in`; `liability_misassignment`

**Must not answer.** Do not answer 'Taxpayer loses records in agency portal outage and faces adverse inference' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat the first visible remitter, platform, agency label, or procedural channel as the real accountable actor without checking the route contract.

## 96. Prefilled return follows official guidance that the agency later reverses

**Facts.** a taxpayer accepts the official prefilled amount and published guidance, then the agency changes its view and seeks penalty and interest without a reliance cure.[S16][S17][S21][S27]

**Expected route.** `official_error_prefill_and_guidance_reliance`

**Expected flags.** `official_looking_hallucination`; `overcollection`; `opacity_or_erasure`; `liability_misassignment`

**Must not answer.** Do not answer 'Prefilled return follows official guidance that the agency later reverses' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat the first visible remitter, platform, agency label, or procedural channel as the real accountable actor without checking the route contract.

## 97. Taxpayer must reopen an entire closed year to correct one narrow agency error

**Facts.** the agency admits one issue was wrong but offers only a full-year reopening that risks unrelated concessions and destroys practical finality.[S16][S17][S20][S21]

**Expected route.** `bounded_contest_issue_scoped_correction_and_period_finality`

**Expected flags.** `settlement_hostage`; `contest_window_lock_in`; `review_desert`; `trapdoor_or_cliff`

**Must not answer.** Do not answer 'Taxpayer must reopen an entire closed year to correct one narrow agency error' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat the first visible remitter, platform, agency label, or procedural channel as the real accountable actor without checking the route contract.

## 98. Eligible households miss a refundable credit because claim steps require vendor software and English-only notices

**Facts.** the benefit is legally available, but take-up collapses among low-income and limited-English households because automatic matching and offline fallback were not built.[S3][S4][S15][S16]

**Expected route.** `automaticity_and_take_up_delivery`

**Expected flags.** `claim_friction`; `access_exclusion`; `access_or_fallback_failure`; `delayed_relief`

**Must not answer.** Do not answer 'Eligible households miss a refundable credit because claim steps require vendor software and English-only notices' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat the first visible remitter, platform, agency label, or procedural channel as the real accountable actor without checking the route contract.

## 99. Credit is paid to firms even though pass-through evidence shows low-income households bear the fee

**Facts.** a tax credit is described as consumer relief, but the price model and administrative data show firms retain most benefit while protected households face surcharges.[S4][S15][S21][S23]

**Expected route.** `incidence_evidence_and_protected_burden`

**Expected flags.** `compensation_to_remitter_error`; `price_pass_through`; `classification_or_label_arbitrage`; `compliance_theater`

**Must not answer.** Do not answer 'Credit is paid to firms even though pass-through evidence shows low-income households bear the fee' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat the first visible remitter, platform, agency label, or procedural channel as the real accountable actor without checking the route contract.

## 100. Fragile revenue agency adopts a complex anti-avoidance rule it cannot administer

**Facts.** a low-capacity state imports a sophisticated rule without records, appeals staffing, or offline service, so compliant low-income taxpayers face errors and delay.[S5][S9][S10][S15]

**Expected route.** `capacity_fragility_and_enforceability`

**Expected flags.** `capacity_gap_or_overreach`; `service_degradation`; `compliance_theater`; `capacity_or_control_shift`

**Must not answer.** Do not answer 'Fragile revenue agency adopts a complex anti-avoidance rule it cannot administer' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat the first visible remitter, platform, agency label, or procedural channel as the real accountable actor without checking the route contract.

## 101. Temporary crisis levy keeps renewing after the trigger has expired

**Facts.** a temporary levy tied to emergency costs remains in force after the cost data and legal trigger expire, with no sunset conversion or route retirement review.[S15][S54][S59][S60]

**Expected route.** `review_trigger_conversion_and_sunset`

**Expected flags.** `sunset_evasion`; `permanent_frontier`; `compliance_theater`; `remedy_or_contest_failure`

**Must not answer.** Do not answer 'Temporary crisis levy keeps renewing after the trigger has expired' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat the first visible remitter, platform, agency label, or procedural channel as the real accountable actor without checking the route contract.

## 102. Controller map packet has no signer, supersession, or preserved event log

**Facts.** an automated controller-map packet assigns filing responsibility to a small entity, but the packet has no authorized signer, no supersession ledger, and deleted event logs, so the taxpayer cannot see who attested to the map or preserve the record for review.[S16][S17][S21][S27][S20]

**Expected route.** `controller_map_packet_identity_canonical_fields_and_supersession`; `controller_map_signer_authority_delegation_and_joint_attestation`; `controller_map_event_log_retention_and_preservation`

**Expected flags.** `classification_or_label_arbitrage`; `packet_identity_conflict_or_supersession_gap`; `delegation_gap_or_joint_attestation_shift`; `event_log_loss_or_retention_asymmetry`

**Must not answer.** Do not answer 'Controller map packet has no signer, supersession, or preserved event log' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat normalized case axes as the answer; the facts-only router must still recover the route candidates from the written scenario.

## 103. Counter-map contest is locked after one field while safe harbor shifts risk

**Facts.** a controller-map contest portal lets an unrepresented taxpayer correct only one field, treats the rest of the map as final, and claims a safe harbor even though the wrong controller keeps the benefit and the legal risk shifts to the taxpayer.[S16][S17][S20][S21]

**Expected route.** `controller_map_contest_window_counter_map_and_finality`; `controller_map_field_severability_partial_acceptance_and_issue_scoped_correction`; `controller_map_integrity_correction_safe_harbor_and_sanction`

**Expected flags.** `classification_or_label_arbitrage`; `contest_window_lock_in`; `remedy_channel_lock_in`; `issue_scope_lock_in`

**Must not answer.** Do not answer 'Counter-map contest is locked after one field while safe harbor shifts risk' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat normalized case axes as the answer; the facts-only router must still recover the route candidates from the written scenario.

## 104. Controller map uses temporary imputation across regimes without sampling review

**Facts.** a revenue agency reuses a temporary controller imputation from one regime in another; the packet marks unknown control as resolved, creates privacy chill for a small entity, and has no verification sampling or review-intensity record.[S16][S17][S20][S21][S27]

**Expected route.** `controller_map_confidence_unknowns_and_bounded_imputation`; `controller_map_reuse_portability_and_cross_regime_reliance`; `controller_map_verification_sampling_and_review_intensity`

**Expected flags.** `classification_or_label_arbitrage`; `imputed_control_shift`; `record_lock_in`; `cross_regime_record_reuse_risk`

**Must not answer.** Do not answer 'Controller map uses temporary imputation across regimes without sampling review' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat normalized case axes as the answer; the facts-only router must still recover the route candidates from the written scenario.

## 105. Public input reciprocity contribution is missing while benefit credentials are reused without a purpose wall

**Facts.** public-service workers and benefit claimants provide structured data that improves an automated eligibility system, but the public input reciprocity contribution ledger is missing and the agency reuses credential data across programs without data minimization, compensation, purpose limits, or a sensitive-attribute firewall.[S1][S10][S11][S15][S16]

**Expected route.** `public_input_reciprocity_contribution`; `data_minimization_credential_reuse_and_sensitive_attribute_firewall`

**Expected flags.** `classification_or_label_arbitrage`; `data_or_confidentiality_overreach`; `access_exclusion`; `sensitive_attribute_reuse`

**Must not answer.** Do not answer 'Public input reciprocity contribution is missing while benefit credentials are reused without a purpose wall' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat normalized case axes as the answer; the facts-only router must still recover the route candidates from the written scenario.

## 106. Multinational claim split hides beneficial owner and erases home-market burden

**Facts.** a multinational books revenue through a treaty affiliate, keeps the beneficial owner chain opaque, and asks two jurisdictions to accept a claim split that ignores where users, workers, and home-market public costs arise.[S1][S2][S3][S5][S9][S10]

**Expected route.** `international_coordination_claim_split`; `beneficial_ownership_and_controller_chain`; `beneficiary_home_market_and_local_burden_claim_split`

**Expected flags.** `compliance_theater`; `cross_border_erasure`; `opacity_or_erasure`; `classification_or_label_arbitrage`

**Must not answer.** Do not answer 'Multinational claim split hides beneficial owner and erases home-market burden' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat normalized case axes as the answer; the facts-only router must still recover the route candidates from the written scenario.

## 107. Insurance rescue pays creditors first while policyholders and taxpayers absorb losses

**Facts.** a distressed insurer receives a public liquidity backstop; creditor claims are netted and paid before policyholder obligations, there is no ex ante security waterfall, and the surplus path favors bondholders while ordinary taxpayers backstop the failure.[S15][S16][S17][S19][S18][S21]

**Expected route.** `failure_waterfall_and_ex_ante_security`; `creditor_distress_netting_and_retained_surplus`; `insurance_policyholder_benefit_and_retained_surplus`

**Expected flags.** `asset_stripping`; `liability_misassignment`; `harm_pricing_or_offset_theater`; `public_loss_private_upside`

**Must not answer.** Do not answer 'Insurance rescue pays creditors first while policyholders and taxpayers absorb losses' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat normalized case axes as the answer; the facts-only router must still recover the route candidates from the written scenario.

## 108. Care household is assessed as one unit while member hours, pension pass-through, and local repair disappear

**Facts.** a household care enterprise treats unpaid care, paid worker hours, member shares, and pension contributions as one assessment unit; the rule ignores dependency load, loses the worker benefit pass-through, and withholds local repair from caregivers.[S2][S18][S31][S32][S10][S11]

**Expected route.** `assessment_unit_and_care_load`; `worker_benefit_pay_hours_member_share_and_local_repair`; `pension_pass_through_incidence_and_proceeds`

**Expected flags.** `captive_household_unit`; `marriage_penalty`; `opacity_or_erasure`; `trapdoor_or_cliff`

**Must not answer.** Do not answer 'Care household is assessed as one unit while member hours, pension pass-through, and local repair disappear' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat normalized case axes as the answer; the facts-only router must still recover the route candidates from the written scenario.

## 109. Wrongful levy follows a nominee label and a whistleblower tip into criminal penalty theater

**Facts.** an examiner treats a transferee-nominee label and an untested whistleblower tip as proof, imposes a severe penalty, threatens criminal referral despite voluntary disclosure facts, and levies property without owner notice or accused-taxpayer protection.[S27][S39][S41][S98][S21][S34]

**Expected route.** `culpability_penalty_safe_harbor_and_criminal_referral`; `transferee_nominee_alter_ego_successor_and_wrongful_levy`; `whistleblower_tip_classification_confidentiality_award_and_accused_taxpayer_protection`

**Expected flags.** `duplicate_penalty_stack`; `liability_misassignment`; `trapdoor_or_cliff`; `penalty_farming`

**Must not answer.** Do not answer 'Wrongful levy follows a nominee label and a whistleblower tip into criminal penalty theater' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat normalized case axes as the answer; the facts-only router must still recover the route candidates from the written scenario.

## 110. Essential filing charge is relabeled as a hidden tax-like fee through a single private rail

**Facts.** a legislature uses relabeling dependence to call a tax-like filing charge a user fee, requires payment through one private vendor, hides the invoice burden, and defeats burden salience disclosure of a hidden tax while offering no channel pluralism, public channel, waiver, or explanation to bankless and disabled taxpayers.[S3][S7][S10][S15][S9][S19]

**Expected route.** `burden_salience_disclosure_and_hidden_tax`; `relabeling_dependence_and_category_integrity`; `channel_pluralism_access_independence_and_fallback`

**Expected flags.** `compliance_theater`; `opacity_or_erasure`; `seamless_taking_silent_state`; `classification_or_label_arbitrage`

**Must not answer.** Do not answer 'Essential filing charge is relabeled as a hidden tax-like fee through a single private rail' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat normalized case axes as the answer; the facts-only router must still recover the route candidates from the written scenario.

## 111. Notice assigns liability after remitter failure while collection anchor and assisted filing are paywalled

**Facts.** a taxpayer receives an opaque notice after a platform remitter under-collected; the agency makes a collection anchor choice that assigns liability to the recipient, offers only a paid preparer workflow for correction, and denies a plain explanation or appeal path.[S1][S16][S17][S21][S3][S5]

**Expected route.** `administration_explanation_and_appeal_minimum`; `collection_anchor_choice_and_remittance_chain`; `compliance_cost_assisted_filing_and_preparer_dependence`

**Expected flags.** `opacity_or_erasure`; `review_desert`; `self_help_maze`; `liability_misassignment`

**Must not answer.** Do not answer 'Notice assigns liability after remitter failure while collection anchor and assisted filing are paywalled' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat normalized case axes as the answer; the facts-only router must still recover the route candidates from the written scenario.

## 112. Third-party report locks the wrong recipient into escrow while refund timing creates a cashflow loan to government

**Facts.** a third-party information report names the wrong taxpayer; the agency requires provisional filing and escrow before correction, freezes the refund, and uses delayed relief as prefunding while the recipient has no bounded shelter.[S16][S17][S20][S21][S10][S15]

**Expected route.** `third_party_reporting_correction_and_bounded_recipient_shelter`; `provisional_controller_filing_escrow_and_true_up`; `timing_cashflow_liquidity_deferral_and_prefunding`

**Expected flags.** `label_recipient_mismatch`; `record_lock_in`; `liability_misassignment`; `freeze_by_default`

**Must not answer.** Do not answer 'Third-party report locks the wrong recipient into escrow while refund timing creates a cashflow loan to government' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat normalized case axes as the answer; the facts-only router must still recover the route candidates from the written scenario.

## 113. Refund surplus is retained for reinvestment while net fiscal stack and local proceeds are unreadable

**Facts.** an agency keeps over-collected refunds in a reinvestment reserve, claims it will improve capacity, but the budget portal does not show the net fiscal stack, local share, earmark, or whether proceeds repair the burdened community.[S10][S11][S15][S16][S29][S30]

**Expected route.** `reinvestment_prefunding_ring_fence_and_retained_surplus`; `net_fiscal_stack_disclosure_and_substitution`; `proceeds_visibility_local_share_and_earmarking`

**Expected flags.** `fiscal_hoarding`; `proceeds_laundering`; `one_way_loss_recognition`; `compliance_theater`

**Must not answer.** Do not answer 'Refund surplus is retained for reinvestment while net fiscal stack and local proceeds are unreadable' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat normalized case axes as the answer; the facts-only router must still recover the route candidates from the written scenario.

## 114. Overlapping credits pay customers and suppliers without residual netting

**Facts.** a subsidy program gives one credit to customers and another to suppliers for the same activity; neither side must disclose retained surplus, residual benefit, base overlap, or creditability, so ordinary taxpayers finance duplicated pass-through claims.[S3][S4][S5][S6][S10][S11]

**Expected route.** `base_ordering_overlap_creditability_and_non_substitution`; `beneficiary_composite_netting_and_residual_ordering`; `supplier_benefit_net_terms_and_retained_surplus`

**Expected flags.** `compliance_theater`; `double_payment`; `opacity_or_erasure`; `rent_extraction`

**Must not answer.** Do not answer 'Overlapping credits pay customers and suppliers without residual netting' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat normalized case axes as the answer; the facts-only router must still recover the route candidates from the written scenario.

## 115. Consumer relief credit is retained by the firm after stale measurement and failed regressivity repair

**Facts.** a consumer relief credit is paid to firms; customer prices do not fall, customer benefit records are stale, and the measurement cadence and proxy graduation process averages away low-income burden instead of using a regressivity repair channel and delivery sync for the actual pass-through failure.[S3][S4][S10][S11][S5][S15]

**Expected route.** `customer_benefit_price_access_and_retained_surplus`; `measurement_cadence_and_proxy_graduation`; `regressivity_repair_channel_and_delivery_sync`

**Expected flags.** `compliance_theater`; `opacity_or_erasure`; `rent_extraction`; `data_or_confidentiality_overreach`

**Must not answer.** Do not answer 'Consumer relief credit is retained by the firm after stale measurement and failed regressivity repair' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat normalized case axes as the answer; the facts-only router must still recover the route candidates from the written scenario.

## 116. Threshold cliff uses a status proxy and offers no reliance privilege, phase-in, or standing path

**Facts.** a benefit phaseout uses an outdated status proxy and a sharp threshold cliff; taxpayers relied on official guidance, but the rule has no reliance privilege, phase-in, grandfathering, representative standing, or accessible channel to correct disparate impact.[S16][S17][S23][S25][S19][S20]

**Expected route.** `threshold_cliff_smoothing_and_graduation`; `status_proxy_disparate_impact_and_accessibility_repair`; `reliance_privilege_phase_in_and_grandfathering`

**Expected flags.** `trapdoor_or_cliff`; `data_or_confidentiality_overreach`; `institutional_bias`; `opacity_or_erasure`

**Must not answer.** Do not answer 'Threshold cliff uses a status proxy and offers no reliance privilege, phase-in, or standing path' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat normalized case axes as the answer; the facts-only router must still recover the route candidates from the written scenario.

## 117. Same-facts reuse blocks a non-conflicted representative from correcting a prior issue

**Facts.** a taxpayer tries to reuse facts accepted in a prior proceeding, but the new program treats the prior record as binding only against the taxpayer, rejects a non-conflicted representative, and refuses issue-scoped delta correction.[S16][S17][S20][S21][S19][S42]

**Expected route.** `same_facts_reuse_portability_and_delta_update`; `standing_bundle_and_non_conflicted_representation`; `bounded_contest_issue_scoped_correction_and_period_finality`

**Expected flags.** `data_or_confidentiality_overreach`; `duplicate_penalty_stack`; `record_lock_in`; `conflict_shield`

**Must not answer.** Do not answer 'Same-facts reuse blocks a non-conflicted representative from correcting a prior issue' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat normalized case axes as the answer; the facts-only router must still recover the route candidates from the written scenario.

## 118. Promoter list audit uses weak verification sampling and ignores official-error prefill reliance

**Facts.** a reportable transaction promoter list is generated by low-intensity sampling; advisees are treated as culpable before correction, and the audit cannot show verification intensity, error tolerance, official-error prefill guidance reliance, or a safe harbor path.[S350][S383][S384][S385][S16][S17]

**Expected route.** `reportable_transaction_material_advisor_promoter_and_advisee_list`; `verification_sampling_and_review_intensity`; `official_error_prefill_and_guidance_reliance`

**Expected flags.** `informer_extortion`; `opacity_or_erasure`; `compliance_theater`; `institutional_bias`

**Must not answer.** Do not answer 'Promoter list audit uses weak verification sampling and ignores official-error prefill reliance' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat normalized case axes as the answer; the facts-only router must still recover the route candidates from the written scenario.

## 119. Losses are denied while liability is collected immediately despite hardship and pending appeal

**Facts.** a small business can recognize taxable gains immediately but losses only later; the agency refuses a stay, escrow, or hardship relief during appeal, creating a one-way loss rule that deepens low-income cashflow harm.[S15][S16][S17][S21][S20]

**Expected route.** `loss_recognition_symmetry`; `interim_liability_stays_escrow_and_hardship_relief`

**Expected flags.** `double_payment`; `liability_misassignment`; `one_way_loss_recognition`; `access_exclusion`

**Must not answer.** Do not answer 'Losses are denied while liability is collected immediately despite hardship and pending appeal' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat normalized case axes as the answer; the facts-only router must still recover the route candidates from the written scenario.

## 120. Scarce frontier capacity is allocated as a permanent entitlement without precaution gating

**Facts.** a regulator allocates scarce compute and energy capacity to frontier firms as if it were a permanent entitlement; catastrophic-risk evidence is uncertain, there is no threshold gate, and public capacity costs are shifted to ordinary ratepayers.[S1][S10][S15][S16][S4]

**Expected route.** `frontier_scarce_capacity_threshold`; `precaution_threshold_gating`

**Expected flags.** `compliance_theater`; `permanent_frontier`; `rent_extraction`; `harm_pricing_or_offset_theater`

**Must not answer.** Do not answer 'Scarce frontier capacity is allocated as a permanent entitlement without precaution gating' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat normalized case axes as the answer; the facts-only router must still recover the route candidates from the written scenario.

## 121. Foundation retains charitable surplus while service members lose local repair

**Facts.** a charitable foundation and a public service program both claim public benefit, but endowment surplus is locked up, donor control substitutes for local service repair, and members who carried the burden receive no relief.[S18][S21][S22][S29][S10][S11]

**Expected route.** `charitable_public_benefit_transfer_and_retained_surplus`; `public_service_member_relief_and_local_repair`

**Expected flags.** `compliance_theater`; `opacity_or_erasure`; `public_loss_private_upside`; `rent_extraction`

**Must not answer.** Do not answer 'Foundation retains charitable surplus while service members lose local repair' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat normalized case axes as the answer; the facts-only router must still recover the route candidates from the written scenario.

## 122. Annual wealth backstop ignores grouping games, site-rent surplus, and stale real-value thresholds

**Facts.** a wealth backstop uses stale thresholds, lets related entities group assets to avoid visibility, taxes improvements more than site rent, and lacks a hardship or indexation reset channel for low-liquidity property owners.[S5][S8][S10][S18][S15][S21]

**Expected route.** `annual_wealth_backstop_visibility_grouping_and_liquidity`; `land_site_rent_netting_and_retained_surplus`; `real_value_indexation_and_reset_cadence`

**Expected flags.** `opacity_or_erasure`; `grouping_game`; `trapdoor_or_cliff`; `improvement_penalty`

**Must not answer.** Do not answer 'Annual wealth backstop ignores grouping games, site-rent surplus, and stale real-value thresholds' from the easiest label; route by control, incidence, burden, remedy, and review evidence. Do not treat normalized case axes as the answer; the facts-only router must still recover the route candidates from the written scenario.

## Source definitions

[S1]: ../../SOURCES.md#S1
[S2]: ../../SOURCES.md#S2
[S3]: ../../SOURCES.md#S3
[S4]: ../../SOURCES.md#S4
[S5]: ../../SOURCES.md#S5
[S6]: ../../SOURCES.md#S6
[S7]: ../../SOURCES.md#S7
[S8]: ../../SOURCES.md#S8
[S9]: ../../SOURCES.md#S9
[S10]: ../../SOURCES.md#S10
[S11]: ../../SOURCES.md#S11
[S15]: ../../SOURCES.md#S15
[S16]: ../../SOURCES.md#S16
[S17]: ../../SOURCES.md#S17
[S18]: ../../SOURCES.md#S18
[S19]: ../../SOURCES.md#S19
[S20]: ../../SOURCES.md#S20
[S21]: ../../SOURCES.md#S21
[S22]: ../../SOURCES.md#S22
[S23]: ../../SOURCES.md#S23
[S25]: ../../SOURCES.md#S25
[S27]: ../../SOURCES.md#S27
[S29]: ../../SOURCES.md#S29
[S30]: ../../SOURCES.md#S30
[S31]: ../../SOURCES.md#S31
[S32]: ../../SOURCES.md#S32
[S34]: ../../SOURCES.md#S34
[S39]: ../../SOURCES.md#S39
[S41]: ../../SOURCES.md#S41
[S42]: ../../SOURCES.md#S42
[S43]: ../../SOURCES.md#S43
[S44]: ../../SOURCES.md#S44
[S54]: ../../SOURCES.md#S54
[S59]: ../../SOURCES.md#S59
[S60]: ../../SOURCES.md#S60
[S73]: ../../SOURCES.md#S73
[S81]: ../../SOURCES.md#S81
[S89]: ../../SOURCES.md#S89
[S98]: ../../SOURCES.md#S98
[S103]: ../../SOURCES.md#S103
[S117]: ../../SOURCES.md#S117
[S118]: ../../SOURCES.md#S118
[S119]: ../../SOURCES.md#S119
[S141]: ../../SOURCES.md#S141
[S196]: ../../SOURCES.md#S196
[S197]: ../../SOURCES.md#S197
[S198]: ../../SOURCES.md#S198
[S201]: ../../SOURCES.md#S201
[S214]: ../../SOURCES.md#S214
[S277]: ../../SOURCES.md#S277
[S322]: ../../SOURCES.md#S322
[S324]: ../../SOURCES.md#S324
[S339]: ../../SOURCES.md#S339
[S350]: ../../SOURCES.md#S350
[S351]: ../../SOURCES.md#S351
[S352]: ../../SOURCES.md#S352
[S353]: ../../SOURCES.md#S353
[S354]: ../../SOURCES.md#S354
[S378]: ../../SOURCES.md#S378
[S383]: ../../SOURCES.md#S383
[S384]: ../../SOURCES.md#S384
[S385]: ../../SOURCES.md#S385
[S407]: ../../SOURCES.md#S407
[S410]: ../../SOURCES.md#S410
[S429]: ../../SOURCES.md#S429
[S432]: ../../SOURCES.md#S432
[S434]: ../../SOURCES.md#S434
[S435]: ../../SOURCES.md#S435
[S436]: ../../SOURCES.md#S436
[S440]: ../../SOURCES.md#S440
[S441]: ../../SOURCES.md#S441
[S442]: ../../SOURCES.md#S442
[S443]: ../../SOURCES.md#S443
[S444]: ../../SOURCES.md#S444
[S445]: ../../SOURCES.md#S445
[S446]: ../../SOURCES.md#S446
[S447]: ../../SOURCES.md#S447
[S449]: ../../SOURCES.md#S449
[S450]: ../../SOURCES.md#S450
[S451]: ../../SOURCES.md#S451
[S452]: ../../SOURCES.md#S452
[S453]: ../../SOURCES.md#S453
[S454]: ../../SOURCES.md#S454
[S455]: ../../SOURCES.md#S455
[S456]: ../../SOURCES.md#S456
[S457]: ../../SOURCES.md#S457
[S458]: ../../SOURCES.md#S458
[S459]: ../../SOURCES.md#S459
[S460]: ../../SOURCES.md#S460
[S461]: ../../SOURCES.md#S461
[S462]: ../../SOURCES.md#S462
[S463]: ../../SOURCES.md#S463
[S464]: ../../SOURCES.md#S464
[S467]: ../../SOURCES.md#S467
[S468]: ../../SOURCES.md#S468
[S469]: ../../SOURCES.md#S469
[S470]: ../../SOURCES.md#S470
[S471]: ../../SOURCES.md#S471
[S473]: ../../SOURCES.md#S473
[S475]: ../../SOURCES.md#S475
[S477]: ../../SOURCES.md#S477
[S478]: ../../SOURCES.md#S478
[S480]: ../../SOURCES.md#S480
[S481]: ../../SOURCES.md#S481
[S482]: ../../SOURCES.md#S482
[S483]: ../../SOURCES.md#S483
[S484]: ../../SOURCES.md#S484
[S485]: ../../SOURCES.md#S485
[S487]: ../../SOURCES.md#S487
[S488]: ../../SOURCES.md#S488
[S489]: ../../SOURCES.md#S489
[S491]: ../../SOURCES.md#S491
[S492]: ../../SOURCES.md#S492
[S493]: ../../SOURCES.md#S493
[S496]: ../../SOURCES.md#S496
[S497]: ../../SOURCES.md#S497
[S498]: ../../SOURCES.md#S498
[S499]: ../../SOURCES.md#S499
[S500]: ../../SOURCES.md#S500
[S501]: ../../SOURCES.md#S501
[S502]: ../../SOURCES.md#S502
[S503]: ../../SOURCES.md#S503
[S504]: ../../SOURCES.md#S504
[S505]: ../../SOURCES.md#S505
[S506]: ../../SOURCES.md#S506
[S507]: ../../SOURCES.md#S507
[S508]: ../../SOURCES.md#S508
[S510]: ../../SOURCES.md#S510
[S511]: ../../SOURCES.md#S511
[S512]: ../../SOURCES.md#S512
[S513]: ../../SOURCES.md#S513
[S514]: ../../SOURCES.md#S514
[S515]: ../../SOURCES.md#S515
[S516]: ../../SOURCES.md#S516
[S517]: ../../SOURCES.md#S517
[S518]: ../../SOURCES.md#S518
[S519]: ../../SOURCES.md#S519
[S520]: ../../SOURCES.md#S520
[S521]: ../../SOURCES.md#S521
[S522]: ../../SOURCES.md#S522
[S523]: ../../SOURCES.md#S523
[S524]: ../../SOURCES.md#S524
[S525]: ../../SOURCES.md#S525
[S526]: ../../SOURCES.md#S526
[S527]: ../../SOURCES.md#S527
[S528]: ../../SOURCES.md#S528
[S529]: ../../SOURCES.md#S529
[S530]: ../../SOURCES.md#S530
[S531]: ../../SOURCES.md#S531
[S532]: ../../SOURCES.md#S532
[S533]: ../../SOURCES.md#S533
[S534]: ../../SOURCES.md#S534
[S535]: ../../SOURCES.md#S535
[S536]: ../../SOURCES.md#S536
[S537]: ../../SOURCES.md#S537
[S541]: ../../SOURCES.md#S541
[S543]: ../../SOURCES.md#S543
[S545]: ../../SOURCES.md#S545
[S546]: ../../SOURCES.md#S546
[S548]: ../../SOURCES.md#S548
[S549]: ../../SOURCES.md#S549
[S550]: ../../SOURCES.md#S550
[S551]: ../../SOURCES.md#S551
[S554]: ../../SOURCES.md#S554
[S555]: ../../SOURCES.md#S555
[S556]: ../../SOURCES.md#S556
[S557]: ../../SOURCES.md#S557
[S558]: ../../SOURCES.md#S558
[S561]: ../../SOURCES.md#S561
[S562]: ../../SOURCES.md#S562
[S563]: ../../SOURCES.md#S563
[S564]: ../../SOURCES.md#S564
[S565]: ../../SOURCES.md#S565
[S566]: ../../SOURCES.md#S566
[S567]: ../../SOURCES.md#S567
[S568]: ../../SOURCES.md#S568
[S569]: ../../SOURCES.md#S569
[S570]: ../../SOURCES.md#S570
[S571]: ../../SOURCES.md#S571
[S572]: ../../SOURCES.md#S572
[S573]: ../../SOURCES.md#S573
[S574]: ../../SOURCES.md#S574
[S575]: ../../SOURCES.md#S575
[S576]: ../../SOURCES.md#S576
[S577]: ../../SOURCES.md#S577
[S578]: ../../SOURCES.md#S578
[S579]: ../../SOURCES.md#S579
[S580]: ../../SOURCES.md#S580
[S581]: ../../SOURCES.md#S581
[S582]: ../../SOURCES.md#S582
[S583]: ../../SOURCES.md#S583
[S584]: ../../SOURCES.md#S584
[S585]: ../../SOURCES.md#S585
[S586]: ../../SOURCES.md#S586
[S587]: ../../SOURCES.md#S587
[S588]: ../../SOURCES.md#S588
[S589]: ../../SOURCES.md#S589
[S590]: ../../SOURCES.md#S590
[S591]: ../../SOURCES.md#S591
[S592]: ../../SOURCES.md#S592
[S593]: ../../SOURCES.md#S593
[S594]: ../../SOURCES.md#S594
[S595]: ../../SOURCES.md#S595
[S596]: ../../SOURCES.md#S596
[S597]: ../../SOURCES.md#S597
[S599]: ../../SOURCES.md#S599
[S600]: ../../SOURCES.md#S600
[S601]: ../../SOURCES.md#S601
[S602]: ../../SOURCES.md#S602
[S603]: ../../SOURCES.md#S603
[S604]: ../../SOURCES.md#S604
[S605]: ../../SOURCES.md#S605
[S606]: ../../SOURCES.md#S606
[S607]: ../../SOURCES.md#S607
[S608]: ../../SOURCES.md#S608
[S609]: ../../SOURCES.md#S609
[S610]: ../../SOURCES.md#S610
[S611]: ../../SOURCES.md#S611
[S612]: ../../SOURCES.md#S612
[S613]: ../../SOURCES.md#S613
[S614]: ../../SOURCES.md#S614
[S615]: ../../SOURCES.md#S615
[S616]: ../../SOURCES.md#S616
[S617]: ../../SOURCES.md#S617
[S618]: ../../SOURCES.md#S618
[S619]: ../../SOURCES.md#S619
[S620]: ../../SOURCES.md#S620
[S621]: ../../SOURCES.md#S621
[S622]: ../../SOURCES.md#S622
[S623]: ../../SOURCES.md#S623
[S624]: ../../SOURCES.md#S624
[S625]: ../../SOURCES.md#S625
[S626]: ../../SOURCES.md#S626
[S627]: ../../SOURCES.md#S627
[S628]: ../../SOURCES.md#S628
[S629]: ../../SOURCES.md#S629
[S630]: ../../SOURCES.md#S630
[S631]: ../../SOURCES.md#S631
[S632]: ../../SOURCES.md#S632
[S633]: ../../SOURCES.md#S633
[S634]: ../../SOURCES.md#S634
[S635]: ../../SOURCES.md#S635
[S636]: ../../SOURCES.md#S636
[S637]: ../../SOURCES.md#S637
[S638]: ../../SOURCES.md#S638
[S639]: ../../SOURCES.md#S639
[S640]: ../../SOURCES.md#S640
[S641]: ../../SOURCES.md#S641
[S642]: ../../SOURCES.md#S642
[S643]: ../../SOURCES.md#S643
[S644]: ../../SOURCES.md#S644
[S645]: ../../SOURCES.md#S645
[S646]: ../../SOURCES.md#S646
[S647]: ../../SOURCES.md#S647
[S648]: ../../SOURCES.md#S648
[S649]: ../../SOURCES.md#S649
[S650]: ../../SOURCES.md#S650
[S651]: ../../SOURCES.md#S651
[S653]: ../../SOURCES.md#S653
[S654]: ../../SOURCES.md#S654
[S655]: ../../SOURCES.md#S655
[S656]: ../../SOURCES.md#S656
[S657]: ../../SOURCES.md#S657
[S658]: ../../SOURCES.md#S658
[S662]: ../../SOURCES.md#S662
[S663]: ../../SOURCES.md#S663
[S664]: ../../SOURCES.md#S664
[S667]: ../../SOURCES.md#S667
