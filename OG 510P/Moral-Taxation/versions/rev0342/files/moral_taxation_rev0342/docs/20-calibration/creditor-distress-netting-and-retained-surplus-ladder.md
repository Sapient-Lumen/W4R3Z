# Creditor distress / netting / retained-surplus ladder

## Question in one sentence

Given the archive's closed rule that **real outside fixed-claim distress can narrow a downstream beneficiary-side windfall claim, but ordinary leverage, affiliate debt, recapitalization, or reserve rhetoric cannot**, **what is the smallest workable ladder for deciding when creditor absorption is real, when the case is mixed, and when a beneficiary-side charge should still attach to retained exceptional surplus?**[S18][S21][S24][S34][S35][S47][S48][S49][S67][S83]

## Closed rules invoked

This memo does **not** reopen the archive's waist. It relies on:

- [`../10-framework/creditor-bondholder-and-debt-service-pass-through-routing.md`](../10-framework/creditor-bondholder-and-debt-service-pass-through-routing.md)
- [`../10-framework/beneficiary-gain-and-windfall-routing.md`](../10-framework/beneficiary-gain-and-windfall-routing.md)
- [`../10-framework/failure-ordering-and-limited-liability-routing.md`](../10-framework/failure-ordering-and-limited-liability-routing.md)
- [`../10-framework/downside-symmetry-and-loss-routing.md`](../10-framework/downside-symmetry-and-loss-routing.md)
- [`../10-framework/beneficial-ownership-and-anti-fragmentation-routing.md`](../10-framework/beneficial-ownership-and-anti-fragmentation-routing.md)

## Minimal workable ladder

| Rung | Facts on the ground | Fiscal answer |
|---|---|---|
| 0. theater | the claim mostly rests on ordinary leverage, affiliate debt, shareholder loans, covenant rhetoric, discretionary reserve talk, or refinancing while exceptional margins or distributions continue | ignore the debt-service defense; keep the beneficiary-side lane on retained gain.[S21][S24][S34][S35][S47][S48][S83] |
| 1. outside claims but no real displacement | genuine outside creditors exist, but the firm is not in meaningful distress and fixed claims are not materially displacing residual upside | ordinary tax plus ordinary incidence review; beneficiary-side screening still applies to the exceptional residual.[S18][S21][S24][S47][S48][S49][S67][S83] |
| 2. mixed case | some incremental gain is visibly going to outside fixed-claim cure or prudential rebuilding, but some exceptional residual remains after netting | tax only the retained exceptional residual after bounded netting of real outside absorption; do not tax gross activity.[S18][S21][S47][S48][S49][S67][S83] |
| 3. real distress absorption | outside fixed claims, covenant cure, or solvency repair are genuinely consuming most of the incremental gain, distributions are constrained, and exceptional residual margins are not the main story | stand down or defer any beneficiary-side charge; stay with ordinary taxation, failure-ordering discipline, and prefunding review.[S21][S47][S48][S49][S67][S83] |
| 4. failure-ordering override | the same case also carries wage arrears, cleanup duties, local repair, or controller-side undercapitalization problems | do not let creditor absorption outrank worker priority, local repair, or ex ante security duties; any relief is bounded by those prior claims.[S15][S21][S47][S48][S49][S67][S69][S83] |

## Settings that matter most

### 1. Net only real outside fixed-claim absorption

Count only payments or reserve rebuilding that are tied to **real outside fixed claims** and are not simultaneously offset by dividends, buybacks, related-party interest, management extraction, affiliate guarantees, or reversible reserve release. The archive's calibration unit is net displacement of residual upside, not headline debt service.[S21][S24][S34][S35][S47][S48][S83]

### 2. Keep the window bounded and episode-linked

Creditor relief is strongest when tied to a visible distress or prudential-repair episode rather than to the firm's ordinary capital structure forever. Use bounded windows, renewal triggers, and re-checks of margins and payouts so a temporary cure does not harden into permanent immunity.[S18][S21][S47][S48][S49][S67][S83]

### 3. Mixed cases should split, not relabel

Where some gain is genuinely being absorbed by outside creditors and some is still being retained as exceptional residual, split the story. The archive should tax only the retained residual slice rather than either denying the distress facts or pretending the entire gain has already diffused.[S18][S21][S47][S48][S49][S67][S83]

### 4. Creditor absorption does not outrank prefunding, workers, or local repair

If the apparent need for debt service really reflects undercapitalized hazard, missing reserves, unpaid workers, or cleanup obligations, the archive still routes first through failure ordering, bonds, reserves, insurance, and controller-side duties. Creditor sympathy is not a license to crowd out those prior claims.[S15][S21][S47][S48][S49][S67][S69][S83]


## Use this memo with

- [`../10-framework/creditor-bondholder-and-debt-service-pass-through-routing.md`](../10-framework/creditor-bondholder-and-debt-service-pass-through-routing.md)
- [`../10-framework/beneficiary-gain-and-windfall-routing.md`](../10-framework/beneficiary-gain-and-windfall-routing.md)
- [`failure-waterfall-and-ex-ante-security-ladder.md`](failure-waterfall-and-ex-ante-security-ladder.md)
- [`automation-dividend-trigger-ladder.md`](automation-dividend-trigger-ladder.md)
- [`beneficiary-home-market-and-local-burden-claim-split-ladder.md`](beneficiary-home-market-and-local-burden-claim-split-ladder.md)

## Failure-mode capsule

Axes: `reserve_or_surplus_retention`, `liability_misassignment`, `trapdoor_or_cliff`.

## Recalibration trigger capsule

Triggers: `proceeds_or_surplus_trace_failure`, `priority_abuse_signal`, `hardship_cure_failure`.


## Accountability capsule

Authoritative assignment: route `creditor_distress_netting_and_retained_surplus` in [`actor-accountability-profiles.json`](../00-meta/actor-accountability-profiles.json).

- Duty owner: `creditor_servicer_receiver_or_insolvency_court_with_claim_netting_priority_and_surplus_distribution_control`.
- Rent/benefit trace: `secured_creditor_servicer_receiver_claim_buyer_or_insolvency_professional_capturing_priority_netting_fees_or_retained_surplus`.
- Bottleneck/evidence: `claim_allowance_priority_and_netting_record; servicer_fee_default_interest_and_collection_channel +2 more`; evidence starts with `loan_contract_claim_amount_default_fee_and_interest_record; netting_setoff_priority_and_collateral_valuation_file +4 more`.
- Fallback duty: `public_body_must_preserve_fallback_notice_cure_surplus_return_and_hardship_or_small_debtor_channel_when creditor distress machinery retains excess value`.


## Source IDs only

[S15]: ../../SOURCES.md#S15
[S18]: ../../SOURCES.md#S18
[S21]: ../../SOURCES.md#S21
[S24]: ../../SOURCES.md#S24
[S34]: ../../SOURCES.md#S34
[S35]: ../../SOURCES.md#S35
[S47]: ../../SOURCES.md#S47
[S48]: ../../SOURCES.md#S48
[S49]: ../../SOURCES.md#S49
[S67]: ../../SOURCES.md#S67
[S69]: ../../SOURCES.md#S69
[S83]: ../../SOURCES.md#S83
