# Data minimization and purpose-bounded verification routing

This note answers the question that comes **after** a tax, credit, rebate, or controller-side duty looks morally targeted but **before** its proof path can count as legitimate: **is the system asking for more data, retention, or matching than the rule's moral object actually requires?** The archive's stable answer is to collect the **narrowest workable claim**, reuse facts already proved elsewhere where possible, escalate to cross-system matching only for named high-stakes purposes, and block designs that need routine raw sensitive data or open-ended retention to function at all.[S1][S16][S17][S23][S27][S39][S40][S41][S44][S89][S91][S92]

A tax can be progressive in rates and still unjust in proof architecture. Repeated document harvest, full-attribute defaulting, and quiet administrative data-lake growth are not neutral implementation details; they change who can comply, who is excluded, and how much domination the state or a platform can exercise through tax administration.[S23][S27][S39][S40][S41][S44][S89][S91][S92]

## Default lanes

| Situation | Default proof path | Why this path usually wins | Main warning |
|---|---|---|---|
| Ordinary low-value credits, filing distinctions, routine rebates, or recurring support renewals | self-attestation, sampled audit, or simple threshold confirmation | routine universal document harvest often costs more than the moral value of proving every case up front | do not suppress lawful take-up by turning small recurring claims into a document maze.[S27][S64][S65][S66][S91] |
| Rules that really need only a band, threshold, or yes/no condition | binary or banded claim rather than full raw attributes | many tax and transfer rules do not need the whole dossier to answer the operative question | do not ask for full birth dates, diagnoses, or detailed histories when a narrow banded answer would do.[S91][S92] |
| Facts already verified elsewhere inside government or through a trusted provider | reusable credential, event confirmation, or narrow assertion | one-time proof plus narrow reuse reduces burden, storage, and repeat exposure | reusable credentials still need logging, revocation, and correction so convenience does not harden into lock-in.[S89][S91][S92] |
| High-value, fraud-sensitive, or cross-system inconsistency review | purpose-bounded matching with field minimization, logging, and time limits | higher stakes can justify more searching verification than routine claims can | do not let targeted matching turn into a standing administrative data lake.[S39][S40][S41][S44][S89][S91][S92] |
| Controller-side AI, platform, or large-firm obligations | structured event records and narrow operational assertions tied to the liability | large actors can bear richer reporting, but the state still needs only the fields relevant to control, base, threshold, or harm | technical visibility into the stack is not permission to ingest every raw trace indefinitely.[S10][S15][S16][S17][S39][S40][S41][S44][S89] |

## Routing rules

### 1. Ask for the smallest morally sufficient fact

Proof architecture should follow the moral object of the rule. If the rule turns on a threshold, status, timing event, or narrow measured base, the state should usually ask for that fact or band directly rather than the full surrounding file.[S1][S23][S27][S91][S92]

### 2. Reuse once-proved facts before recollecting raw documents

If identity, residence, payroll receipt, controller role, or similar facts have already been verified, later tax and relief channels should usually consume a narrow credential, event record, or signed assertion instead of recollecting the underlying documents from scratch.[S27][S39][S44][S89][S92]

### 3. Treat sensitive attributes as firewall material, not default inputs

Disability detail, migration history, nationality, family-status detail, biometrics, and similar intimate or protected-status-adjacent data require extra justification. Where a narrower proxy, threshold confirmation, or credential can do the work, the richer attribute should stay out of routine tax processing.[S17][S23][S40][S44][S74][S91][S92]

### 4. Escalate to matching only when stakes justify it and the purpose stays bounded

Cross-system matching can be morally justified where the public stakes are high, fraud patterns are serious, or the amount at issue is large enough to justify more invasive verification. But the archive treats matching as an escalated lane, not a default: it should be field-minimized, logged, time-limited, correctable, and tied to a named tax purpose.[S39][S40][S41][S44][S89][S91][S92]

Identity-compromise recovery is one of the places where richer proofing can be justified, but only for the recovery purpose. Affidavits, IP PINs, account locks, fraud flags, and cross-checks should resolve the unauthorized filing or account-capture problem without turning victim recovery into broad sensitive-data harvesting, permanent risk scoring, or a paid identity-broker market.[S40][S65][S68][S148][S149][S150][S151][S153]

Household-status correction may also justify some relationship facts, but only at the field level needed for spouse relief, injured-spouse allocation, dependency correction, custody / support treatment, or separated-household status. Do not turn a narrow allocation question into broad intimate-history collection, ongoing household surveillance, or proof demands that expose the lower-power person to the very household actor being contested.[S31][S32][S33][S40][S42][S65][S161][S162][S164][S165][S166][S167]

### 5. Redesign or block rules that need excess collection to function

