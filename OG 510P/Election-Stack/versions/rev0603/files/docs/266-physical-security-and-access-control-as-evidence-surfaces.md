# 266. Physical security and access control as evidence surfaces

**Track:** Shared

Physical security is not “just operations.” It is a **primary integrity control** for ballots, voting equipment, tabulation environments, and the staff who operate them.

This document defines a **minimal, publishable** set of physical-security artifacts that:
- Improve checkability and post-incident reconstruction,
- Avoid doxxing / intimidation risk,
- Avoid leaking sensitive facility layouts and defensive details,
- Compose cleanly with the archive’s **CommitLog / CPP** patterns (`261`, `265`) and **Chain-of-Custody** surfaces (`247`, `251`, `254`).

---

## Design constraints

### Do publish (digest-first)
Publish **hashes, counts, attestations, and coarse timelines** that can be verified and cross-checked.

### Do not publish
- Floor plans, camera placements, alarm details, lock models, keying systems, guard schedules.
- Names of staff in sensitive roles (use role tags).
- Serial numbers for sensitive devices unless you already treat them as public identifiers and have a strong safety case.

---

## Minimal publishable artifacts

### 1) Physical Security Posture Statement (PSPS)
A short, stable statement of your **baseline posture**:
- Controlled areas / public areas definition (coarse),
- Access authorization model (roles, not names),
- Two-person integrity where required,
- How seal custody works (who can apply, who can verify),
- How access logs are retained and audited.

Publish: the statement + a **hash commitment** to the controlled detailed procedures (kept internal).

### 2) Controlled Access Log Digest (CALD)
An **append-only digest** of access events for controlled areas (e.g., ballot storage, tabulation room).
- Each entry: timestamp window, role class (e.g., “Elections staff”, “Facilities”, “Law enforcement escort”), reason code, and a hash pointer to the internal log record.
- Publish daily/weekly rollups (counts by role class + reason code), plus a log hash chain.

### 3) Key / Credential Control Attestation (KCCA)
A minimal statement of:
- Who holds which class of credential (roles only),
- Rotation / revocation cadence,
- Escalation path if a credential is suspected compromised.

Publish: the attestation + last rotation date (coarse).

### 4) Seal Inventory Snapshot (SIS)
Seals and tamper-evident materials are evidence-bearing controls.
Publish a periodic snapshot:
- Seal type classes (not vendor models),
- Starting and ending counts for the period,
- Loss/damage anomalies (counts + high-level disposition),
- Hash commitment to the internal seal ledger.

### 5) Facility Incident Capsule (FIC)
For **physical incidents** (break-ins, vandalism, threats, unauthorized entry, environmental hazards):
- “What happened / what we know / what we do not know”
- What integrity-relevant assets could be affected (classes only)
- What the next verification step is (e.g., custody check, reconciliation, audit escalation)
- A pointer to the public incident disclosure surface (`259`) if needed.

---

## Role and reason codes

Keep reason codes stable and boring. Example starter set:
- `ACCESS_NORMAL_OPS`
- `ACCESS_CHAIN_CUSTODY_TRANSFER`
- `ACCESS_EQUIPMENT_MAINT`
- `ACCESS_EMERGENCY_FACILITIES`
- `ACCESS_ESCORTED_VISITOR`
- `ACCESS_INCIDENT_RESPONSE`

Publish the **dictionary**, not the detailed narratives.

---

## Composition rules

### Pair with Chain-of-Custody
Where custody transfers occur (ballot transport, drop box retrieval, ballot-room moves), emit:
- custody record hashes (`247`, `251`),
- a matching access digest entry (CALD) for entry to controlled storage areas.

### Pair with Change control and ENR snapshots
When software/config changes are made in controlled rooms:
- link the change-control packet hash (`256`) to the access digest (CALD) window for that session.

### Pair with Audit Publication Pack
If a tabulation audit requires opening controlled storage:
- reference the same CALD window and custody hashes in the APP (`260`).

---

## Stop conditions (anti-weaponization)

If any request (public or PRR) asks for details that would:
- enable bypassing security controls,
- facilitate intimidation or targeted harassment,
- expose sensitive staff identities,
- expose precise storage or movement routes,

then respond with:
- the relevant **publishable digest artifacts** above,
- and a redaction/denial record under `253` (Public records bounds), explaining the category and basis for withholding.

---

## Primary anchors (cite-first)
- CISA: *Physical Security of Voting Locations and Election Facilities* (v2). xref: cisa_physical_security_of_voting_location_facilities_v2_508
- CISA: *Physical Security Checklist for Election Offices* (Sep 2024). xref: cisa_2024_09_physical_security_checklist_for_offices_508
- EAC: *Election Management Guidelines — Chapter 3: Physical Security*. xref: eac_event_document_management_guidelines_chapter_3_physical_security
- EAC: *Chain of Custody Best Practices* (Jul 2021). xref: eac_bestpractices_chain_of_custody_best_practices
- NIST: SP 800-53 Rev. 5 (Physical & Environmental Protection family). xref: nist_pubs_sp_800_53_r5_upd1_final
