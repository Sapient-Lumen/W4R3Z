# Administration, explanation, and appeal routing

This note answers the question that comes **after** a tax base, subject, and collection anchor look morally plausible but **before** the system can count as legitimate in practice: **can the liability be stated clearly enough to compute, explained clearly enough to contest, and reviewed clearly enough to reverse when it is wrong?** The archive's stable answer is that administrative design is not a mere backend concern. A tax that depends on black-box determinations, hidden proxies, unusable review channels, or software legibility without human auditability fails even when its base and rates look attractive on paper.[S1][S16][S17][S23][S25][S27][S44]

## Core rule

Build every serious tax around six linked requirements:

1. **publish the operative rule version and effective dates**,
2. **show the measured base, rate, threshold, and jurisdictional basis**,
3. **disclose the main data sources, proxy variables, and update cadence**,
4. **keep the rule machine-readable but human-auditable**,
5. **guarantee a real correction and appeal lane with authority to reverse**, and
6. **minimize collection, retention, and sharing of data beyond what the rule actually needs**.[S1][S16][S17][S23][S25][S27][S44]

A proposal fails if ordinary people, small firms, or reviewed subjects cannot reconstruct the claim against them without expert decoding or proprietary model access. When the live dispute is specifically **whether model assistance may decide, how much explanation must travel with it, what kind of human review makes it answerable, or how far verification may escalate beyond facial completeness**, route next through [`model-assisted-tax-administration-and-accountable-review-routing.md`](model-assisted-tax-administration-and-accountable-review-routing.md) and [`verification-sampling-and-review-intensity-routing.md`](verification-sampling-and-review-intensity-routing.md). If the live dispute is instead **whether the state's own prefill, calculator, portal, or guidance created the error being enforced**, route next through [`official-error-prefill-and-guidance-reliance-routing.md`](official-error-prefill-and-guidance-reliance-routing.md). For remaining settings work — exact notice contents, assistance floors, when generic reconciliation can stay compact, and what level of adverse action requires richer explanation and real reversal authority — continue with [`../20-calibration/administration-explanation-and-appeal-minimum-standard.md`](../20-calibration/administration-explanation-and-appeal-minimum-standard.md).

## Default routing by context

| Context | Administrative default | Why this is usually more defensible | Main warning |
|---|---|---|---|
| Ordinary wage and transfer taxation | withholding plus clear year-end reconciliation, prefilled where possible, with visible explanation of pay, base, and offsets | routine obligations should be the easiest to understand and correct | do not let payroll automation hide rate logic, floor protection, or refund paths behind unreadable codes or post hoc dispute mazes.[S1][S16][S27][S65][S66] |
| Recurrent property, land, and local charges | public valuation method, update cadence, parcel-specific notice, and simple contest path | place-bound taxes are legible only if valuation and situs claims are inspectable | stale assessments, hidden vendor models, or opaque local formulas corrode legitimacy fast.[S5][S23][S25][S27] |
| Small firms and simplified regimes | limited proxy use, clear graduation rules, and plain-language explanation of why the regime applies | simplification is justified when it reduces burden without trapping firms forever | a simplified regime becomes unjust when the proxy is secret, sticky, or impossible to challenge.[S16][S23][S26][S27] |
| Cross-border or multi-level claims | notice that names the claiming jurisdiction, nexus theory, and dispute path between levels as well as for the taxpayer | multi-level taxation needs visible grounds for who is asking and why | overlapping claims without explanation turn jurisdictional complexity into arbitrary extraction.[S3][S23][S27][S28] |
| Model-assisted audit, triage, or enforcement | bounded assistance only; final liability and coercive recovery stay reviewable by accountable humans | predictive tools can help triage, but they scale error and bias as well as efficiency | a score is not a reason; black-box targeting is not cured merely by saying an official clicked approve.[S16][S17][S27][S39][S40][S41][S44] |
| Controller-side AI taxation | registry-quality disclosures for compute, energy, location, beneficiary chain, and review triggers, with explainable proxy use where direct measurement is noisy | present AI taxes sit on complex technical stacks and therefore need unusually strong explanation discipline | do not let compute thresholds, risk scores, or controller maps become proprietary mysteries that only the biggest labs can parse.[S10][S15][S16][S17][S23][S44] |
| Future rights-bearing artificial person, if threshold is actually crossed | person-like notice, representation, explanation, and appeal rights before any direct civic liability | direct taxation without intelligible process would contradict the archive's standing rule | do not move to direct machine taxation without the procedural bundle that makes civic subjection answerable at all.[S19][S20][S42][S43][S44] |

## Routing rules

### 1. Machine-readable is necessary, not sufficient

Tax rules should be representable clearly enough for software, but software clarity alone is not legitimacy. The same rule must remain inspectable by people who need to understand, challenge, or revise it.[S1][S16][S17][S27]

### 2. Notice should name the claim, not just the amount

Every serious notice should say **what rule was used, what base was measured, what data sources or proxies mattered, what rate or threshold applied, what jurisdiction is claiming, and how to correct or appeal**. A number without this structure is extraction, not explanation.[S16][S17][S23][S27]

### 3. Proxy use should be disclosed and contestable

When the administration relies on appraisals, presumptive methods, model-assisted estimates, or safe-harbor proxies, it should say so openly and show the approximation ladder. Hidden proxies are especially dangerous where they track protected-status or locality proxies by accident or design.[S23][S25][S27][S44]

### 4. Appeals must be real enough to reverse outcomes

A nominal review path is not enough. Correction and appeal need a reachable lane, understandable deadlines, accessible help, and authority to change the result rather than merely reaffirm the same automated output.[S16][S17][S27]

### 4.5 Baseline correction and appeal cannot be sold back to the subject

A system fails administratively if the only practical route to first-line correction or merits review runs through large filing charges, mandatory paid intermediaries, software gatekeeping, or full prepayment of the disputed amount. Anti-frivolous filters, issue-scoping, and bounded documentary discipline can be justified; review paywalls and pay-first traps cannot be the ordinary path.[S16][S27][S39][S41][S42][S44][S117][S118]

Where the live dispute is specifically **whether a contested amount must be paid now or may be stayed, escrowed, narrowed to the undisputed share, or hardship-adjusted while review is live**, route next through [`interim-liability-stays-escrow-and-hardship-relief-routing.md`](interim-liability-stays-escrow-and-hardship-relief-routing.md).

