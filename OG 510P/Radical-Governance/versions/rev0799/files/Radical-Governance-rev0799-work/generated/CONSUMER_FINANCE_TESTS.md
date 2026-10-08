# Consumer finance / credit / debt / account continuity tests matrix

Generated for `rev0799` from `metadata/consumer_finance_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `FIN-01` Person, account, card, and authority spine | Does the packet bind person, household, representative, account/card/wallet, address, language/disability, and fraud/identity state before accepting a finance row? | `424`, `425`, `426`, `475`, `482`, `489`, `506`, `509`, `520`, `521`, `535`, `557`, `562`, `573`, `577`, `884`, `889`, `902`, `903`, `905`, `911`, `912`, `919`, `920`, `950`, `951`, `956`, `957`, `958`, `959`, `961`, `962` | Open a person-account docket and downgrade account evidence to denominator state. |
| `FIN-02` Deposit and prepaid usability | Is account/prepaid/card status joined to balance, holds, fees, direct deposit, replacement, branch/ATM/digital access, and cash-out route? | `424`, `425`, `426`, `475`, `482`, `489`, `506`, `509`, `520`, `521`, `535`, `557`, `562`, `573`, `577`, `884`, `889`, `902`, `903`, `905`, `911`, `912`, `919`, `920`, `950`, `951`, `956`, `957`, `958`, `959`, `961`, `962` | Do not treat banked or carded as usable until money and channel access are joined. |
| `FIN-03` EFT, debit, ACH, and error-resolution clock | Are transaction, authorization, error notice, provisional credit, investigation, reversal/denial, and final balance joined? | `424`, `425`, `426`, `475`, `482`, `489`, `506`, `509`, `520`, `521`, `535`, `557`, `562`, `573`, `577`, `884`, `889`, `902`, `903`, `905`, `911`, `912`, `919`, `920`, `950`, `951`, `956`, `957`, `958`, `959`, `961`, `962` | Treat payment history as contested until Regulation E or equivalent error-resolution outcome is visible. |
| `FIN-04` Credit report and furnisher dispute continuity | Does the report/score evidence identify CRA or specialty report, furnisher, dispute, reinvestigation, correction/deletion, freeze/fraud alert, and adverse-action consequence? | `424`, `425`, `426`, `475`, `482`, `489`, `506`, `509`, `520`, `521`, `535`, `557`, `562`, `573`, `577`, `884`, `889`, `902`, `903`, `905`, `911`, `912`, `919`, `920`, `950`, `951`, `956`, `957`, `958`, `959`, `961`, `962` | Do not treat report or score as creditworthiness proof until dispute and downstream use are resolved. |
| `FIN-05` Debt validation, dispute, and collection boundary | Are collector, owner, amount, itemization, validation notice, dispute, time-barred/litigation/garnishment, contact limits, and credit-report effects joined? | `424`, `425`, `426`, `475`, `482`, `489`, `506`, `509`, `520`, `521`, `535`, `557`, `562`, `573`, `577`, `884`, `889`, `902`, `903`, `905`, `911`, `912`, `919`, `920`, `950`, `951`, `956`, `957`, `958`, `959`, `961`, `962` | Treat collector notice as a claim until debt identity, amount, owner, and remedy are proven. |
| `FIN-06` Complaint and regulator routing outcome | Is complaint ID joined to company response, regulator jurisdiction, handoff, escalation, restitution, corrected account/report/debt, and downstream restoration? | `424`, `425`, `426`, `475`, `482`, `489`, `506`, `509`, `520`, `521`, `535`, `557`, `562`, `573`, `577`, `884`, `889`, `902`, `903`, `905`, `911`, `912`, `919`, `920`, `950`, `951`, `956`, `957`, `958`, `959`, `961`, `962` | Do not count complaint filing as remedy until corrected state and outcome restoration are shown. |
| `FIN-07` Fee, overdraft, closure, and screening cascade | Are overdraft/NSF/maintenance fees, account screening, closure, collections, ChexSystems/specialty reports, and public-payment impacts joined? | `424`, `425`, `426`, `475`, `482`, `489`, `506`, `509`, `520`, `521`, `535`, `557`, `562`, `573`, `577`, `884`, `889`, `902`, `903`, `905`, `911`, `912`, `919`, `920`, `950`, `951`, `956`, `957`, `958`, `959`, `961`, `962` | Do not treat fee disclosure as safety; test whether the cascade blocked money or service access. |
| `FIN-08` Public-service dependency and household outcome | Does the packet show whether wages, benefits, tax refunds, housing, utilities, food, transport, immigration/work, education, or emergency aid were preserved or restored? | `424`, `425`, `426`, `475`, `482`, `489`, `506`, `509`, `520`, `521`, `535`, `557`, `562`, `573`, `577`, `884`, `889`, `902`, `903`, `905`, `911`, `912`, `919`, `920`, `950`, `951`, `956`, `957`, `958`, `959`, `961`, `962` | Escalate to payment-redress/benefit/housing/tax packet if finance failure blocks a public-service outcome. |
| `FIN-09` Assisted access and non-digital fallback | Are branch, phone, mail, interpreter, disability, broadband/device, representative, and paper routes actually usable for disputes and complaints? | `424`, `425`, `426`, `475`, `482`, `489`, `506`, `509`, `520`, `521`, `535`, `557`, `562`, `573`, `577`, `884`, `889`, `902`, `903`, `905`, `911`, `912`, `919`, `920`, `950`, `951`, `956`, `957`, `958`, `959`, `961`, `962` | Do not treat online tools as access until fallback and assistance channels are usable. |
| `FIN-10` Source-currentness and denominator boundary | Are complaint, survey, rule, consumer-tool, and regulator-routing sources marked as denominator/currentness surfaces rather than proof of person-level financial access? | `424`, `425`, `426`, `475`, `482`, `489`, `506`, `509`, `520`, `521`, `535`, `557`, `562`, `573`, `577`, `884`, `889`, `902`, `903`, `905`, `911`, `912`, `919`, `920`, `950`, `951`, `956`, `957`, `958`, `959`, `961`, `962` | Annotate source boundary and reopen if a source is used as proof rather than evidence lane. |
| `FIN-11` Deposit-account screening and adverse-action file | Does the packet join the account application, screening company, adverse-action reason, consumer report, furnisher, dispute, correction/removal result, and final account-opening outcome? | `424`, `425`, `426`, `475`, `482`, `489`, `506`, `509`, `520`, `521`, `535`, `557`, `562`, `573`, `577`, `884`, `889`, `902`, `903`, `905`, `911`, `912`, `919`, `920`, `950`, `951`, `956`, `957`, `958`, `959`, `961`, `962` | Do not classify the household as voluntarily unbanked or repaired until screening-file access, dispute, and account-opening outcome are joined. |
| `FIN-12` Account closure, reopening, and returned-funds continuity | Does the packet distinguish consumer-requested closure, unexpected closure, unilateral reopening, restriction, remaining balance, fees, pending deposits/debits, and returned-funds proof? | `424`, `425`, `426`, `475`, `482`, `489`, `506`, `509`, `520`, `521`, `535`, `557`, `562`, `573`, `577`, `884`, `889`, `902`, `903`, `905`, `911`, `912`, `919`, `920`, `950`, `951`, `956`, `957`, `958`, `959`, `961`, `962` | Treat a closure code as insufficient until money, fees, pending transactions, and replacement access are resolved. |
| `FIN-13` Funds availability, hold, and actual withdrawal path | Does the packet join deposit type, banking day, business-day clock, hold/exception basis, notice, available-for-withdrawal date, channel availability, and actual release/use? | `424`, `425`, `426`, `475`, `482`, `489`, `506`, `509`, `520`, `521`, `535`, `557`, `562`, `573`, `577`, `884`, `889`, `902`, `903`, `905`, `911`, `912`, `919`, `920`, `950`, `951`, `956`, `957`, `958`, `959`, `961`, `962` | Do not treat ledger credit or pending balance as usable funds without withdrawal-channel and release evidence. |
| `FIN-14` Garnishment, levy, offset, and protected-benefit access | Does the packet show the order, creditor/agency/court, protected-payment lookback, protected amount, freeze/sweep treatment, notice, exemption path, and post-review available balance? | `424`, `425`, `426`, `475`, `482`, `489`, `506`, `509`, `520`, `521`, `535`, `557`, `562`, `573`, `577`, `884`, `889`, `902`, `903`, `905`, `911`, `912`, `919`, `920`, `950`, `951`, `956`, `957`, `958`, `959`, `961`, `962` | Do not infer access from direct deposit; require proof that protected funds stayed available and any excess freeze was bounded and noticed. |
| `FIN-15` Fintech, custodial-account, and partner-bank ledger reconciliation | Does the packet join app balance, partner bank, custodial account, beneficial owner, subledger balance, recordkeeper, reconciliation, interruption/bankruptcy/receivership event, and payout or transfer outcome? | `424`, `425`, `426`, `475`, `482`, `489`, `506`, `509`, `520`, `521`, `535`, `557`, `562`, `573`, `577`, `884`, `889`, `902`, `903`, `905`, `911`, `912`, `919`, `920`, `950`, `951`, `956`, `957`, `958`, `959`, `961`, `962` | Do not accept app balance, routing/account number, or marketing label as proof that the bank can identify or pay the consumer. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `959` | `FIN-01`, `FIN-02`, `FIN-03`, `FIN-04`, `FIN-05`, `FIN-06`, `FIN-07`, `FIN-08`, `FIN-09`, `FIN-10` |
| `962` | `FIN-01`, `FIN-02`, `FIN-03`, `FIN-04`, `FIN-05`, `FIN-06`, `FIN-07`, `FIN-08`, `FIN-09`, `FIN-10`, `FIN-11`, `FIN-12`, `FIN-13`, `FIN-14`, `FIN-15` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `424` | 15 |
| `425` | 15 |
| `426` | 15 |
| `475` | 15 |
| `482` | 15 |
| `489` | 15 |
| `506` | 15 |
| `509` | 15 |
| `520` | 15 |
| `521` | 15 |
| `535` | 15 |
| `557` | 15 |
| `562` | 15 |
| `573` | 15 |
| `577` | 15 |
| `884` | 15 |
| `889` | 15 |
| `902` | 15 |
| `903` | 15 |
| `905` | 15 |
| `911` | 15 |
| `912` | 15 |
| `919` | 15 |
| `920` | 15 |
| `950` | 15 |
| `951` | 15 |
| `956` | 15 |
| `957` | 15 |
| `958` | 15 |
| `959` | 15 |
| `961` | 15 |
| `962` | 15 |

## Use rule

Run consumer-finance continuity tests whenever a banked or unbanked status, checking/savings/prepaid/card account, direct deposit, ACH/debit/EFT transaction, overdraft/fee, credit report, score, consumer report, debt validation notice, collector contact, garnishment, complaint ID, CFPB/OCC/FTC/state routing, or company response is cited as proof of financial access or remedy. Separate person, account, transaction, credit file, furnisher, debt owner, collector, complaint, regulator, correction, money receipt, and downstream public-service outcome before accepting the row as access.
