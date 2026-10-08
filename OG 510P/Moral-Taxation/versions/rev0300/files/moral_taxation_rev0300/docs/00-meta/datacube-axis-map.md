# Datacube axis map

The datacube is now a comprehensive calibration index. Rev0286 adds a family-normalized audit layer: route records must carry all required axes, use explicit sentinel values instead of silent blanks, and keep taxpayer-side-AI values confined to AI/preparer/model-governance records. Every `docs/20-calibration/*.md` file must have a route record in `cube-index.json` or an explicit exemption. Route records should classify the case before prose expansion, link volatile sources to the currentness registry, and point golden cases to expected routes.


## Rev0288 remedy-profile policy

Rev0288 keeps the 23-axis cube intact but adds a separate remedy spine. `remedy_type` remains a classifier; the operational layer now lives in [`remedy-profiles.json`](remedy-profiles.json) and is validated by `tools/audit_remedy_profiles.py`. Each route gets one profile naming the remedy family, incidence problem, default move, blocked move, guardrails, escalation trigger, source-currentness linkage, and proceeds-integrity posture. This implements the administrative rights intuition behind correct-amount, challenge, appeal, finality, privacy, and representation protections without forcing every route into a taxpayer-only frame.[S117][S118][S141][S196]

## Rev0287 source-lineage/currentness policy

A route may cite many sources, but only a few should be marked as source-currentness dependencies. Rev0287 therefore separates ordinary `primary_sources` from `source_currentness_refs`. A currentness ref is allowed only when the route's answer would change if the source's legal status, operational rule, litigation posture, quarterly factor, implementation phase, AI-governance rule, or official data projection changed. Each currentness ref must now have a local `source_currentness_claims` entry explaining the claim and the review reason.

This pass also repairs the S15 taint: IEA's AI-energy projection remains a valid ordinary citation in many AI-adjacent memos, but it is a currentness dependency only for data-center/frontier-AI capacity routes. Beneficial-ownership reporting and global-minimum-tax coordination are now currentness-aware through FinCEN BOI interim-final-rule sources and OECD May 2026 GloBE filing/exchange guidance.[S526][S527][S652]

## Rev0286 audit and normalization policy

Every `route_records[*].axes` object must now include each required axis. If a route is not market-specific, channel-specific, or remedy-specific, it must say so with a sentinel such as `not_market_specific`, `not_channel_specific`, or `not_remedy_specific`; omission is no longer allowed. Route records also carry a `family` field so audits can detect semantic leakage, such as `ai_tax_advice` appearing in non-AI family records. Use [`cube-schema.json`](cube-schema.json) and `tools/audit_cube.py` for the machine-readable rule.

## Required axes

| Axis | Meaning | Typical values |
|---|---|---|
| subject | Who is liable, protected, represented, grouped, or controlling the rail | human, taxpayer, worker, household, firm, public body, platform gatekeeper, insurer, telecom carrier, tax preparer, software vendor |
| base | What fiscal or moral object is being reached | labor, rent, harm, information reporting, refund access, insurance backstop, universal-service surcharge, ad-market rent, AI tax advice |
| scale | Level of claim | local, state/provincial, national, club, cross-border, global, failure state |
| instrument | Legal or administrative tool | tax, fee, levy, withholding, information return, tariff, penalty, rebate, public option, safe harbor, fallback channel |
| incidence | Who likely bears the real burden | protected floor, worker, consumer, ratepayer, policyholder, small vendor, source state, ordinary taxpayer, public backstop |
| proof_posture | Evidentiary posture | clear record, record asymmetry, third-party mismatch, model score, fake source, rejected payment, platform data asymmetry |
| stage | Procedural moment | design, filing, reporting, withholding, notice, correction, appeal, collection, refund, settlement, post-review |
| floor_risk | Protected-side burden marker | low income, bankless, disability, language access, immigrant, expat, rural, elderly, identity compromised, overburdened community |
| proceeds_route | Where money or repair should go | general fund, visible rebate, local repair, ratepayer credit, reserve fund, public backstop repair, source-state share |
| anti_pattern | Trap being blocked | rent on access, foreignness as guilt, electronic-only exclusion, hidden surcharge, bailout rent, speech gag, classification safe harbor |
| evidence_state | Source quality | authoritative source, official guidance, administrative data, court opinion, oversight report, model output, speculative frontier |
| review_trigger | Event requiring recalibration | public channel removed, quarterly factor change, rulemaking, litigation, rejected-payment spike, source drift, model-error pattern |
| legal_status | Legal posture of the rule/source | proposed rule, final rule, guidance only, decided, remanded, enjoined, repealed, current guidance, unknown |
| source_freshness | How time-sensitive the anchor is | stable reference, current guidance, quarterly factor, rulemaking sensitive, litigation sensitive, operational filing season |
| market_structure | Market/rail shape | competitive market, regulated monopoly, two-sided platform, essential private rail, insurer of last resort, labor platform |
| delivery_channel | How the burden or benefit is delivered | public channel, tax software, bank account, wallet, carrier bill, insurer assessment, vendor-mediated, offline fallback |
| burden_mechanic | How incidence happens in practice | price pass-through, wage suppression, fee/surcharge, service degradation, coverage withdrawal, refund delay, legal-risk transfer |
| rights_affected | Non-price interest at stake | speech, due process, privacy, labor status, housing, health, mobility, disability/accessibility, taxpayer standing |
| remedy_type | Corrective form | rebate, waiver, deferral, credit, clawback, public option, no-go rule, disclosure, data minimization, victim relief, fallback channel |
| moral_operation | What the instrument is morally doing | revenue raising, rent capture, harm pricing, floor repair, public-capacity funding, prohibition/no-go, risk pooling, information integrity |
| severity | Moral magnitude | low, medium, high, catastrophic |
| confidence | Confidence in the classification | low, medium, high |
| review_cadence | When to refresh | quarterly, annual, filing season, rulemaking triggered, litigation triggered, source refresh triggered, event triggered |