### 4.6 Baseline account history and notice access cannot be sold back as record rent

A system is still procedurally unjust if people can theoretically contest a claim but must first pay to see their own ordinary notices, balances, payment history, transcripts, or machine-readable account record. Cost-priced exceptional certification may sometimes be justified; baseline self-access and ordinary export should not become a fee-bearing explanation toll or vendor lock-in lane.[S16][S27][S39][S42][S44][S65][S66][S89][S127][S128]

### 4.7 Baseline language access, alternative media, and communication assistance cannot be sold back as comprehension tolls

A system is still procedurally unjust if the claim exists on paper or on-screen but the subject must buy translation, alternative media, interpreter help, or comparable communication assistance just to understand an ordinary notice, filing demand, payment instruction, or correction path. Optional expert help may still exist; baseline comprehension support should not become a fee-bearing side market.[S16][S27][S39][S42][S44][S65][S129][S130][S131][S132]

### 4.8 Baseline response submission and ordinary tax-case correspondence cannot be sold back as submission tolls

A system is still procedurally unjust if the subject can theoretically understand the claim but must then pay to answer it through per-upload charges, premium correspondence lanes, mandatory paid intermediaries, or fee-bearing message channels. Cost-priced exceptional production may sometimes be justified; ordinary notice responses, routine supporting-document uploads, and baseline case correspondence should not become the next monetized gate in the chain.[S16][S27][S39][S41][S42][S44][S65][S138][S139][S140]


### 4.9 Baseline representative authorization and tax-information delegation cannot be sold back as proxy-access rents

A system is still procedurally unjust if the subject can understand and answer the claim but must pay, subscribe, or route through a captive intermediary merely to authorize a representative, give limited tax-information access, check who has access, or revoke that access. Professional standards and identity proofing may still matter; the baseline proxy switchboard belongs with standing, confidentiality, and review rather than with a paid gate.[S16][S27][S40][S42][S44][S117][S118][S141][S142][S143]


### 4.10 Baseline account-coordinate and withholding updates cannot be sold back as update rents

A system is still procedurally unjust if the subject can see, understand, answer, and delegate a tax matter but cannot keep ordinary contact, address, refund, payment, responsible-party, or withholding / prepayment records current without fees, captive portals, or paid intermediaries. Stale-record consequences should not harden into waiver, penalty, refund delay, or collection escalation where the update lane itself was inaccessible, fee-bearing, or controlled by the wrong actor.[S27][S39][S42][S65][S66][S68][S124][S128][S144][S145][S146][S147]

### 4.11 Tax-identity compromise recovery cannot be sold back as victim rent

A system is still procedurally unjust if the subject can obtain credentials and update records in ordinary cases, but must pay, hire help, or endure unbounded limbo when an impostor files first, redirects a refund, reports phantom wages, captures the account, or forges authorization. Fraud proofing may be strict, but tax-identity recovery must be correction-first, status-visible, and no-rent; an unauthorized filing or account action is disputed evidence, not the victim's admission.[S27][S39][S40][S41][S42][S65][S66][S68][S141][S148][S149][S150][S151][S152][S153]

### 4.12 Third-party reporting mismatch correction cannot be sold back as reporter-hostage rent

A system is still procedurally unjust if the subject can recover from identity compromise but remains trapped by ordinary third-party reporting error: a missing or wrong W-2, incorrect 1099, mistaken 1099-K, bad withholding credit, duplicated platform report, or stale payer feed should trigger a field-specific no-rent mismatch lane. The recipient may owe a concrete counterstatement; the stronger issuer, platform, payer, or reporting system should carry the main correction or affirmation burden.[S27][S39][S41][S42][S65][S66][S68][S154][S155][S156][S157][S158]

### 4.13 Deadline preservation and retransmission cannot be sold back as time-trap rent

A system is still procedurally unjust if the subject can file, pay, answer, delegate, update, recover from identity compromise, and dispute third-party mismatches, but loses the right because an extension, disaster postponement, rejected submission, channel outage, or reasonable-cause impossibility lane is fee-bearing, invisible, or unavailable. Deadlines may coordinate administration; they should not convert good-faith attempts, official-channel failures, or documented emergencies into automatic forfeiture or paid deadline rescue.[S16][S17][S27][S39][S41][S42][S65][S66][S168][S170][S172][S173][S174][S175]

### 4.14 Ledger reconciliation is part of explanation and appeal

A notice that says a payment, credit, carryforward, refund, or offset is missing should explain enough of the ledger for the subject to test the claim: period, tax type, payment date, posting date, source, amount, offset bucket, returned-payment status, and the bounded proof path for correction. If the taxpayer supplies a confirmation number, bank record, transcript, corrected information return, refund trace, or comparable proof, the disputed slice should move to reconciliation rather than collection-by-default.[S176][S177][S178][S179][S180][S181]

### 4.15 Collection-restraint release is part of explanation and appeal

A collection marker should be explainable not only when imposed but also when kept in force. Notices and account surfaces should show what liability, period, amount, appeal status, payment arrangement, hardship status, or certification fact currently justifies a lien, levy, wage or bank hold, passport certification, offset block, or public collection marker, and what no-rent step will release, withdraw, decertify, return, or narrow it when the predicate changes.[S16][S27][S39][S41][S42][S182][S183][S184][S185][S187][S188][S189][S190]

### 4.16 Examination contact and audit reconsideration cannot be sold back as inspection rent

A system is still procedurally unjust if the subject can retrieve records, answer notices, preserve deadlines, and appeal in theory, but an examination itself becomes a paid or impossible channel. Audit notices should name the issue, records, deadline, channel, and disagreement path; document requests and interviews should stay proportional to the disputed fact; ordinary rescheduling, manager contact, appeal, and audit reconsideration should be no-rent rather than default-assessment traps.[S191][S192][S193][S194][S195][S196]

### 4.17 Preparer misconduct cannot be sold back as a captive paid-rescue lane

A system is still procedurally unjust if the subject can understand, answer, and appeal official action, but a paid preparer or e-file intermediary can alter the return, divert the refund, withhold records, fail to file, use ghost credentials, or misuse PTIN / EFIN access while the taxpayer must then buy a second private rescue lane. Notices, transcripts, refund traces, complaint channels, and account-correction paths should separate the taxpayer's intended return from preparer conduct before penalties, refund loss, or default finality harden.[S197][S198][S199][S200][S201][S202][S203]

