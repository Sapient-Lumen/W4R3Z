# 693 — Shared-regime personal-data-and-privacy constitutions: legal basis, purpose limits, minimization, subject rights, transfers, breach response, and no mission by data drift

## One-line thesis

Shared regimes should publish a **typed personal-data-and-privacy constitution** that separates lawful basis, purpose limitation, necessity and minimization, role allocation, sensitive-data treatment, retention, transfer rules, subject-rights handling, breach response, and accountability review — so mission work does not quietly become mission by data drift, uncontrolled onward sharing, or privacy promises with no operating spine.

## Why this matters

The archive now explains how shared regimes type institutional information (`691`) and how they govern systems, access, incidents, and recovery (`692`). It also explains procurement and vendor lanes (`685`), private-law claims and remedy (`688`), and external participation channels (`677`).

That is enough to explain **where information sits, how systems work, how outsiders enter, and how operational vendors are bounded**. It is still not enough to explain **when a regime may process personal data at all, what purposes are legitimate, when data should be anonymized or pseudonymized, who can authorize onward transfers, how long identifiable data may be kept, what individuals can ask for, and how breaches or misuse are escalated and repaired**.

That gap matters because many shared regimes now process staff data, delegate credentials, travel records, procurement and vendor contacts, complaint files, beneficiary or participant information, research data, and incident information that can affect identifiable persons.

Without a typed personal-data constitution, seven familiar pathologies appear.

The first is **mission by data drift**: data collected for one narrow purpose quietly starts governing other purposes because the regime never typed a lawful basis, compatible-use test, or reauthorization lane.

The second is **consent theater**: people are shown broad notices or forms, but the regime actually relies on mandate, contract, security, or operational necessity without ever saying so cleanly.

The third is **minimization failure**: teams collect full identifiers, free-text notes, and long-lived copies because nobody required field-level necessity or role-based redaction.

The fourth is **partner-transfer fog**: data moves to contractors, cloud providers, implementing partners, experts, or other organizations without a visible adequacy, safeguards, or onward-transfer rule.

The fifth is **rights-without-route**: the regime announces privacy principles but cannot show where access, correction, objection, deletion, or review requests actually travel.

The sixth is **retention amnesia**: personal data survives because the system keeps it, not because the regime re-justified the continuing need to identify the person.

The seventh is **breach-by-procedure-gap**: incidents are discussed as cybersecurity events but not as privacy harms requiring containment, notification analysis, and remedial follow-through.

Shared regimes need a tighter privacy grammar.

## Pattern pack

### 1) Processing map and lawful-basis register

Maintain one register for material personal-data processing activities that names:

- the processing purpose;
- the accountable business owner;
- the categories of data subjects and data;
- the lawful or mandate basis relied upon;
- the systems, partners, and locations involved;
- whether the activity includes sensitive or high-risk personal data;
- the retention rule and review clock.

No consequential personal-data processing should be ownerless or basisless.

### 2) Purpose limitation and compatibility test

For each processing activity, state:

- the primary purpose;
- clearly permitted secondary uses;
- when renewed notice, re-approval, or extra safeguards are required;
- when de-identification is sufficient for reuse.

Do not treat operational convenience as a lawful purpose-expansion rule.

### 3) Necessity, minimization, and field discipline

Require data-collection and form design to answer:

- why each identifier or field is needed;
- whether less identifying alternatives exist;
- whether free text is necessary;
- whether high-risk data can be separated, masked, tokenized, or collected later;
- whether role-based views can show less than the full record.

The safest field is often the one never collected.

### 4) Sensitive-data and high-risk lane

Type a stricter lane for data whose misuse could create substantial risk to persons or groups, including where applicable:

- health data;
- child-related data;
- disciplinary or complaint information;
- biometric or identity-enabling data;
- geolocation, movement, or protection-sensitive records;
- data whose misuse could expose people to retaliation, discrimination, or stigma.

Require enhanced access limits, transfer scrutiny, and review authority for this lane.

### 5) Data-subject rights and review route

If the regime recognizes privacy and data-protection rights, it should show one visible route for:

- access requests;
- correction or completion requests;
- deletion, restriction, or objection where those rights exist;
- explanations of the regime’s applicable limits;
- internal review or reconsideration.

Rights without routing are decorative.

### 6) Third-party transfer and adequacy lane

For transfers to contractors, cloud providers, implementing partners, collaborating institutions, or other organizations, require:

