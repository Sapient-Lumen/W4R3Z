---
status: active_case
claim_kind: case_memo
route_role: public_balance_sheet_core
canonical_anchor: false
route_refs:
- public_balance_sheet_core
- case_calibration_core
supersedes: null
depends_on:
- ../docs/20-program/public-balance-sheet-gate-and-sovereign-backstop-scorecard.md
source_refresh_due: 2026-08-19
case_pressure: rev0318_public_balance_sheet
---

# Social Security and Medicare claim-security case — rev0379

## Verdict

**Correction required.** Trustees project OASI reserve depletion in 2033, hypothetical combined OASDI depletion in 2034, and HI depletion in 2033; the public floor cannot ignore these legal/actuarial cliffs.[S351][S352][S356]

## Dominant breach

The breach is promised-claim vulnerability: retirement and health security are treated as public wealth substitutes, but trust-fund depletion and formula-repair uncertainty can create claim-haircut risk.

## Gate 20 finding

Gate 20 is **blocked for comfort certification** unless the case proves that public downside, debt service, and backstop obligations are transparent, financed, incidence-scored, and paired with ordinary-claimant protection or public upside recovery.

## Opening package

Repair solvency progressively, protect low earners, caregivers, disabled claimants, survivors, and interrupted workers, publish claim-haircut scenarios, and score whether any age/formula/COLA changes shift risk onto lower-wealth cohorts.

## Evidence debt

Benefit adequacy by lifetime earnings, gender, caregiver history, disability, race/ethnicity, migrant status, and marital status; political durability of revenue options; legal treatment of trust-fund depletion.

## Source anchors

[S351][S352][S356]

## rev0319 Gate 20 operationalization addendum

rev0319 converts this from a short Gate 20 launch memo into a structured public-balance-sheet stress row. The scoreboard now includes a `public_balance_sheet_register`, `gate_20_subgates`, a `seniority_waterfall`, and a full 20-gate inventory.

### Active Gate 20 subgates

- **20B_claim_security — blocked:** Trust-fund depletion makes public claim security a live haircut and repair-allocation issue.
- **20H_generational_intergovernmental_incidence — watch:** Repair choices can shift burden among workers, retirees, disabled claimants, survivors, and future cohorts.

### Seniority waterfall under stress

1. **Current statutory beneficiaries** — Strong near-term claim. Benefits are paid while reserves and current income permit full payment.
2. **Near-retirees and disabled/survivor claimants** — High reliance but exposed to repair design. They have less time to substitute private wealth if claim terms change.
3. **Younger workers** — Repair funders and future claimants. Can bear taxes, retirement-age shifts, or future benefit redesign.
4. **Lower-wealth households** — Residual exposure. Private retirement wealth is least able to absorb a public-claim haircut.

### Case-specific evidence debt

- scheduled-benefit haircut incidence by cohort/income/disability/survivor status
- repair package distribution across payroll tax, benefits, general revenue, and provider payment
- legal/political durability of automatic post-depletion cuts
- interaction with private retirement wealth gaps
- Medicare HI provider-beneficiary incidence

### Operator implication

The case cannot use aggregate public capacity as a benign counterweight unless the stress waterfall shows ordinary claimants are protected before asset holders, creditors, or intermediaries, or unless public downside is paired with enforceable upside recovery and transparent loss sharing.

## rev0328 substantive hardening addendum

rev0328 promotes the paired scoreboard from `seed` to `active` because the evidence now supports operational scoring rather than placeholder doctrine.

### Active finding

Social Security and Medicare are not generic long-run fiscal pressures. They are claim-security promises whose stress must be translated into a waterfall: who gets scheduled benefits or care, who gets premium/tax/provider-payment changes, who is residual claimant, and which repair package protects low-income, disabled, survivor, and high-care-need households first.

### Current source anchors

[S449] [S450]

### Operator instruction

Do not certify this case with aggregate solvency, subsidy, or balance-sheet language. The operator must show claimant seniority, ordinary-claimant protection, distributional incidence, loss sharing, public-upside recovery, and source refresh status.


## Rev0344 source-use burn-down note

Rev0344 binds formerly unused direct/context sources into this active case so the source ledger no longer carries high-value evidence outside the case/evidence/currentness lineage: [S41]. These bindings do not relax the verdict; they clarify which measurement, authority, or context burden the source supports.


