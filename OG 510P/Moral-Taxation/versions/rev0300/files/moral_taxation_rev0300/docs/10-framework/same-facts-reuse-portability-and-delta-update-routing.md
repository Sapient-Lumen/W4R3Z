# Same-facts reuse, portability, and delta-update routing

This note answers the question that comes **after** a filing packet, controller map, rebate claim, or liability record is already good enough for one nearby tax period or authority: **must the archive make the same actor prove the same facts again?** The archive's stable answer is usually **no**. Reuse the operative packet when the live facts, governed object, and legal test are materially the same; require a **bounded delta** for narrow changes; require a **local supplement** when a later regime asks a genuinely different question; and never let portability outrank integrity, contestability, or material-change reopening.[S16][S17][S27][S39][S40][S41][S44][S68][S89][S91][S92]

## When this note governs

| Live posture | Default answer | Why it usually fits | Must not do |
|---|---|---|---|
| Same person, firm, asset, or governed AI layer; same nearby period; materially same test | reuse the operative packet or prior determination | repeated full refiling adds friction faster than truth | do not treat repeated asking as integrity work when nothing material changed.[S27][S39][S41][S68][S89] |
| Same object and test, but one narrow fact changed | require a short delta or no-change / changed-fact attestation | the archive usually needs the changed fact, not a rebuilt dossier | do not force whole-case reconstruction for a bounded update.[S27][S39][S41][S68][S89] |
| Later authority, levy, or audience tier asks a narrower or different question | reuse the common core, then add a local supplement | portability should reduce duplication without flattening real legal difference | do not export one regime's closure point as a universal passport.[S20][S27][S39][S40][S41][S44][S91][S92] |
| Prior packet is stale, false, strategically partial, or materially contested | suspend easy reliance and reopen the disputed piece | bad portability spreads bad answers faster | do not let reuse travel farther than integrity, verification, and reopening allow.[S16][S17][S27][S39][S40][S41][S44][S89][S91][S92] |

## Five routing rules

1. **Same facts first, fresh paperwork second.** If the moral object, period logic, and live legal test are materially the same, the default is reliance on the operative prior packet rather than clean-sheet refiling.[S27][S39][S41][S68][S89]
2. **Delta before rebuild.** Narrow changes should travel as short deltas, not as whole reconstructed filings whose real effect is to raise cost, blur lineage, and hide what actually changed.[S27][S39][S41][S68][S89]
3. **Shared core, local edge.** Where later regimes need extra fields, tighter secrecy, or a different legal cut, they should add a bounded supplement to the reusable core rather than discard the core entirely.[S20][S27][S39][S40][S41][S44][S91][S92]
4. **Portability is conditional, not absolute.** Reuse never outranks proof correction, audience-tier rights, material-change reopening, or integrity-triggered suspension.[S16][S17][S27][S39][S40][S41][S44][S89][S91][S92]
5. **Once-only is a justice rule, not just an efficiency rule.** The strongest reasons for reuse appear when repeated refiling would hit weaker people, small firms, or downstream users who do not control the records and cannot cheaply rebuild them every time.[S27][S39][S41][S68][S89][S91][S92]

## What this closes

This rule keeps several already-settled archive commitments from regrowing into separate edge-case notes:

- data minimization means **do not recollect the whole file** when a reusable claim already exists,[S40][S89][S91][S92]
- filing parity means **relief should not require more repeated proof than liability**,[S27][S39][S41][S68]
- record asymmetry means the stronger record-holder should not win by forcing everyone else to restate hidden facts from scratch,[S27][S39][S41][S44]
- and bounded finality means portability should usually move through a visible operative packet plus narrow updates, not through endless reproofing.[S16][S17][S27][S39][S41][S89]


### 6. Corrected third-party reports should travel as shared deltas

A corrected W-2, 1099, 1099-K, withholding statement, platform report, payer letter, or official recipient counterstatement is a paradigmatic same-facts object. Once the disputed field has been corrected or annotated, the new fact should move across filing, refund, collection, penalty, benefits, and audit surfaces without forcing the recipient to relitigate the same upstream reporting error in every channel.[S27][S39][S41][S42][S68][S89][S154][S156][S157][S158][S159]

