# 961 — Deposit-account screening, closure, holds, garnishment, custodial funds, and fintech access continuity dockets: no usable money by account approval

## One-line thesis

Consumer-finance access cannot be proved by an approved account, a banked-household category, a complaint ID, or a displayed app balance. The continuity test has to follow whether the person can open, keep, fund, withdraw from, and repair a transaction account or wallet after screening-file denials, fraud/KYC holds, unexpected closures, garnishment orders, custodial-ledger breaks, and bank/fintech partner failures.

## Why this matters

### Why this is the riskiest unfinished consumer-finance gap

The earlier consumer-finance packet correctly rejected proof-by-account-row, but it still leaned too much on complaint, reporting, debt, and regulator-routing surfaces. The more dangerous failure is upstream and operational: someone can be counted as banked, have a nominal account, have a complaint in process, or have an app balance, while wages, tax refunds, public benefits, emergency aid, or rent money are still unavailable.

This docket therefore moves the cube from **financial-access status** to **usable-money continuity**. The unit of analysis is not the institution's account row. It is a person-level chain that joins account-opening eligibility, specialty consumer reports, adverse-action/dispute records, account status, hold/freeze reason, funds-availability clock, protected-payment/garnishment review, custodial beneficial-owner ledger, customer remedy, and downstream household consequence.

## Minimum record that must exist before saying “access”

A deposit-account continuity record should include, at minimum:

| Surface | Required joined fields | Why the account row alone fails |
| --- | --- | --- |
| Person and authority | consumer identity, representative/caregiver authority, mailing and digital contact, language/disability supports, household dependency | a bank can identify an account without proving the person can receive notice or act |
| Account-opening screen | application channel, product requested, bank/fintech/partner, screening vendor, BSA/AML/KYC flag, adverse-action reason, denial/approval outcome | approval or denial is meaningless without the file that triggered it |
| Specialty reporting file | ChexSystems/Early Warning or similar report, furnisher, reported closure reason, suspected fraud tag, unpaid balance, dispute path, correction/removal receipt | a hidden report can block future access even after a consumer “has” or “had” an account |
| Account status and closure | open/closed/reopened/frozen/restricted state, consumer request, institution action, closure reason, balance at closure, returned-funds receipt | closed or reopened accounts can create fees, third-party access, or missing balances |
| Funds availability | deposit type, date/time received, business-day clock, exception invoked, notice, available-for-withdrawal date, actual withdrawal channel | a ledger credit does not prove cash, debit, bill pay, or ACH usability |
| Fraud/AML hold | rule or risk basis, communication to consumer, duration, release or termination path, appeal/review receipt, partial access | “security review” can become indefinite non-access unless time-bounded and reviewable |
| Garnishment/levy/offset | order type, benefit lookback, protected amount, frozen excess, notice, exemption process, court/agency outcome | a protected benefit can be deposited and still be functionally inaccessible |
| Custodial/fintech ledger | bank partner, program manager, custodial account, beneficial owner, subledger balance, bank ledger reconciliation, failure/insolvency event | an app balance is not proof the bank can identify or pay the consumer |
| Remedy and household outcome | complaint/referral, company response, correction, redress, funds returned, reopened account, replacement account, rent/food/utility/payroll outcome | complaint process is not remedy until the money and downstream dependency are repaired |

## Pattern pack

- **No usable money by account approval.** Approval, banked status, or an app-facing balance is only a starting state; the live question is whether money can be received, held, withdrawn, transferred, protected, and restored.
- **Screening file as access gate.** Checking-account reports, adverse-action reasons, fraud flags, and furnisher disputes are account-access infrastructure, not credit-report side issues.
- **Account state as operational risk.** Closed, reopened, restricted, or frozen accounts need balance, notice, pending-transaction, returned-funds, and replacement-access evidence.
- **Ledger balance versus available balance.** Funds availability, holds, exceptions, notices, and withdrawal channels must be joined before a deposit counts as usable.
- **Protected payment as access test.** Garnishment, levy, and offset rows must preserve protected amounts and prove the consumer could use protected funds.
- **Custodial subledger as public-service dependency.** Fintech and program-manager balances require beneficial-owner, partner-bank, reconciliation, and payout evidence.
- **Complaint lane as secondary evidence.** A complaint or referral is useful only when joined to corrected account state, released money, redress, and household outcome.