## rev0370 Medicare Advantage payment-integrity and denial addendum

Rev0370 adds Medicare Advantage as a live claim-security surface rather than treating Medicare stress only as trustees-report solvency. Payment-integrity evidence now includes risk adjustment, coding intensity, favorable selection, chart-review diagnosis policy, plan bids/rebates, audits, and public recovery. Care-access evidence now includes prior-authorization requests, denials, appeals, overturns, post-acute care settings, contractors, and beneficiary delay or harm. [S578] [S579] [S580] [S581] [S582] [S583]

This addendum is **noncertifying**. OIG and KFF/CMS data prove a material perimeter, not a final verdict that every denial was improper or every payment dollar is overpayment. Certification still requires plan-service-contract-level records, audit recoveries, quality and outcome data, network adequacy, bid/rebate/margin analysis, appeal latency, and explicit public-upside or beneficiary-remedy terms.

## rev0372 addendum — MA contract-level claim-security sprint

Rev0372 converts the Medicare Advantage branch from a policy-warning perimeter into an acquisition spine. CMS Part C reporting requirements and the CY2026 technical specifications identify the organization-determination and reconsideration data family that must be acquired, including completed decisions and adverse/partially adverse outcomes [S584][S585]. CMS's Part C/D data-validation route shows that contract-level Limited Data Set files can be released after validation and CMS review, but access, timing, and data-use limits remain certification blockers rather than proof [S586]. Monthly CMS contract/enrollment data supply denominator and organization keys for joining denial, appeal, quality, service-area, and parent-organization records [S587].

Payment integrity now has a concrete public-recovery route. CMS's RADV program is the recovery pathway for unsupported risk-adjustment diagnoses, while the RADV documents/data page exposes audited-contract lists, audit methods, results, and overpayment spreadsheets by payment year [S588][S589]. Utilization-management criteria are also no longer purely hidden: beginning with the 2026 coverage year, CMS requires MA organizations to submit internal coverage criteria used by organizations and delegated entities for Part C prior authorization, although criteria submission is not the same as service-level denial, delay, harm, or remedy evidence [S590].

Certification remains blocked. The case still lacks public plan-service-level denial/outcome records, delay and harm measures, contract-level recovery amounts tied to coding/risk-score/payment drift, parent/delegated-entity accountability, and beneficiary remedy terms. Rev0372 therefore advances the riskiest MA work without certifying the Social Security/Medicare claim-security case current.



## rev0373 addendum — MA row-contract remedy, appeal, and quality workbench

Rev0373 closes the most dangerous gap left by rev0372: source routes existed, but the archive still lacked an enforceable row contract for what must be present before a Medicare Advantage claim-security case can pass. The new workbench requires a joined contract-year/service-category row: contract and enrollment denominator, organization-determination and reconsideration outcomes, service category, UM criterion and delegated entity, IRE or appeal remedy route, denial notice, delay/harm/remedy measures, quality/performance context, and RADV/payment-integrity recovery context.

CMS's Parts C/D RR LDS page identifies raw reporting datasets by reporting section and contract as an acquisition route, subject to validation/review, disclosure limits, timing, data-use agreement, and fee constraints [S591]. CMS's managed-care appeals and grievance page and Part C/D decision-search route anchor the remedy/IRE side of the row but cannot represent unappealed denials or supply complete denominators by themselves [S592][S593]. CMS Part C/D performance data supplies Star Ratings/display-measure context that must be joined rather than used as a reputational offset [S594]. CMS-0057-F creates future prior-authorization metric/API infrastructure, but future reporting architecture is not current outcome evidence [S595]. The MA Denial Notice route anchors notice and appeal-rights operability, but the existence of a form is not proof of comprehension, timely relief, or adequate remedy [S596].

Certification remains blocked. No aggregate-only, route-only, star-rating-only, or appeal-overturn-only proof can certify this case. The minimum viable pilot is one contract-year/service-category join with denominator, denial, appeal, overturn, criteria/delegation, delay/harm, RADV/payment, quality, notice, and remedy fields populated from source rows.


## rev0374 addendum — MA appeal-burden public pilot