### 4.18 Self-correction, amended returns, refund claims, and abatement requests cannot be sold back as amendment rent

A system is still procedurally unjust if the subject can retrieve records, answer notices, preserve deadlines, survive audit contact, and escape preparer misconduct, but must then buy a private amendment gate or accept penalty confession merely to correct a filed return, file a timely superseding return, claim an overpayment, or request abatement of a penalty, fee, interest, or addition. Self-correction should be issue-scoped, status-visible, channel-plural, and non-confessional unless independent culpability facts show strategic falsehood.[S39][S41][S42][S65][S66][S204][S205][S206][S207][S208][S209][S210][S211]


### 4.19 Deadlock escalation and low-income dispute help cannot be sold back as rescue rent

A system is still procedurally unjust if every first-line lane exists in form, but a stuck case can move only through paid tax-resolution firms, premium preparer leverage, insider status brokers, or a former owner's account. When normal channels fail, hardship is live, the agency repeatedly does not respond, a system or procedure is not working, or a low-income / language-vulnerable taxpayer needs dispute help, the escalation and clinic-help path should be visible, channel-plural, and no-rent rather than another black box.[S141][S212][S213][S214][S215][S216]

### 4.20 Private-collection assignment cannot be sold back as collector rent

A system is still procedurally unjust if a taxpayer can pay, verify, appeal, seek help, and preserve hardship rights with the public agency, but loses those rights when the file is assigned to a private collection contractor. Outsourced collection contact must keep prior public notice, two-way verification, direct public payment rails, excluded-case screening, return-to-agency access, and no-rent correction / hardship routes; otherwise the public debt becomes a scam-like private gate.[S133][S148][S153][S212][S217][S218][S219][S220][S221][S222]

### 4.21 Automated adjustment notices cannot be sold back as auto-adjustment rents

A system is still procedurally unjust if math-error, CP11 / CP12, CP2000 / CP2501, automated underreporter, or comparable summary-adjustment notices change accounts faster than people can understand or reverse them. Automated notices should identify the affected line or schedule, source record or computation, status of the change, exact response or reversal window, and no-rent reply channels; otherwise high-volume correction becomes liability by default.[S223][S224][S225][S226][S227][S228][S229][S230][S231]

### 4.22 Statutory-notice petition access cannot be sold back as docket rent

A system is still procedurally unjust if a statutory notice of deficiency, notice of determination, passport certification, worker-status determination, or comparable petitionable notice preserves judicial review in theory but loses it in practice through hidden court deadlines, fee friction, portal-only filing, stale-address traps, or confusion between answering the IRS and petitioning the Tax Court. Petition cues, fee-waiver routes, small-case options where available, and mail / paper / e-filing / hand-delivery options should be visible before the dispute is pushed into pay-first litigation.[S117][S118][S232][S233][S234][S235][S236][S237][S238][S239]

### 4.23 Collection alternatives cannot be sold back as compromise rent

A system is still procedurally unjust if a taxpayer can receive notices, petition, answer, pay, and escalate deadlock, but cannot seek offer-in-compromise, currently-not-collectible, or other collection-alternative review without buying a settlement-mill package. Compromise and hardship review should stay lane-specific, fee-waivable where low-income rules apply, and status-clear about returns, rejections, appeals, and collection effects.[S39][S42][S160][S162][S180][S212][S240][S241][S242][S244][S246][S247]
### 4.24 Bankruptcy and discharge status cannot be sold back as fresh-start rent

A system is still procedurally unjust if bankruptcy filing, automatic-stay recognition, discharge-injunction repair, refund / trustee coordination, remaining-balance explanation, or cancellation-of-debt exclusion review depends on paid proof or private tax-bankruptcy brokerage. Valid post-petition and nondischargeable tax claims may remain, but the account should mark the case posture, affected periods, refund predicate, and public insolvency contact clearly enough that fresh-start relief does not become a discharge-proof toll.[S249][S250][S251][S252][S253][S254][S255][S256][S257]


### 4.25 Nonfiler and substitute-return reconstruction cannot be sold back as default-base rent

A system is still procedurally unjust if CP59 / CP2566 / CP3219N nonfiler notices, substitute returns, wage-and-income transcript reconstruction, late original filing, or refund-limit explanations are usable only through paid rescue markets. An agency-computed return can protect revenue, but it should stay visibly provisional, state the limited third-party records used, preserve the separate Tax Court petition clock, and let the taxpayer file or reconstruct the correct return through no-rent public channels.[S238][S258][S259][S260][S261][S262][S263][S264][S265][S266]

### 4.26 Refundable-credit audits and recertification cannot be sold back as credit rent

A system is still procedurally unjust if low-income, child, dependent, education, or floor-protecting credits exist in statute but can be claimed, defended, or restored only through paid preparers, proprietary software, hidden Form 8862 recertification knowledge, or impossible documentation. CP75-family audits, CP79-family recertification, PATH Act timing holds, Form 8867 preparer due-diligence, and 2-year / 10-year credit bans should remain issue-scoped, document-plural, status-visible, and no-rent rather than turning EITC / ACTC / CTC / ODC / AOTC access into a poverty-audit toll.[S21][S27][S31][S32][S33][S39][S41][S42][S64][S65][S66][S117][S118][S173][S177][S178][S276][S277][S278][S279][S280][S281][S282][S283][S284][S285][S286][S287][S288][S289][S290]

### 5. Data minimization is part of equality, not only privacy

The state should not collect every possible datum merely because analytics make it tempting. Excessive data hunger raises exclusion, error, and proxy-discrimination risks while shifting power toward large actors who can navigate the machinery best.[S16][S17][S27][S44]

### 6. Controller-first AI taxation needs stronger administrative disclosure, not weaker

Because present AI taxation runs through controller chains rather than direct model personhood, the administrative burden falls on labs, clouds, deployers, and major beneficiaries to disclose enough about compute, energy, siting, proxy methods, and affiliate structure for the levy to be audited. Complexity is not a moral exemption.[S10][S15][S16][S17][S20][S44]


### 7.18 Keep basis reconciliation from becoming gross-proceeds finality

