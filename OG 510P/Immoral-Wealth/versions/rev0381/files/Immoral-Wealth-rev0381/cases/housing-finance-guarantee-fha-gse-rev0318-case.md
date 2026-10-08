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
source_refresh_due: 2027-03-31
case_pressure: rev0318_public_balance_sheet
---

# Housing-finance guarantee, FHA, and GSE case — rev0355

## Verdict

**Correction required.** FHA reports strong MMI Fund capital and heavy first-time-homebuyer use, while Fannie Mae and Freddie Mac remain under conservatorship with Treasury support agreements; these facts make guarantee design a public balance-sheet issue.[S363][S364][S365][S366][S367]

## Dominant breach

The breach is guarantee-incidence opacity: mortgage guarantees can open homeownership but can also subsidize leverage, asset prices, and intermediaries unless public risk, borrower benefit, and taxpayer upside are jointly scored.

## Gate 20 finding

Gate 20 is **blocked for comfort certification** unless the case proves that public downside, debt service, and backstop obligations are transparent, financed, incidence-scored, and paired with ordinary-claimant protection or public upside recovery.

## Opening package

Score mortgage insurance and GSE support by first-time buyer access, home-price inflation, lender/intermediary benefit, taxpayer risk, capital adequacy, and whether public support creates public upside or only private asset appreciation.

## Evidence debt

Borrower wealth/income/race/place distribution; fair-value subsidy; guarantee fee adequacy; stress losses; effect on prices/rents; GSE exit scenarios and public claim on upside.

## Source anchors

[S363][S364][S365][S366][S367]

## rev0319 Gate 20 operationalization addendum

rev0319 converts this from a short Gate 20 launch memo into a structured public-balance-sheet stress row. The scoreboard now includes a `public_balance_sheet_register`, `gate_20_subgates`, a `seniority_waterfall`, and a full 20-gate inventory.

### Active Gate 20 subgates

- **20C_contingent_liabilities_guarantees — blocked:** Mortgage guarantees are major contingent liabilities requiring fair-value and stress visibility.
- **20E_public_upside_recovery — watch:** GSE warrants/preferred shares create some public upside; FHA/subsidy paths need clearer incidence.

### Seniority waterfall under stress

1. **Guaranteed MBS investors** — Very senior through federal guarantee/support. Cash-flow protection can be stronger than homeowner equity protection.
2. **Homeowners/borrowers** — Partially protected through access, not loss guarantee. Default, foreclosure, and negative equity remain household risks.
3. **Taxpayers/public balance sheet** — Residual stress absorber. Support becomes public cost if guarantee fees/capital are insufficient.
4. **Renters/non-owners** — Outside claimant perimeter. May pay through higher prices without receiving mortgage-credit upside.

### Case-specific evidence debt

- guarantee-fee incidence by borrower income/race/first-time-buyer status
- owner/renter split of subsidy and price support
- stress-loss allocation between borrowers, taxpayers, guarantors, investors, and servicers
- fair-value subsidy comparison and capital buffers
- public upside recovery under GSE conservatorship and FHA stress

### Operator implication

The case cannot use aggregate public capacity as a benign counterweight unless the stress waterfall shows ordinary claimants are protected before asset holders, creditors, or intermediaries, or unless public downside is paired with enforceable upside recovery and transparent loss sharing.

## rev0328 substantive hardening addendum

rev0328 promotes the paired scoreboard from `seed` to `active` because the evidence now supports operational scoring rather than placeholder doctrine.

### Active finding

Housing finance guarantees can be access infrastructure or wealth-price support. The case now requires borrower/intermediary/investor/taxpayer incidence, renter/owner split, stress-loss waterfall, FCRA/fair-value sensitivity, and upside recovery under FHA/GSE support.

### Current source anchors

[S365] [S366] [S367] [S363]

### Operator instruction

Do not certify this case with aggregate solvency, subsidy, or balance-sheet language. The operator must show claimant seniority, ordinary-claimant protection, distributional incidence, loss sharing, public-upside recovery, and source refresh status.
