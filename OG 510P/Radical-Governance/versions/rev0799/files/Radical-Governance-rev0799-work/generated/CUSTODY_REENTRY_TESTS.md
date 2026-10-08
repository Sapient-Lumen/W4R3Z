# Custody / corrections / release / reentry continuity tests matrix

Generated for `rev0799` from `metadata/custody_reentry_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `CR-01` Legal custody and hold state | Does the packet separate arrest, booking, charge, sentence, hold, detainer, transfer, supervision violation, credits, and release authority before accepting custody as lawful or current? | `425`, `475`, `557`, `558`, `857`, `936`, `937` | Open a custody-authority docket and downgrade any claim that treats a custody row as legal proof. |
| `CR-02` Intake and acute-risk triage | Does the record prove suicide, withdrawal, medications, disability, pregnancy, age, language, victimization, mental health, and emergency medical risks were screened and acted on? | `424`, `426`, `482`, `502`, `923`, `936`, `937` | Treat booking as incomplete until high-risk triage and action receipts are visible. |
| `CR-03` Conditions, violence, and segregation safety | Can the packet join housing unit, staffing, violence, contraband, use of force, sexual abuse, segregation, sanitation, food, ADA accommodation, grievances, and monitoring? | `502`, `557`, `856`, `857`, `936`, `937` | Do not treat jail census, prison count, or classification as safe custody without conditions evidence. |
| `CR-04` Health, medication, and MOUD continuity | Can the packet prove medical records, medications, MOUD, chronic care, mental health, hospital transfer, disability supports, pregnancy care, and release prescriptions continued across custody and discharge? | `426`, `482`, `874`, `923`, `936`, `937` | Open a health passport; do not accept sick-call or referral status as care continuity. |
| `CR-05` Death, injury, and serious-incident accountability | Does a death or serious incident connect DCRA/MCI reporting, incident narrative, investigation, family notice, public denominator, corrective action, and litigation or monitor status? | `422`, `502`, `553`, `557`, `857`, `936`, `937` | Do not cite annual death statistics as accountability until incident-level investigation and repair tails are joined. |
| `CR-06` Communication, counsel, family, and grievance access | Does the packet prove attorney/court access, phone/mail/video, family notice, interpreter, disability accommodation, grievance, and retaliation-safe reporting remained available? | `424`, `425`, `426`, `494`, `558`, `577`, `936`, `937` | Treat communication blockage as a liberty and due-process risk, not as facility administration. |
| `CR-07` Release calculation and gate execution | Can the record prove credits, FSA/good time, parole/release eligibility, detainers, transportation, property, gate time, medications, and discharge instructions were executed? | `472`, `473`, `475`, `485`, `557`, `936`, `937` | Do not treat projected release date as release until gate execution and downstream conditions are visible. |
| `CR-08` Benefits, IDs, and coverage bridge | Does the packet prove Medicaid/coverage, ID documents, Social Security card, birth certificate, address, phone, appointments, records, and consent were usable at release? | `562`, `574`, `577`, `901`, `923`, `928`, `936`, `937` | Do not accept application, referral, or demonstration authority as continuity until usable benefits and documents are confirmed. |
| `CR-09` Housing, treatment, work, and supervision tail | Does release connect to RRC/home confinement, shelter or housing, employment/education, treatment, family reunification, supervision conditions, fees, electronic monitoring, and violation/modification route? | `514`, `557`, `576`, `577`, `928`, `936`, `937` | Do not treat reentry referral or supervision compliance flag as stable community return. |
| `CR-10` Source posture and denominator boundary | Does the packet mark which sources are aggregate counts, live program rules, oversight findings, mortality records, or local case files before drawing conclusions? | `451`, `484`, `857`, `910`, `927`, `936`, `937` | Downgrade claims that cite BJS, CMS, GAO, SAMHSA, BOP, or DOJ sources outside their evidentiary boundary. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `937` | `CR-01`, `CR-02`, `CR-03`, `CR-04`, `CR-05`, `CR-06`, `CR-07`, `CR-08`, `CR-09`, `CR-10` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `422` | 1 |
| `424` | 2 |
| `425` | 2 |
| `426` | 3 |
| `451` | 1 |
| `472` | 1 |
| `473` | 1 |
| `475` | 2 |
| `482` | 2 |
| `484` | 1 |
| `485` | 1 |
| `494` | 1 |
| `502` | 3 |
| `514` | 1 |
| `553` | 1 |
| `557` | 5 |
| `558` | 2 |
| `562` | 1 |
| `574` | 1 |
| `576` | 1 |
| `577` | 3 |
| `856` | 1 |
| `857` | 4 |
| `874` | 1 |
| `901` | 1 |
| `910` | 1 |
| `923` | 3 |
| `927` | 1 |
| `928` | 2 |
| `936` | 10 |
| `937` | 10 |

## Use rule

Run custody/reentry tests whenever booking, detention, jail/prison custody, transfer, classification, medical/MOUD need, death or serious injury, release calculation, First Step Act or sentence credits, Medicaid reentry, ID documents, RRC/home confinement, housing, supervision, electronic monitoring, or reentry referrals can affect liberty, safety, health, accountability, or community return. Separate legal authority, intake risk, conditions, health, incident reporting, communication/counsel, release execution, benefits/IDs, housing/treatment, supervision, and source posture before treating a custody row, count, release date, or referral as proof.
