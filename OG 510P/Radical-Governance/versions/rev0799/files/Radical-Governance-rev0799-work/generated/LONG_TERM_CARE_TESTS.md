# Long-term services/supports and care-continuity tests matrix

Generated for `rev0799` from `metadata/long_term_care_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `LTC-01` Person, setting, and authority | Does the packet identify resident/participant, facility or HCBS setting, payer, admission/service authority, responsible agency, representative or guardian, and rights notice before accepting a care status? | `424`, `425`, `475`, `521`, `923`, `938`, `939` | Open an LTSS authority docket and downgrade facility or enrollment rows to denominator evidence. |
| `LTC-02` Assessment, care plan, and medication continuity | Can assessment, acuity, ADLs/IADLs, medication, dementia/behavioral health, therapy, nursing, diet, infection control, and care-plan changes be joined to actual delivery? | `426`, `482`, `506`, `923`, `924`, `938`, `939` | Treat the care-plan date as insufficient until delivered care and missed-care evidence is visible. |
| `LTC-03` Staffing and delivered-hours reality | Does the packet separate staffing policy or reported hours from actual shifts, acuity fit, weekend/night coverage, home-care worker availability, backup care, and missed visits? | `462`, `506`, `856`, `938`, `939` | Do not cite staffing rules, repeals, or reported hours as safety without delivery and acuity evidence. |
| `LTC-04` Resident rights, consent, and communication | Are informed consent, visitation, family contact, privacy, resident council, interpreter, disability accommodation, grievance, and retaliation-safe communication usable? | `424`, `426`, `455`, `521`, `905`, `938`, `939` | Open a resident-rights route before treating posted rights or facility policy as usable rights. |
| `LTC-05` APS and elder-justice response | Does APS or elder-justice evidence prove intake, investigation, risk assessment, protective services, law enforcement or court action, financial protection, recurrence check, and closure reason? | `422`, `475`, `857`, `938`, `939` | Treat APS intake or NAMRS data as reporting evidence only until protective action and recurrence prevention are visible. |
| `LTC-06` Ombudsman complaint and remedy tail | Does the packet show resident access to the ombudsman, complaint coding, verification, resolution, retaliation protection, systemic escalation, and unresolved-tail status? | `419`, `422`, `425`, `857`, `938`, `939` | Do not treat ombudsman program existence as remedy without complaint-tail evidence. |
| `LTC-07` Transfer, discharge, and relocation continuity | Before transfer, discharge, closure, hospital-to-post-acute discharge, or evacuation, are notice, lawful basis, appeal, destination, records, medication, transport, receiving-care acceptance, and follow-up proven? | `425`, `461`, `472`, `473`, `884`, `923`, `938`, `939` | Treat discharge or transfer as incomplete until receiving-care and follow-up evidence exists. |
| `LTC-08` HCBS community-living continuity | Does HCBS evidence show authorized and delivered hours, provider capacity, backup workers, housing, transportation, technology, caregiver support, emergency backup, and institutional-risk mitigation? | `521`, `894`, `923`, `924`, `928`, `938`, `939` | Do not cite HCBS enrollment or QMS measures as community living without person-level delivery evidence. |
| `LTC-09` Guardianship and fiduciary accountability | Does a guardianship/fiduciary packet preserve scope, less-restrictive alternatives, accounting, fees, visitation, medical/property decisions, complaints, and restoration review? | `439`, `475`, `857`, `905`, `938`, `939` | Do not treat guardian appointment as protection until authority scope and accountability evidence are visible. |
| `LTC-10` Emergency preparedness, evacuation, and closure tail | Can the packet prove emergency staffing, transport, receiving beds, medication/records, generator/power, infection control, heat/cooling, family notice, return, and closure/relocation tail? | `422`, `462`, `511`, `884`, `925`, `926`, `938`, `939` | Do not cite emergency compliance as readiness without evacuation and continuity execution evidence. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `939` | `LTC-01`, `LTC-02`, `LTC-03`, `LTC-04`, `LTC-05`, `LTC-06`, `LTC-07`, `LTC-08`, `LTC-09`, `LTC-10` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `419` | 1 |
| `422` | 3 |
| `424` | 2 |
| `425` | 3 |
| `426` | 2 |
| `439` | 1 |
| `455` | 1 |
| `461` | 1 |
| `462` | 2 |
| `472` | 1 |
| `473` | 1 |
| `475` | 3 |
| `482` | 1 |
| `506` | 2 |
| `511` | 1 |
| `521` | 3 |
| `856` | 1 |
| `857` | 3 |
| `884` | 2 |
| `894` | 1 |
| `905` | 2 |
| `923` | 4 |
| `924` | 2 |
| `925` | 1 |
| `926` | 1 |
| `928` | 1 |
| `938` | 10 |
| `939` | 10 |

## Use rule

Run long-term-care tests whenever nursing-home provider data, Care Compare ratings, SFF status, staffing rules or repeals, facility-initiated discharge, HCBS enrollment or quality measures, APS/NAMRS data, ombudsman routes, guardianship/fiduciary authority, assisted-living/residential settings, home care, emergency evacuation, closure, medication, restraints, resident rights, or family/caregiver continuity can affect older adults or people with disabilities. Separate setting, authority, care delivery, staffing, rights, APS, ombudsman, transfer/discharge, HCBS, guardianship, emergency, and source-currentness before treating a facility row, HCBS slot, intake, guardian order, or rating as care.