When administration matches a sale, exchange, broker report, digital-asset disposition, or real-estate proceeds report, the explanation must distinguish proceeds from gain. The taxpayer should see whether basis was reported, missing, noncovered, or disputed; how Form 8949-style adjustment or equivalent correction works; and which upstream record-holder can be asked to correct transfer, lot, wallet, or closing records. A proceeds match without a basis lane is not an adequate explanation of liability.[S27][S39][S41][S42][S65][S66][S154][S155][S291][S292][S294][S295][S296][S298][S299][S301][S302]

## Five anti-patterns

1. **Black-box extraction** — money is demanded because an unseen score, vendor model, or opaque cross-match says so.
2. **Appeal by fiction** — review exists on paper but is too slow, costly, digital-only, or authority-starved to matter.
3. **Review paywall** — correction or appeal is formally available only after major fees, mandatory paid intermediaries, or effective pay-first design.
4. **Proxy laundering** — valuation estimates, fraud scores, household defaults, or locality codes quietly substitute for the real moral variable.
5. **Version opacity** — taxpayers cannot tell which rule set, update, or threshold schedule actually governed the claim.
6. **Complexity as privilege** — the system is technically machine-legible yet effectively only navigable by large firms, repeat players, or expert intermediaries.  
7. **Record rent** — ordinary notices, transcripts, or account history are effectively paywalled, subscription-bound, or locked behind proprietary access even though the administration already holds them.[S16][S17][S23][S25][S27][S39][S41][S42][S44][S89][S117][S118][S127][S128]
8. **Comprehension toll** — the subject can technically retrieve the claim, but translation, alternative media, or communication assistance needed to understand it is sold back through a fee market or proprietary gate.[S16][S27][S39][S42][S44][S65][S129][S130][S131][S132]
9. **Submission toll** — the subject can read the claim, but must pay to answer it through per-upload fees, premium message channels, or a paid correspondence broker.[S16][S27][S39][S41][S42][S44][S65][S138][S139][S140]
10. **Proxy-access rent** — the subject can answer or appeal only if representative authorization, tax-information delegation, or revocation runs through a fee-bearing or captive intermediary gate.[S16][S27][S40][S42][S44][S141][S142][S143]
11. **Update rent / stale-record trap** — ordinary account-coordinate, contact-route, refund, payment, or withholding updates are fee-bearing, captive, or too slow, so old records quietly defeat notice, refund delivery, payment compliance, or review rights.[S27][S39][S42][S65][S66][S68][S124][S128][S144][S145][S146][S147]
12. **Victim-rent identity recovery** — an unauthorized return, account takeover, forged authorization, or phantom wage record forces the real subject into paid restoration, unbounded fraud-hold limbo, or penalties before the account is treated as disputed.[S27][S39][S40][S41][S42][S65][S66][S68][S148][S149][S150][S151][S152][S153]
13. **Reporter-hostage mismatch** — a standardized third-party statement, platform feed, or withholding record is treated as final until the recipient pays for cleanup or persuades an unreachable issuer to repair its own report.[S154][S155][S156][S157][S158]
14. **Time-trap rent / outage forfeiture** — extension, postponement, retransmission, or reasonable-cause relief is formally available but practically reachable only through paid help, proprietary channels, or hindsight-perfect proof after the deadline has already passed.[S168][S170][S172][S173][S174][S175]
15. **Ledger black box** — payment, credit, carryforward, refund, offset, or returned-payment status is asserted as final while the ordinary reconciliation facts remain invisible or fee-mediated.[S176][S177][S178][S179][S180][S181]
16. **Release black box** — a lien, levy, passport certification, wage hold, bank hold, or public collection marker persists without a visible current predicate or no-rent release path.[S182][S183][S184][S187][S188][S190]
17. **Inspection-rent audit** — a correspondence or in-person examination hardens into liability because answer, scheduling, copies, manager contact, appeal, or reconsideration is available only through paid help or impossible availability.[S191][S192][S193][S194][S195][S196]
18. **Captive-preparer finality** — the filed return, refund route, or missing record is treated as the taxpayer's final act even after credible evidence of preparer alteration, ghost filing, refund diversion, or withheld records.[S197][S198][S199][S200][S201][S202][S203]
19. **Amendment confession trap** — an amended return, refund claim, or abatement request is available only through paid help, hidden timing knowledge, or automatic culpability inferences.[S204][S205][S206][S207][S208][S209][S210][S211]
20. **Rescue-rent escalation** — a refund freeze, levy, identity lock, failed amendment, or repeated nonresponse can be unstuck only by paying a private tax-resolution actor or premium gatekeeper.[S212][S213][S214][S215][S216]
21. **Collector-impersonation outsourcing** — a private collection assignment is credible only through a caller or contractor letter, payments drift toward private rails, and refusal to trust an unverified collector becomes taxpayer blame.[S217][S218][S219][S220][S221][S222]
22. **Auto-adjustment default** — a math-error, underreporter, or summary-adjustment notice changes the account, starts a hidden clock, or moves to collection before the subject sees the line-item reason and no-rent reversal or response path.[S223][S224][S225][S226][S227][S230][S231]
23. **Docket-rent petition trap** — a deficiency or petitionable notice preserves court review in form but loses it through hidden deadline cues, fee / waiver friction, portal-only filing, or IRS-response confusion.[S232][S233][S235][S236][S237][S238][S239]
24. **Compromise-rent settlement trap** — offer-in-compromise, CNC, or hardship review is practically reachable only through paid settlement mills, hidden fee-waiver knowledge, or opaque return / rejection status.[S240][S241][S242][S244][S246][S247][S248]
25. **Fresh-start rent / discharge-proof trap** — bankruptcy filing, stay protection, discharge recognition, remaining-balance explanation, refund turnover / offset status, or cancellation-of-debt exclusion review works only if the debtor buys private proof or repeatedly re-proves a public case status.[S249][S250][S251][S253][S254][S255][S256][S257]

26. **Nonfiler default-base trap** — a missing or late return becomes a government-computed tax base that is practically final unless the taxpayer buys transcript reconstruction, late-filing help, or petition-deadline rescue.[S238][S258][S259][S260][S261][S262][S263][S264][S265][S266]