- purpose-specific transfer authority;
- recipient category and role;
- minimum safeguards and confidentiality duties;
- onward-transfer restrictions;
- incident-reporting duties;
- return, deletion, or archival rules when the relationship ends.

### 7) Retention, anonymization, and deletion lane

Every processing activity should carry a rule for:

- identifiable retention duration or trigger;
- review clocks for continued necessity;
- anonymization, pseudonymization, or aggregation where feasible;
- secure deletion or irreversible de-identification;
- archival exception rules where records must survive.

### 8) Breach and privacy-incident discipline

Connect privacy harms to the cyber and incident architecture by separating:

- suspected personal-data incident intake;
- containment and evidence preservation;
- affected-data and affected-person assessment;
- notification or non-notification decision lane where applicable;
- remedial action;
- post-incident correction or control strengthening.

### 9) Accountability roles and independent oversight

Name at minimum:

- a data-protection and privacy lead or equivalent;
- accountable business owners for major processing streams;
- an internal review or audit lane;
- escalation routes for high-risk projects, disputes, or recurrent failures.

### 10) Privacy by design in forms, systems, and analytics

Require new forms, data collections, platforms, and analytical uses to answer before launch:

- what personal data is truly necessary;
- what de-identification or separation is feasible;
- what sharing is planned;
- what retention rule will apply;
- what rights and notice packet will exist;
- what additional review is needed if the use is novel or high-risk.

## Working matrix

| Privacy lane | Core constitutional question | Minimum visible packet |
|---|---|---|
| Processing basis | why may the regime process this personal data at all? | purpose, lawful basis, owner, system and partner map |
| Minimization | is every identifying element actually needed? | field justification, masking or separation rule, role-based view |
| Sensitive data | what requires enhanced protection? | stricter access limits, transfer scrutiny, review authority |
| Subject rights | how can affected persons ask for access, correction, objection, or deletion where applicable? | request route, response rules, limits explanation, review lane |
| Third-party transfers | when may data leave the regime’s direct control? | recipient class, safeguards, onward-transfer and return rules |
| Retention and de-identification | how long must the regime keep this identifiable? | retention trigger, review clock, anonymization or deletion rule |
| Breach response | when does a cyber event become a privacy event? | intake, assessment, containment, notification analysis, remediation |

## Guardrails

- Do not use personal data merely because it is available or convenient to collect.
- Do not collapse all processing into fake consent when mandate, contract, employment, or security lanes do the real work.
- Do not treat anonymization, pseudonymization, aggregation, and raw identifiers as if they were interchangeable.
- Do not let vendors, partners, or other organizations receive personal data without a visible safeguard and return or deletion rule.
- Do not separate privacy incidents from the main incident architecture so no one owns the human harm side.
- Do not promise rights that the regime cannot route, time, explain, or review.

## Failure modes

- **Data drift** — new uses quietly appear because purpose limits were never typed.
- **Sensitive-data sprawl** — high-risk personal data sits in ordinary tools and broad mailing lists.
- **Transfer opacity** — data leaves the regime through vendors or partners with no visible adequacy or onward-sharing rules.
- **Retention by inertia** — data persists because deletion was never built, not because continued identification is justified.
- **Rights theater** — privacy notices exist, but there is no credible access, correction, or review route.
- **Breach split-brain** — cyber responders restore systems while privacy harms to persons remain unassessed.

## Practical tests

1. Can the regime list its major personal-data processing activities, their owners, and their lawful bases?
2. Does each collection form or workflow show why each identifying field is necessary?
3. Are high-risk and sensitive data streams visibly separated from ordinary operational data?
4. Can the regime explain which transfers to vendors, partners, or other organizations are allowed and on what safeguards?
5. Is there one visible route for access, correction, objection, or deletion requests where those rights apply?
6. Do identifiable records have real retention triggers, review clocks, and de-identification or deletion rules?
7. When a system incident affects personal data, can the regime show who evaluates the privacy harm side?
8. Is there a named privacy lead, review lane, or audit function for high-risk processing?
9. Does new data collection or analytical use face a pre-launch privacy-by-design check rather than post hoc patching?

## Compression rule for the archive

If a shared regime can show **what information it holds and what systems it runs** but not **why it may process personal data, how it limits use and retention, how it governs transfers and rights requests, and how it connects breaches to human harm**, then it still has **information and cyber governance without an honest personal-data-and-privacy constitution**.
