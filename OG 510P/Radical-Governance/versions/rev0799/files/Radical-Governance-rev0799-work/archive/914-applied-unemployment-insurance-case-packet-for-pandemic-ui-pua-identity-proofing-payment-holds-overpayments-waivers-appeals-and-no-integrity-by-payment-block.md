# 914 — Applied unemployment-insurance case packet for pandemic UI, PUA, identity proofing, payment holds, overpayments, waivers, appeals, and no integrity by payment block

## One-line thesis

Pandemic UI and PUA form a federal-state benefit-integrity and claimant-access waist: identity proofing, eligibility, fraud flags, payment holds, overpayments, waivers, appeals, recovery, and modernization must be separated before blocked payment is treated as integrity or paid benefit as success.

## Why this matters

This applied packet repairs `GAP-002`. The pandemic UI system was too large and too urgent to be reduced to either “fraud crisis” or “access failure.” It was both. Emergency programs expanded eligibility and dollars while state systems, identity checks, employer interfaces, call centers, old technology, payment rails, and appeal routes were overloaded. That combination made fraud control indispensable and claimant access fragile.

The case is useful because it prevents the archive from making two opposite mistakes. The first mistake is to excuse weak controls because claimants needed money quickly. The second is to let fraud panic normalize unexplained holds, inaccessible identity proofing, payment silence, recovery demands, or debt labels that valid claimants cannot contest. A serious case packet must keep fraud prevention, prompt payment, identity repair, overpayment classification, waiver, and appeal in the same frame.

The applied holding is: **no integrity by payment block**. A blocked payment can be necessary, but it is not proof of integrity unless the system records the signal, reason, unresolved fact, claimant notice, cure path, appeal right, resulting overpayment or waiver state, and eventual outcome.

## Pattern pack

### 1. Dispatcher result

| Field | Holding |
| --- | --- |
| trigger | claim surge, emergency eligibility expansion, identity proofing, suspicious claim signal, payment hold, overpayment notice, waiver request, appeal, recovery, or modernization claim |
| first-form question | whether the case is ordinary benefit administration, payment redress, credential access, entitlement continuity, model decision, supplier dependency, or UI integrity / claimant-access waist |
| lower-form test | ordinary claims processing is too thin where federal emergency rules, state implementation, identity proofing, fraud controls, payment holds, overpayment recovery, waiver, appeal, and system capacity interact |
| heavier-form test | a single federal UI authority is too thick because state law, employer accounts, state appeal systems, local operations, federal funding, federal oversight, vendors, and payment rails remain distinct |
| form verdict | federal-state benefit-integrity and claimant-access waist with fraud / access / overpayment state separation |

### 2. Boundary map

| Component | Boundary rule |
| --- | --- |
| federal emergency program | defines funding, program rules, guidance, reporting, oversight, and minimum control expectations; it is not the whole claimant record |
| state workforce agency | owns claims administration, notices, adjudication, payment, appeal routing, and many system choices under state law |
| identity provider | verifies or fails to verify identity; it does not decide UI entitlement |
| fraud-control system | flags, holds, refers, or clears suspicious facts; it does not replace notice and appeal |
| payment processor | issues, reverses, offsets, or delays payment; it is not a merits adjudicator |
| employer interface | supplies separation and wage facts; employer silence or delay should be a visible state |
| appeals body | corrects fact, law, notice, and process errors; appeal outcomes are delivery metrics |
| recovery function | collects final debts subject to waiver and legal limits; collection is not repair by itself |
| modernization program | supplies standards, pilots, code, grants, and practices; it is not state performance evidence until measured |

### 3. Evidence-grade table

