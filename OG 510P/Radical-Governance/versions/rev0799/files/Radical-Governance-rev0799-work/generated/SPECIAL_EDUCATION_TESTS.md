# Special education / IEP / Section 504 continuity tests matrix

Generated for `rev0799` from `metadata/special_education_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `SPED-01` Student, legal lane, and participation | Does the packet identify the student, school, district, IDEA/504/Part C lane, parent/surrogate/guardian, consent, language/access needs, and responsible owner before accepting a status? | `424`, `425`, `426`, `508`, `521`, `524`, `940`, `941` | Open a student-authority docket and downgrade IEP/504/enrollment rows to denominator evidence. |
| `SPED-02` Evaluation and eligibility clock | Can referral, consent, assessment, eligibility, reevaluation, primary language, adverse impact, and service need be reconstructed with timelines? | `424`, `473`, `508`, `521`, `940`, `941` | Treat disability category or eligibility row as incomplete until evaluation and timeline proof is joined. |
| `SPED-03` IEP/504 design versus delivery | Does the packet separate plan design from actual delivered services, accommodations, related services, assistive technology, transport, and progress reporting? | `426`, `475`, `482`, `508`, `521`, `923`, `940`, `941` | Do not treat minutes grids or plan dates as delivered service; open a missed-service and compensatory-repair docket. |
| `SPED-04` Accessibility, communication, and family access | Are accessible formats, interpreter/translation, digital access, meeting access, student voice, and family communication usable before deadlines expire? | `424`, `426`, `438`, `521`, `577`, `940`, `941` | Open an access/notice repair route before treating procedural safeguards as usable participation. |
| `SPED-05` Least restrictive environment and inclusion reality | Does the packet prove curriculum, peer access, supports, extracurriculars, transport, and progress rather than only placement percentage? | `508`, `521`, `524`, `940`, `941` | Treat LRE percentage as insufficient until inclusion supports and learning access are shown. |
| `SPED-06` Discipline, restraint, seclusion, and police referral | Are removals, manifestation determination, FBA/BIP, restraint, seclusion, law-enforcement referral, arrest, notice, trauma/health follow-up, and return plan joined? | `425`, `502`, `508`, `521`, `557`, `940`, `941` | Do not accept a discipline code as lawful exclusion; open disability-nexus, safety, and return-to-learning review. |
| `SPED-07` Attendance, shortened day, homebound, and compensatory repair | Does the packet show whether absences, shortened days, transport failures, homebound/hospital instruction, virtual access, or missed services were repaired? | `482`, `508`, `521`, `923`, `934`, `940`, `941` | Open a compensatory education/service docket when access loss is hidden behind enrollment or attendance rows. |
| `SPED-08` Transition and successor receipt | Are Part C-to-Part B, preschool, district transfer, foster/custody/hospital return, high-school transition, graduation/age-out, VR/adult services, health/Medicaid, and records transfer joined? | `472`, `475`, `508`, `521`, `923`, `934`, `936`, `940`, `941` | Do not treat a transition meeting or exit code as receipt; require successor-service proof. |
| `SPED-09` Dispute resolution and remedy usability | Can the student/family use prior written notice, meeting requests, mediation, state complaints, due process, OCR complaints, stay-put, corrective action, and compensatory services? | `425`, `494`, `558`, `577`, `857`, `940`, `941` | Treat remedy existence as insufficient until cost, access, language, records, representation, and implementation are shown. |
| `SPED-10` Aggregate data and source-currentness boundary | Does the packet distinguish Section 618, SPP/APR, annual reports, CRDC, NCES, GAO, guidance, and student-level records before making a claim? | `457`, `484`, `508`, `521`, `857`, `927`, `940`, `941` | Downgrade aggregate data to denominator evidence until student-level proof is joined. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `941` | `SPED-01`, `SPED-02`, `SPED-03`, `SPED-04`, `SPED-05`, `SPED-06`, `SPED-07`, `SPED-08`, `SPED-09`, `SPED-10` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `424` | 3 |
| `425` | 3 |
| `426` | 3 |
| `438` | 1 |
| `457` | 1 |
| `472` | 1 |
| `473` | 1 |
| `475` | 2 |
| `482` | 2 |
| `484` | 1 |
| `494` | 1 |
| `502` | 1 |
| `508` | 8 |
| `521` | 9 |
| `524` | 2 |
| `557` | 1 |
| `558` | 1 |
| `577` | 2 |
| `857` | 2 |
| `923` | 3 |
| `927` | 1 |
| `934` | 2 |
| `936` | 1 |
| `940` | 10 |
| `941` | 10 |

## Use rule

Run special-education tests whenever an IEP, Section 504 plan, eligibility label, evaluation, related-service grid, LRE percentage, assistive technology, transport, discipline removal, restraint, seclusion, law-enforcement referral, Part C/Part B transition, graduation/age-out, dispute-resolution route, or federal/state aggregate source is cited as proof that a student received FAPE or equal access. Separate legal lane, evaluation, plan, delivered service, accessibility, discipline, transition, remedy, and source-currentness before treating a row, plan, determination, or dataset as education continuity.
