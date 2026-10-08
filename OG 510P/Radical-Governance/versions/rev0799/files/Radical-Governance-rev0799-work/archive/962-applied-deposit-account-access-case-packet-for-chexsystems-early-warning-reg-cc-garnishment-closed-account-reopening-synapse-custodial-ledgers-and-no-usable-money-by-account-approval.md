# 962 — Applied deposit-account access case packet for ChexSystems, Early Warning, Reg CC, garnishment, closed-account reopening, Synapse, custodial ledgers, and no usable money by account approval

## One-line thesis

A deposit account, prepaid card, fintech wallet, or app balance proves usable money only when the packet joins screening, account state, funds availability, protected-payment, custodial-ledger, complaint, and household-outcome evidence.

## Why this matters

The consumer-finance cube can otherwise mistake nominal access for practical access: a person may be approved for an account, see a balance, file a complaint, or receive a direct deposit while still being unable to open a replacement account, withdraw funds, avoid unlawful fees, preserve protected benefits, or recover money trapped in a custodial ledger.

## Case packet verdict

Apply a usable-money continuity packet whenever a consumer-finance matter turns on whether a person can open, keep, use, withdraw from, or repair a bank account, prepaid account, fintech wallet, or custodial-account subledger. The packet is mandatory when the record contains a checking-account denial, specialty screening file, account closure or reopening, hold/freeze, funds-availability delay, garnishment/levy/offset, app-balance/subledger break, or complaint that has not yet been joined to restored money.

## Pattern pack

- **Screening denial lane.** Join application, screening report, adverse action, furnisher, dispute, and opened/replacement account.
- **Closure/reopening lane.** Join status reason, consumer request, balance, pending transactions, fees, returned funds, and replacement access.
- **Funds-availability lane.** Join deposit type, banking day, hold/exception, notice, available date, withdrawal channel, and actual release.
- **Fraud/KYC restriction lane.** Join risk basis, notice constraints, verification steps, review path, duration, and funds-return or closure outcome.
- **Garnishment/protected-payment lane.** Join order, lookback, protected amount, freeze/sweep handling, notice, exemption route, and available balance.
- **Fintech/custodial lane.** Join app balance, partner bank, beneficial owner, subledger, reconciliation, interruption/insolvency event, and payout outcome.
- **Complaint-to-money lane.** Join complaint/referral, company response, jurisdiction, investigation, redress, and household outcome.

## Trigger facts

Escalate from a generic consumer-finance packet to this packet if any of these facts appear:

- A consumer was denied or deterred from opening a checking account.
- A ChexSystems, Early Warning, or similar specialty report is cited, requested, disputed, or suspected.
- A bank or credit union closed, reopened, restricted, or failed to close an account.
- A deposit appears in the ledger but is unavailable for cash withdrawal, debit, bill pay, ACH, card use, or transfer.
- Funds are held because of suspected fraud, suspicious activity, identity verification, AML/KYC, or third-party risk.
- A garnishment, levy, offset, court order, child support order, or debt-collection action touches an account holding wages, benefits, refunds, or emergency aid.
- A fintech app, program manager, bank partner, or custodial account stands between the consumer and the bank ledger.
- A complaint or regulator referral exists, but funds, account state, report correction, or household outcome has not been proven.

## Evidence lanes and required joins

### 1. Checking-account screening and adverse-action lane

The packet must capture the application, product, channel, financial institution, screening company, reason code, adverse-action notice, report request, furnisher, dispute, correction/removal result, and final account-opening outcome. A denial row is too thin unless it identifies the report and the repair path.

**Pass evidence:** the record shows which report was used, which institution or furnisher supplied the negative information, whether the consumer obtained and reviewed the report, whether inaccurate or unfamiliar information was disputed, and whether corrected reporting changed the account-opening outcome.

**Fail/repair:** add report-access and furnisher-dispute evidence before treating the household as excluded, repaired, or voluntarily unbanked.

### 2. Account closure, reopening, and returned-funds lane

The packet must distinguish requested closure, unexpected closure, unilateral reopening, fraud restriction, and operational closure. It must also show balance at closure, pending deposits/debits, fee/reward effects, address/payment path for remaining funds, returned-funds receipt, and replacement access.

**Pass evidence:** closure state, consumer request or institution reason, remaining balance, check/ACH/debit handling, fees, and money-return proof are joined.

