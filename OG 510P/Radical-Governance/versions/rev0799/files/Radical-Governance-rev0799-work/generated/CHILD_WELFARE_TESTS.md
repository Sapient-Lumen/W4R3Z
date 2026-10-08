# Child welfare / foster care continuity tests matrix

Generated for `rev0799` from `metadata/child_welfare_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `CW-01` Intake, screen, and investigation clock | Does the packet separate referral, reporter, allegation, screen result, response priority, investigation actions, safety assessment, disposition, notice, and appeal before calling a child safe? | `424`, `425`, `426`, `524`, `857`, `934`, `935` | Open an intake and investigation clock; downgrade any claim that treats hotline status as safety. |
| `CW-02` Prevention and family-support delivery | Can the packet prove prevention, reasonable efforts, kinship help, in-home supports, disability/language access, and economic stabilizers were actually reachable before removal or reunification failure? | `424`, `426`, `494`, `506`, `524`, `894`, `901`, `934`, `935` | Do not treat a prevention plan or program authority as family preservation until service delivery and timing are visible. |
| `CW-03` Removal, court authority, and notice | Does the packet distinguish emergency removal, voluntary placement, custody order, counsel, GAL/CASA, parent notice, youth notice, tribal notice, review hearing, and appeal route? | `424`, `425`, `426`, `557`, `558`, `817`, `818`, `934`, `935` | Open a legal-authority docket before treating custody status as due process. |
| `CW-04` Placement suitability, kinship, siblings, and tribal continuity | Can the packet show why the placement is least restrictive, family-approximating, kin/sibling/tribal-aware, school-preserving, disability/behavioral-health appropriate, and safely monitored? | `524`, `557`, `558`, `788`, `905`, `928`, `934`, `935` | Do not treat an available bed or placement row as appropriate placement. |
| `CW-05` Health, Medicaid, trauma, medication, and education passport | Are insurance, medical records, trauma screening, therapy, psychotropic consent/monitoring, dental, disability supports, school enrollment, IEP/504, credits, and transportation joined? | `494`, `506`, `524`, `879`, `894`, `901`, `923`, `934`, `935` | Do not infer health or school continuity from eligibility, placement, or medication rows. |
| `CW-06` Missing-from-care report, search, return, and trafficking screen | When a child is missing from care or returns, does the packet show law-enforcement/NCMEC/NCIC route where required, search plan, caregiver/court/attorney notice, return interview, trafficking screen, and revised prevention plan? | `524`, `788`, `857`, `874`, `884`, `887`, `934`, `935` | Do not close a missing episode on return date alone; require return assessment and prevention repair. |
| `CW-07` Caseworker contact, supervision, provider capacity, and incident escalation | Does the packet prove caseworker visits, supervisor review, provider capacity, incident reporting, specialized placement availability, and escalation authority? | `813`, `814`, `815`, `816`, `819`, `820`, `821`, `823`, `824`, `856`, `859`, `934`, `935` | Treat contracted capacity as unproven until child-specific capacity and escalation are visible. |
| `CW-08` Family time, permanency, and transition clocks | Does the packet join family time, reunification services, guardianship/adoption route, APPLA/aging-out, documents, benefits, housing, education/work, and post-exit support? | `424`, `425`, `426`, `482`, `524`, `894`, `897`, `901`, `905`, `928`, `934`, `935` | Do not treat a permanency goal or case closure as durable permanency. |
| `CW-09` Child/youth voice, counsel, grievance, and retaliation-safe route | Can the child, youth, parent, kin caregiver, tribe, or representative contest facts, services, placement, school, health, medication, family-time, or permanency without losing safety or support? | `404`, `424`, `425`, `426`, `557`, `558`, `817`, `818`, `879`, `887`, `934`, `935` | Add a voice and contestability route before accepting case-plan compliance. |
| `CW-10` Aggregate data and public oversight denominator | Are AFCARS, NCANDS/Child Maltreatment, CFSR, NYTD, state dashboards, audits, and provider reports labeled by denominator, refresh clock, exclusion, and case-level repair path? | `856`, `857`, `917`, `923`, `927`, `934`, `935` | Do not cite aggregate child-welfare data as child-specific safety or permanency proof. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `935` | `CW-01`, `CW-02`, `CW-03`, `CW-04`, `CW-05`, `CW-06`, `CW-07`, `CW-08`, `CW-09`, `CW-10` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `404` | 1 |
| `424` | 5 |
| `425` | 4 |
| `426` | 5 |
| `482` | 1 |
| `494` | 2 |
| `506` | 2 |
| `524` | 6 |
| `557` | 3 |
| `558` | 3 |
| `788` | 2 |
| `813` | 1 |
| `814` | 1 |
| `815` | 1 |
| `816` | 1 |
| `817` | 2 |
| `818` | 2 |
| `819` | 1 |
| `820` | 1 |
| `821` | 1 |
| `823` | 1 |
| `824` | 1 |
| `856` | 2 |
| `857` | 3 |
| `859` | 1 |
| `874` | 1 |
| `879` | 2 |
| `884` | 1 |
| `887` | 2 |
| `894` | 3 |
| `897` | 1 |
| `901` | 3 |
| `905` | 2 |
| `917` | 1 |
| `923` | 2 |
| `927` | 1 |
| `928` | 2 |
| `934` | 10 |
| `935` | 10 |

## Use rule

Run child-welfare tests whenever a maltreatment report, investigation, safety plan, removal, prevention service, placement change, missing-from-care episode, psychotropic medication, congregate/out-of-state placement, permanency decision, or transition deadline can affect a child or family. Separate safety, family support, legal authority, placement suitability, health, education, missing-from-care response, youth voice, permanency, and oversight denominators before accepting protection claims.
