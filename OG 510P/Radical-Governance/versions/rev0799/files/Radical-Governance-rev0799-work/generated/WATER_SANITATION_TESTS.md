# Water and sanitation continuity tests matrix

Generated for `rev0799` from `metadata/water_sanitation_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `WATER-01` User, premise, and system identity | Does the packet identify household/facility, service address, PWSID or private well/septic edge, premise plumbing, vulnerable users, and responsible owners before accepting a water status? | `424`, `425`, `426`, `510`, `532`, `942`, `943` | Open a user-system docket and downgrade compliance rows to denominator evidence. |
| `WATER-02` Operating state and pressure | Can source water, treatment, pressure, storage, distribution, staffing, chemicals, backup power, and wastewater/sewer state be reconstructed for the relevant period? | `510`, `532`, `851`, `852`, `925`, `942`, `943` | Treat plant/service status as incomplete until operating and sanitation records are joined. |
| `WATER-03` Compliance data boundary | Are SDWIS, ECHO, CCR, lab, public-notice, and enforcement rows separated by date, source role, and currentness? | `857`, `927`, `942`, `943` | Mark federal/state data as source posture, not tap safety, until current local records are joined. |
| `WATER-04` Lead and premise plumbing | Does the packet join lead service line, galvanized/premise plumbing, schools/child care, filters, flushing, replacement, disturbance, and post-work sampling evidence? | `532`, `925`, `942`, `943` | Do not treat inventory or rule compliance as lead exposure reduction; open a lead-tap repair file. |
| `WATER-05` PFAS and chemical risk | Are PFAS/chemical test results, treatment, disposal, public notice, vulnerable-population advice, funding, and compliance clocks joined? | `857`, `923`, `942`, `943` | Do not treat a final/proposed rule or extension as exposure reduction without treatment and interim-water proof. |
| `WATER-06` Advisory reach and alternate water | Did boil, do-not-drink, or do-not-use advisories reach affected users in usable formats with bottled water, formula/dialysis/medical, school, shelter, care, and sanitation support? | `424`, `426`, `923`, `925`, `934`, `936`, `938`, `942`, `943` | Treat advisory posting as incomplete until receipt and alternate-water logistics are proven. |
| `WATER-07` Wastewater, septic, and stormwater | Are wastewater treatment, sewer overflow, septic failure, stormwater/flood intrusion, sanitation in congregate settings, and cleanup records joined to public-health risk? | `532`, `851`, `852`, `936`, `938`, `942`, `943` | Do not treat drinking-water compliance or NPDES status as sanitation continuity without sewer/septic/stormwater proof. |
| `WATER-08` Emergency, climate, and AWIA readiness | Can AWIA RRA/ERP, mutual aid, alternate source, tankers, backup power, fuel, chemicals, operators, drought/flood/wildfire/heat, and priority users be tested? | `511`, `925`, `926`, `942`, `943` | Treat certification as a planning signal only; require executable emergency-water proof. |
| `WATER-09` Cyber/OT and supplier resilience | Are remote access, authentication, OT segmentation, vendor access, manual operation, incident response, and recovery proof joined to water service continuity? | `859`, `930`, `931`, `942`, `943` | Do not treat cyber guidance or checklist completion as resilient water without utility-specific controls and recovery proof. |
| `WATER-10` Affordability, shutoff, remedy, and equity | Are rates, arrears, shutoffs, payment plans, low-income/vulnerable protections, bottled-water costs, complaints, reimbursement, repair receipts, and equity denominators joined? | `489`, `513`, `925`, `926`, `928`, `942`, `943` | Open an affordability/remedy docket before treating service account or assistance page as water access. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `943` | `WATER-01`, `WATER-02`, `WATER-03`, `WATER-04`, `WATER-05`, `WATER-06`, `WATER-07`, `WATER-08`, `WATER-09`, `WATER-10` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `424` | 2 |
| `425` | 1 |
| `426` | 2 |
| `489` | 1 |
| `510` | 2 |
| `511` | 1 |
| `513` | 1 |
| `532` | 4 |
| `851` | 2 |
| `852` | 2 |
| `857` | 2 |
| `859` | 1 |
| `923` | 2 |
| `925` | 5 |
| `926` | 2 |
| `927` | 1 |
| `928` | 1 |
| `930` | 1 |
| `931` | 1 |
| `934` | 1 |
| `936` | 2 |
| `938` | 2 |
| `942` | 10 |
| `943` | 10 |

## Use rule

Run water/sanitation tests whenever drinking-water system rows, SDWIS/ECHO data, Consumer Confidence Reports, lead service line inventories, PFAS rules, boil/do-not-drink/do-not-use advisories, AWIA risk/resilience plans, wastewater/septic/stormwater records, water shutoffs, affordability burdens, cyber/OT incidents, emergency supply, or critical-facility water dependencies can determine whether people actually have safe water and sanitation. Separate user, premise, source, treatment, contaminant, notice, wastewater, emergency, cyber, affordability, and remedy states before treating a compliance row, report, inventory, permit, or certification as safe water.