27. **Credit-rent recertification trap** — a floor-protecting credit can be claimed or restored only through paid help, hidden Form 8862 knowledge, whole-refund holds, rigid documentation demands, or credit bans without clear culpability and appeal cues.[S276][S279][S280][S281][S282][S283][S284][S285][S286][S287][S288][S289]
28. **Responsible-person notice trap** — a proposed trust-fund recovery assessment names a person but does not make authority, willfulness, periods, payments in dispute, Letter 1153 protest rights, or provider-failure facts usable before assessment.[S321][S322][S323][S324][S325][S326][S327][S328][S329]

## Order of preference

When two designs pursue the same revenue or corrective goal, the archive usually prefers the one that:

1. can be explained in plain language and machine-readable form at the same time,
2. uses observable data before disputed proxies,
3. provides correction before coercive escalation,
4. keeps baseline correction and first review reachable without major price barriers or pay-first traps,
5. gives model-assisted tools only bounded and reviewable roles,
6. keeps baseline comprehension reachable without fee-bearing translation or accessibility gates,
7. keeps baseline answer and document-submission lanes reachable without fee-bearing upload or correspondence gates,
8. keeps representative authorization, tax-information access delegation, and revocation subject-controlled rather than captive,
9. keeps account-coordinate, contact-route, payment, refund, and withholding updates timely and no-rent,
10. treats tax-identity compromise recovery as correction-first and no-rent,
11. keeps ordinary third-party reporting mismatches field-specific, issuer-facing, and no-rent,
12. preserves deadlines through free extension, postponement, retransmission, and reasonable-cause lanes when compliance was attempted or made temporarily impossible,
13. reconciles payment, credit, carryforward, refund, offset, and returned-payment records through a visible no-rent lane before duplicate collection, penalty escalation, or refund capture,
14. releases, withdraws, decertifies, or narrows collection restraints when their predicate changes,
15. keeps examination, interview, and audit-reconsideration lanes issue-scoped, reschedulable where reasonable, and no-rent,
16. separates preparer misconduct from the taxpayer's intended return before penalties, refund loss, or default finality harden,
17. keeps self-correction, amended-return, refund-claim, and abatement lanes issue-scoped, status-visible, no-rent, and non-confessional,
18. keeps deadlock escalation and low-income dispute help no-rent, visible, and independent enough to break official nonresponse without becoming a paid rescue market,
19. keeps private collection assignment public-noticed, mutually verifiable, direct-pay, screened for vulnerable / live-dispute cases, and returnable to the agency without paid collector leverage,
20. keeps automated adjustment notices line-item explained, status-distinct, no-rent to answer, and stayed on the disputed slice while review runs,
21. keeps statutory-notice and petitionable-review paths court-distinct, fee-waivable, channel-plural, and protected against stale-address or IRS-response confusion,
22. keeps compromise, CNC, hardship, and collection-alternative review public, fee-waivable where applicable, status-clear, and protected from settlement-mill displacement,
23. keeps bankruptcy, automatic-stay, discharge, refund / trustee, and cancellation-of-debt statuses public, account-linked, and no-rent to verify,
24. keeps nonfiler, substitute-return, late original filing, wage-and-income reconstruction, refund-limit explanation, and CP3219N petition-preservation lanes public, provisional, and no-rent,
25. and keeps data collection narrower than the maximal analytic appetite of the administration.

This is why administrative legibility belongs in the narrow waist rather than living only in archive note `112`.

## Use this note with