| Evidence | Governance meaning |
| --- | --- |
| GAO pandemic UI fraud estimate | establishes high-stakes fraud magnitude, uncertainty, DOL disagreement, and need for control evidence |
| DOL OIG UI oversight page | grounds the persistent improper-payment, PUA, investigative, and claim-surge risk diagnosis |
| GAO PUA fraud-control report | anchors why PUA controls and emergency eligibility created particular fraud exposure |
| GAO UI IT modernization report | shows state legacy systems, contractor reliance, performance-measure gaps, and modernization oversight risk |
| GAO overpayment recovery report | separates overpayment, waiver, recovery, outstanding debt, recovery-rate calculation, and identity-theft recovery difficulty |
| DOL UIPL identity guidance | anchors shared ID verification, Login.gov / USPS routes, non-digital option requirements, due-process duties, and implementation clocks |
| DOL UI modernization materials | source for ARPA modernization, claim-status playbooks, open UI, sample application code, CX, plain-language, and new-tech work |
| DOL UI transformation plan and TEN customer-experience checklist | implementation scaffolding to be tested against state performance, not treated as proof of repair |
| GAO PUA racial-disparity recommendation | reminder that emergency benefit receipt and access must be examined across claimant groups, not only totals |

### 4. Live chain notes

Use `848`, `860`, `861`, `913`, and this packet first. For this case, live fields are:

- `813` for federal / state authority, emergency-program terms, DOL guidance, state law, appeal bodies, and claimant-right boundaries;
- `814` for UI trust funds, federal emergency appropriations, overpayments, waivers, recovery, payment rails, and fiscal exposure;
- `815` for claim intake, weekly certification, adjudication queues, call centers, identity proofing, payment release, employer interfaces, document upload, and recovery operations;
- `816` for DOL oversight, DOL OIG, GAO, state auditors, legislative oversight, performance standards, and public metrics;
- `817` for claimants, workers with unstable records, PUA contingent workers, identity-theft victims, people without digital credentials, limited-English claimants, people with disabilities, employers, state staff, and taxpayers;
- `818` for notices, reason codes, status maps, proof requirements, appeal packets, overpayment categories, waiver decisions, and source hierarchy;
- `819` for state workforce agencies, DOL, OIG, GAO, GSA / Login.gov, USPS, identity vendors, payment vendors, employers, courts, and legal aid;
- `820` for temporary emergency programs, ARPA modernization, new identity guidance, pilots, standards, and later supersession;
- `821` for administrative appeals, redeterminations, waiver requests, identity-theft remediation, fraud-victim reporting, and payment release after cure;
- `823` for Login.gov, state portals, payment processors, data matches, call-center platforms, fraud analytics, cloud / contractor dependencies, and open-source components;
- `824` for fraud detection, improper-payment controls, overpayment recovery, criminal referral, employer fraud, identity theft, and data-sharing with OIG.

Reserve `822` for physical asset transitions not central to UI claim, proof, payment, or recovery governance.

### 5. Unemployment-insurance tests activated

This packet activates the `UNEMPLOYMENT_INSURANCE_TESTS` matrix:

1. claim-state split;
2. identity-proofing route preservation;
3. payment-hold reason and cure clock;
4. fraud-signal evidence and false-positive telemetry;
5. employer / separation issue routing;
6. overpayment classification and waiver;
7. appeal, redetermination, and retroactive-payment receipt;
8. identity-theft victim remediation;
9. state IT performance and modernization evidence;
10. public metrics that report both payment integrity and claimant-access harm.

### 6. Rival readings

**Rival 1: Fraud was so large that access criticism is secondary.** Fraud was large and control failures were severe. The packet does not deny that. It says fraud control must be legible enough to distinguish genuine fraud from unresolved identity, agency error, employer delay, and valid claims blocked by control systems.

**Rival 2: Claimant access was so urgent that controls caused the real harm.** Access harm was real, but uncontrolled payment also harms the program, taxpayers, employers, and future claimants. The repair is not weaker control. It is state-specific, appealable, measured control.

**Rival 3: Modernization work has already fixed the problem.** Modernization artifacts are promising, but the archive treats grants, playbooks, pilots, prototypes, standards, and open-source components as scaffolding until state performance and claimant outcomes are measured.