Rev0374 moves from route design to a public evidence pilot. KFF's 2024 analysis of CMS-submitted MA prior-authorization data reports 52.8 million determinations, 4.1 million full or partial denials, a 7.7% denial rate, only 11.5% of denials appealed, and 80.7% of appealed denials overturned [S582]. HHS-OIG's June 2024 SNF review reports a 12% denial rate across 19 MAOs, a 0.4% to 23% denial-rate range, 18% of denials appealed, and 95% of appealed denials overturned [S579]. HHS-OIG's LTCH/IRF review reports higher denial rates among the three largest MAOs than most peers, 36% LTCH and 43% IRF appealed-denial overturn rates, an IRF overturn-rate range from 14% to 86%, and contractor-denial concerns [S578].

The substantive correction is that appeal outcomes are now treated as an appeal-burden alarm, not as a self-correction proof. High overturn rates combined with low appeal rates force the case to account for unappealed denials, time-to-care, beneficiary harm, service ultimately furnished, and restoration of out-of-pocket or provider-payment loss. CMS Part C reporting specifications and the LDS route establish the reporting architecture [S584][S585][S591], while CMS-0057-F and the denial-notice route establish future/process and notice rails [S595][S596]. None certifies the case current without joined contract-year/service-category rows.


## rev0375 addendum — MA contractor, resident-harm, and enforcement bridge

Rev0375 targets the remaining false-comfort seam in the Medicare Advantage branch: appeal-burden metrics can still hide **who reviewed the request**, **which vulnerable subgroup was denied**, and **whether audit/enforcement created actual restoration**. OIG's SNF review reports that naviHealth processed half of all SNF admission requests, denied 14%, and had 97% of appealed naviHealth denials overturned; it also reports SNF-level-care requests from nursing-home residents were denied 40% of the time versus 11% for other enrollees [S579]. OIG's recommendation to collect request-level prior-authorization data with service type and contractor information confirms that the row contract must preserve contractor and service keys [S579].

The accountability side is now explicit. CMS's program-audit route supplies audit protocols, results, and audit/enforcement reports, but CMS cautions that audit data-collection specifications and record layouts are monitoring tools and not policy interpretation [S597]. CMS's enforcement-actions route supplies CMP, intermediate-sanction, and termination rails, but the case must still show whether an action links to the same contract/service denial pattern and restores care or money [S598]. CMS's CY2026 final-rule fact sheet adds plan-obligation fields: approved inpatient authorizations must generally be honored except obvious error or fraud, concurrent decisions are organization determinations subject to appeal rules, providers must receive coverage-decision notice when they submit a request, and enrollee liability cannot be fixed before a contracted-provider claim decision [S599].

Certification remains blocked until one SNF or other service-specific contract-month row joins contractor/delegated-entity identity, vulnerable-resident status, request/denial/appeal/overturn counts, notice, time-to-care, service furnished, financial restoration, audit finding, enforcement action, quality context, and RADV/payment-integrity context.


## rev0376 addendum — MA equity-disaggregation and beneficiary-experience join

Rev0376 closes the next false-comfort seam. After rev0375, the case preserved contractor identity and nursing-home-resident vulnerability, but a contract-level MA row could still average away **dual/LIS status, disability-entitlement status, race/ethnicity, geography, and beneficiary-reported access burden**. The Master Beneficiary Summary File route supplies beneficiary enrollment and denominator fields including race, reason for entitlement, monthly Part C enrollment, dual eligible status, Part C plan/enrollment information, and low-income cost-sharing indicators [S600]. CMS Mapping Medicare Disparities supplies public subgroup/place context for disparities in outcomes, utilization, and spending, but it is context, not denial proof [S601]. MCBS supplies beneficiary-reported social and medical risk factors, utilization, outcomes, and information not otherwise available through administrative data [S602]. MA/PDP CAHPS supplies contract-comparable plan-experience evidence, but experience ratings cannot substitute for service-level denial/remedy proof [S603].

The Star Ratings equity corrective cannot be assumed active for this window. CMS's CY2027 final-rule fact sheet says CMS is not implementing the Excellent Health Outcomes for All reward, formerly the Health Equity Index reward, for 2027 Star Ratings [S604]. Therefore the MA claim-security case cannot treat Star Ratings or a near-term health-equity reward as an adequate remedy unless a different active corrective instrument is shown.