## Default cube workflow

1. Create or update the route record first: path, primary sources, all applicable axes, and source-currentness references for volatile law or operations.
2. Confirm every calibration file is represented in `cube-index.json`; the Rev0285 checker treats unindexed calibration files as failures.
3. Add or update a machine-readable golden case in `docs/00-meta/golden-cases.json` and keep the prose card in `docs/00-meta/golden-case-cards.md` continuous.
4. If a route depends on a current legal posture, add a source-currentness entry with status, effective date, last checked date, review due date, and volatility.
5. If a proposal routes public duties through a necessary private channel, classify delivery channel, market structure, burden mechanic, rights affected, and fallback remedy before choosing the tax subject.

## Rev0285 additions

Rev0285 hardens the cube rather than adding only prose. It adds comprehensive calibration coverage, machine-readable golden cases, source-currentness metadata, a JSON-canonical scorecard renderer, and checker rules for source bijection, scorecard sync, cube coverage, duplicate ladders, and golden-case route IDs.

The most important new routing pass is the necessary-private-rail pass. Filing, refunds, rebates, telecom surcharges, insurance backstops, app stores, payment processors, identity vendors, and preparer software can become de facto tax administrators. The cube therefore separates `delivery_channel`, `market_structure`, `burden_mechanic`, and `rights_affected` from the old instrument label.[S443][S444][S648]

Rev0285 also makes volatile current-law status explicit. Universal-service contribution factors are quarterly and tax-like in incidence; prediction-market/event-contract treatment is rulemaking-sensitive; platform-worker classification is proposed-rule terrain; refund-payment operations are filing-season sensitive; CBAM/global-minimum-tax coordination is implementation-sensitive; and digital-ad pass-through rules can raise speech and salience problems.[S632][S633][S635][S641][S647][S649][S652][S653]

The new calibration ladders for taxpayer-side AI and mandatory private rails treat AI advice, preparer identity, refund destination, source traceability, rejected payments, and paper/electronic fallback as routing facts. A model does not become the tax person merely by producing text, but vendors, preparers, signers, filing rails, and refund controllers can become responsible bottlenecks.[S654][S655][S656][S657][S658][S659]

The rewritten Rev0284 ladders are now mechanism-specific: insurance/reinsurance ladders distinguish affordability support from bailout rent and residual-market assessments; universal-service ladders distinguish connectivity floors from regressive bill surcharges; digital-ad ladders distinguish rent capture from speech suppression; and cumulative-burden ladders distinguish mitigation payments from no-go siting rules.[S638][S639][S640][S650][S651]

## Source IDs only

[S443]: ../../SOURCES.md#S443
[S444]: ../../SOURCES.md#S444
[S632]: ../../SOURCES.md#S632
[S633]: ../../SOURCES.md#S633
[S635]: ../../SOURCES.md#S635
[S638]: ../../SOURCES.md#S638
[S639]: ../../SOURCES.md#S639
[S640]: ../../SOURCES.md#S640
[S641]: ../../SOURCES.md#S641
[S647]: ../../SOURCES.md#S647
[S648]: ../../SOURCES.md#S648
[S649]: ../../SOURCES.md#S649
[S650]: ../../SOURCES.md#S650
[S651]: ../../SOURCES.md#S651
[S652]: ../../SOURCES.md#S652
[S653]: ../../SOURCES.md#S653
[S654]: ../../SOURCES.md#S654
[S655]: ../../SOURCES.md#S655
[S656]: ../../SOURCES.md#S656
[S657]: ../../SOURCES.md#S657
[S658]: ../../SOURCES.md#S658
[S659]: ../../SOURCES.md#S659
[S526]: ../../SOURCES.md#S526
[S527]: ../../SOURCES.md#S527
[S117]: ../../SOURCES.md#S117
[S118]: ../../SOURCES.md#S118
[S141]: ../../SOURCES.md#S141
[S196]: ../../SOURCES.md#S196
