# Veterans benefits / care / support continuity tests matrix

Generated for `rev0799` from `metadata/veterans_continuity_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `VET-01` Person, authority, and discharge/status lane | Does the packet bind the veteran, survivor, dependent, caregiver, representative, service/discharge/character lane, address, and urgency before accepting VA status evidence? | `424`, `425`, `426`, `475`, `482`, `506`, `509`, `520`, `557`, `558`, `562`, `574`, `577`, `902`, `903`, `952`, `953` | Open a person-status docket and downgrade VA row evidence to denominator state. |
| `VET-02` Claim, evidence, exam, and payment | Are claim type, evidence, service records, C&P exam, rating, decision, notice, payment, dependent/survivor effects, and error-correction receipts separated? | `424`, `425`, `426`, `475`, `482`, `506`, `509`, `520`, `557`, `558`, `562`, `574`, `577`, `902`, `903`, `913`, `914`, `952`, `953` | Do not treat claims inventory or completed-claim counts as support until payment and correction evidence are joined. |
| `VET-03` Rating criteria and modernization risk | Does the packet identify rating criteria vintage, body system, medical/earnings-loss assumptions, exam quality, contractor oversight, and rework risk? | `424`, `425`, `426`, `475`, `482`, `506`, `509`, `520`, `557`, `558`, `562`, `574`, `577`, `902`, `903`, `952`, `953` | Flag rating criteria/exam quality for review before relying on percentage or decision. |
| `VET-04` PACT Act and toxic-exposure path | Are exposure, presumptive condition, PACT eligibility, health-care enrollment, claim, exam, decision, payment, and treatment path joined? | `424`, `425`, `426`, `475`, `482`, `506`, `509`, `520`, `557`, `558`, `562`, `574`, `577`, `902`, `903`, `506`, `913`, `914`, `952`, `953` | Treat PACT dashboards as implementation evidence only until person-level toxic-exposure claim and care evidence exist. |
| `VET-05` Health enrollment, priority, and care delivery | Does eligibility or priority group connect to appointment, medication, specialty, travel, telehealth, covered benefits, and care-plan continuity? | `424`, `425`, `426`, `475`, `482`, `506`, `509`, `520`, `557`, `558`, `562`, `574`, `577`, `902`, `903`, `506`, `938`, `939`, `952`, `953` | Do not score eligibility as care until appointment, medication, and follow-up evidence exist. |
| `VET-06` Community-care authorization and follow-up | Are community-care referral, eligibility, authorization, provider scheduling, records exchange, claim payment, and clinical follow-up joined? | `424`, `425`, `426`, `475`, `482`, `506`, `509`, `520`, `557`, `558`, `562`, `574`, `577`, `902`, `903`, `506`, `938`, `939`, `950`, `951`, `952`, `953` | Downgrade authorization to routing evidence until provider and clinical continuity evidence are present. |
| `VET-07` Appeal, review, representative, and remand continuity | Do supplemental claim, higher-level review, Board appeal, hearing, hardship, representative, remand, and decision notice remain connected to payment/care consequences? | `424`, `425`, `426`, `475`, `482`, `506`, `509`, `520`, `557`, `558`, `562`, `574`, `577`, `902`, `903`, `494`, `558`, `913`, `914`, `952`, `953` | Open an appeal-continuity repair file when docket status is cited as remedy proof. |
| `VET-08` Records, EHRM, portal, and digital handoff | Are claims file, medical record, service records, EHRM site state, portal/identity, medication, problem-list, referral, downtime, and correction path joined? | `424`, `425`, `426`, `475`, `482`, `506`, `509`, `520`, `557`, `558`, `562`, `574`, `577`, `902`, `903`, `902`, `903`, `930`, `931`, `950`, `951`, `952`, `953` | Treat EHRM and portal milestones as source-currentness warnings until record-level continuity is verified. |
| `VET-09` Crisis, homelessness, and housing stabilization | Are Veterans Crisis Line, homeless call-center, HUD-VASH/SSVF/GPD, ID, income, lease-up, case management, safety plan, and follow-up joined? | `424`, `425`, `426`, `475`, `482`, `506`, `509`, `520`, `557`, `558`, `562`, `574`, `577`, `902`, `903`, `505`, `928`, `929`, `936`, `937`, `946`, `947`, `952`, `953` | Do not treat hotline availability or voucher allocation as stabilization without handoff, placement, and follow-up. |
| `VET-10` Education, caregiver, transition, and outcome closure | Are GI Bill entitlement/school certification/payment, caregiver eligibility/assignment/stipend/respite/wellness contacts, and transition outcomes joined to remedy receipts? | `424`, `425`, `426`, `475`, `482`, `506`, `509`, `520`, `557`, `558`, `562`, `574`, `577`, `902`, `903`, `508`, `509`, `938`, `939`, `952`, `953` | Keep program rows open until school payment, caregiver support, and transition outcome evidence exists. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `953` | `VET-01`, `VET-02`, `VET-03`, `VET-04`, `VET-05`, `VET-06`, `VET-07`, `VET-08`, `VET-09`, `VET-10` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `424` | 10 |
| `425` | 10 |
| `426` | 10 |
| `475` | 10 |
| `482` | 10 |
| `494` | 1 |
| `505` | 1 |
| `506` | 13 |
| `508` | 1 |
| `509` | 11 |
| `520` | 10 |
| `557` | 10 |
| `558` | 11 |
| `562` | 10 |
| `574` | 10 |
| `577` | 10 |
| `902` | 11 |
| `903` | 11 |
| `913` | 3 |
| `914` | 3 |
| `928` | 1 |
| `929` | 1 |
| `930` | 1 |
| `931` | 1 |
| `936` | 1 |
| `937` | 1 |
| `938` | 3 |
| `939` | 3 |
| `946` | 1 |
| `947` | 1 |
| `950` | 2 |
| `951` | 2 |
| `952` | 10 |
| `953` | 10 |

## Use rule

Run veterans-continuity tests whenever VA claims, ratings, PACT Act evidence, health-care eligibility, community care, appeals, EHRM, crisis lines, homelessness programs, GI Bill, caregiver support, survivor/dependent benefits, or VA digital-status surfaces are cited as proof that a veteran, survivor, dependent, caregiver, or family received support. Separate person, claim, exam, rating, appeal, care, authorization, records, housing, crisis, education, caregiver, payment, remedy, and source-currentness before treating a claim row, rating, dashboard, eligibility, authorization, docket, voucher, certification, or caregiver row as support.