Certification remains blocked until one service-specific contract-month row joins subgroup denominator fields, contractor/delegated-entity identity, resident/post-hospital status, request/denial/appeal/overturn/unappealed-denial counts, notice, time-to-care, service furnished, beneficiary/provider restoration, CAHPS/MCBS experience context where linkable, MMD place/subgroup context, Star Ratings/EHO4All status, audit/enforcement, RADV/payment-integrity context, and explicit privacy/suppression notes. No aggregate, Star Rating, survey-only, MMD-context-only, or HEI/EHO4All-existence proof can certify the case.


## Rev0377 clinical-correctness and remedy-effectuation guardrails

Rev0377 closes a more dangerous false-pass seam in the Medicare Advantage branch: a denial/appeal row is not substantively useful until it can say whether the denied or unpaid service met Medicare coverage rules, whether the plan used internal criteria beyond the public Medicare coverage authority, whether records were actually sufficient, and whether a reversal restored care or payment within the applicable effectuation deadline. HHS-OIG's case-file and physician-review work found that some denied prior-authorization and payment requests met Medicare coverage or MAO billing rules, with causes including plan clinical criteria outside Medicare coverage rules, documentation denials despite sufficient records, and manual or system-processing errors [S605]. CMS's 2024 rule guardrail states that MA organizations must provide the same medically necessary care as Traditional Medicare and constrains internal criteria to evidence-based and public criteria when Medicare coverage rules are not fully established [S606]. The current Part 422 Subpart C benefit rules and Subpart M appeal-effectuation rules mean the next certifying row must preserve coverage authority, denial reason, payment entitlement, effectuation deadline, and actual restoration dates rather than treating an appeal or overturn as remedy by itself [S607] [S608]. Rev0377 also records that CY2026 AI guardrails were not finalized as proof that algorithmic/delegated review opacity cannot be assumed solved merely because it appeared in rulemaking [S599].


## Rev0378 access-availability, ghost-network, and denied-claim visibility bridge

Rev0378 addresses the next false-completion seam in the Medicare Advantage branch: even a row with denial, appeal, clinical criteria, and remedy-effectuation fields can still be misleading if the plan's network, provider directory, active provider availability, and denied-claim visibility cannot be joined to the same service. OIG found limited behavioral-health provider networks and inactive “ghost” providers that can make managed-care networks appear larger than they are [S609]. CMS network-adequacy guidance supplies the HSD table, specialty/facility, automated criteria-check, ZIP-code failure, triennial-review, triggering-event, and exception surfaces, but those surfaces must be treated as access predicates rather than completed access proof [S610]. CMS's CY2026 Medicare Plan Finder provider-directory implementation route and Provider Directory API timing rule create public/digital directory surfaces, but neither proves that a listed provider is active, accepts the enrollee, or has an appointment available [S611][S612]. OIG's behavioral-health access work also requires active-provider and travel/appointment fields rather than nominal workforce counts [S613]. Finally, OIG found that MA encounter data lacks a definitive denied-claim indicator and that the relevant recommendation remains open; the cube must not certify payment-denial/restoration rows from adjustment codes alone [S614].


## Rev0379 payment-integrity, rebate-value, risk-coding, and public-cost waterfall

Rev0379 closes the next MA false-completion seam: a row that proves denial/access/remedy can still be incomplete if the same contract-year cannot explain how the plan was paid and whether payment accuracy, rebates, supplemental-benefit value, and public-cost incidence offset or compound claim-security failure. MedPAC's March 2026 MA status work says average 2026 MA payments include rebate payments, that average rebate payments are projected to be $2,660 per beneficiary, that rebates account for a projected 15 percent of Medicare MA payments, and that available data do not show enough beneficiary use of supplemental benefits to weigh rebate costs against added value [S581]. The same chapter estimates 2026 MA payments exceed comparable FFS spending by 14 percent, or $76 billion, and raise aggregate Part B premiums by about $11 billion; those estimates make taxpayer and premium incidence mandatory fields rather than background context [S581]. CMS's 2027 rate announcement is a current payment-policy surface, not a claim-security pass: it finalizes a 2.48 percent, over $13 billion, MA payment increase, preserves the 2024 MA risk-adjustment model for 2027, excludes unlinked chart-review-record diagnoses with an exception, and states that the expected average change excludes an underlying MA coding trend of 2.50 percent [S580]. CMS's 2026 rate announcement and ratebook/bid-pricing data routes supply payment-factor, benchmark, bid, and rebate fields, but they do not show actual care, benefit use, denial correctness, or restoration [S615][S616][S617][S618]. RADV remains necessary because CMS describes RADV as its primary way to address MA overpayments and the final rule explains recovery when risk-adjustment diagnoses are not supported by medical records, including extrapolation beginning with payment year 2018 [S588][S620]. OIG's 2024 HRA/chart-review report is the strongest payment-integrity bridge: diagnoses found only on HRAs or HRA-linked chart reviews, and not on any other 2022 service records, generated an estimated $7.5 billion in 2023 MA payments and raised concern that diagnoses were inaccurate or that enrollees did not receive needed care [S619].


