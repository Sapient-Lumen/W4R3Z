# Emergency response / 911 / EMS / 988 / public alerting continuity tests matrix

Generated for `rev0799` from `metadata/emergency_response_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `ER-01` Caller/person/channel binding | Does the record bind the affected person, caller/bystander, channel, language, disability/access needs, callback, and location uncertainty before scoring emergency access? | `424`, `426`, `475`, `502`, `521`, `530`, `946`, `947` | Open a person/channel ledger and stop treating a call or contact row as rescue. |
| `ER-02` Routing and PSAP continuity | Can the packet prove correct PSAP/center routing, transfer, queue, abandoned/overflow state, backup path, and outage fallback? | `425`, `475`, `502`, `510`, `515`, `930`, `946`, `947` | Join carrier, PSAP, transfer, backup, and outage records before treating answer as service. |
| `ER-03` Actionable location | Was location accurate, timely, responder-visible, and actionable, including indoor, z-axis, dispatchable-location, GIS, and rural/tribal edges? | `425`, `502`, `510`, `515`, `531`, `946`, `947` | Separate coordinate, routing, GIS, and responder use; repair map/location before closing rescue. |
| `ER-04` Dispatch/CAD to unit handoff | Does CAD/dispatch evidence connect priority, unit recommendation, assignment, radio/MDT delivery, mutual aid, status updates, and scene arrival/contact? | `422`, `425`, `475`, `502`, `535`, `946`, `947` | Do not close on dispatch; demand unit contact or justified non-response evidence. |
| `ER-05` EMS clinical and transport continuity | Does EMS evidence prove assessment, treatment, medication, refusal, transport, destination, diversion, transfer-of-care, and clinical QA where relevant? | `506`, `535`, `855`, `923`, `924`, `946`, `947` | Treat NEMSIS/national data as denominator only until local EMS clinical and handoff records are joined. |
| `ER-06` 988 and behavioral-crisis continuity | Does 988/crisis evidence prove routing, answer, backup flowout, language/deaf access, safety planning, mobile crisis, 911 transfer, and follow-up? | `506`, `521`, `523`, `879`, `923`, `946`, `947` | Do not treat contact metrics as stabilization; join local crisis and transfer/follow-up records. |
| `ER-07` Public alert and warning receipt | Can the packet prove IPAWS/WEA/EAS authorization, message content, geography, timing, language/accessibility, receipt, and protective action? | `424`, `426`, `475`, `511`, `530`, `911`, `942`, `946`, `947` | Treat alert sent as unproven warning until receipt/comprehension/protective-action evidence is joined. |
| `ER-08` Degraded operations and resilience | Does the packet document telecom, NG911, CAD, radio, cyber, power, vendor, backup-center, manual-log, reroute, and restoration states? | `407`, `420`, `422`, `510`, `859`, `930`, `931`, `946`, `947` | Open degraded-mode incident command and stop treating reliability certification as continuity. |
| `ER-09` Equity, language, disability, and setting access | Were LEP, Deaf/HoH, disability, age, rural/tribal, homelessness, custody, school, nursing-home, hospital, and household-setting risks handled explicitly? | `424`, `426`, `521`, `530`, `531`, `934`, `936`, `938`, `940`, `946`, `947` | Add access/function-needs lanes before claiming emergency service reached all affected people. |
| `ER-10` Outcome, remedy, and source-currentness | Does the packet distinguish rules, self-reports, datasets, dashboards, monthly metrics, alerts, and incident records, then tie outcomes to QA/corrective action? | `419`, `422`, `457`, `857`, `910`, `946`, `947` | Keep national metrics as denominator-only and require incident-level outcome and repair records. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `947` | `ER-01`, `ER-02`, `ER-03`, `ER-04`, `ER-05`, `ER-06`, `ER-07`, `ER-08`, `ER-09`, `ER-10` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `407` | 1 |
| `419` | 1 |
| `420` | 1 |
| `422` | 3 |
| `424` | 3 |
| `425` | 3 |
| `426` | 3 |
| `457` | 1 |
| `475` | 4 |
| `502` | 4 |
| `506` | 2 |
| `510` | 3 |
| `511` | 1 |
| `515` | 2 |
| `521` | 3 |
| `523` | 1 |
| `530` | 3 |
| `531` | 2 |
| `535` | 2 |
| `855` | 1 |
| `857` | 1 |
| `859` | 1 |
| `879` | 1 |
| `910` | 1 |
| `911` | 1 |
| `923` | 2 |
| `924` | 1 |
| `930` | 2 |
| `931` | 1 |
| `934` | 1 |
| `936` | 1 |
| `938` | 1 |
| `940` | 1 |
| `942` | 1 |
| `946` | 10 |
| `947` | 10 |

## Use rule

Run emergency-response continuity tests whenever 911, text-to-911, RTT, VoIP/wireless routing, PSAP answer, NG911 profile, FCC reliability/location/outage evidence, CAD dispatch, radio/MDT delivery, EMS/NEMSIS data, 988 contact metrics, mobile crisis, IPAWS, WEA/EAS, outage, cyber, power, language/accessibility, or after-action records are cited as proof that help reached people. Separate caller/person, channel, routing, location, dispatch, responder, care, crisis, alert, degraded-mode, equity, remedy, and source-currentness before treating a call, dispatch, contact, alert, or dataset as rescue.
