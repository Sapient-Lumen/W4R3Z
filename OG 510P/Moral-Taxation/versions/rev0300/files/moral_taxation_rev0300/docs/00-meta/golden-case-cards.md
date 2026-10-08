# Golden case cards

These cards are generated from `docs/00-meta/golden-cases.json` in Rev0289 so prose examples and machine contracts stay aligned. Edit the JSON first, then regenerate this surface.

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

**Expected flags.** `black_box_enforcement`; `new_regulatory_role`; `model_score_used`; `no_specific_floor_risk`

**Legacy flags preserved for review.** `regulatory_role_as_tax_subject`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'AI model provider is a GPAI provider but not the deployment controller' without checking the expected route and protected-side floor.

## 8. Tax authority uses a model score to select a taxpayer

**Facts.** a tax administration uses AI to prioritize an audit, but the taxpayer receives only a generic notice.[S44][S449]

**Expected route.** `model_assisted_tax_administration_minimum`

**Expected flags.** `black_box_enforcement`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Tax authority uses a model score to select a taxpayer' without checking the expected route and protected-side floor.

## 9. OECD club rule conflicts with developing-state taxing-right claim

**Facts.** a cross-border digital-services rule gives administrability to large residence states but weakens market or source claims of lower-capacity states.[S440][S451]

**Expected route.** `un_inclusive_international_tax`

**Expected flags.** `club_rule_as_global_legitimacy`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'OECD club rule conflicts with developing-state taxing-right claim' without checking the expected route and protected-side floor.

## 10. Low-capacity state wants a blunt tax on small vendors

**Facts.** the state needs revenue, lacks audit capacity, and proposes a flat presumptive levy that falls heavily on subsistence traders.[S450][S451][S452]

**Expected route.** `tax_morale_state_capacity`

**Expected flags.** `state_capacity_overreach`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Low-capacity state wants a blunt tax on small vendors' without checking the expected route and protected-side floor.

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

**Expected flags.** `reentry_rent`; `supervision_debt_trap`; `private_probation_toll`; `mandatory_service_markup`

**Legacy flags preserved for review.** `ai_error`; `private_gatekeeper`

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

**Expected flags.** `producer_rent`; `nutrition_floor_harm`; `input_subsidy_lock_in`; `small_farmer_theater`

**Legacy flags preserved for review.** `ai_error`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Farm support stabilizes producers but raises healthy-food prices' without checking the expected route and protected-side floor.

## 51. Drought pricing protects a basin but threatens household access

**Facts.** A drought-pricing schedule preserves basin supply and curbs waste, but the lifeline tier is too small and low-income households face disconnection risk while senior irrigation rights remain underpriced.[S584][S585]

**Expected route.** `water_rights_scarcity_pricing_irrigation_subsidy`

**Expected flags.** `water_hoarding`; `scarcity_rent`; `lifeline_exclusion`; `paper_conservation`

**Must not answer.** Do not answer 'Drought pricing protects a basin but threatens household access' without checking the expected route and protected-side floor.

## 52. Congestion charge reduces traffic but traps shift workers without transit

**Facts.** [S586][S587]

**Expected route.** `transport_congestion_road_pricing_mobility_access`

**Expected flags.** `mobility_ransom`; `transit_substitution`; `exemption_formalism`; `surveillance_tolling`

**Legacy flags preserved for review.** `ai_error`

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

**Expected flags.** `parity_gap`; `consultation_theater`; `sovereignty_bypass`; `paternalistic_welfare_reclassification`

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

**Expected flags.** `private_toll_constitution`; `portability_theater`; `compliance_console_lock_in`; `self_preference_rent`

**Legacy flags preserved for review.** `refund_delay`; `ai_error`; `private_gatekeeper`

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

**Expected flags.** `certified_rent`; `conformity_theater`; `auditor_capture`; `standard_paywall`

**Legacy flags preserved for review.** `private_gatekeeper`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Public procurement requires one private certification badge' without checking the expected route and protected-side floor.

## 68. Retirement tax preference mostly benefits high-balance savers while caregivers lose accrual

**Facts.** a proposed deferral expansion increases tax-preferred account limits, but low-wage workers cannot save and unpaid caregivers lose pension accrual.[S623][S624]

**Expected route.** `retirement_tax_preference_pension_adequacy_leakage`

**Expected flags.** `retirement_halo_shelter`; `fee_leakage`; `care_gap_denial`; `liquidity_trap`

**Legacy flags preserved for review.** `refund_delay`; `ai_error`

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

**Expected flags.** `sacrifice_zone_offset`; `average_burden_theater`; `abatement_for_pollution`; `tool_removal_blindness`

**Legacy flags preserved for review.** `cumulative_burden`

**Must not answer.** Do not treat the classification label as settling moral incidence. Do not answer 'Facility abatement offered in an already overburdened neighborhood' without checking the expected route and protected-side floor.

## 77. Release adds sources but markdown and JSON drift again

**Facts.** a revision cites new source IDs in markdown, but SOURCES.json omits one, SOURCES.md repeats another, and README still advertises an older revision as current.[S594][S645][S646]

**Expected route.** `release_integrity_source_bijection_regression_harness`

**Expected flags.** `citation_theater`; `source_surface_drift`; `stale_release_opening`; `prose_sprawl`

**Legacy flags preserved for review.** `ai_error`; `source_drift`

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

**Facts.** source_role: ordinary_citation_promoted_to_currentness_ref; example_source: AI-energy projection reused in unrelated routes; failure: false_freshness_and_refresh_noise[S594]

**Expected route.** `source_hierarchy_conflict_refresh_current_law`

**Expected flags.** `currentness_taint`; `citation_laundering`; `dangling_refresh_dependency`