- [`measurement-valuation-and-proxy-routing.md`](measurement-valuation-and-proxy-routing.md)
- [`collection-and-remittance-routing.md`](collection-and-remittance-routing.md)
- [`model-assisted-tax-administration-and-accountable-review-routing.md`](model-assisted-tax-administration-and-accountable-review-routing.md)
- [`official-error-prefill-and-guidance-reliance-routing.md`](official-error-prefill-and-guidance-reliance-routing.md)
- [`enforcement-proportionality-and-recovery-routing.md`](enforcement-proportionality-and-recovery-routing.md)
- [`interim-liability-stays-escrow-and-hardship-relief-routing.md`](interim-liability-stays-escrow-and-hardship-relief-routing.md)
- [`standing-representation-and-remedy-routing.md`](standing-representation-and-remedy-routing.md)
- [`anti-discrimination-and-status-proxy-routing.md`](anti-discrimination-and-status-proxy-routing.md)
- [`../20-calibration/administration-explanation-and-appeal-minimum-standard.md`](../20-calibration/administration-explanation-and-appeal-minimum-standard.md)
- [`../20-calibration/data-minimization-credential-reuse-and-sensitive-attribute-firewall-ladder.md`](../20-calibration/data-minimization-credential-reuse-and-sensitive-attribute-firewall-ladder.md)
- [`../../archive/182-automated-math-error-underreporter-and-summary-adjustment-notices-should-not-be-turned-into-auto-adjustment-rents-or-liability-by-default-traps.md`](../../archive/182-automated-math-error-underreporter-and-summary-adjustment-notices-should-not-be-turned-into-auto-adjustment-rents-or-liability-by-default-traps.md)
- [`../../archive/181-tax-debt-outsourcing-private-collection-and-third-party-collector-contact-should-not-be-turned-into-collector-rents-or-impersonation-traps.md`](../../archive/181-tax-debt-outsourcing-private-collection-and-third-party-collector-contact-should-not-be-turned-into-collector-rents-or-impersonation-traps.md)
- [`../../archive/112-administration-visibility-appeals-and-machine-legibility.md`](../../archive/112-administration-visibility-appeals-and-machine-legibility.md)
- [`../../archive/160-basic-correction-challenge-and-appeal-should-not-be-turned-into-review-paywalls-or-pay-first-traps.md`](../../archive/160-basic-correction-challenge-and-appeal-should-not-be-turned-into-review-paywalls-or-pay-first-traps.md)
- [`../../archive/165-basic-language-access-alternative-media-interpretation-and-accessibility-assistance-should-not-be-turned-into-comprehension-tolls.md`](../../archive/165-basic-language-access-alternative-media-interpretation-and-accessibility-assistance-should-not-be-turned-into-comprehension-tolls.md)
- [`../../archive/168-basic-ordinary-response-submission-supporting-document-upload-and-tax-case-correspondence-should-not-be-turned-into-submission-tolls-or-premium-correspondence-lanes.md`](../../archive/168-basic-ordinary-response-submission-supporting-document-upload-and-tax-case-correspondence-should-not-be-turned-into-submission-tolls-or-premium-correspondence-lanes.md)
- [`../../archive/169-basic-representative-authorization-tax-information-access-delegation-and-revocation-should-not-be-turned-into-proxy-access-rents-or-captive-agent-gates.md`](../../archive/169-basic-representative-authorization-tax-information-access-delegation-and-revocation-should-not-be-turned-into-proxy-access-rents-or-captive-agent-gates.md)
- [`../../archive/170-basic-tax-account-coordinate-contact-route-and-withholding-updates-should-not-be-turned-into-stale-record-traps-or-update-rents.md`](../../archive/170-basic-tax-account-coordinate-contact-route-and-withholding-updates-should-not-be-turned-into-stale-record-traps-or-update-rents.md)
- [`../../archive/171-tax-identity-compromise-unauthorized-filing-and-account-recovery-should-not-be-turned-into-victim-rents-or-impersonation-traps.md`](../../archive/171-tax-identity-compromise-unauthorized-filing-and-account-recovery-should-not-be-turned-into-victim-rents-or-impersonation-traps.md)
- [`../../archive/172-third-party-tax-reporting-errors-withholding-credit-and-information-return-correction-should-not-be-turned-into-mismatch-rents-or-reporter-hostage-traps.md`](../../archive/172-third-party-tax-reporting-errors-withholding-credit-and-information-return-correction-should-not-be-turned-into-mismatch-rents-or-reporter-hostage-traps.md)
- [`../../archive/174-basic-deadline-preservation-extension-retransmission-and-impossibility-relief-should-not-be-turned-into-time-trap-rents-or-outage-forfeitures.md`](../../archive/174-basic-deadline-preservation-extension-retransmission-and-impossibility-relief-should-not-be-turned-into-time-trap-rents-or-outage-forfeitures.md)
- [`../../archive/176-tax-lien-levy-passport-certification-and-collection-restraint-release-should-not-be-turned-into-collateral-control-rents-or-release-ransom.md`](../../archive/176-tax-lien-levy-passport-certification-and-collection-restraint-release-should-not-be-turned-into-collateral-control-rents-or-release-ransom.md)
- [`../../archive/175-basic-payment-credit-carryforward-offset-and-account-ledger-correction-should-not-be-turned-into-suspense-rents-or-missing-credit-traps.md`](../../archive/175-basic-payment-credit-carryforward-offset-and-account-ledger-correction-should-not-be-turned-into-suspense-rents-or-missing-credit-traps.md)
- [`../../archive/178-tax-return-preparer-misconduct-ghost-preparer-refund-diversion-and-efin-abuse-should-not-be-turned-into-captive-preparer-rents-or-preparer-hostage-traps.md`](../../archive/178-tax-return-preparer-misconduct-ghost-preparer-refund-diversion-and-efin-abuse-should-not-be-turned-into-captive-preparer-rents-or-preparer-hostage-traps.md)
- [`../../archive/179-amended-superseding-refund-claim-and-abatement-correction-should-not-be-turned-into-self-correction-rents-or-confession-traps.md`](../../archive/179-amended-superseding-refund-claim-and-abatement-correction-should-not-be-turned-into-self-correction-rents-or-confession-traps.md)
- [`../../archive/180-tax-administration-deadlock-taxpayer-advocate-and-low-income-dispute-help-should-not-be-turned-into-rescue-rents-or-escalation-hostage-traps.md`](../../archive/180-tax-administration-deadlock-taxpayer-advocate-and-low-income-dispute-help-should-not-be-turned-into-rescue-rents-or-escalation-hostage-traps.md)
- [`../../archive/177-basic-tax-examination-audit-response-and-reconsideration-should-not-be-turned-into-inspection-rents-or-default-assessment-traps.md`](../../archive/177-basic-tax-examination-audit-response-and-reconsideration-should-not-be-turned-into-inspection-rents-or-default-assessment-traps.md)
- [`../../archive/184-offer-in-compromise-currently-not-collectible-and-collection-alternative-access-should-not-be-turned-into-compromise-rents-or-settlement-mill-traps.md`](../../archive/184-offer-in-compromise-currently-not-collectible-and-collection-alternative-access-should-not-be-turned-into-compromise-rents-or-settlement-mill-traps.md)
- [`../../archive/183-statutory-notice-tax-court-petition-and-prepayment-review-should-not-be-turned-into-docket-rents-or-lost-prepayment-review-traps.md`](../../archive/183-statutory-notice-tax-court-petition-and-prepayment-review-should-not-be-turned-into-docket-rents-or-lost-prepayment-review-traps.md)
- [`../../archive/192-trust-fund-recovery-penalty-responsible-person-payroll-withholding-and-third-party-payer-rules-should-not-be-turned-into-responsible-person-rents-or-payroll-collapse-scapegoat-traps.md`](../../archive/192-trust-fund-recovery-penalty-responsible-person-payroll-withholding-and-third-party-payer-rules-should-not-be-turned-into-responsible-person-rents-or-payroll-collapse-scapegoat-traps.md)
- [`../../archive/185-bankruptcy-automatic-stay-discharge-and-tax-insolvency-relief-should-not-be-turned-into-fresh-start-rents-or-discharge-proof-traps.md`](../../archive/185-bankruptcy-automatic-stay-discharge-and-tax-insolvency-relief-should-not-be-turned-into-fresh-start-rents-or-discharge-proof-traps.md)

- [`../../archive/186-delinquent-return-nonfiler-substitute-return-and-past-due-filing-reconstruction-should-not-be-turned-into-nonfiler-rents-or-default-base-traps.md`](../../archive/186-delinquent-return-nonfiler-substitute-return-and-past-due-filing-reconstruction-should-not-be-turned-into-nonfiler-rents-or-default-base-traps.md)
- [`../../archive/188-refundable-credit-audits-recertification-and-low-income-floor-claims-should-not-be-turned-into-credit-rents-or-recertification-traps.md`](../../archive/188-refundable-credit-audits-recertification-and-low-income-floor-claims-should-not-be-turned-into-credit-rents-or-recertification-traps.md)


## Rev0270 criminal-tax boundary addendum

Administration must explain posture before people can protect rights. If a case is civil, say so and keep correction, appeal, abatement, and payment-plan routes open. If the case is in fraud development, a referral is pending, CI has accepted or declined, DOJ/AUSA jurisdiction is implicated, voluntary disclosure is being screened, or restitution / probation conditions drive later civil action, the subject needs plain-language routing rather than ambiguous threat letters or paid-representative decoding.[S355][S356][S357][S359][S360][S361][S362]