**Fail/repair:** do not let a closed-account code stand for repair if funds or fees remain unresolved.

### 3. Funds-availability and hold lane

The packet must record the deposit type, banking day, business-day clock, account age, hold/exception reason, notice, dollar amount delayed, available-for-withdrawal date, channel availability, and actual release. It must distinguish ledger credit from available funds.

**Pass evidence:** the funds-availability clock and withdrawal channel prove when the consumer could actually use the money.

**Fail/repair:** add hold notice, exception basis, available-date proof, and post-release transaction evidence.

### 4. Fraud/KYC/AML restriction lane

The packet must preserve the institution's risk basis without allowing a hidden risk label to erase consumer remedy. The joined record should include notice limits, identity-verification steps, allowed partial access, appeal/review path, duration, closure decision, and funds-return route.

**Pass evidence:** there is a time-bounded restriction or closure pathway, not an indefinite “security review” placeholder.

**Fail/repair:** require a release, closure, funds-return, or adverse-action path; otherwise classify the matter as account-access non-continuity.

### 5. Garnishment, levy, offset, and protected-benefit lane

The packet must capture the order, creditor/agency/court, account review, lookback period, protected amount, nonprotected excess, freeze/sweep state, notice, exemption process, and post-review available balance. It must not infer benefit access from direct deposit alone.

**Pass evidence:** the protected amount remains available, frozen funds are legally bounded, and the account holder can use the protected balance without asserting a separate exemption first when applicable.

**Fail/repair:** add protected-amount calculation, notice, court/agency/exemption outcome, and actual available-balance proof.

### 6. Fintech, custodial-account, and partner-bank lane

The packet must join the app-facing balance to the partner bank, custodial account, beneficial owner, program manager, ledger/subledger reconciliation, recordkeeper, bankruptcy/receivership or business-interruption event, consumer communications, and payment/reconciliation outcome.

**Pass evidence:** the bank or responsible recordkeeper can identify the beneficial owner and the amount attributable to that person, reconcile the subledger to bank records, and pay or transfer the funds.

**Fail/repair:** do not accept an app balance, marketing label, or routing/account number as proof of deposit protection or access.

### 7. Complaint and regulator-routing lane

The packet may use CFPB, OCC, Federal Reserve, state, bank, or fintech complaint records, but the complaint lane is secondary. It must join complaint filing, referral, company response, jurisdiction, investigation result, restitution/order if any, funds returned, account/report/debt correction, and downstream household result.

**Pass evidence:** the complaint is connected to actual corrected state and usable money.

**Fail/repair:** keep the complaint as a pending evidence lane and do not close the case as repaired.

## Minimal case-table schema

Every applied row should carry these fields:

```text
person_id_or_household_unit
representative_or_assisted_access
institution_or_bank_partner
fintech_or_program_manager_if_any
product_type
application_or_account_id
screening_report_vendor
adverse_action_or_denial_reason
account_status_and_status_date
closure_or_reopening_reason
balance_at_status_event
deposit_or_payment_type
funds_availability_clock
hold_or_freeze_reason
protected_payment_or_garnishment_flag
custodial_beneficial_owner_balance
complaint_or_regulator_route
company_response_or_bank_action
money_returned_or_released
replacement_access
public_service_or_household_outcome
source_currentness_flag
```

## Anti-theater tests

- No account access by approval or routing number.
- No available money by ledger or app balance.
- No repair by complaint filing or referral.
- No screening correction by report request alone.
- No closure repair by account-status code.
- No protected-benefit access by direct deposit alone.
- No custodial proof without beneficial-owner and reconciliation evidence.
- No consumer safety by indefinite fraud/KYC hold.

## Negative controls

Do not apply this packet when the matter is only a generalized policy discussion with no account, wallet, card, report, payment, hold, closure, garnishment, custodial, or complaint fact. Do apply it even if the money amount is small, because small withheld amounts can break rent, food, utilities, transport, medical care, filing deadlines, or replacement-account access.

## Cube repair performed

This packet repairs the gap left by rev0762: the earlier consumer-finance cube had complaint, credit-report, debt, Reg E, bank-account, FDIC, and OCC lanes, but it did not yet make **deposit-account usability** a dedicated case packet. This note adds the account-screening, closure, funds-availability, garnishment, and custodial-ledger tests that prevent the cube from accepting a nominal account as proof of usable money.
