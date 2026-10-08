# Food and nutrition assistance continuity tests matrix

Generated for `rev0799` from `metadata/food_nutrition_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `FOOD-01` Participant and household identity | Does the packet bind household, child, infant, pregnancy/postpartum category, disability, language, homeless/custody/care/school status, tribal/rural edge, and representative authority before accepting a food-assistance status? | `424`, `425`, `426`, `513`, `520`, `524`, `944`, `945` | Open a participant-continuity docket and downgrade program rows to denominator evidence. |
| `FOOD-02` Eligibility and clock integrity | Can application, expedited SNAP, recertification, WIC certification, direct certification, verification, notice, and appeal clocks be reconstructed? | `425`, `473`, `482`, `509`, `895`, `944`, `945` | Treat eligibility/approval as incomplete until clock and notice records are joined. |
| `FOOD-03` Issuance and spendability | Is the benefit actually spendable through EBT/eWIC card/PIN/account, issuance date, online purchase, POS, replacement-card, and transaction evidence? | `538`, `574`, `895`, `923`, `944`, `945` | Do not count issued benefits as food access until card and transaction usability are proven. |
| `FOOD-04` Retailer and food availability | Does retailer evidence show authorized store, distance, stock, formula/food package, price, transport, disability access, delivery/online route, and rural/tribal availability? | `513`, `531`, `577`, `942`, `944`, `945` | Downgrade retailer locators to access denominators until reachable food is proven. |
| `FOOD-05` WIC service delivery | Does the WIC lane prove certification appointment, nutrition-risk assessment, eWIC issuance, food package/formula, breastfeeding support, referrals, proxy pickup, and redemption? | `506`, `520`, `524`, `944`, `945` | Treat WIC participation/category rows as incomplete until service and redemption records are joined. |
| `FOOD-06` Child meals and summer gap | Are school breakfast/lunch, CACFP, SFSP, Summer EBT, special diets, school closure, meal-service days, direct certification, and child-level receipt joined? | `508`, `520`, `524`, `940`, `944`, `945` | Do not treat reimbursement or plan rows as child nutrition without child-level meal or benefit evidence. |
| `FOOD-07` Disaster and emergency nutrition | Does the packet join D-SNAP, replacement, hot-food, USDA Foods, destroyed food, power outage, retailer operations, shelter/mobile distribution, and transport? | `911`, `912`, `925`, `942`, `944`, `945` | Treat disaster waivers as authority only until survivor food receipt and logistics are proven. |
| `FOOD-08` Theft, fraud, and integrity harm | Are stolen benefits, card skimming/cloning, replacement authority, fraud holds, overissuance, trafficking controls, notice, appeal, and household repair separated? | `435`, `442`, `444`, `913`, `914`, `944`, `945` | Do not call integrity successful until false-positive and unrepaired-theft harms are visible. |
| `FOOD-09` Outcome and equity denominator | Does the packet separate participation/spending from food insecurity, missed meals, diet quality, disability, language, child, older adult, tribal/rural, shelter/custody/care, and transportation effects? | `489`, `513`, `520`, `521`, `524`, `531`, `944`, `945` | Publish residual hunger and access gaps instead of treating program participation as outcome proof. |
| `FOOD-10` Source currentness and role boundary | Are USDA/FNA/ERS pages, program data, timeliness tables, dashboards, guidance, waivers, and local records separated by source role and review clock? | `857`, `910`, `927`, `944`, `945` | Mark federal sources as posture/denominator and require live state/school/clinic/processor records for decisions. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `945` | `FOOD-01`, `FOOD-02`, `FOOD-03`, `FOOD-04`, `FOOD-05`, `FOOD-06`, `FOOD-07`, `FOOD-08`, `FOOD-09`, `FOOD-10` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `424` | 1 |
| `425` | 2 |
| `426` | 1 |
| `435` | 1 |
| `442` | 1 |
| `444` | 1 |
| `473` | 1 |
| `482` | 1 |
| `489` | 1 |
| `506` | 1 |
| `508` | 1 |
| `509` | 1 |
| `513` | 3 |
| `520` | 4 |
| `521` | 1 |
| `524` | 4 |
| `531` | 2 |
| `538` | 1 |
| `574` | 1 |
| `577` | 1 |
| `857` | 1 |
| `895` | 2 |
| `910` | 1 |
| `911` | 1 |
| `912` | 1 |
| `913` | 1 |
| `914` | 1 |
| `923` | 1 |
| `925` | 1 |
| `927` | 1 |
| `940` | 1 |
| `942` | 2 |
| `944` | 10 |
| `945` | 10 |

## Use rule

Run food/nutrition continuity tests whenever SNAP, WIC, school meals, CACFP, SFSP, Summer EBT/SUN Bucks, D-SNAP, replacement benefits, EBT/eWIC cards, stolen benefits, retailer access, formula/food packages, disaster feeding, or food-security statistics are cited as proof that people received timely, usable food. Separate participant identity, eligibility clocks, issuance, card security, retailer access, WIC service, child meals, summer/disaster routes, integrity/remedy, outcome, and source-currentness before treating benefit rows, data tables, meal counts, plans, waivers, dashboards, or retailer rows as food security.
