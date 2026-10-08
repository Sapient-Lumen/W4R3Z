# 930 — Cyber incident, software provenance, and public-service continuity dockets: runtime SBOM, supplier access, recovery, and no resilience by attestation

## One-line thesis

A secure-software attestation, SBOM, inventory row, CPG checklist, breach notice, incident page, uptime statement, or restoration announcement is not public-service resilience. Cyber/software continuity needs a joined docket across public function, supplier, runtime asset, privileged access, exploitable exposure, degraded operation, data exposure, notification, recovery, and affected-person tail.

## Governing repair phrase

**No resilience by attestation.**

## Why this matters now

Recent government and public-service cyber failures have made three things hard to ignore.

First, modern public administration runs on supplier-dependent software, clearinghouses, identity brokers, labs, clouds, payment rails, cultural repositories, and managed services. A breach or outage in one provider can become a benefits, claims, clinical, court, knowledge-access, or records-continuity event.

Second, the assurance stack has multiplied. Agencies can request attestations, inventories, SBOMs, secure-development evidence, vulnerability remediation status, incident reports, recovery statements, and breach notifications. Those artifacts matter, but none of them alone proves that a person still got care, pay, food, shelter, appointment access, records access, appeal time, or a safe fallback route.

Third, the recovery tail is often longer than the visible outage. Data exposure, identity-fraud risk, delayed claims, missed appointments, deferred workarounds, paper queues, lost trust, and contract-renewal inertia outlast the incident banner.

## Split the docket before scoring resilience

Use four ledgers, not one score.

| Ledger | What it asks | Bad shortcut |
|---|---|---|
| Assurance | Did the supplier claim secure development, inventory, SBOM, vulnerability management, MFA, logging, and incident response? | Treating attestation as proof of runtime safety. |
| Exposure | Which components, identities, systems, data classes, and public functions were reachable or vulnerable? | Treating a software list as a live dependency map. |
| Incident | What happened, when was it known, who was notified, what systems were degraded, and what was stolen or unavailable? | Treating an incident page as complete public accountability. |
| Continuity | Which people, claims, appointments, payments, records, deadlines, and remedies still worked during and after the event? | Treating restoration or uptime as service recovery. |

## Minimum joined docket

A usable cyber/software continuity docket includes:

1. **Public-function map.** The services that can fail: claims, payments, appointments, diagnostics, records, benefits, identity proofing, public access, filing, notice, or appeal.
2. **Supplier and runtime asset map.** Vendor, product, hosted service, version, cloud tenancy, managed-service role, embedded component, hardware or firmware dependency, and whether the asset is actually in the path of service delivery.
3. **Identity and privileged-access map.** Administrative accounts, service accounts, vendor access, MFA posture, logging, break-glass procedure, and revocation route.
4. **Vulnerability and exploit docket.** Known exploited vulnerabilities, patch windows, exception approvals, compensating controls, unsupported systems, and exposure to the internet or supplier remote access.
5. **Incident command record.** Detection time, containment time, reporting time, public communication, legal notification, business-associate / contractor notification, ransom-payment posture, and authority to switch to degraded mode.
6. **Degraded-mode record.** Manual, paper, alternate vendor, queue, payment, clinical, court, benefit, or access route; trigger to activate it; staffing; and how long it can safely operate.
7. **Affected-person tail.** People whose claims, appointments, payments, records, credentials, eligibility, deadlines, or personal data were affected, including those who never received individualized notice.
8. **Recovery evidence.** Not just systems restored, but backlog cleared, data integrity checked, false-denial and duplicate-payment risk reviewed, records reconciled, affected parties notified, and lessons converted into procurement or architecture changes.

## Pattern pack

### 1. Attestation is an input, not a waist

A software or hardware security attestation can identify minimum provider claims and give agencies a procurement hook. It cannot identify every operational dependency, affected household, deferred appointment, unpaid claim, breached record, or manually processed backlog. Treat attestation as a piece of evidence in the supplier ledger.

### 2. SBOM is a map fragment, not continuity

A bill of materials can expose component risk and accelerate vulnerability triage. It does not say whether the vulnerable component is deployed, reachable, compensated, privileged, exploitable, or tied to a public service. SBOM belongs in the exposure ledger.

### 3. Vulnerability remediation is not degraded-service readiness

A patch exception can be rational for legacy systems, medical dependencies, court systems, or benefits platforms, but every exception must name the service tail: who is harmed if the asset fails before the patch lands, and what route keeps them served.

### 4. Incident reporting is not affected-person repair

Regulatory reporting and public breach notification can be timely and still miss the practical injury: rescheduled lab work, missing claims, pharmacy blocks, denial letters, frozen records, exposure to fraud, missed appeal windows, or lost access to cultural and research materials.

### 5. Restoration is not reconciliation

A system can be declared restored while queues, data integrity, paper workarounds, duplicate work, debt, adverse decisions, or downstream screening errors persist. Recovery is not complete until the affected-person and service ledgers close.

## Upgrade triggers

Route the matter to a full cyber/software continuity docket when any of the following are true:

- a supplier, cloud, clearinghouse, lab, identity provider, managed service, or embedded software product sits between the public agency and service delivery;
- the incident affects health care, benefits, payroll, courts, education, public safety, cultural memory, or other public functions;
- public communication emphasizes restoration while downstream people, claims, appointments, payments, records, or deadlines remain unresolved;
- breach notification exists but service-continuity injury is not measured;
- secure-development assurance exists but runtime assets, privileged access, or exploited vulnerabilities are not joined to public-function consequences;
- an emergency fallback route exists only as policy language, not as tested staffing, authority, and reconciliation.

## Downshift conditions

A lighter procurement or security-control review is enough only when the system is not in a public-service path, the supplier can be isolated without service loss, no personal or protected data are exposed, no critical deadline or payment is affected, and recovery can be verified without joining case-level or person-level outcomes.

## Failure modes

- **No resilience by attestation:** accepting a secure-software form as proof that public services will continue.
- **No security by SBOM:** treating component disclosure as evidence of deployed exposure, patching, exploitability, or continuity.
- **No continuity by incident page:** letting a public status page substitute for claims, payments, appointments, records, and access evidence.
- **No restoration by uptime:** closing recovery while queues, data integrity, paper workarounds, or affected-person remedies remain unresolved.
- **No breach repair by notification count:** reporting data exposure without fraud, correction, service, and downstream-denial tail.
- **No supplier governance by renewal:** renewing the same dependency without concentration, exit-right, identity, logging, or fallback consequences.

## Audit questions

- Which public functions would fail if this supplier or runtime asset is unavailable for one day, one week, and one month?
- What is the difference between the attested software product and the deployed production dependency?
- Who can approve degraded mode, and how is the backlog reconciled afterward?
- Which affected people need notice, remedy, extension, credit, replacement service, fraud monitoring, or appeal reopening?
- Which controls are tested against the specific failure mode rather than asserted against a generic framework?
- Which contract terms, concentration risks, or architecture decisions made the incident harder to contain or recover from?

## Source posture

This note uses official policy, technical, incident, and public-body sources: OMB risk-based software and hardware security guidance, NIST SSDF, CISA software-attestation, CPG, KEV, ransomware, and CIRCIA materials, HHS Change Healthcare incident materials, NHS Synnovis incident updates, and the British Library cyber-attack lessons review. The official sources are necessary, but they remain status surfaces; a live case still needs service-level and affected-person evidence.
