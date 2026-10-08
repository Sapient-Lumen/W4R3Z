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

A proposal fails if ordinary people, small firms, or reviewed subjects cannot reconstruct the claim against them without expert decoding or proprietary model access.

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

### 5. Data minimization is part of equality, not only privacy

The state should not collect every possible datum merely because analytics make it tempting. Excessive data hunger raises exclusion, error, and proxy-discrimination risks while shifting power toward large actors who can navigate the machinery best.[S16][S17][S27][S44]

### 6. Controller-first AI taxation needs stronger administrative disclosure, not weaker

Because present AI taxation runs through controller chains rather than direct model personhood, the administrative burden falls on labs, clouds, deployers, and major beneficiaries to disclose enough about compute, energy, siting, proxy methods, and affiliate structure for the levy to be audited. Complexity is not a moral exemption.[S10][S15][S16][S17][S20][S44]

## Five anti-patterns

1. **Black-box extraction** — money is demanded because an unseen score, vendor model, or opaque cross-match says so.
2. **Appeal by fiction** — review exists on paper but is too slow, costly, digital-only, or authority-starved to matter.
3. **Proxy laundering** — valuation estimates, fraud scores, household defaults, or locality codes quietly substitute for the real moral variable.
4. **Version opacity** — taxpayers cannot tell which rule set, update, or threshold schedule actually governed the claim.
5. **Complexity as privilege** — the system is technically machine-legible yet effectively only navigable by large firms, repeat players, or expert intermediaries.[S16][S17][S23][S25][S27][S44]

## Order of preference

When two designs pursue the same revenue or corrective goal, the archive usually prefers the one that:

1. can be explained in plain language and machine-readable form at the same time,
2. uses observable data before disputed proxies,
3. provides correction before coercive escalation,
4. gives model-assisted tools only bounded and reviewable roles,
5. and keeps data collection narrower than the maximal analytic appetite of the administration.

This is why administrative legibility belongs in the narrow waist rather than living only in archive note `112`.

## Use this note with

- [`measurement-valuation-and-proxy-routing.md`](measurement-valuation-and-proxy-routing.md)
- [`collection-and-remittance-routing.md`](collection-and-remittance-routing.md)
- [`enforcement-proportionality-and-recovery-routing.md`](enforcement-proportionality-and-recovery-routing.md)
- [`standing-representation-and-remedy-routing.md`](standing-representation-and-remedy-routing.md)
- [`anti-discrimination-and-status-proxy-routing.md`](anti-discrimination-and-status-proxy-routing.md)
- [`../20-calibration/data-minimization-credential-reuse-and-sensitive-attribute-firewall-ladder.md`](../20-calibration/data-minimization-credential-reuse-and-sensitive-attribute-firewall-ladder.md)
- [`../../archive/112-administration-visibility-appeals-and-machine-legibility.md`](../../archive/112-administration-visibility-appeals-and-machine-legibility.md)

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

For post-waist calibration on when taxes may stay low-salience, when line-item or annual-summary disclosure is required, and when tax-side support must become budget-visible to count as honest administration, start from [`../20-calibration/burden-salience-disclosure-and-hidden-tax-ladder.md`](../20-calibration/burden-salience-disclosure-and-hidden-tax-ladder.md).
For post-waist calibration on when ordinary filing may stay self-service, when prefilling or public assistance should replace private gatekeepers, and when an apparently legal rule still fails because it effectively requires paid preparers or proprietary software to comply safely, start from [`../20-calibration/compliance-cost-assisted-filing-and-preparer-dependence-ladder.md`](../20-calibration/compliance-cost-assisted-filing-and-preparer-dependence-ladder.md).
