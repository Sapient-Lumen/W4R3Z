# Public filing floor, refund rail, and channel fallback ladder

## Question in one sentence

How should a tax system set minimum filing, correction, refund, and payment-channel requirements when direct public filing is unavailable, partner free-filing is eligibility-limited, and paper refund checks or paper payments are being phased down?[S119][S441][S442][S443][S444][S661]

Rev0286 filing-floor source note: the current IRS Free File page makes the public/private boundary more concrete by distinguishing partner guided software, Free File Fillable Forms, partner eligibility criteria, state-return limitations, and no-upsell/deceptive-practice guardrails.[S661]

## Companion routes

[`../10-framework/public-filing-floor-and-refund-rail-fallback-routing.md`](../10-framework/public-filing-floor-and-refund-rail-fallback-routing.md) · [`../10-framework/channel-pluralism-and-access-independence-routing.md`](../10-framework/channel-pluralism-and-access-independence-routing.md) · [`../10-framework/automaticity-and-claim-friction-routing.md`](../10-framework/automaticity-and-claim-friction-routing.md) · [`../10-framework/official-error-prefill-and-guidance-reliance-routing.md`](../10-framework/official-error-prefill-and-guidance-reliance-routing.md) · [`../10-framework/overcollection-return-setoff-and-refund-symmetry-routing.md`](../10-framework/overcollection-return-setoff-and-refund-symmetry-routing.md)

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — private market is enough | rely on commercial software, preparers, banks, and card/wallet rails. | Reject: private abundance does not equal rights access when eligibility, upsells, fees, accounts, or identity gates block people. |
| B — free partner lane only | make partner software the practical public floor. | Too weak unless every required taxpayer has a no-cost, state-compatible, no-upsell, accessible route.[S119][S441] |
| C — public core plus private supplements | maintain a no-rent public lane and let private channels compete above it. | Adopt. |
| D — electronic-only refunds with discretionary paper exceptions | prefer electronic rails but hold refunds until taxpayers solve account problems. | Reject unless exception, assistance, reissue, and hardship timing are explicit.[S443][S444] |

## Nine-gate ladder

1. **required-duty gate** — identify whether filing, amendment, information return, payment, refund claim, identity proof, or correction is legally required.
2. **public-lane gate** — name the public no-rent channel: direct file, public e-file, free fillable form, paper, phone-assisted, in-person, VITA/TCE, or equivalent.[S441]
3. **private-supplement gate** — if software partners or preparers are relied on, test AGI, age, military, state, language, disability, device, and upsell limits.[S119][S441]
4. **simple-return data gate** — for wage/withholding cases, ask what the state already knows and whether prefill, return-free filing, or one-click confirmation is feasible.
5. **state-return gate** — if federal filing is free but state filing is not, record the hidden total cost before calling the lane no-rent.[S441]
6. **refund-rail gate** — identify ACH, card, direct express, check, wallet, cash-equivalent, or assisted reissue options; no one rail may become a practical hostage condition.[S443][S444]
7. **failed-payment gate** — rejected direct deposit, wrong account, closed account, frozen bank, fraud marker, or identity hold must trigger a bounded public repair path.[S444]
8. **protected-access gate** — test bankless, disability, language, elderly, rural, incarcerated, recently unhoused, domestic-abuse, and identity-compromised cases before finalizing the channel mix.
9. **review-and-metrics gate** — publish uptake, rejection, refund-hold, state-fee, accessibility, and assistance metrics; revise when private rails substitute for rights access.

## Minimum standard

- one no-rent filing path for required routine returns;
- one no-rent correction path for official or third-party mismatch;
- one no-rent refund-reissue path when the preferred rail fails;
- one accessible non-digital or assisted channel where digital-only would exclude protected users;
- no refund product, paid preparer, bank account, partner eligibility screen, identity vendor, or private wallet as the sole practical gate to an owed public payment.

## Accountability capsule

Profile route `public_filing_refund_floor` in [`actor-accountability-profiles.json`](../00-meta/actor-accountability-profiles.json); the profile is authoritative for owner, benefit, evidence, fallback, and anti-misattribution.

## Source IDs only

[S119][S441][S442][S443][S444][S661]

[S119]: ../../SOURCES.md#S119
[S441]: ../../SOURCES.md#S441
[S442]: ../../SOURCES.md#S442
[S443]: ../../SOURCES.md#S443
[S444]: ../../SOURCES.md#S444

[S661]: ../../SOURCES.md#S661