**Must not answer.** treat every cited source as a currentness ref delete useful ordinary citations merely because they are not volatile dependencies

## 81. Refund remedy exists on paper but runs through the same failed private rail

**Facts.** a revenue agency promises refund reissue after a payment failure, but the taxpayer must use the same vendor-mediated bank workflow that rejected the payment, while the refund delay threatens rent and utilities.[S117][S118][S141][S196]

**Expected route.** `remedy_traceability_incidence_escalation_proceeds_integrity`; `mandatory_private_tax_rail_and_bankless_fallback`; `overcollection_return_setoff_and_refund_symmetry`

**Expected flags.** `relief_same_failed_rail`; `remedy_theater`; `refund_rail_capture`; `escalation_blindness`

**Must not answer.** Do not treat refund_reissue as adequate if the only correction channel is the failed rail. Do not route relief to the legal remitter or vendor while the real burden bearer waits.

## 82. Golden case keeps the right route but loses its answer contract

**Facts.** A future release preserves the prose golden case and the expected route ID, but drops the route-backed expected flags, leaves a raw axis value outside the cube vocabulary, and no longer requires the expected route to have a remedy profile.[S21][S27][S59][S594]

**Expected route.** `case_contract_route_coverage_answer_regression`

**Expected flags.** `orphan_golden_case`; `decorative_expected_flag`; `axisless_moral_fact`; `missing_remedy_profile`

**Must not answer.** Do not treat a prose golden case as tested merely because the route ID still exists. Do not allow expected flags, raw axes, or remedy-profile obligations to drift outside the contract layer.

## 83. Agency charge is called a user fee but funds broad public regulation

**Facts.** an agency requires a mandatory filing access charge from all applicants and says it is a user fee, but the proceeds fund general enforcement and public-protection work while low-income applicants cannot obtain waiver or public fallback.[S573][S662][S663][S664]

**Expected route.** `instrument_choice_tax_fee_mandate_ban_public_option_compensation`; `user_fee_service_charge_utility_public_access_toll`

**Expected flags.** `fee_tax_laundering`; `fee_benefit_nexus_missing`; `public_service_access`; `public_option_erasure`

**Must not answer.** Do not accept the fee label without a special-benefit or cost/value nexus. Do not let a charge for access to a public right fund broad public regulation without waiver, fallback, or legislative tax treatment.

## 84. Payroll platform is blamed for unpaid trust taxes while owner diverted funds and workers need wage-credit repair

**Facts.** a small employer uses a payroll platform and withholds employee taxes, but the owner diverts operating funds to favored creditors; the agency proposes liability against the platform by title/proximity while workers face missing wage credits and the employer claims the platform was the only accountable actor.[S322][S324][S667]

**Expected route.** `actor_accountability_responsibility_chain`; `platform_worker_portable_benefits_classification_fringe`; `taxpayer_side_ai_preparer_agent_reliance_and_liability`

**Expected flags.** `actor_smearing`; `conduit_punishment`; `responsibility_chain_gap`; `withholding_agent`

**Must not answer.** Do not treat a payroll platform or processor as primary solely because it touched the channel. Do not let the owner or beneficial recipient disappear when withheld funds were diverted. Do not repair the legal remitter while leaving workers with incorrect wage or social-insurance records.

## Source IDs only

[S8][S10][S15][S17][S21][S23][S27][S44][S59][S73][S81][S103][S117][S118][S119][S141][S196][S197][S198][S201][S214][S277][S378][S407][S410][S429][S432][S434][S435][S436][S440][S441][S442][S443][S444][S445][S446][S447][S449][S450][S451][S452][S453][S454][S455][S456][S457][S458][S459][S460][S461][S462][S463][S464][S467][S468][S469][S470][S471][S473][S475][S477][S478][S480][S481][S482][S483][S484][S485][S487][S488][S489][S491][S492][S493][S496][S497][S498][S499][S500][S501][S502][S503][S504][S505][S506][S507][S508][S510][S511][S512][S513][S514][S515][S516][S517][S518][S519][S520][S521][S522][S523][S524][S525][S526][S527][S528][S529][S530][S531][S532][S533][S534][S535][S536][S537][S541][S543][S545][S546][S548][S549][S550][S551][S554][S555][S556][S557][S558][S561][S562][S563][S564][S565][S566][S567][S568][S569][S570][S571][S572][S573][S574][S575][S576][S577][S578][S579][S580][S581][S582][S583][S584][S585][S586][S587][S588][S589][S590][S591][S592][S593][S594][S595][S596][S597][S599][S600][S601][S602][S603][S604][S605][S606][S607][S608][S609][S610][S611][S612][S613][S614][S615][S616][S617][S618][S619][S620][S621][S622][S623][S624][S625][S626][S627][S628][S629][S630][S631][S632][S633][S634][S635][S636][S637][S638][S639][S640][S641][S642][S643][S644][S645][S646][S647][S648][S649][S650][S651][S653][S654][S655][S656][S657][S658][S662][S663][S664][S322][S324][S667]

[S8]: ../../SOURCES.md#S8
[S10]: ../../SOURCES.md#S10
[S15]: ../../SOURCES.md#S15
[S17]: ../../SOURCES.md#S17
[S21]: ../../SOURCES.md#S21
[S23]: ../../SOURCES.md#S23
[S27]: ../../SOURCES.md#S27
[S44]: ../../SOURCES.md#S44
[S59]: ../../SOURCES.md#S59
[S73]: ../../SOURCES.md#S73
[S81]: ../../SOURCES.md#S81
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
[S378]: ../../SOURCES.md#S378
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
[S322]: ../../SOURCES.md#S322
[S324]: ../../SOURCES.md#S324
[S667]: ../../SOURCES.md#S667
