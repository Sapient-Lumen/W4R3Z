# Tax filing / refund / credit continuity tests matrix

Generated for `rev0799` from `metadata/tax_refund_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `TAX-01` Taxpayer, household, and authority spine | Does the packet bind taxpayer, spouse, dependents, TINs, address, bank account, representative/preparer, language/disability, and hardship stakes before accepting a tax row? | `424`, `425`, `426`, `475`, `482`, `489`, `506`, `509`, `520`, `521`, `535`, `557`, `562`, `573`, `577`, `884`, `889`, `902`, `903`, `905`, `911`, `912`, `944`, `945`, `950`, `951`, `956`, `957` | Open a taxpayer-household docket and downgrade return/transcript evidence to denominator state. |
| `TAX-02` Return filing and processing boundary | Are e-file/paper, accept/reject, processing, amended/prior-year state, extension, state-return handoff, and preparer/free-file route separated? | `424`, `425`, `426`, `475`, `482`, `489`, `506`, `509`, `520`, `521`, `535`, `557`, `562`, `573`, `577`, `884`, `889`, `902`, `903`, `905`, `911`, `912`, `944`, `945`, `950`, `951`, `956`, `957` | Do not treat submitted or accepted as processed until IRS and state filing states are joined. |
| `TAX-03` Refund tracker and payment receipt | Is Where’s My Refund/account status joined to refund amount, issue date, direct deposit, rejected/frozen deposit, paper check, nonreceipt, and bank/prepaid account control? | `424`, `425`, `426`, `475`, `482`, `489`, `506`, `509`, `520`, `521`, `535`, `557`, `562`, `573`, `577`, `884`, `889`, `902`, `903`, `905`, `911`, `912`, `944`, `945`, `950`, `951`, `956`, `957` | Treat tracker status as navigation evidence until payment receipt or offset/nonreceipt repair is shown. |
| `TAX-04` EITC, CTC, ACTC, and refundable-credit proof | Are credit rows joined to qualifying person, valid TIN, earned income, residency, filing status, due diligence, disallowance, and appeal/recertification? | `424`, `425`, `426`, `475`, `482`, `489`, `506`, `509`, `520`, `521`, `535`, `557`, `562`, `573`, `577`, `884`, `889`, `902`, `903`, `905`, `911`, `912`, `944`, `945`, `950`, `951`, `956`, `957` | Do not treat a credit schedule or table as entitlement until qualifying and disallowance evidence is joined. |
| `TAX-05` ITIN application, renewal, and original-document continuity | Are W-7, new/renewal status, tax-season processing clock, original documents, CAA/VITA route, attached return, credit effects, and refund delay joined? | `424`, `425`, `426`, `475`, `482`, `489`, `506`, `509`, `520`, `521`, `535`, `557`, `562`, `573`, `577`, `884`, `889`, `902`, `903`, `905`, `911`, `912`, `944`, `945`, `950`, `951`, `956`, `957` | Treat ITIN submission as pending identity infrastructure until document and processing consequences are resolved. |
| `TAX-06` Identity theft, IP PIN, and fraud-filter continuity | Are IP PIN, TPP letter, identity verification, Form 14039/IDTVA, duplicate filing, account correction, refund hold, and dependent identity resolved? | `424`, `425`, `426`, `475`, `482`, `489`, `506`, `509`, `520`, `521`, `535`, `557`, `562`, `573`, `577`, `884`, `889`, `902`, `903`, `905`, `911`, `912`, `944`, `945`, `950`, `951`, `956`, `957` | Do not treat fraud control as neutral if it delays refund or account correction without hardship route. |
| `TAX-07` Offset, debt, and injured-spouse/hardship route | Are TOP/BFS/IRS offset, debt type, creditor agency, notice, call/contact route, injured-spouse claim, offset-bypass hardship, and restored payment tracked? | `424`, `425`, `426`, `475`, `482`, `489`, `506`, `509`, `520`, `521`, `535`, `557`, `562`, `573`, `577`, `884`, `889`, `902`, `903`, `905`, `911`, `912`, `944`, `945`, `950`, `951`, `956`, `957` | Do not treat offset as resolved until debt correctness and hardship/injured-spouse routes are traceable. |
| `TAX-08` Notice, audit, math-error, and appeal deadlines | Are mailed/online notices, math-error/audit/exam/disallowance letters, deadlines, receipt/comprehension, representative authority, and appeal or Tax Court route joined? | `424`, `425`, `426`, `475`, `482`, `489`, `506`, `509`, `520`, `521`, `535`, `557`, `562`, `573`, `577`, `884`, `889`, `902`, `903`, `905`, `911`, `912`, `944`, `945`, `950`, `951`, `956`, `957` | Do not count notice as meaningful until a usable response route and preserved deadline are shown. |
| `TAX-09` Free filing, assisted access, and digital/paper fallback | Are Free File, Fillable Forms, VITA/TCE, TAC, online account, phone, paper, language/disability, device/broadband, and state-return handoff tested? | `424`, `425`, `426`, `475`, `482`, `489`, `506`, `509`, `520`, `521`, `535`, `557`, `562`, `573`, `577`, `884`, `889`, `902`, `903`, `905`, `911`, `912`, `944`, `945`, `950`, `951`, `956`, `957` | Do not treat free filing as access until the taxpayer can actually complete federal/state filing and remedy tasks. |
| `TAX-10` Hardship outcome and restored liquidity | Does the packet prove that refund, credit, offset, ITIN, identity, notice, or appeal repair restored household liquidity or preserved basic needs? | `424`, `425`, `426`, `475`, `482`, `489`, `506`, `509`, `520`, `521`, `535`, `557`, `562`, `573`, `577`, `884`, `889`, `902`, `903`, `905`, `911`, `912`, `944`, `945`, `950`, `951`, `956`, `957` | Keep the case open as operational harm until household consequence and repair receipt are documented. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `957` | `TAX-01`, `TAX-02`, `TAX-03`, `TAX-04`, `TAX-05`, `TAX-06`, `TAX-07`, `TAX-08`, `TAX-09`, `TAX-10` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `424` | 10 |
| `425` | 10 |
| `426` | 10 |
| `475` | 10 |
| `482` | 10 |
| `489` | 10 |
| `506` | 10 |
| `509` | 10 |
| `520` | 10 |
| `521` | 10 |
| `535` | 10 |
| `557` | 10 |
| `562` | 10 |
| `573` | 10 |
| `577` | 10 |
| `884` | 10 |
| `889` | 10 |
| `902` | 10 |
| `903` | 10 |
| `905` | 10 |
| `911` | 10 |
| `912` | 10 |
| `944` | 10 |
| `945` | 10 |
| `950` | 10 |
| `951` | 10 |
| `956` | 10 |
| `957` | 10 |

## Use rule

Run tax-refund continuity tests whenever federal or state tax return rows, IRS filing-season data, Where's My Refund, refund transcripts, EITC, CTC, ACTC, refundable credits, ITIN applications/renewals, IP PINs, identity-theft victim assistance, direct deposit, paper checks, Treasury offsets, Free File, VITA/TCE, Taxpayer Assistance Centers, TAS cases, notices, audits, math-error corrections, or appeal deadlines are cited as proof that a household received tax relief. Separate taxpayer, return, credit, identity/ITIN, refund/payment, offset, notice/appeal, assisted access, and hardship outcome before treating a return, tracker, schedule, PIN, or offset row as relief.
