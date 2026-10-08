# 267 — Personnel security, insider risk, and worker safety as evidence surfaces

**Track:** Shared (cross-cutting)

This doc defines **bounded, publishable proof surfaces** for the human side of election operations:
who has access, how access is controlled, how insider risk is mitigated, and how worker safety threats are handled —
**without** publishing rosters, personal data, or operationally sensitive details.

It composes with:
- **CommitLog / transparency** (`261`)
- **Crypto-Proof Packaging (CPP)** (`265`)
- **Physical security & access** (`266`)
- **Incident disclosure** (`259`)
- **Training / tabletop** (`258`)

## Non-goals

- Not a “background check how-to”, not a hiring manual.
- Not a surveillance program blueprint.
- Not a jurisdiction-specific legal guide.
- Not a replacement for law enforcement processes or HR/legal counsel.

## Core principle

Publish **attestations + digests + change records** that let an independent observer answer:

> “Is access controlled and reviewed, are roles separated, and are threats handled — *without* exposing people or creating new attack surfaces?”

## Minimal publishable artifacts

### 1) Personnel Security Posture Statement (PSPS)

A public statement of **policy posture**, not implementation detail.

**Must include (public):**
- Role classes (e.g., *tabulation operator*, *ballot intake supervisor*, *IT admin*, *observer coordinator*) — **no names**
- “Two-person integrity” roles (where required)
- Vetting posture in broad terms (e.g., “screening performed consistent with jurisdiction policy”)
- Training posture (required training modules + recert cadence)
- How concerns are reported (public channel + escalation path)

**Should not include:**
- Screening criteria details, internal thresholds, or investigative methods
- Shift rosters, contact details, or home/work locations beyond public office info

### 2) Role/Access Boundary Map Digest (RABMD)

A digest that makes **who-can-do-what** legible without leaking credentials.

**Shape (publishable):**
- A role-to-capability matrix at coarse granularity (e.g., `can_export_results_digest`, `can_open_seal_inventory`, `can_run_LA_test`)
- A hash commitment to the full internal mapping and approval record (CPP)

### 3) Access Review Ledger (ARL)

An append-only ledger of access reviews.

**Publishable fields:**
- Review period, reviewer role, systems/classes reviewed
- Counts: grants, removals, exceptions
- Exceptions must have: reason code + expiry + approving role (not person)

Bind each ARL entry into CommitLog (`261`) so deletions are detectable.

### 4) Training & Credentialing Digest (TCD)

A digest proving training happened without publishing personnel info.

**Publishable fields:**
- Training syllabus identifier (e.g., “Poll Worker Core vX.Y”, “Tabulation Room Access vX.Y”)
- Date range and counts completed
- A hash commitment to internal completion records

This composes with the bounded exercise artifacts in `258`.

### 5) Insider-Concern Intake Capsule (ICIC)

A minimal capsule that an insider concern channel exists and is used responsibly.

**Publishable fields:**
- Intake channel class (hotline / web form / in-person)
- Reporting protections posture (“no retaliation” policy reference)
- Aggregate counts by category (optional), in coarse bins
- Escalation partner class (internal / external law enforcement) without case details

### 6) Threat & Harassment Handling Capsule (THHC)

A bounded public artifact for threats directed at election workers.

**Publishable fields:**
- Time window, threat categories (coarse), reporting confirmation
- “What we did” at policy level (e.g., reported, documented, coordinated with law enforcement)
- Links to official guidance for officials/workers on personal security and documentation

Do **not** publish: identifying details, attacker details, addresses, or operational changes that increase risk.

## “Stop conditions” (do not publish)

- Any roster or individual-level identifiers (names, phone, email, home address).
- Facility layout details or routes beyond already-public info.
- Screening criteria thresholds, investigative playbooks, monitoring tactics.
- Details that could facilitate intimidation, doxxing, or targeted coercion.

## Primary anchors (cite-first)

- EAC: **Poll worker best practices** — recruitment, training, retention pointers.  
  xref: eac_officials_poll_worker_best_practices

- EAC: **Election official security** — threat documentation/reporting quick reference.  
  xref: eac_officials_official_security

- EAC: **Personal security & mental health clearinghouse resources** (stress, challenging interactions, PII removal memo).  
  xref: eac_officials_clearinghouse_personal_security_mental_health

- EAC: **Poll worker training guide (Paraquad RAAV)** (training structure, accessibility reminders).  
  xref: eac_assets_1_1_paraquad_raav_worker_training_guide

- EAC: **Adult Learning tip sheet** (effective poll worker training).  
  xref: eac_2025_12_eac_adult_learning_one_pager_508

- CISA: **Insider Threat Mitigation Guide** (program framework; not election-specific but applicable).  
  xref: cisa_insider_threat_mitigation_guide
