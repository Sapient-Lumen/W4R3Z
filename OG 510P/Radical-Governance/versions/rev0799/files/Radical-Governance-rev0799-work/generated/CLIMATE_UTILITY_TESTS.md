# Climate / utility shutoff and medical-baseline continuity tests matrix

Generated for `rev0799` from `metadata/climate_utility_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `CU-01` Account and event-state split | Can the packet separate final notice, nonpayment shutoff, reconnection, storm outage, PSPS / de-energization, fuel delivery, arrears, deposit, and payment-plan states before calling service continuous? | `420`, `424`, `425`, `894`, `897`, `925`, `926` | Do not merge outage and nonpayment logic; build an event-type ladder before assigning duty, remedy, or metric. |
| `CU-02` Medical baseline and device inventory | Does the record identify medical-baseline / serious-illness state, electricity-dependent equipment, medication refrigeration, battery duration, caregiver / representative contact, and renewal clock? | `422`, `424`, `905`, `923`, `925`, `926` | Treat medical flags as stale until equipment, renewal, contact, and backup-power requirements are visible. |
| `CU-03` Energy-assistance and arrears posting | Can assistance eligibility, award, vendor posting, shutoff hold, reconnection fee, residual debt, and next bill be traced at account level? | `424`, `426`, `894`, `897`, `923`, `925`, `926` | Do not count assistance as continuity until the utility or vendor record shows the disconnection clock changed. |
| `CU-04` Climate hazard and life-safety clock | Does the packet set a safe-time clock for heat, cold, smoke, storm, battery duration, medication cold chain, elevator / mobility access, and communications? | `420`, `422`, `424`, `851`, `925`, `926` | Do not use ordinary billing or restoration queues when hazard duration exceeds the household life-safety clock. |
| `CU-05` Notice, contact cascade, and representative route | Does the record show accessible notice and live contact attempts to customer, authorized representative, caregiver, clinician, utility, emergency manager, and community route? | `425`, `426`, `905`, `925`, `926` | A single mailed, emailed, or IVR notice is not enough for medical-baseline or climate-hazard continuity. |
| `CU-06` Backup power, cooling, warming, and relocation logistics | Is there evidence of usable battery / generator / charging support, cooling or warming access, transport, caregiver accommodation, and device-compatible relocation? | `420`, `422`, `424`, `851`, `925`, `926` | Do not cite a cooling center, shelter, or preparedness page as safety without transport and compatibility evidence. |
| `CU-07` PSPS and wildfire de-energization boundaries | Can PSPS authority, affected circuit / territory, medical-baseline notice, actual de-energization, restoration, and vulnerable-customer support be separated? | `420`, `424`, `851`, `925`, `926` | Do not treat medical-baseline enrollment or PSPS notice as energization or life-safety support. |
| `CU-08` Reconnection, restoration, and treatment repair tail | Does the packet track service restoration, reconnection fees, repeated shutoff risk, food / medication spoilage, equipment damage, missed treatment, and complaint / appeal outcomes? | `424`, `425`, `426`, `894`, `897`, `923`, `925`, `926` | Do not close the case at restoration if treatment, debt, or equipment damage remains unresolved. |
| `CU-09` Public metrics and subgroup denominators | Do public reports separate final notices, shutoffs, reconnections, medical-baseline accounts, assistance posting lag, climate-event disconnections, service territories, and vulnerability denominators? | `420`, `424`, `857`, `894`, `897`, `925`, `926` | Aggregate disconnection counts cannot prove equity or safety without medical, assistance, territory, and climate-event denominators. |
| `CU-10` Cross-program handoff and emergency-management route | Can utility, LIHEAP / energy office, public health, emergency management, disability services, weatherization / repair, and health-system handoffs be traced to an accountable owner? | `424`, `425`, `426`, `851`, `897`, `905`, `925`, `926` | Do not count referral as repair until the receiving program has an owner, deadline, and outcome receipt. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `926` | `CU-01`, `CU-02`, `CU-03`, `CU-04`, `CU-05`, `CU-06`, `CU-07`, `CU-08`, `CU-09`, `CU-10` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `420` | 5 |
| `422` | 3 |
| `424` | 9 |
| `425` | 4 |
| `426` | 4 |
| `851` | 4 |
| `857` | 1 |
| `894` | 4 |
| `897` | 5 |
| `905` | 3 |
| `923` | 3 |
| `925` | 10 |
| `926` | 10 |

## Use rule

Run climate / utility tests whenever utility final notices, nonpayment shutoffs, reconnections, LIHEAP or state energy assistance, medical-baseline or serious-illness certificates, electricity-dependent equipment, refrigerated medication, heat / cold / smoke / storm risk, PSPS / de-energization, outage maps, cooling or warming centers, backup power, transport, or emergency-management outreach can determine whether a household actually retains life-safety utility continuity. Separate account, medical, assistance, hazard, notice, backup, reconnection, and aftercare states before treating an account code, certificate, map, award, or notice as safety.
