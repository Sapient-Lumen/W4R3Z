# 959 — Applied consumer-finance continuity case packet for CFPB complaints, credit reports, debt collection, FDIC banking status, Regulation E, OCC complaints, and no financial access by account row

## One-line thesis

CFPB complaint data, FDIC household-banking categories, credit-report tools, FCRA/Regulation V disputes, debt-collection validation notices, Regulation E/prepaid error-resolution rules, OCC complaint routing, and bank-account consumer tools are separate evidence lanes. None proves financial access unless the person-level chain joins account, card, transaction, credit file, debt, complaint, response, correction, money, and downstream public-service outcome.

## Why this matters

Consumer-finance rows sit underneath many other packets. Tax refunds, wages, benefits, housing deposits, utility payments, school fees, transportation, immigration filings, and emergency aid can all fail if account access, credit-file accuracy, payment-error remedy, or debt-collection repair fails. This packet prevents the archive from treating a private financial status row as if it were public-service continuity.

The governing repair phrase is **no financial access by account row**.

## Pattern pack

- **CFPB complaints are escalation evidence, not remedy evidence.** The database records complaints sent to companies for response; it does not prove correction, restitution, or downstream recovery.
- **FDIC banking categories are population denominators, not individual access proof.** Fully banked, underbanked, and unbanked categories do not show whether a household can receive or keep public money.
- **Credit reports are contested data products.** A report or score must be joined to furnisher, dispute, reinvestigation, correction, and adverse-action consequences.
- **Debt-validation notices begin, not end, the proof chain.** Validation information must be joined to ownership, itemization, dispute, time-barred/litigation/garnishment, and credit-report effects.
- **Regulation E/prepaid rules are clocks and duties, not guaranteed restored money.** Error-resolution surfaces must be joined to transaction receipt, notice date, provisional credit, final decision, and account balance.
- **OCC routing is jurisdictional triage, not a finished repair.** A complaint may need the bank, OCC, CFPB, FDIC, FRB, NCUA, CSBS, or state route before remedy can happen.

## Evidence lanes in this packet

| Source family | What it helps show | What it cannot show alone |
|---|---|---|
| CFPB Consumer Complaint Database / submit complaint | consumer-product complaint, company-response lane, categories accepted by CFPB | corrected account/report/debt, restitution, household recovery |
| FDIC unbanked/underbanked survey | population-level account and nonbank financial-service access denominator | individual ability to receive wages, benefits, refunds, emergency aid |
| CFPB bank account/overdraft tools | deposit account and overdraft consumer-rights lane | account not frozen, fee-free, accessible, or benefit-compatible |
| Regulation E / prepaid account rules | EFT/prepaid error-resolution and liability lane | transaction was corrected or money restored |
| CFPB credit-report tools / FCRA / Regulation V | CRA/furnisher dispute and consumer-report rights lane | report accuracy, score recovery, adverse-action reversal |
| Debt Collection Rule / FDCPA | debt-validation and collector-conduct lane | debt validity, ownership, amount, limitations, or lawsuit/garnishment repair |
| OCC and HelpWithMyBank | national-bank complaint and referral lane | whether another regulator/company corrected the account |

## Case diagnosis

A consumer-finance packet is thick enough only when it can answer:

1. Which person, account/card/wallet, report, debt, or transaction is affected?
2. Which regulator, company, furnisher, collector, bank, processor, or CRA has the legal duty?
3. What did the person receive—statement, validation notice, adverse-action notice, report, complaint response, or denial?
4. Which clocks apply—EFT error, credit-report dispute, debt validation, chargeback, complaint response, or lawsuit/garnishment deadline?
5. What correction happened—money restored, fee reversed, report corrected, debt withdrawn, account reopened, deposit completed, or complaint escalated?
6. Which public-service or household consequence changed—refund, wage, benefit, rent, utility, food, housing, transit, work, immigration, education, or emergency aid?

## Continuity tests to run

Use `metadata/consumer_finance_tests.json` and generated `CONSUMER_FINANCE_TESTS.*` whenever a banked/unbanked row, account status, payment log, credit score, credit report, validation notice, dispute letter, complaint ID, or regulator routing decision is cited as proof that financial access exists.

## Failure modes

- Complaint closed, account still frozen.
- Credit dispute completed, inaccurate furnisher data remains or reappears.
- Debt notice sent, wrong-person/time-barred/paid debt still collected or reported.
- Benefit/refund direct deposit sent, prepaid/debit account closed or card inaccessible.
- Regulation E notice filed, provisional credit denied or final decision not joined to balance.
- National-bank complaint filed with OCC, but regulator routing misses the correct entity or downstream public-service consequence.
- Household counted as banked, but uses check cashing, payday/title/pawn, BNPL, or money order routes because the account is not practically usable.

## Negative controls

Do not use this packet for generic banking-sector stability, macro credit, or institutional finance unless person-level account, payment, credit-report, debt, complaint, or public-service consequences are at stake. Do use it when public services depend on privately mediated financial rails.
