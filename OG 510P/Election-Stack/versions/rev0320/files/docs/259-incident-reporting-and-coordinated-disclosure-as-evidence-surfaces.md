# 259 — Incident reporting and coordinated disclosure as evidence surfaces

**Track:** Shared

This spec defines **digest-first, publishable** evidence surfaces for incident reporting and coordinated disclosure in election infrastructure.
It is written to improve **defensive convergence** (who knows what, when, and how it was handled) **without** publishing operational details that enable attackers or enable intimidation.

> This document is not legal advice and does not determine whether an incident is “reportable” under any statute or policy.

## 259.1 Why this exists

In disputes, two failures recur:

1. **Silent handling:** an incident happened, but there is no checkable record of triage, scope, or closure.
2. **Over-sharing:** “transparency” publishes exploitable details or voter/staff PII.

We want a third posture: **bounded disclosure** that is (a) independently checkable and (b) minimally harmful.

For election infrastructure, CISA publishes voluntary incident reporting guidance intended for election stakeholders.  
For public communications during incidents, EAC/CISA provide an incident response communications guide.  
For incident-handling structure, NIST SP 800-61r3 provides updated guidance on incident response processes and considerations.

## 259.2 Non‑claims and boundaries

- This spec does **not** provide exploit steps, scanning guidance, or operational attack playbooks.
- This spec does **not** publish IOCs, internal hostnames, IP ranges, credentials, vendor configs, ballot images, or voter identity data.
- This spec does **not** attempt to “compel” or substitute for statutory reporting regimes. For example, CISA’s CIRCIA rulemaking is an evolving process; treat any reporting timelines as jurisdiction- and regime-specific and consult primary sources.

## 259.3 Evidence surfaces (what we *can* publish)

### 259.3.1 Incident Disclosure Stub (IDS)

A minimal, publishable statement that:

- **an incident class occurred** (taxonomy only),
- **time-bounds** (start/containment/closure as *ranges* if needed),
- **systems affected (coarse)** (e.g., “public website”, “ENR pipeline”, “workstation fleet”),
- **current posture** (investigating / contained / resolved / monitoring),
- **link to follow-up commitments** (next update window).

**Publish as:** `PublicNotice` (kind `hfv.public_notice`) with a new `notice_type=incident_stub`.  
(Use the correction discipline and supersedes graph rules already defined for notices.) See `186`, `219–221`, `234–236`.

### 259.3.2 Incident Timeline Digest (ITD)

An append-only, timestamped list of **events described at a high level** (e.g., “phone report received”, “systems isolated”, “forensics engaged”, “patch applied”), each event line hashed.

- The public artifact is the **hash chain**, not the internal timeline text.
- Public releases may include selected event summaries, but only at “coarse” granularity.

**Publish as:** an evidence object (new schema suggested below) or as a hash list embedded in a `PublicNotice` attachment digest.

### 259.3.3 External Notification Ledger (ENL)

A publishable ledger that records **which external entities were notified**, **when**, and **by which channel class**, without revealing sensitive contents.

Example entries:

- “State election authority notified (secure email)”
- “CISA voluntary report filed (portal)”
- “Vendor support case opened (ticket)”
- “Law enforcement contacted (phone)”

For voluntary reporting references, use the CISA election infrastructure guidance as the *anchor*, not as a claim of compliance.

### 259.3.4 Public Communications Packet (PCP)

When communications are needed, publish a **bounded packet**:

- what is known / unknown,
- what is being done,
- how the public can verify official updates (OfficialChannelDirectory + parity),
- what changes will be announced and when.

Anchor to the EAC/CISA incident response communications guide.

## 259.4 Suggested schema additions (bounded)

If implementing new evidence objects, keep them tiny:

- `hfv.incident.disclosure_stub` (or reuse `PublicNotice` only)
- `hfv.incident.timeline_digest` (hash chain + coarse labels)
- `hfv.incident.external_notification_ledger` (recipient category + timestamp + channel class + optional digest)

Avoid adding objects that carry operational details.

## 259.5 Stop conditions (anti‑weaponization)

Immediately stop and escalate to the archive’s “non-claims / boundaries” posture (`167`) if any draft artifact contains:

- voter identity data, ballot images, signatures, or individualized cure/provisional details
- staff identities beyond role labels (unless explicitly authorized and necessary)
- exploitability details (exact vuln names + versions + reachable surfaces) before coordinated disclosure
- network diagrams, internal IPs, hostnames, or vendor configuration screenshots
- instructions that would enable intimidation, disruption, or targeted harassment

When in doubt, publish **hashes + commitments + update windows**, not substance.

## 259.6 Minimal templates (copy-paste safe)

**IDS fields** (in prose or structured):

- Incident class: `physical_threat | cyber_intrusion | outage | misconfiguration | misinformation_event | other`
- Scope: `public_surface | internal_ops | reporting_pipeline | tabulation | unknown`
- Status: `investigating | contained | resolved | monitoring`
- Next update by: `<UTC timestamp or range>`
- Links: Official channels (`203`) + status board (`195`) + parity snapshot policy (`201`)

## 259.7 Integration hooks

- Use `216` (incident triage quickmap) as the operator entrypoint; add a row mapping incident classes → IDS/ITD/ENL/PCP.
- Bind IDS/PCP updates into the same correction discipline as results (`234`) so audiences can converge on “current state”.
- When incidents affect ENR/unofficial results, bind IDS to the URSP + corrections log (`252`).


## Primary anchors

- [CISA — Voluntary Incident Reporting Guidance for Election Infrastructure (PDF)](https://www.cisa.gov/sites/default/files/2024-07/2024-Voluntary-Incident-Reporting-Guidance-for-EI-Stakeholder_6.26.24_508c.pdf)
- [EAC/CISA — Election Infrastructure Incident Response Comms Guide (PDF)](https://www.eac.gov/sites/default/files/2024-10/Election_Infrastructure_Incident_Response_Comms_Guide_508.pdf)
- [NIST — SP 800-61r3 (PDF)](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r3.pdf)
- [CISA — CIRCIA overview](https://www.cisa.gov/topics/cyber-threats-and-advisories/information-sharing/cyber-incident-reporting-critical-infrastructure-act-2022-circia)