Voluntary disclosure deserves especially careful explanation: it can be a path back to compliance for willful exposure, but it is not guaranteed immunity, has timeliness / completeness / truthfulness / eligibility limits, and can be revoked. That makes it a disclosure route, not a no-rent substitute for ordinary amended, delinquent, nonfiler, abatement, or correction procedures.[S359][S360]


## Rev0271 whistleblower explanation and appeal addendum

A confidential source can remain confidential without making the taxpayer defend against a ghost. Any adverse adjustment, penalty, collection step, or referral that relies on whistleblower information must still be translated into line items, periods, facts, computations, documents, legal theories, and ordinary routes to answer, appeal, petition, abate, refund, or contest collection.[S375][S377][S379]

Whistleblower process and taxpayer process are separate. Status notices, preliminary award recommendations, determination letters, confidentiality-agreement review, and award appeals do not give the whistleblower control over taxpayer merits, and taxpayer appeal rights do not automatically expose protected source identity.[S371][S372][S375][S381]

Add [`../../archive/196-whistleblower-informant-return-information-disclosure-and-award-claims-should-not-be-turned-into-bounty-rents-or-accusation-traps.md`](../../archive/196-whistleblower-informant-return-information-disclosure-and-award-claims-should-not-be-turned-into-bounty-rents-or-accusation-traps.md) when explanation must protect both source confidentiality and taxpayer contestability.

### International information-return notice and pre-assessment voice

International information-return penalties require unusually clear notices because the same fact pattern may implicate FBAR, Form 8938, Form 3520 / 3520-A, Form 5471, Form 5472, Form 8865, Form 8858, or several regimes at once. The notice should state the form, year, legal duty, penalty unit, continuation rule, asset or entity at issue, whether income was omitted, and what reasonable-cause or correction lane is available. A notice that merely says a foreign form is missing does not make the penalty morally legible.[S407][S408][S409][S410][S416][S419][S423][S425][S426][S427]

Where a taxpayer files late international information returns with a reasonable-cause statement, the archive prefers pre-assessment review when administratively possible. If assessment occurs before meaningful review, the appeal or abatement route must be easy to find, status-visible, and empowered to consider the taxpayer's good-faith facts rather than treating collection as the first real hearing.[S409][S430][S173][S432][S433]

[S355]: ../../SOURCES.md#S355
[S356]: ../../SOURCES.md#S356
[S357]: ../../SOURCES.md#S357
[S359]: ../../SOURCES.md#S359
[S360]: ../../SOURCES.md#S360
[S361]: ../../SOURCES.md#S361
[S362]: ../../SOURCES.md#S362