### 7. Household-status allocations should travel as bounded deltas

An accepted spouse-relief decision, injured-spouse allocation, dependent correction, custody fact, or separated-household status update should also travel as a bounded reusable delta. A person should not have to re-prove the same household-status fact separately for refund release, offset reversal, filing-status review, credit eligibility, penalty abatement, and later audit defense.[S31][S32][S33][S39][S41][S42][S161][S162][S164][S165][S166][S167]

### 8. Reconciled ledger fields should travel as deltas

Once a payment, credit, carryforward, offset, refund trace, or returned-payment correction has been accepted, adjacent systems should reuse the corrected ledger fact instead of making the subject prove it again for collection, refund, penalty, transcript, account-access, or future-year surfaces. The portable fact is bounded: amount, period, account, source, correction date, and the systems to which it applies.[S176][S178][S180][S181]


### 9. Basis, lot, and exclusion corrections should travel as deltas

Once a corrected basis, holding period, lot selection, transfer history, digital-asset wallet history, home-sale exclusion fact, or real-estate cost adjustment is accepted, adjacent systems should reuse that bounded correction for automated notices, audit, refund, collection, penalty, and future-year carryover surfaces. The taxpayer should not have to reprove the same disposition every time a proceeds report appears in a new workflow.[S39][S42][S154][S155][S175][S291][S292][S294][S295][S298][S299][S301][S302]

## Anti-patterns

- **refile theater** — demanding a fresh full packet simply because the authority can, not because the facts or test materially changed.[S27][S39][S41][S68]
- **passport absolutism** — pretending one prior determination binds every later regime despite changed legal tests, periods, or audience rights.[S20][S27][S39][S40][S41]
- **delta laundering** — hiding a foundational change inside what is labeled a small update.[S16][S17][S27][S39][S41]
- **silent reuse against strangers** — relying on a packet against affected parties who never had the access tier needed to contest it.[S40][S41][S44][S91][S92]
- **mismatch relitigation loop** — a corrected or annotated third-party report fixes one surface while refund, collection, penalty, or audit systems continue to demand the same proof again.[S154][S156][S157][S158][S159]
- **household-status relitigation loop** — a spouse-relief, injured-spouse, dependency, custody, or separated-household correction fixes one surface while adjacent systems still behave as though the old merged record were final.[S161][S162][S164][S165][S166][S167]
- **ledger relitigation loop** — a payment, credit, carryforward, offset, or refund-trace correction posts in one place while collection, penalty, refund, or transcript systems continue to demand the same proof again.[S176][S178][S180][S181]


- **basis relitigation loop** — a corrected basis, holding-period, lot-selection, wallet-history, or home-sale exclusion fact is accepted once but ignored by underreporter, audit, refund, penalty, or collection systems.[S291][S294][S295][S298][S299][S301][S302]

## Use this with

