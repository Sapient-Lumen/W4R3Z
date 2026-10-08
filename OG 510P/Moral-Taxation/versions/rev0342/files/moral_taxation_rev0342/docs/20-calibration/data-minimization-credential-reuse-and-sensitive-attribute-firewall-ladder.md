# Data minimization, credential reuse, and sensitive-attribute firewall ladder

## Question in one sentence

Which five-rung evidence ladder should govern tax administration so the state uses self-attestation, banded claims, reusable credentials, bounded matching, or redesign/blocking in proportion to what the rule morally needs rather than defaulting to raw-document harvest or general surveillance?[S1][S16][S17][S23][S27][S39][S40][S41][S44][S89][S91][S92]

## Closed rules invoked

Routes: [`../10-framework/administration-explanation-and-appeal-routing.md`](../10-framework/administration-explanation-and-appeal-routing.md), [`../10-framework/enforcement-proportionality-and-recovery-routing.md`](../10-framework/enforcement-proportionality-and-recovery-routing.md), [`../10-framework/automaticity-and-claim-friction-routing.md`](../10-framework/automaticity-and-claim-friction-routing.md), [`../10-framework/anti-discrimination-and-status-proxy-routing.md`](../10-framework/anti-discrimination-and-status-proxy-routing.md), [`../10-framework/standing-representation-and-remedy-routing.md`](../10-framework/standing-representation-and-remedy-routing.md), and [`../10-framework/collection-and-remittance-routing.md`](../10-framework/collection-and-remittance-routing.md).

Closed rule: collect, retain, and share only what the rule actually needs; keep notice and challenge usable; do not let administrative appetite for more data replace privacy, equality, and reviewability.[S1][S16][S17][S23][S27][S39][S40][S41][S44][S89][S91][S92]

## Why calibration is still needed

A usable ladder still has to avoid six recurring failures:

1. **document-harvest default**, where low- or medium-stakes taxes and supports demand full documents, repeated uploads, or in-person proof when narrower claims would do,[S64][S65][S66][S91][S92]
2. **sensitive-attribute spill**, where the system asks for full birth dates, national identifiers, biometrics, household maps, or disability details when the real question is only a threshold or yes/no status,[S74][S91][S92]
3. **repeat-proofing friction**, where the same person has to prove the same fact again and again because agencies refuse reusable credentials, event confirmations, or shared attestations with revocation and logging,[S64][S65][S66][S89][S92]
4. **cross-system mission creep**, where tax administration slowly becomes a general surveillance mesh because every potentially useful data source is treated as fair game for matching and retention,[S39][S40][S41][S44][S89][S91]
5. **proxy discrimination through data hunger**, where extra collection expands the chance that protected-status proxies, documentation gaps, or skewed source data distort outcomes,[S17][S44][S74]
6. **large-actor privilege**, where only big firms, platforms, or professionally advised households can survive the documentation and systems burden that the tax now assumes.[S23][S27][S89]

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — raw-document default | Ask for full records, identifiers, and original documents whenever a claim, liability, or relief item matters materially, even when the rule really turns only on a threshold or categorical condition.[S91][S92] | Reject: overshoots moral need, raises exclusion and breach risk, and hands administrators more power than the base can justify. |
| B — siloed repeated proofing | Limit what each program stores, but force people and firms to re-prove the same status to each office, platform, or relief channel because reusable credentials or event feeds are not trusted.[S64][S65][S66][S89][S92] | Reject: lowers some concentration but recreates burden, friction, and unequal access. |
| C — minimization and credential-reuse ladder | Use a five-rung ladder that starts with self-attestation and narrow claims, reuses proved facts where possible, allows bounded matching where justified, and blocks designs that only work through excess collection.[S1][S16][S17][S23][S27][S39][S40][S41][S44][S89][S91][S92] | Adopt. |
| D — integrated administrative data-lake default | Make broad cross-government or public-private integration the baseline, with minimization and challenge handled later through internal governance rather than narrow collection design.[S39][S40][S41][S89][S44] | Reject: some integration is necessary, but technical visibility is not moral permission for pervasive matching or retention. |

## Five-rung ladder

1. **self-attestation plus sampled audit lane** where stakes are modest, reversibility is high, and fraud risk does not justify routine document harvest,[S64][S65][S66][S91]
2. **binary or banded claim lane** where the rule only needs a threshold answer — for example yes/no, above/below, resident/non-resident, dependent/not dependent, small/large, over/under — rather than full raw attributes,[S91][S92]
3. **reusable credential or event-confirmation lane** where identity or status has already been validated once, so later tax and transfer decisions should consume a narrow assertion, token, or structured event rather than recollecting the underlying documents,[S89][S92]
4. **purpose-bounded cross-system match lane** where higher stakes, high fraud risk, or major public loss justify controlled matching, but only with field minimization, logging, time limits, revocation or correction paths, and governance strong enough to keep the match tied to the tax purpose,[S39][S40][S41][S89][S44][S91][S92]
5. **redesign-or-block lane** where the proposal still depends on full sensitive attributes, broad ongoing scraping, open-ended retention, or protected-status data flows that are materially wider than the rule's moral object.[S17][S39][S40][S41][S44][S74][S91]

## Provisional recommendation

Adopt **Option C — the minimization and credential-reuse ladder** as the archive's default calibration for live data-hunger disputes.[S1][S16][S17][S23][S27][S39][S40][S41][S44][S89][S91][S92]