If a proposal only works by demanding raw sensitive data, repeated proofing, broad scraping, or indefinite retention materially wider than the tax or relief purpose, the archive treats that as a design failure. The right response is usually redesign, narrower proxies, or a different instrument, not a privacy footnote.[S16][S17][S39][S40][S41][S44][S89][S91][S92]

## Five anti-patterns

1. **Show-me-everything administration** — full files are demanded because systems can store them, not because the rule morally needs them.  
2. **Same-proof-again syndrome** — people and small firms must re-prove the same fact across filing, correction, and relief lanes.  
3. **Sensitive-attribute defaulting** — intimate or protected-status-adjacent data becomes routine when a threshold claim or credential would do.  
4. **Silent matching creep** — targeted verification quietly becomes broad ongoing matching and retention.  
5. **Raw-trace exceptionalism for AI** — because controller-side systems emit abundant telemetry, the administration assumes it may ingest the whole stack.[S16][S17][S39][S40][S41][S44][S89][S91][S92]
6. **Fraud-proofing creep** — identity-theft recovery or protective credentialing becomes a standing excuse for broad sensitive-data collection, permanent fraud scoring, or paid identity-broker dependence.[S40][S65][S68][S148][S149][S150][S151][S153]
7. **Household-intimacy overproofing** — spouse relief, dependency, or separated-household correction demands more relationship history, custody detail, or private conflict evidence than the bounded tax allocation requires.[S161][S162][S164][S165][S166][S167]

### 5.5 Summons and third-party contacts do not defeat minimization

Administrative summons, third-party contact, third-party summons, and John Doe tools belong on the same minimization ladder as ordinary proof. A legally available information power still needs a named tax purpose, issue scope, notice posture, quash or review route where available, privilege handling, and deletion or non-use of nonresponsive records. The existence of bank files, platform logs, source code, prompt traces, payroll systems, or advisor workpapers is not itself a reason to ingest the full record universe.[S339][S340][S343][S344][S345][S346][S348][S349][S350]

8. **Summons minimization failure** — compulsory record power is used to bypass the ordinary small-fact, narrow-credential, or targeted-cross-check path.[S339][S340][S343][S345][S346][S348][S349]

## Compression rule

If a proposal mainly fails because **it asks for too much data**, **re-proves what is already known**, or **defaults to sensitive attributes where narrow claims would do**, route through this card and the relevant administration or filing-parity note rather than writing a new sector-specific doctrine.

## Use with

- [`administration-explanation-and-appeal-routing.md`](administration-explanation-and-appeal-routing.md)
- [`compliance-burden-and-filing-parity-routing.md`](compliance-burden-and-filing-parity-routing.md)
- [`collection-and-remittance-routing.md`](collection-and-remittance-routing.md)
- [`automaticity-and-claim-friction-routing.md`](automaticity-and-claim-friction-routing.md)
- [`../20-calibration/data-minimization-credential-reuse-and-sensitive-attribute-firewall-ladder.md`](../20-calibration/data-minimization-credential-reuse-and-sensitive-attribute-firewall-ladder.md)
- [`../../archive/171-tax-identity-compromise-unauthorized-filing-and-account-recovery-should-not-be-turned-into-victim-rents-or-impersonation-traps.md`](../../archive/171-tax-identity-compromise-unauthorized-filing-and-account-recovery-should-not-be-turned-into-victim-rents-or-impersonation-traps.md)
- [`../../archive/173-joint-return-spouse-debt-dependent-claim-and-household-status-records-should-not-be-turned-into-captive-household-rents-or-relational-liability-traps.md`](../../archive/173-joint-return-spouse-debt-dependent-claim-and-household-status-records-should-not-be-turned-into-captive-household-rents-or-relational-liability-traps.md)

- [`../../archive/194-summons-third-party-contact-john-doe-record-demands-and-privilege-claims-should-not-be-turned-into-surveillance-rents-or-notice-bypass-traps.md`](../../archive/194-summons-third-party-contact-john-doe-record-demands-and-privilege-claims-should-not-be-turned-into-surveillance-rents-or-notice-bypass-traps.md)


## Rev0270 criminal-tax boundary addendum

Fraud suspicion narrows the purpose; it does not authorize total data appetite. Even in fraud development or CI-adjacent work, the state should collect records tied to the affirmative-act theory, relevant periods, suspected actors, and proof method. Digital assets, platform telemetry, AI logs, source-code traces, payroll exports, and workpapers can be evidence, but the existence of rich machine records is not a license for full-account ingestion or indefinite retention.[S354][S355][S358]

The minimization rule is symmetric: use data to distinguish willful concealment from complexity, nonwillful mistake, preparer misconduct, payroll-agent failure, or administrative error, not to presume criminal intent from technological form.[S354][S358]


### 5.6 Whistleblower channels require two-sided minimization

