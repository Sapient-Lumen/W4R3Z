# Immigration / asylum / status continuity tests matrix

Generated for `rev0799` from `metadata/immigration_status_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `IMM-01` Person, family, identity, and representative lane | Does the packet bind the person/family unit, A-number, receipt numbers, aliases, representative/helper, language/disability needs, address, and urgent service consequences before accepting status evidence? | `424`, `425`, `426`, `475`, `482`, `489`, `507`, `509`, `520`, `530`, `562`, `573`, `577`, `884`, `889`, `894`, `896`, `903`, `905`, `913`, `914`, `915`, `916`, `936`, `937`, `950`, `951`, `954`, `955` | Open a person-status docket and downgrade receipt or portal evidence to denominator state. |
| `IMM-02` Receipt, case status, and processing-time boundary | Are receipt, case status, office/form/category, processing-time posture, service request, biometrics, RFE/NOID, and decision/card production separated? | `424`, `425`, `426`, `475`, `482`, `489`, `507`, `509`, `520`, `530`, `562`, `573`, `577`, `884`, `889`, `894`, `896`, `903`, `905`, `913`, `914`, `915`, `916`, `936`, `937`, `950`, `951`, `954`, `955` | Do not treat case-status or processing-time rows as status or work proof until case action and notice evidence are joined. |
| `IMM-03` Notice and address split across USCIS and EOIR | Are USCIS address records, EOIR address records, service proof, portal/email/SMS notice, returned mail, and deadline/hearing consequences joined? | `424`, `425`, `426`, `475`, `482`, `489`, `507`, `509`, `520`, `530`, `562`, `573`, `577`, `884`, `889`, `894`, `896`, `903`, `905`, `913`, `914`, `915`, `916`, `936`, `937`, `950`, `951`, `954`, `955` | Treat address form submission as incomplete until both relevant agencies and actual notice consequences are verified. |
| `IMM-04` Asylum/protection filing and court routing | Does the packet separate I-589 completion, USCIS or EOIR lane, NTA/court routing, acceptance/rejection, DHS service, evidence, interpreter, interview/hearing, and appeal/remedy? | `424`, `425`, `426`, `475`, `482`, `489`, `507`, `509`, `520`, `530`, `562`, `573`, `577`, `884`, `889`, `894`, `896`, `903`, `905`, `913`, `914`, `915`, `916`, `936`, `937`, `950`, `951`, `954`, `955` | Treat I-589 upload or receipt as filing evidence only until protection lane and court/service state are joined. |
| `IMM-05` Work authorization, EAD clock, and card continuity | Are I-765 category, asylum EAD clock, applicant-caused delays, approval, card production/delivery, renewal, replacement, and employer/agency recognition proven? | `424`, `425`, `426`, `475`, `482`, `489`, `507`, `509`, `520`, `530`, `562`, `573`, `577`, `884`, `889`, `894`, `896`, `903`, `905`, `913`, `914`, `915`, `916`, `936`, `937`, `950`, `951`, `954`, `955` | Do not treat asylum-clock time or I-765 filing as work authorization until card/extension and acceptance evidence exist. |
| `IMM-06` EOIR court file, hearing, and electronic filing | Are ACIS, Respondent Access, ECAS/eROP, hearing date, filings, acceptance/rejection emails, evidence, interpreter, counsel, appeals, and outage/deadline rules separated? | `424`, `425`, `426`, `475`, `482`, `489`, `507`, `509`, `520`, `530`, `562`, `573`, `577`, `884`, `889`, `894`, `896`, `903`, `905`, `913`, `914`, `915`, `916`, `936`, `937`, `950`, `951`, `954`, `955` | Do not treat docket lookup or portal visibility as due process without filing, notice, hearing, language, and remedy evidence. |
| `IMM-07` SAVE and downstream agency verification | Does the packet connect SAVE request, requesting agency, initial/additional verification, CaseCheck, mismatch, agency decision, and correction/restoration route? | `424`, `425`, `426`, `475`, `482`, `489`, `507`, `509`, `520`, `530`, `562`, `573`, `577`, `884`, `889`, `894`, `896`, `903`, `905`, `913`, `914`, `915`, `916`, `936`, `937`, `950`, `951`, `954`, `955` | Treat SAVE as a verification lane only until the benefit/license/work/school decision and correction are proven. |
| `IMM-08` Digital, paper, language, and assisted-access fallback | Are portal account, device/broadband, mobile/desktop limits, paper filing, language/disability access, trusted helper, and account recovery available before deadlines run? | `424`, `425`, `426`, `475`, `482`, `489`, `507`, `509`, `520`, `530`, `562`, `573`, `577`, `884`, `889`, `894`, `896`, `903`, `905`, `913`, `914`, `915`, `916`, `936`, `937`, `950`, `951`, `954`, `955` | Add assisted access and deadline protection before relying on online-only case or filing surfaces. |
| `IMM-09` Custody, enforcement, release, and status consequence | If detention, transfer, check-in, bond, release, removal, or custody transport is involved, are notice, counsel, medical, family, court, and status consequences preserved? | `424`, `425`, `426`, `475`, `482`, `489`, `507`, `509`, `520`, `530`, `562`, `573`, `577`, `884`, `889`, `894`, `896`, `903`, `905`, `913`, `914`, `915`, `916`, `936`, `937`, `950`, `951`, `954`, `955` | Activate custody/reentry and watchlist/border tests before treating enforcement rows as status resolution. |
| `IMM-10` Remedy, correction, and source currentness | Does the packet prove service request, inquiry, motion, appeal, record correction, card reissue, SAVE correction, restored downstream service, and source-currentness posture? | `424`, `425`, `426`, `475`, `482`, `489`, `507`, `509`, `520`, `530`, `562`, `573`, `577`, `884`, `889`, `894`, `896`, `903`, `905`, `913`, `914`, `915`, `916`, `936`, `937`, `950`, `951`, `954`, `955` | Downgrade complaint/inquiry status to unresolved until corrected records and restored consequences are documented. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `955` | `IMM-01`, `IMM-02`, `IMM-03`, `IMM-04`, `IMM-05`, `IMM-06`, `IMM-07`, `IMM-08`, `IMM-09`, `IMM-10` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `424` | 10 |
| `425` | 10 |
| `426` | 10 |
| `475` | 10 |
| `482` | 10 |
| `489` | 10 |
| `507` | 10 |
| `509` | 10 |
| `520` | 10 |
| `530` | 10 |
| `562` | 10 |
| `573` | 10 |
| `577` | 10 |
| `884` | 10 |
| `889` | 10 |
| `894` | 10 |
| `896` | 10 |
| `903` | 10 |
| `905` | 10 |
| `913` | 10 |
| `914` | 10 |
| `915` | 10 |
| `916` | 10 |
| `936` | 10 |
| `937` | 10 |
| `950` | 10 |
| `951` | 10 |
| `954` | 10 |
| `955` | 10 |

## Use rule

Run immigration-status tests whenever USCIS receipts, case-status pages, processing times, I-589 asylum filings, I-765 work-authorization applications, asylum EAD-clock evidence, USCIS/EOIR address changes, immigration-court dockets, Respondent Access/ECAS/eROP records, SAVE responses, CaseCheck, detention/release, or downstream benefit/license/work/school decisions are cited as proof that a person has status, work authorization, notice, hearing safety, access, or remedy. Separate person, case, notice, filing, asylum/protection, work, court, SAVE/downstream, digital access, custody, representative, and repair states before treating a receipt, docket, clock, address form, portal, or verification response as status.