## Priority correction to the cube

The cube should stop treating **banked status**, **account approval**, **complaint filed**, and **app balance displayed** as adjacent but separate evidence lanes. They belong in one continuity packet whenever money availability depends on private deposit rails.

Use the following rule:

> If a household's wages, refund, benefit, relief payment, rent, utility, food, transport, medical, education, immigration, or emergency-aid access depends on a deposit account, prepaid card, wallet, fintech app, or custodial account, the cube must include a usable-money continuity packet.

## Failure modes newly promoted to first-class rows

1. **Screening-file exclusion.** A consumer is denied or deterred from opening a checking account because a specialty report records an unpaid balance, closure, suspected fraud, identity mismatch, or prior account issue. The repair is not “try another bank”; it is report access, adverse-action reason, furnisher identity, dispute, correction/removal, and replacement access.

2. **Closure without continuity.** A bank closes or restricts an account, or fails to close it when requested, while deposits, checks, ACH debits, fees, rewards, or remaining funds remain unresolved. The repair is a closure-state ledger, balance-at-closure proof, returned-funds path, stop/reversal of fees, and replacement access.

3. **Funds-availability theater.** The account shows a deposit or pending transaction but the consumer cannot withdraw, pay bills, use a debit card, or transfer money. The repair is a funds-availability clock joined to actual withdrawal channels and notices.

4. **Fraud/KYC freeze without time-bounded pathway.** Security review, suspicious-activity concern, or identity verification blocks funds without a noticeable and reviewable path. The repair is not merely risk documentation; it is a consumer-facing release, denial, closure, or appeal outcome.

5. **Protected benefit garnishment failure.** Federal benefit funds, wages, refunds, or emergency payments are deposited, then frozen or swept under a garnishment, levy, or offset process without preserving legally protected access. The repair is a protected-amount calculation, notice, exemption process, and actual available balance.

6. **Custodial-account/subledger break.** A fintech or program manager shows money in an app while the partner bank or receiver cannot reconcile beneficial-owner balances. The repair is bank-ledger reconciliation, beneficial-owner identification, direct access to records, and payment to the consumer.

7. **Complaint-as-remedy substitution.** CFPB, OCC, Federal Reserve, state, or company complaint routing records are cited as repair while funds, reports, account state, and household consequences remain unresolved. The repair is a complaint-to-outcome join.

## Audit/refactor performed in this revision

The source-health generated surface was consuming repeated reader cost. This revision changes `tools/build_source_health.py` so `generated/SOURCE_HEALTH.json` is emitted as compact JSON while keeping the markdown reader surface. This is deliberately small but concrete: it reduces generated-surface bloat without deleting source-health evidence, and it moves the archive away from paying a formatting tax on every substantive turn.

## Anti-theater tests

- No account access by application approval.
- No money access by banked-household category.
- No funds availability by ledger balance.
- No remedy by complaint ID.
- No dispute repair by letter sent.
- No protected benefit by direct deposit.
- No custody proof by app balance.
- No closure repair by closure code.
- No consumer safety by fraud hold.
- No access fallback by online-only portal.

## Source boundary

This docket depends on official/public source keys for checking-account denial guidance, checking-account screening companies, Regulation CC, federal-benefit garnishment protections, closed-account reopening, Synapse/fintech custodial-funds failures, FDIC custodial-account recordkeeping proposals, Federal Reserve Evolve partner-bank enforcement, Federal Reserve complaint summaries, CFPB complaint routing, and OCC complaint routing. Those sources are evidence lanes, not self-executing proof that any particular consumer's money was available or restored.
