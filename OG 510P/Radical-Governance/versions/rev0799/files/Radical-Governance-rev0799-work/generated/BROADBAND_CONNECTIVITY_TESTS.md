# Broadband / telecommunications / digital-access continuity tests matrix

Generated for `rev0799` from `metadata/broadband_connectivity_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `CONNECT-01` Household, address, and serviceability | Does the packet bind the household, address/unit, BSL, mobile area, public-service dependency, and installation/serviceability state before accepting coverage evidence? | `475`, `489`, `509`, `520`, `535`, `948`, `950`, `951` | Open a household-location docket and downgrade map rows to denominator evidence. |
| `CONNECT-02` Provider availability, challenge, and local verification | Are provider-reported availability, technology, speed tier, line extension, mobile signal, and map/challenge outcomes separated from actual service? | `475`, `535`, `911`, `912`, `950`, `951` | Do not treat self-reported availability as access until challenge and installation evidence are joined. |
| `CONNECT-03` Affordability, bill, and subsidy cliff | Does the packet join plan price, fees, deposit, data cap, Lifeline, ACP end state, bill shock, shutoff risk, and low-cost alternatives? | `489`, `509`, `520`, `895`, `897`, `950`, `951` | Open an affordability file and mark labels or subsidy rows as incomplete. |
| `CONNECT-04` Lifeline, National Verifier, and recertification | Can eligibility, documentation, National Verifier state, enrollment, annual recertification, benefit amount, tribal support, and loss notice be reconstructed? | `903`, `905`, `907`, `908`, `950`, `951` | Do not treat eligibility as service until enrollment and recertification continuity are proven. |
| `CONNECT-05` Device, premises, accessibility, and language | Does the packet check device, modem/router, wiring, power/backup, assistive technology, accessible equipment, language route, privacy, and digital skills? | `508`, `520`, `521`, `940`, `941`, `950`, `951` | Treat network availability as incomplete until household usability is verified. |
| `CONNECT-06` Performance, data caps, and actual usability | Are measured speed, latency, congestion, data caps, throttling, reliability, and performance terms joined to user tasks? | `878`, `930`, `931`, `942`, `950`, `951` | Do not treat advertised speed or labels as usable performance. |
| `CONNECT-07` Outage, restoration, and degraded public-service mode | Does the packet join outage reports, provider repair tickets, restoration time, power dependency, backup, public-service fallback, and customer credits? | `911`, `912`, `930`, `931`, `946`, `947`, `950`, `951` | Do not treat outage filings or restoration statements as household repair. |
| `CONNECT-08` Public-service portal and deadline continuity | Are portal uptime, user connectivity, identity proofing, notice, upload, telehealth, court, school, benefit, tax, work, or emergency tasks joined to deadline preservation? | `878`, `884`, `889`, `903`, `913`, `914`, `950`, `951` | Do not treat portal uptime as user access without connectivity and deadline proof. |
| `CONNECT-09` Community anchor and public-access fallback | Can libraries, schools, clinics, shelters, public Wi-Fi, hotspots, device lending, hours, privacy, transport, and accessibility be verified? | `508`, `520`, `531`, `928`, `944`, `948`, `950`, `951` | Do not treat public Wi-Fi as home access unless it preserves the specific service duty. |
| `CONNECT-10` Complaint, challenge, equal-access, and correction loop | Does the packet track FCC/state/provider complaint, map challenge, digital-discrimination/equal-access route, billing dispute, installation remedy, corrected row, and learning loop? | `475`, `489`, `573`, `905`, `919`, `920`, `950`, `951` | Do not treat complaint availability as remedy without changed access or preserved outcome. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `951` | `CONNECT-01`, `CONNECT-02`, `CONNECT-03`, `CONNECT-04`, `CONNECT-05`, `CONNECT-06`, `CONNECT-07`, `CONNECT-08`, `CONNECT-09`, `CONNECT-10` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `475` | 3 |
| `489` | 3 |
| `508` | 2 |
| `509` | 2 |
| `520` | 4 |
| `521` | 1 |
| `531` | 1 |
| `535` | 2 |
| `573` | 1 |
| `878` | 2 |
| `884` | 1 |
| `889` | 1 |
| `895` | 1 |
| `897` | 1 |
| `903` | 2 |
| `905` | 2 |
| `907` | 1 |
| `908` | 1 |
| `911` | 2 |
| `912` | 2 |
| `913` | 1 |
| `914` | 1 |
| `919` | 1 |
| `920` | 1 |
| `928` | 1 |
| `930` | 2 |
| `931` | 2 |
| `940` | 1 |
| `941` | 1 |
| `942` | 1 |
| `944` | 1 |
| `946` | 1 |
| `947` | 1 |
| `948` | 2 |
| `950` | 10 |
| `951` | 10 |

## Use rule

Run broadband/connectivity tests whenever a coverage map, Broadband Serviceable Location, provider availability claim, speed tier, broadband label, Lifeline/National Verifier row, ACP history, BEAD milestone, public Wi-Fi fallback, outage filing, portal dependency, or digital-access complaint is cited as proof that a person can use public services online. Separate household, address, serviceability, affordability, subsidy, device, performance, outage, portal task, fallback, remedy, and source-currentness before treating a polygon, row, label, dashboard, or filing as access.