[S1]: ../../SOURCES.md#S1
[S3]: ../../SOURCES.md#S3
[S5]: ../../SOURCES.md#S5
[S10]: ../../SOURCES.md#S10
[S15]: ../../SOURCES.md#S15
[S16]: ../../SOURCES.md#S16
[S17]: ../../SOURCES.md#S17
[S19]: ../../SOURCES.md#S19
[S20]: ../../SOURCES.md#S20
[S23]: ../../SOURCES.md#S23
[S25]: ../../SOURCES.md#S25
[S26]: ../../SOURCES.md#S26
[S27]: ../../SOURCES.md#S27
[S28]: ../../SOURCES.md#S28
[S39]: ../../SOURCES.md#S39
[S40]: ../../SOURCES.md#S40
[S41]: ../../SOURCES.md#S41
[S42]: ../../SOURCES.md#S42
[S43]: ../../SOURCES.md#S43
[S44]: ../../SOURCES.md#S44
[S65]: ../../SOURCES.md#S65
[S66]: ../../SOURCES.md#S66
[S68]: ../../SOURCES.md#S68
[S89]: ../../SOURCES.md#S89
[S117]: ../../SOURCES.md#S117
[S118]: ../../SOURCES.md#S118
[S124]: ../../SOURCES.md#S124
[S127]: ../../SOURCES.md#S127
[S128]: ../../SOURCES.md#S128
[S129]: ../../SOURCES.md#S129
[S130]: ../../SOURCES.md#S130
[S131]: ../../SOURCES.md#S131
[S132]: ../../SOURCES.md#S132
[S133]: ../../SOURCES.md#S133
[S138]: ../../SOURCES.md#S138
[S139]: ../../SOURCES.md#S139
[S140]: ../../SOURCES.md#S140
[S141]: ../../SOURCES.md#S141
[S142]: ../../SOURCES.md#S142
[S143]: ../../SOURCES.md#S143
[S144]: ../../SOURCES.md#S144
[S145]: ../../SOURCES.md#S145
[S146]: ../../SOURCES.md#S146
[S147]: ../../SOURCES.md#S147
[S148]: ../../SOURCES.md#S148
[S149]: ../../SOURCES.md#S149
[S150]: ../../SOURCES.md#S150
[S151]: ../../SOURCES.md#S151
[S152]: ../../SOURCES.md#S152
[S153]: ../../SOURCES.md#S153
[S154]: ../../SOURCES.md#S154
[S155]: ../../SOURCES.md#S155
[S156]: ../../SOURCES.md#S156
[S157]: ../../SOURCES.md#S157
[S158]: ../../SOURCES.md#S158
[S160]: ../../SOURCES.md#S160
[S162]: ../../SOURCES.md#S162
[S168]: ../../SOURCES.md#S168
[S170]: ../../SOURCES.md#S170
[S172]: ../../SOURCES.md#S172
[S173]: ../../SOURCES.md#S173
[S174]: ../../SOURCES.md#S174
[S175]: ../../SOURCES.md#S175
[S176]: ../../SOURCES.md#S176
[S177]: ../../SOURCES.md#S177
[S178]: ../../SOURCES.md#S178
[S179]: ../../SOURCES.md#S179
[S180]: ../../SOURCES.md#S180
[S181]: ../../SOURCES.md#S181
[S182]: ../../SOURCES.md#S182
[S183]: ../../SOURCES.md#S183
[S184]: ../../SOURCES.md#S184
[S185]: ../../SOURCES.md#S185
[S187]: ../../SOURCES.md#S187
[S188]: ../../SOURCES.md#S188
[S189]: ../../SOURCES.md#S189
[S190]: ../../SOURCES.md#S190
[S191]: ../../SOURCES.md#S191
[S192]: ../../SOURCES.md#S192
[S193]: ../../SOURCES.md#S193
[S194]: ../../SOURCES.md#S194
[S195]: ../../SOURCES.md#S195
[S196]: ../../SOURCES.md#S196
[S197]: ../../SOURCES.md#S197
[S198]: ../../SOURCES.md#S198
[S199]: ../../SOURCES.md#S199
[S200]: ../../SOURCES.md#S200
[S201]: ../../SOURCES.md#S201
[S202]: ../../SOURCES.md#S202
[S203]: ../../SOURCES.md#S203
[S204]: ../../SOURCES.md#S204
[S205]: ../../SOURCES.md#S205
[S206]: ../../SOURCES.md#S206
[S207]: ../../SOURCES.md#S207
[S208]: ../../SOURCES.md#S208
[S209]: ../../SOURCES.md#S209
[S210]: ../../SOURCES.md#S210
[S211]: ../../SOURCES.md#S211
[S212]: ../../SOURCES.md#S212
[S213]: ../../SOURCES.md#S213
[S214]: ../../SOURCES.md#S214
[S215]: ../../SOURCES.md#S215
[S216]: ../../SOURCES.md#S216
[S217]: ../../SOURCES.md#S217
[S218]: ../../SOURCES.md#S218
[S219]: ../../SOURCES.md#S219
[S220]: ../../SOURCES.md#S220
[S221]: ../../SOURCES.md#S221
[S222]: ../../SOURCES.md#S222
[S223]: ../../SOURCES.md#S223
[S224]: ../../SOURCES.md#S224
[S225]: ../../SOURCES.md#S225
[S226]: ../../SOURCES.md#S226
[S227]: ../../SOURCES.md#S227
[S228]: ../../SOURCES.md#S228
[S229]: ../../SOURCES.md#S229
[S230]: ../../SOURCES.md#S230
[S231]: ../../SOURCES.md#S231
[S232]: ../../SOURCES.md#S232
[S233]: ../../SOURCES.md#S233
[S234]: ../../SOURCES.md#S234
[S235]: ../../SOURCES.md#S235
[S236]: ../../SOURCES.md#S236
[S237]: ../../SOURCES.md#S237
[S238]: ../../SOURCES.md#S238
[S239]: ../../SOURCES.md#S239
[S240]: ../../SOURCES.md#S240
[S241]: ../../SOURCES.md#S241
[S242]: ../../SOURCES.md#S242
[S244]: ../../SOURCES.md#S244
[S246]: ../../SOURCES.md#S246
[S247]: ../../SOURCES.md#S247
[S248]: ../../SOURCES.md#S248
[S249]: ../../SOURCES.md#S249
[S250]: ../../SOURCES.md#S250
[S251]: ../../SOURCES.md#S251
[S252]: ../../SOURCES.md#S252
[S253]: ../../SOURCES.md#S253
[S254]: ../../SOURCES.md#S254
[S255]: ../../SOURCES.md#S255
[S256]: ../../SOURCES.md#S256
[S257]: ../../SOURCES.md#S257
[S258]: ../../SOURCES.md#S258
[S259]: ../../SOURCES.md#S259
[S260]: ../../SOURCES.md#S260
[S261]: ../../SOURCES.md#S261
[S262]: ../../SOURCES.md#S262
[S263]: ../../SOURCES.md#S263
[S264]: ../../SOURCES.md#S264
[S265]: ../../SOURCES.md#S265
[S266]: ../../SOURCES.md#S266
[S21]: ../../SOURCES.md#S21
[S31]: ../../SOURCES.md#S31
[S32]: ../../SOURCES.md#S32
[S33]: ../../SOURCES.md#S33
[S64]: ../../SOURCES.md#S64
[S276]: ../../SOURCES.md#S276
[S277]: ../../SOURCES.md#S277
[S278]: ../../SOURCES.md#S278
[S279]: ../../SOURCES.md#S279
[S280]: ../../SOURCES.md#S280
[S281]: ../../SOURCES.md#S281
[S282]: ../../SOURCES.md#S282
[S283]: ../../SOURCES.md#S283
[S284]: ../../SOURCES.md#S284
[S285]: ../../SOURCES.md#S285
[S286]: ../../SOURCES.md#S286
[S287]: ../../SOURCES.md#S287
[S288]: ../../SOURCES.md#S288
[S289]: ../../SOURCES.md#S289
[S290]: ../../SOURCES.md#S290
[S291]: ../../SOURCES.md#S291
[S292]: ../../SOURCES.md#S292
[S294]: ../../SOURCES.md#S294
[S295]: ../../SOURCES.md#S295
[S296]: ../../SOURCES.md#S296
[S298]: ../../SOURCES.md#S298
[S299]: ../../SOURCES.md#S299
[S301]: ../../SOURCES.md#S301
[S302]: ../../SOURCES.md#S302

[S321]: ../../SOURCES.md#S321
[S322]: ../../SOURCES.md#S322
[S323]: ../../SOURCES.md#S323
[S324]: ../../SOURCES.md#S324
[S325]: ../../SOURCES.md#S325
[S326]: ../../SOURCES.md#S326
[S327]: ../../SOURCES.md#S327
[S328]: ../../SOURCES.md#S328
[S329]: ../../SOURCES.md#S329
[S371]: ../../SOURCES.md#S371
[S372]: ../../SOURCES.md#S372
[S375]: ../../SOURCES.md#S375
[S377]: ../../SOURCES.md#S377
[S379]: ../../SOURCES.md#S379
[S381]: ../../SOURCES.md#S381
[S407]: ../../SOURCES.md#S407
[S408]: ../../SOURCES.md#S408
[S409]: ../../SOURCES.md#S409
[S410]: ../../SOURCES.md#S410
[S416]: ../../SOURCES.md#S416
[S419]: ../../SOURCES.md#S419
[S423]: ../../SOURCES.md#S423
[S425]: ../../SOURCES.md#S425
[S426]: ../../SOURCES.md#S426
[S427]: ../../SOURCES.md#S427
[S430]: ../../SOURCES.md#S430
[S432]: ../../SOURCES.md#S432
[S433]: ../../SOURCES.md#S433
