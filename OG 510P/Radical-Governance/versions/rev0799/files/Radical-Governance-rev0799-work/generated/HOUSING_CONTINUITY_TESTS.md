# Housing stability / eviction / rental-assistance continuity tests matrix

Generated for `rev0799` from `metadata/housing_continuity_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `HC-01` Household, unit, landlord, and authority split | Can the packet identify the household, unit, lease / occupancy, subsidy, landlord / property manager, plaintiff, payment recipient, authorized helper, language, disability, and safety constraints before assigning housing status? | `424`, `426`, `894`, `901`, `905`, `928`, `929` | Do not treat a portal account, docket caption, landlord ledger, or voucher record as the person/unit map; reconcile identities first. |
| `HC-02` Notice, service, and possession clock | Does the record show rent demand or pay-or-quit notice, service method, summons, hearing, default, judgment, warrant, lockout / execution, move-out, and appeal clock as separate states? | `424`, `425`, `874`, `894`, `917`, `928`, `929` | Do not infer physical eviction from filing alone or safety from a closed docket alone; build the possession timeline. |
| `HC-03` Rental-assistance posting and court effect | Can assistance be traced from application through eligibility, award, landlord acceptance, payment, ledger posting, stay / dismissal effect, residual balance, court costs, and future-rent bridge? | `425`, `426`, `894`, `897`, `928`, `929` | Do not count assistance as stability until it changes the ledger and possession clock. |
| `HC-04` Representation capacity and hearing posture | Does the packet distinguish outreach, intake, eligibility, advice, brief service, full representation, adjournment, settlement quality, hearing coverage, and provider capacity? | `424`, `426`, `856`, `894`, `905`, `928`, `929` | Do not treat a right-to-counsel law or referral as counsel at the consequential event. |
| `HC-05` Tenant-screening record and adverse action | Can eviction, criminal, credit, and court-record entries in tenant-screening reports be traced to source, disposition, age, sealed / dismissed status, adverse action, consumer disclosure, dispute, correction, and reapplication effect? | `425`, `857`, `874`, `917`, `928`, `929` | Do not call a case resolved until downstream tenant-screening records and adverse-action routes are bounded. |
| `HC-06` Shelter, relocation, and re-housing bridge | If tenancy is not preserved, does the record show shelter / motel / rapid-rehousing placement, transport, storage, school / work continuity, disability accommodation, safety, pets, and permanent-housing search? | `424`, `426`, `856`, `894`, `923`, `928`, `929` | Do not treat a referral, bed count, or PIT statistic as a safe relocation outcome. |
| `HC-07` Informal eviction and extra-legal pressure | Does the packet look for lockout, utility shutoff pressure, harassment, constructive eviction, uninhabitable conditions, retaliation, illegal fees, or move-out under threat that may not appear as a clean court outcome? | `420`, `424`, `425`, `856`, `925`, `928`, `929` | Do not rely only on court records where informal or constructive displacement is plausible. |
| `HC-08` Tail risk: debt, sealing, credit, and recurrence | Does the record preserve debt, judgment, collections, court costs, sealing / expungement, screening correction, reapplication, repeat filings, next rent, and subsidy / renewal clocks after the immediate case closes? | `425`, `857`, `884`, `894`, `897`, `928`, `929` | Do not close the continuity packet at dismissal, payment, or move-out if durable exclusion remains. |
| `HC-09` Equity denominators and landlord concentration | Can filing, default, judgment, warrant, execution, assistance, representation, screening, shelter, and repeat-filing outcomes be disaggregated by race, income, disability, language, family status, neighborhood, property type, subsidy status, and landlord concentration? | `856`, `857`, `894`, `917`, `919`, `928`, `929` | Do not call a program equitable from citywide or statewide averages alone. |
| `HC-10` Source-currentness and local-law boundary | Does the packet distinguish live dashboards, annual reports, local court rules, expired federal assistance authority, local program windows, enforcement actions, and research reports before generalizing? | `857`, `910`, `917`, `919`, `927`, `928`, `929` | Do not generalize a local portal, expired federal program, or monitored-sites dataset into a national operational rule. |
| `HC-11` Household outcome and non-user denominator | Does the packet distinguish filing, portal, counsel, payment, screening, and shelter surfaces from household outcome, informal eviction, non-use, and subgroup burden evidence? | `404`, `425`, `426`, `857`, `894`, `927`, `928`, `929`, `983`, `984` | Do not treat eviction filing counts, portal states, counsel eligibility, payment awards, screening pages, or shelter counts as household stability proof until outcome and non-user denominators are explicit. |
| `HC-12` Housing remedy-completion and durable-stability receipt | Can the packet prove that a housing remedy changed possession, debt, screening, shelter, or durable housing status rather than merely being offered, awarded, or logged? | `404`, `425`, `426`, `719`, `720`, `857`, `894`, `927`, `928`, `929`, `983`, `984` | Do not score assistance approval, payment issuance, legal eligibility, report correction, or shelter referral as repair until durable household consequence is evidenced. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `929` | `HC-01`, `HC-02`, `HC-03`, `HC-04`, `HC-05`, `HC-06`, `HC-07`, `HC-08`, `HC-09`, `HC-10`, `HC-11`, `HC-12` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `404` | 2 |
| `420` | 1 |
| `424` | 5 |
| `425` | 7 |
| `426` | 6 |
| `719` | 1 |
| `720` | 1 |
| `856` | 4 |
| `857` | 6 |
| `874` | 2 |
| `884` | 1 |
| `894` | 9 |
| `897` | 2 |
| `901` | 1 |
| `905` | 2 |
| `910` | 1 |
| `917` | 4 |
| `919` | 2 |
| `923` | 1 |
| `925` | 1 |
| `927` | 3 |
| `928` | 12 |
| `929` | 12 |
| `983` | 2 |
| `984` | 2 |

## Use rule

Run housing-continuity tests whenever rental assistance, eviction notices, court filings, possession clocks, right-to-counsel routes, tenant-screening reports, shelter referrals, relocation, voucher / subsidy cliffs, landlord ledgers, or informal displacement can determine whether a household is actually stably housed. Separate household, unit, arrears, assistance, court, possession, representation, screening, shelter, and tail-risk states before treating a portal, docket, report, or referral as housing stability.
