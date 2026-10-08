# 931 — Applied cyber/software-continuity case packet for Change Healthcare, Synnovis, British Library, OMB/NIST/CISA, and no resilience by attestation

## One-line thesis

Change Healthcare, Synnovis, the British Library, and federal secure-software assurance reforms show the same administrative failure mode: a cyber event is not just a breach, outage, or compliance control problem. It is a supplier-dependent public-service continuity event unless claims, appointments, payments, access, records, data rights, degraded mode, recovery, and affected-person repair are joined.

## Why this matters

These cases are not being collected for incident trivia. They establish a repeatable risk class: when a public service depends on supplier software, labs, clearinghouses, managed services, or cultural-access systems, a cyber event can interrupt rights, care, payments, access, records, and data protection long after the incident headline.

## Case packet verdict

Route cyber/software incidents that touch public services through a continuity waist before accepting any restoration, attestation, or breach-notification claim.

The applied rule is **no resilience by attestation**.

## Pattern pack

- **Clearinghouse dependency becomes service dependency** when claims, payments, pharmacy access, provider cash flow, and breach notification are joined.
- **Lab supplier outage becomes clinical continuity** when diagnostics, outpatient appointments, elective procedures, stolen data, and restoration queues are joined.
- **Cultural-memory ransomware becomes public-access continuity** when catalogues, reader services, staff workflows, records, data protection, and infrastructure rebuild are joined.
- **Assurance stack becomes useful only as evidence** when OMB/NIST/CISA controls, attestations, SBOMs, KEV posture, ransomware guidance, and incident reporting are tied to deployed service outcomes.

## Why these cases belong together

| Case surface | What it shows | Continuity question |
|---|---|---|
| Change Healthcare | A health-care clearinghouse and payment/claims dependency can create nationwide operational and data-rights consequences. | Which claims, providers, patients, payments, pharmacies, notifications, and downstream records were affected beyond the breach count? |
| Synnovis | A supplier incident in pathology services can delay appointments and elective care while data exposure and recovery unfold over months. | Which clinical pathways, diagnostics, rescheduling queues, and patient communications were protected during degraded mode? |
| British Library | A public knowledge institution can lose core access functions and face long restoration after ransomware. | Which users, catalogues, records, services, staff workflows, and public access obligations were maintained or rebuilt? |
| OMB / NIST / CISA assurance reforms | Secure-development attestations, SSDF practices, CPGs, KEV, incident reporting, and ransomware guidance create evidence hooks. | How are assurance hooks joined to actual runtime dependencies and affected-service outcomes? |

## Continuity state ladder

1. **Critical function.** Name the public function: claims, payment, diagnostics, appointment scheduling, records access, research access, identity, benefits, court filing, notice, or appeal.
2. **Supplier dependency.** Identify the provider, product, hosted service, managed-service role, clearinghouse, lab, data processor, cloud, hardware, firmware, or component in the live service path.
3. **Runtime asset.** Distinguish the procured product from deployed instances, versions, exposed endpoints, service accounts, privileged consoles, connected data stores, and backup or replication paths.
4. **Assurance evidence.** Record attestation, SSDF claim, SBOM availability, CPG posture, vulnerability-management practice, contract clause, audit report, and exception memo.
5. **Exposure proof.** Join KEV status, exploit path, unsupported system, MFA or logging gap, remote-access channel, lateral-movement risk, data class, and compensating control.
6. **Incident command.** Record detection, containment, reporting, public communication, contractor and agency duties, breach notification, and decision rights for degraded mode.
7. **Degraded mode.** Prove that manual, alternate, paper, emergency, mutual-aid, or substitute process worked for the people whose service depended on the failed system.
8. **Affected-person tail.** Track delayed care, missed payment, blocked claim, inaccessible record, fraud exposure, deadline loss, repeated submission, duplicate work, and notification gap.
9. **Recovery evidence.** Show backlog reconciliation, data integrity, restored access, reopened deadlines, remediated security controls, lessons implemented, and concentration risk reduced.
10. **Contract and architecture consequence.** Record whether procurement, supplier concentration, exit rights, escrow, redundancy, logging, identity, and incident clauses changed.

## Case application

### Change Healthcare

The continuity docket must not stop at the incident, breach-notification, or restoration surfaces. The relevant public-service questions are: which claims and payments were interrupted, which patients and providers faced workarounds, which pharmacies or care pathways were affected, which protected data required notice, which business associates or covered entities had obligations, and which downstream fraud or record-correction risks remain open.

A strong repair packet would include payer/provider claim volumes, pharmacy disruption indicators, patient-notification channels, payment-advance or bridge mechanisms, backlog clearance, breach-notification status, and provider solvency or access effects.

### Synnovis

The continuity docket must join pathology-service availability to appointment delay, elective-care delay, patient notice, stolen-data response, and restoration proof. A supplier outage that affects diagnostics is not just a technology incident. It is a clinical scheduling and patient-risk event.

A strong repair packet would include affected trusts and services, delayed outpatient and elective appointments, sample routing or alternate lab capacity, patient-contact rules, data-exposure notification, restoration milestones, and post-incident clinical backlog review.

### British Library

The continuity docket must treat access to knowledge, catalogues, user accounts, internal workflows, and institutional memory as service surfaces. Restoration cannot be measured only by whether a website returns. It also needs collection access, reader services, staff operations, data protection, legacy-system replacement, and public trust.

A strong repair packet would include catalogue and collection availability, reader-service substitutions, staff-workflow restoration, affected-data categories, incident lessons, infrastructure modernization, and resilience decisions for cultural-memory services.

### OMB / NIST / CISA assurance stack

The assurance stack creates leverage only when it is used as a joined evidence system. OMB-style risk-based software and hardware security guidance, NIST SSDF practices, CISA attestation forms, cross-sector performance goals, KEV remediation, ransomware guidance, and incident-reporting rules are useful because they give agencies questions to ask. They are not substitutes for proof that public-service continuity survived the event.

## Required test packet

A cyber/software continuity file should contain the following artifacts before it is called mature:

- a critical-function map;
- deployed runtime and supplier dependency map;
- attestation and secure-development evidence;
- SBOM or component evidence when proportionate;
- KEV / vulnerability / exception docket;
- identity and privileged-access docket;
- incident timeline and notification responsibilities;
- degraded-mode activation and staffing record;
- affected-person, payment, claim, appointment, record, or access tail;
- recovery, reconciliation, backlog, and integrity proof;
- contract and architecture consequence log.

## Anti-theater tests

Apply these as hard falsifiers before accepting a recovery or assurance claim.

## Anti-theater rules

- No resilience by attestation.
- No security by SBOM.
- No continuity by incident page.
- No restoration by uptime.
- No public-health system by clearinghouse availability.
- No patient repair by breach count.
- No cultural-access recovery by website return.
- No supplier governance by contract renewal alone.

## Falsifiers

The packet should be downgraded if it cannot show which public functions depended on the failed supplier, which people or records were affected, which fallback mode actually ran, which backlog was reconciled, which controls changed, and which contract or architecture decisions were corrected.

## Dispatch rule

Use this packet whenever a cyber incident, secure-software assurance claim, SBOM request, CISA KEV exposure, vendor outage, cloud or managed-service failure, breach notification, ransomware event, or system restoration announcement might affect public-service continuity.