## Rev0380 encounter, benefit-use, and minimum certifying row lock

Rev0380 prevents the MA branch from passing on plan design or service fragments. A certifying row must now distinguish five things that earlier revisions intentionally kept separate but had not yet locked into one artifact: (1) a benefit was offered in a plan/PBP, (2) a service was requested, (3) a service was denied or approved, (4) a service encounter was actually furnished, and (5) money changed hands or a remedy restored care/payment. ResDAC's MA SNF encounter file contains diagnosis/procedure/RUG, dates, organization NPI, contract/PBP, and no payment variables [S621]. The carrier encounter file likewise exposes professional-service identifiers but no payment information and is rarely sufficient by itself [S622]. CMS Benefits Data and 2026 PBP Benefits identify approved plan benefit designs, not delivered care or restoration [S624][S625]. CMS Part C specifications make the gap sharper: supplemental-benefit utilization/cost rows are for furnished/approved services and denied supplemental-benefit coverage is not reported as utilization/cost for that item [S585]. KFF's 2026 MA overview says supplemental benefits remain widely offered, prior authorization is nearly universal for at least some services, but supplemental-benefit use/spending data are not yet available to researchers or consumers and detailed prior-authorization data for those benefits are not collected/reported [S626]. MedPAC's supplemental-benefits chapter adds a public-cost warning: rebate allocations are projections and may not reflect actual use, while rebates are financed through trust funds and Part B premiums [S627]. Therefore the next certification object is not an aggregate benefit table, encounter file, rebate line, or appeal count; it is one joined contract/PBP/benefit/request/encounter/payment/remedy row that survives all five separations.


## Rev0381 MA steering, lock-in, broker incentive, and exit-rights bridge

Rev0381 moves the Medicare Advantage claim-security branch upstream from a denied service to the beneficiary's plan-entry and exit conditions. A denial/remedy row can still be misleading if the beneficiary was steered into a plan through broker, TPMO, lead-generator, provider, or health-care-provider marketing incentives, if the plan universe presented to the beneficiary is unknown, if disability or complex-care beneficiaries were targeted or avoided, or if the beneficiary cannot realistically leave after a serious diagnosis or claim failure. CMS publishes plan-level independent-agent compensation surfaces and describes initial and later-year payments when members remain enrolled or make like-type changes [S628]. CMS finalized CY2025 guardrails because excessive broker compensation and bonuses can steer beneficiaries based on financial interests instead of health needs [S629]. OIG's special fraud alert treats suspect MA marketing payments as a steering, misleading-enrollment, and selective-targeting risk [S630]. DOJ's 2025 complaint alleges kickbacks, steering to higher-paying plans regardless of suitability, and disability discrimination by MA insurers and broker organizations; this is contrary-risk evidence, not adjudicated proof [S631]. OIG's active work plan keeps marketing complaints, harms, and incentive structures on the open evidence perimeter [S632]. The exit side is equally material: KFF finds that most MA enrollees ages 65+ lack guaranteed Medigap issue protections beyond initial windows [S633], Medicare.gov identifies the official six-month and limited guaranteed-issue windows [S634], and a 2025 cancer-diagnosis study associates Medigap guaranteed-issue protections with higher switching from MA to Traditional Medicare [S635]. Therefore the next certifying row must join enrollment provenance, compensation/lead/referral incentives, plan-universe evidence, complaint/correction rights, Medigap guaranteed-issue status, and exit feasibility to the denial/access/remedy/payment row.