**Rival 4: State variation makes a common matrix unrealistic.** State law matters, but the matrix does not demand identical state law. It demands comparable minimum state evidence: why a claim is held, how it can be cured, what appeal exists, what payment happened, and how integrity / access harms are measured.


## Rev0786 affected-person pilot status

Rev0786 does not treat this official-source packet as complete claimant proof. It adds note `984`, `UI-11`, and `UI-12` because a DOL playbook, modernization report, claim-status tool, fraud metric, waiver route, or overpayment statistic is not yet evidence that a valid claimant received money or a completed remedy.

The next claimant sample must preserve at least one held-claim path from issue state through notice, burden, assisted or non-digital channel, cure evidence, appeal or waiver if needed, certification restoration, payment after cure, and remaining harm. It must also record who fell out before the formal claim or survey surface. Until that exists, this packet remains an official-source and operational-test packet, not field validation.

## Findings table

| Risk | Bad shortcut | Repair |
| --- | --- | --- |
| claim surge | rely on queue status | claim-state map and payment-clock ledger |
| PUA expansion | rely on self-certification or blanket suspicion | evidence ladder by program rule and risk class |
| identity proof | route everyone through one digital gate | digital, in-person, non-digital, assisted, disability, language, and representative paths |
| fraud analytics | invisible payment block | signal, reason, confidence, cure, notice, appeal, and outcome |
| overpayment recovery | collect by debt label | fraud / nonfraud / waiver / appeal / identity-theft state split |
| modernization | count grants and pilots | state performance, claimant task completion, error, delay, and appeal metrics |
| public reporting | improper-payment rate only | paired integrity and access dashboard |
| case closure | paid / denied / recovered totals | eventual claimant and program-state receipt |

## Failure modes

- **Payment-block theater**: a held payment is scored as fraud prevention without knowing whether the claimant was valid.
- **Improper-payment monism**: improper-payment rates dominate while timeliness, false-positive, waiver, and appeal facts disappear.
- **Claim-status fog**: claimants see “pending” while the agency holds identity, separation, monetary, certification, fraud, or payment reasons internally.
- **Identity-provider substitution**: a shared provider's verification result silently becomes the public entitlement gate.
- **Non-digital route fiction**: an in-person proofing option that still requires online setup is counted as the whole assisted route.
- **Overpayment debt flattening**: fraudulent, nonfraudulent, waivable, agency-caused, identity-theft, and appeal-pending debts are merged.
- **Modernization halo**: ARPA funding, open UI, CX playbooks, or AI adjudicator prototypes are treated as repair without state performance evidence.
- **Equity averaging**: program totals hide differential burden for PUA workers, identity-theft victims, people without stable documents, limited-English claimants, disabled claimants, and people with weak internet access.

## Anti-theater tests

1. Pick any held claim. Can the record identify the specific unresolved issue, trigger, evidence reviewed, missing proof, claimant notice, cure path, and appeal route?
2. Pick any identity-failed claimant. Can they use an assisted and non-digital route that preserves the claim date, certification ability, and payment if eligible?
3. Pick any fraud metric. Is there paired evidence of false positives, valid-claimant delays, reversals, and eventual payments?
4. Pick any overpayment total. Can fraudulent, nonfraudulent, waived, appealed, recovered, outstanding, and identity-theft amounts be separated?
5. Pick any modernization claim. Does it include state performance against standards, not only funding, implementation, or prototype status?
6. Pick any public dashboard. Does it let users see timeliness, hold reasons, appeal outcomes, waivers, identity problems, access channels, and claimant-group burden?
7. Pick any employer separation dispute. Does employer nonresponse or delay show as a state, with claimant notice and payment consequences?
8. Pick any recovery effort. Does it distinguish collecting money from correcting the underlying control, notice, waiver, and access failure?