Presumption:

- use **self-attestation plus sampled audit** where claims are reversible, amounts are modest, and routine proofing would mainly suppress compliance or take-up,
- move to **binary or banded claims** when the rule really needs only a threshold answer,
- prefer **reusable credentials or event confirmations** when a fact has already been proved once and can be reused through a narrow assertion,
- escalate to **purpose-bounded matching** only when stakes or fraud patterns justify it and field minimization, logging, retention limits, notice, and correction are all in place,
- and move to **redesign or block** whenever the proposal depends on raw sensitive data, repeated proofing, or broad matching materially wider than the tax or relief purpose itself.

For controller-side AI taxes, this still means structured disclosure about compute, siting, energy, affiliates, or beneficiary chains should usually arrive as narrow assertions or event records rather than open-ended ingestion of every operational trace. “The stack can be measured” is not the same as “the state may keep the whole stack.”[S10][S15][S16][S17][S23][S39][S40][S41][S44][S89]

## Default verification table

| Context | Default rung | Why this rung usually fits | Archive warning |
|---|---|---|---|
| ordinary low-value credits, rebate confirmations, or recurring support renewals | self-attestation plus sampled audit | routine proofing costs can exceed the moral value of universal document harvest.[S64][S65][S66][S91] | do not let anti-fraud rhetoric justify suppressing lawful take-up through paperwork. |
| threshold-based eligibility or filing distinctions | binary or banded claim | many rules only need a yes/no or above/below answer, not the full raw record.[S91][S92] | do not ask for full birth dates, detailed diagnoses, or full income histories when the rule only needs a banded result. |
| identity or status already verified elsewhere inside government or through a trusted provider | reusable credential or event-confirmation | one-time proof plus narrow re-use can reduce burden, storage, and repeat exposure.[S89][S92] | reusable credentials still need revocation, correction, and logging so convenience does not become lock-in. |
| high-value fraud-sensitive claims, major refunds, or cross-system inconsistency review | purpose-bounded cross-system match | higher stakes can justify controlled verification beyond self-attestation.[S39][S40][S41][S89][S44][S91][S92] | matching must stay field-minimized, logged, time-limited, and tied to a named purpose rather than becoming a standing data lake. |
| disability, migration, family-status, nationality, or other protected-status-adjacent contexts | binary claim or reusable credential first; redesign if full sensitive data is treated as routine | protected-status-adjacent data creates unusually high discrimination and privacy risk.[S17][S44][S74][S91][S92] | do not let status proof become a proxy pipeline for unrelated scoring, enforcement, or exclusion. |
| controller-side AI, platform, or large-firm regimes | purpose-bounded structured reporting, often via narrow assertions or event records | large actors can bear structured reporting, but the rule should still collect only what the liability or threshold actually needs.[S10][S15][S16][S17][S23][S89][S44] | controller sophistication is not a license for indefinite retention of every raw trace the administration can technically ingest. |

## Summons and third-party-contact overlay

Compulsory information-gathering sits at the high end of the minimization ladder, not outside it. A summons packet should record the tax purpose, issue, record category, notice posture, quash route, privilege handling, reimbursement path, and nonresponsive-record minimization before the state moves from targeted cross-checking to compelled production.[S339][S340][S343][S345][S346][S347][S348][S349][S350]

Route remaining information-power settings through [`summons-third-party-contact-john-doe-and-privilege-ladder.md`](summons-third-party-contact-john-doe-and-privilege-ladder.md).

## Failure-mode capsule

Axes: `data_or_confidentiality_overreach`, `access_exclusion`, `sensitive_attribute_reuse`. Block credential reuse that turns benefit access into surveillance, exclusion, or sensitive-attribute leakage.

## Recalibration trigger capsule

Triggers: `access_or_fallback_failure`, `privacy_or_confidentiality_breach`, `record_or_measurement_staleness`. Reopen on privacy incidents, data-field creep, credential outage, or inaccessible low-data fallback.

## Accountability capsule
Authoritative assignment: route `data_minimization_credential_reuse_and_sensitive_attribute_firewall` in [`actor-accountability-profiles.json`](../00-meta/actor-accountability-profiles.json).

- Duty owner: `benefit_data_controller_or_credential_reuse_system_owner`.
- Rent/benefit trace: `identity_vendor_data_broker_or_agency_program_capturing_extra_data_reuse_or_error_shifting_from_claimants`.
- Bottleneck/evidence: `credential_wallet_or_identity_proofing_gate; sensitive_attribute_data_store +2 more`; evidence starts with `data_field_authority_and_necessity_map; credential_reuse_retention_and_access_log +3 more`.
- Fallback duty: `fallback_public_body_must_preserve_low_data_offline_assisted_and_nonforfeiture_channel_with_notice_cure_deletion_and_human_review`.


## Source IDs only

[S1][S10][S15][S16][S17][S23][S27][S39][S40][S41][S44][S64][S65][S66][S74][S89][S91][S92]

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
[S339]: ../../SOURCES.md#S339
[S340]: ../../SOURCES.md#S340
[S343]: ../../SOURCES.md#S343
[S345]: ../../SOURCES.md#S345
[S346]: ../../SOURCES.md#S346
[S347]: ../../SOURCES.md#S347
[S348]: ../../SOURCES.md#S348
[S349]: ../../SOURCES.md#S349
[S350]: ../../SOURCES.md#S350
