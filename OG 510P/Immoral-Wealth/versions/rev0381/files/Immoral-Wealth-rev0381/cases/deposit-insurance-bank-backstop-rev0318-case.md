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
source_refresh_due: 2026-09-30
case_pressure: rev0318_public_balance_sheet
---

# Deposit insurance and bank-backstop case — rev0355

## Verdict

**Acceptable but vulnerable.** The FDIC reports a positive DIF balance and reserve ratio, but banking stress, uninsured deposits, and financial-stability monitoring remain relevant backstop surfaces.[S357][S358][S359][S368]

## Dominant breach

The breach is systemic exception risk: prefunded deposit insurance can be a real public stabilizer, but systemic failures can expand public backing beyond explicit pricing and tilt rescue value toward uninsured depositors, banks, and financial markets.

## Gate 20 finding

Gate 20 is **blocked for comfort certification** unless the case proves that public downside, debt service, and backstop obligations are transparent, financed, incidence-scored, and paired with ordinary-claimant protection or public upside recovery.

## Opening package

Keep risk-based assessments, systemic-risk exception transparency, clawback and loss-recovery rules, depositor/payment continuity for households and small firms, and public reporting of who benefited from extraordinary protection.

## Evidence debt

Distribution of deposit-insurance value by account size, firm size, bank business model, region, and uninsured balance; systemic-risk exception incidence; recovery from failed-bank owners and managers.

## Source anchors

[S357][S358][S359][S368]

## rev0319 Gate 20 operationalization addendum

rev0319 converts this from a short Gate 20 launch memo into a structured public-balance-sheet stress row. The scoreboard now includes a `public_balance_sheet_register`, `gate_20_subgates`, a `seniority_waterfall`, and a full 20-gate inventory.

### Active Gate 20 subgates

- **20C_contingent_liabilities_guarantees — watch:** Deposit insurance is explicit but systemic exceptions can expand the claimant perimeter.
- **20D_crisis_backstop_governance — blocked:** Crisis exceptions require clear rescue hierarchy, conditions, and loss-sharing.
- **20E_public_upside_recovery — blocked:** Public upside recovery is often weaker than public downside protection.

### Seniority waterfall under stress

1. **Insured depositors** — Explicitly senior up to limit. Core claimant protection is rule-bound.
2. **Uninsured depositors in systemic cases** — May become protected by exception. This can turn private cash-management choices into public stability claims.
3. **Shareholders and managers** — Formally loss-bearing. Resolution can wipe equity, but deterrence depends on enforcement.
4. **Banks/customers/future borrowers** — Assessment incidence channel. Special assessments can pass through to credit or fees.

### Case-specific evidence debt

- insured/uninsured depositor beneficiary split under systemic exceptions
- assessment incidence by bank size, borrower, and depositor group
- creditor/manager/shareholder loss-sharing record
- local payroll and small-business continuity benefits
- public upside or penalty pricing when blanket protection is used

### Operator implication

The case cannot use aggregate public capacity as a benign counterweight unless the stress waterfall shows ordinary claimants are protected before asset holders, creditors, or intermediaries, or unless public downside is paired with enforceable upside recovery and transparent loss sharing.

## rev0328 substantive hardening addendum

rev0328 promotes the paired scoreboard from `seed` to `active` because the evidence now supports operational scoring rather than placeholder doctrine.

### Active finding

Deposit insurance is stabilizing and partly prefunded, but systemic-risk exceptions can convert uninsured cash-management choices into public stability claims. The case now requires insured/uninsured beneficiary split, assessment incidence, resolution loss sharing, and public-upside recovery before extraordinary protection is treated as clean.

### Current source anchors

[S452] [S358] [S359] [S368]

### Operator instruction

Do not certify this case with aggregate solvency, subsidy, or balance-sheet language. The operator must show claimant seniority, ordinary-claimant protection, distributional incidence, loss sharing, public-upside recovery, and source refresh status.


## Rev0344 source-use burn-down note

Rev0344 binds formerly unused direct/context sources into this active case so the source ledger no longer carries high-value evidence outside the case/evidence/currentness lineage: [S32]. These bindings do not relax the verdict; they clarify which measurement, authority, or context burden the source supports.