- [`compliance-burden-and-filing-parity-routing.md`](compliance-burden-and-filing-parity-routing.md)
- [`data-minimization-and-purpose-bounded-verification-routing.md`](data-minimization-and-purpose-bounded-verification-routing.md)
- [`record-asymmetry-burden-shifting-and-adverse-inference-routing.md`](record-asymmetry-burden-shifting-and-adverse-inference-routing.md)
- [`bounded-contest-issue-scoped-correction-and-period-finality-routing.md`](bounded-contest-issue-scoped-correction-and-period-finality-routing.md)
- [`collection-and-remittance-routing.md`](collection-and-remittance-routing.md)
- [`administration-explanation-and-appeal-routing.md`](administration-explanation-and-appeal-routing.md)
- [`third-party-reporting-correction-and-bounded-recipient-shelter-routing.md`](third-party-reporting-correction-and-bounded-recipient-shelter-routing.md)
- [`../../archive/172-third-party-tax-reporting-errors-withholding-credit-and-information-return-correction-should-not-be-turned-into-mismatch-rents-or-reporter-hostage-traps.md`](../../archive/172-third-party-tax-reporting-errors-withholding-credit-and-information-return-correction-should-not-be-turned-into-mismatch-rents-or-reporter-hostage-traps.md)
- [`../../archive/173-joint-return-spouse-debt-dependent-claim-and-household-status-records-should-not-be-turned-into-captive-household-rents-or-relational-liability-traps.md`](../../archive/173-joint-return-spouse-debt-dependent-claim-and-household-status-records-should-not-be-turned-into-captive-household-rents-or-relational-liability-traps.md)
- [`../../archive/175-basic-payment-credit-carryforward-offset-and-account-ledger-correction-should-not-be-turned-into-suspense-rents-or-missing-credit-traps.md`](../../archive/175-basic-payment-credit-carryforward-offset-and-account-ledger-correction-should-not-be-turned-into-suspense-rents-or-missing-credit-traps.md)
- [`../20-calibration/same-facts-reuse-portability-and-delta-update-ladder.md`](../20-calibration/same-facts-reuse-portability-and-delta-update-ladder.md)
- [`../20-calibration/controller-map-reuse-portability-and-cross-regime-reliance-ladder.md`](../20-calibration/controller-map-reuse-portability-and-cross-regime-reliance-ladder.md)
- [`../20-calibration/controller-map-packet-identity-canonical-fields-and-supersession-ladder.md`](../20-calibration/controller-map-packet-identity-canonical-fields-and-supersession-ladder.md)

[S16]: ../../SOURCES.md#S16
[S17]: ../../SOURCES.md#S17
[S20]: ../../SOURCES.md#S20
[S27]: ../../SOURCES.md#S27
[S39]: ../../SOURCES.md#S39
[S40]: ../../SOURCES.md#S40
[S41]: ../../SOURCES.md#S41
[S44]: ../../SOURCES.md#S44
[S68]: ../../SOURCES.md#S68
[S89]: ../../SOURCES.md#S89
[S91]: ../../SOURCES.md#S91
[S92]: ../../SOURCES.md#S92

[S154]: ../../SOURCES.md#S154
[S156]: ../../SOURCES.md#S156
[S157]: ../../SOURCES.md#S157
[S158]: ../../SOURCES.md#S158
[S159]: ../../SOURCES.md#S159

[S42]: ../../SOURCES.md#S42
[S31]: ../../SOURCES.md#S31
[S32]: ../../SOURCES.md#S32
[S33]: ../../SOURCES.md#S33
[S161]: ../../SOURCES.md#S161
[S162]: ../../SOURCES.md#S162
[S164]: ../../SOURCES.md#S164
[S165]: ../../SOURCES.md#S165
[S166]: ../../SOURCES.md#S166
[S167]: ../../SOURCES.md#S167

[S176]: ../../SOURCES.md#S176
[S178]: ../../SOURCES.md#S178
[S180]: ../../SOURCES.md#S180
[S181]: ../../SOURCES.md#S181

A later amended return, superseding return, refund claim, or abatement request is also a delta-update setting. The subject should not have to re-prove the whole tax file merely to change one field, nor should the administration treat the changed field as a license to ignore already-accepted facts absent a material coupling or integrity concern.[S39][S41][S42][S204][S206][S208][S209][S210][S211]
[S204]: ../../SOURCES.md#S204
[S206]: ../../SOURCES.md#S206
[S208]: ../../SOURCES.md#S208
[S209]: ../../SOURCES.md#S209
[S210]: ../../SOURCES.md#S210
[S211]: ../../SOURCES.md#S211
[S291]: ../../SOURCES.md#S291
[S292]: ../../SOURCES.md#S292
[S294]: ../../SOURCES.md#S294
[S295]: ../../SOURCES.md#S295
[S298]: ../../SOURCES.md#S298
[S299]: ../../SOURCES.md#S299
[S301]: ../../SOURCES.md#S301
[S302]: ../../SOURCES.md#S302
[S155]: ../../SOURCES.md#S155
[S175]: ../../SOURCES.md#S175