Whistleblower identity and taxpayer return information are both protected. A claim file should collect enough source information to test specificity, credibility, and lawful use, but any disclosure back to the whistleblower, representative, contractor, or third party must be legally authorized, necessary, narrow, safeguarded, and tied to a recorded tax-administration purpose.[S366][S369][S377][S378][S380][S381][S382]

9. **Whistleblower disclosure creep** — an informant file becomes a standing excuse to circulate taxpayer return information, source identity, family conflict, worker conflict, platform records, or competitor narratives beyond what the live tax issue needs.[S377][S379][S380]

Add [`../../archive/196-whistleblower-informant-return-information-disclosure-and-award-claims-should-not-be-turned-into-bounty-rents-or-accusation-traps.md`](../../archive/196-whistleblower-informant-return-information-disclosure-and-award-claims-should-not-be-turned-into-bounty-rents-or-accusation-traps.md) to any source-triggered data request or disclosure decision.

### Foreign-account data minimization and FATCA / FBAR purpose limits

Foreign account and asset data can be highly sensitive: it may reveal migration history, family support, political risk, local-life banking, employer authority, inheritance, trust relationships, or business structure. FATCA, FBAR, and international information-return data should therefore be used for tax and BSA purposes with issue-bounded retention, access logging, and explanation of which asset, account, entity, or trust fact matters. A foreign account report is not a general warrant to profile a household's cross-border life.[S410][S411][S413][S416][S417][S418]

When matching systems detect foreign assets, the first output should be a discrepancy explanation and correction route, not a risk label that silently intensifies all enforcement. Use the offshore ladder to convert third-party or foreign-reporting data into named issues, not standing surveillance.[S407][S428][S429][S430][S432]

[S354]: ../../SOURCES.md#S354
[S355]: ../../SOURCES.md#S355
[S358]: ../../SOURCES.md#S358

[S1]: ../../SOURCES.md#S1
[S10]: ../../SOURCES.md#S10
[S15]: ../../SOURCES.md#S15
[S16]: ../../SOURCES.md#S16
[S17]: ../../SOURCES.md#S17
[S23]: ../../SOURCES.md#S23
[S27]: ../../SOURCES.md#S27
[S39]: ../../SOURCES.md#S39
[S40]: ../../SOURCES.md#S40
[S41]: ../../SOURCES.md#S41
[S44]: ../../SOURCES.md#S44
[S64]: ../../SOURCES.md#S64
[S65]: ../../SOURCES.md#S65
[S66]: ../../SOURCES.md#S66
[S74]: ../../SOURCES.md#S74
[S89]: ../../SOURCES.md#S89
[S91]: ../../SOURCES.md#S91
[S92]: ../../SOURCES.md#S92
[S148]: ../../SOURCES.md#S148
[S149]: ../../SOURCES.md#S149
[S150]: ../../SOURCES.md#S150
[S151]: ../../SOURCES.md#S151
[S153]: ../../SOURCES.md#S153
[S68]: ../../SOURCES.md#S68
[S31]: ../../SOURCES.md#S31
[S32]: ../../SOURCES.md#S32
[S33]: ../../SOURCES.md#S33
[S42]: ../../SOURCES.md#S42
[S161]: ../../SOURCES.md#S161
[S162]: ../../SOURCES.md#S162
[S164]: ../../SOURCES.md#S164
[S165]: ../../SOURCES.md#S165
[S166]: ../../SOURCES.md#S166
[S167]: ../../SOURCES.md#S167
[S339]: ../../SOURCES.md#S339
[S340]: ../../SOURCES.md#S340
[S343]: ../../SOURCES.md#S343
[S344]: ../../SOURCES.md#S344
[S345]: ../../SOURCES.md#S345
[S346]: ../../SOURCES.md#S346
[S348]: ../../SOURCES.md#S348
[S349]: ../../SOURCES.md#S349
[S350]: ../../SOURCES.md#S350
[S366]: ../../SOURCES.md#S366
[S369]: ../../SOURCES.md#S369
[S377]: ../../SOURCES.md#S377
[S378]: ../../SOURCES.md#S378
[S379]: ../../SOURCES.md#S379
[S380]: ../../SOURCES.md#S380
[S381]: ../../SOURCES.md#S381
[S382]: ../../SOURCES.md#S382
[S407]: ../../SOURCES.md#S407
[S410]: ../../SOURCES.md#S410
[S411]: ../../SOURCES.md#S411
[S413]: ../../SOURCES.md#S413
[S416]: ../../SOURCES.md#S416
[S417]: ../../SOURCES.md#S417
[S418]: ../../SOURCES.md#S418
[S428]: ../../SOURCES.md#S428
[S429]: ../../SOURCES.md#S429
[S430]: ../../SOURCES.md#S430
[S432]: ../../SOURCES.md#S432
