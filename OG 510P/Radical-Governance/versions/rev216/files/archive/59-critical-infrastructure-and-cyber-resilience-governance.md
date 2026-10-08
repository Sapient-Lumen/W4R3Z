# Critical Infrastructure & Cyber Resilience Governance

**Purpose:** keep critical infrastructure resilient while preventing secrecy and vendors from becoming accountability black holes.

When essential services depend on digital systems (IT and OT), **cybersecurity becomes governance**: outages and breaches can function like rights violations, fiscal shocks, or covert coercion. This memo defines a compact **Minimum Viable Critical Infrastructure & Cyber Resilience Governance Spine (MV-CICRG)** that reuses existing join-keys and registers (no new ID families).

**Anchor set (start here):** NIST Cybersecurity Framework 2.0 ([BIB-NIST-CSF-2-0]); CISA Cross‑Sector Cybersecurity Performance Goals 2.0 ([BIB-CISA-CPG-2-0]); ISO/IEC 27001:2022 ([BIB-ISO-27001-2022]); IEC 62443 (OT security) ([BIB-IEC-62443]); NIS2 Directive (EU) 2022/2555 ([BIB-EU-NIS2]).

**See also:** `48-asset-and-infrastructure-register.md` (`AST-*`), `13-regulation-utilities-and-soes.md` (regulated utilities), `06-digital-and-algorithmic-governance.md` (vendor + system governance), `23-emergency-governance-and-exceptions.md` (`EMR-*`), `24-mutual-aid-and-serious-incident-protocol.md` (multi‑agency incident command), `55-oversight-findings-and-response-register.md` (`OFR-*`), `53-publication-integrity-and-tamper-evident-logs.md` (tamper evidence).


## Kernel anchors (do not repeat)
- Person-facing invariants: `98-persons-path-and-accessibility-invariants.md` (incl. non‑digital/non‑reading options), service journeys `47-...`, remedy lanes `36-...` / `08-...`.
- Protective legibility + adoption dynamics: `99-protective-legibility-and-adoption-dynamics.md` (transparency ≠ accountability; identify who loses discretion / who gains contestation capacity).
- Publication integrity (no silent edits; “as‑of” access): `53-...` and `31-...` where relevant.
- Emergency exceptions + incident command: `23-...` and `24-...` (avoid “incident” becoming a blank cheque).
- Secrecy/retaliation constraints for reporting and disclosures: `77-...`.

## Named tensions (design must surface these)
- Transparency vs exploit leakage (what builds trust vs what helps attackers).
- Rapid containment vs due process and service continuity (don’t launder unlawful denials through “system outage”).
- Centralization for security vs decentralization for resilience (avoid single points of failure).
- Vendor/commercial secrecy vs public accountability for essential services.
- Triage under outage vs fairness (who gets restored first and why).

---

## 1) What this covers (scope)
**Critical infrastructure (CI):** assets and services whose failure threatens life, safety, rights, or large economic harm (energy, water, health, transport, communications, core government registries, major payment rails).

**Cyber resilience:** the ability to prevent, withstand, recover from, and learn from malicious or accidental digital failures — including supply-chain compromise and operational technology (OT) failures.

**Rule:** treat **service‑critical IT/OT** as first‑class `AST-*` objects (or as `AST` subcomponents) so maintenance, outages, procurement, and oversight can join.

---

## 2) The spine (interfaces and required artifacts)

### A) Asset visibility (`AST-*`)
For CI assets and service‑critical systems:
- the Asset & Infrastructure Register (AIR) MUST record ownership/operator Unit IDs and criticality tier (`48-...`).
- the AIR SHOULD include a **public cyber posture pointer** (coarsened): baseline standard(s) (`STD-*`) and the latest security assessment/capability release (`REL-*`), without disclosing exploit‑useful detail.

### B) Baseline standards (`STD-*`) + exceptions as decisions (`DRR-*`)
- Each CI operator MUST publish a baseline controls profile (as a `REL-*` release) mapped to one or more governance‑grade standards (e.g., CSF 2.0 / ISO 27001 / sector baselines) and register the pinned standard versions as `STD-*` where applicable.
- **Risk acceptance / exception approvals** (e.g., delayed patching, legacy OT that cannot be upgraded, compensating controls) MUST emit a `DRR-*` with:
  - affected `AST-*` (and `SRV-*` where service impacts are foreseeable),
  - cited baseline controls (`STD-*` / `REL-*`),
  - reason codes (`RC-CY-*` where applicable),
  - expiry/review date and compensating controls,
  - oversight/approval identity (Unit ID) and the appeal/whistleblower lane (`AL-*`).

### C) Incident logging and public notice (reuse `DRR` + `REL`)
Do **not** create a new “incident ID” family by default. Use:
- `DRR-*` tagged `DRR-TYPE: INCIDENT` for the incident record (time, affected `AST-*`/`SRV-*`, containment actions, authority invoked).
- `REL-*` for public releases: outage/breach notices, timelines, service restoration metrics, and (when appropriate) redacted technical postmortems.

**Rule:** public outage/breach notices are *person-facing determinations* about access and risk; they MUST be written so affected users can understand and act (comprehension test + navigation duty), and MUST include at least one non-digital channel if digital delivery is compromised. (`98-persons-path-and-accessibility-invariants.md`, `61-...`, `82-...`)

**Rule:** if an outage/breach changes service access, eligibility, or enforcement posture, affected decisions MUST still issue normal receipts (`DRR` + `AL-*`). “The system was down” is not a lawful denial.

### D) Oversight follow‑through (`OFR-*`)
- Material incidents MUST open an `OFR-*` case within a short window and close it with findings + corrective actions (see `55-...`).
- Repeat incidents or chronic exceptions SHOULD produce a standalone `OFR-*` finding (systemic) even when no single incident is catastrophic.

### E) Emergency powers (`EMR-*`)
When emergency authority is invoked (e.g., emergency procurement, forced shutdown, extraordinary data-sharing), it MUST be logged as `EMR-*` and joined to the incident `DRR-*`, with explicit sunset/renewal and post‑incident review requirements (`23-...`, `45-...`).

---

## 3) Minimum control domains (keep it small)
Use a **small, measurable baseline** (CPG-like) plus a maturity track (CSF/ISO). The baseline SHOULD include, at minimum:

1) **Identity & access control** (least privilege; MFA where feasible; privileged access isolation).  
2) **Asset inventory + configuration control** (especially OT and vendor-managed components).  
3) **Patch/vulnerability management** (time-bounded; typed exceptions).  
4) **Backups + restore tests** (immutable/offline where feasible; prove restore works).  
5) **Logging + monitoring** (detection, alert triage, retention; protect logs from tampering).  
6) **Incident response readiness** (runbooks, roles, tabletop drills, contact trees).  
7) **Supply-chain / vendor obligations** (security requirements, disclosure timelines, SBOM/attestation where feasible, audit rights; link to the CLC pack in `38-...`).  
8) **Segmentation and safety for OT** (separate IT/OT; constrain remote access; safe shutdown modes).

**Governance rule:** when a baseline is adopted, publish it as a `REL-*` with methods and an “as‑of” date, and bind procurement/service contracts to it (join `CON-*` ↔ baseline `REL-*` / `STD-*`).

---

## 4) Incident regime (disclosure + due process)
### A) Tiered disclosure (two-layer, by design)
- Maintain a protected operational incident log (full detail), but publish a **coarsened public record** quickly unless a narrow, typed exemption applies (`31-...`).
- Public releases SHOULD include: what happened (plain language), affected services, time window, what users should do, and what comes next (timeline for fuller reporting), plus the relevant remedy lane(s) when individuals may need evidence or compensation.

### B) Individuals’ rights and remedy
If a breach/outage plausibly harms individuals (identity theft, benefit interruption, unlawful surveillance, wrongful enforcement):
- publish the remedy lane(s) (`AL-*`) and practical steps,
- default to interim protections where feasible (service continuity for `ESS-1`, fraud/credit protection support, fee waivers) while contestation is pending, to prevent outage/breach harm from compounding.
- provide a way to obtain evidence needed for remedies (without unsafe disclosure),
- join to the data governance registers (`DPR-*`, `ADS-*` where relevant).

### C) Learning loop (prevent “incident theater”)
For material incidents, publish a post-incident learning artifact (often as a `REL-*`) that:
- states what will change (controls/processes/contracts),
- includes time-bounded commitments (join to `PROG-*` / `EVAL-*` when substantial),
- and links to the `OFR-*` closure artifact.

---

## 5) Cross-scope coordination (mutual aid for cyber)
Critical incidents cross boundaries (vendors, shared networks, shared utilities). Use **compacts** rather than ad-hoc favors:
- establish cyber mutual-aid compacts (`CMP-*`) with defined triggers, command-and-control doctrine, evidence integrity rules, cost rules, and dispute lanes (`19-...`, `24-...`).
- ensure data sharing during incidents is purpose-limited, logged, and time-bounded (cite `DPR-*` and any emergency data-sharing `EMR-*`).

---

## 6) Minimal metrics (portable; avoid KPI theater)
Use a small set that maps to outcomes and can be audited:
1) **Time to detect** and **time to contain/restore** (median; by criticality tier).  
2) **Patch latency distribution** (including % with expired exceptions).  
3) **Backup restore test success rate** (and last successful restore date) for CI systems.  
4) **Outage hours** for `ESS-1` services attributable to cyber/IT failure.  
5) **Repeat incident rate** for the same `AST-*` class (signals systemic failure).  
6) **% high-value contracts with CLC + security obligations present** (from `CON-*` coverage).

---

## 7) Common failure modes (and how the spine prevents them)
- **Secrecy laundering:** “security” used to block basic accountability.  
  Counter: two-layer publication model + typed exemptions + time-bounded review (FOI + oversight).
- **Risk acceptance becomes permanent:** exceptions never expire.  
  Counter: exceptions are time-bounded `DRR`s with review dates and oversight sampling.
- **Vendor black boxes:** operators cannot prove controls or recover.  
  Counter: procurement join rules + audit rights + portability/exit + incident disclosure obligations.
- **OT neglect:** “too hard to patch” becomes “never secure.”  
  Counter: explicit compensating controls and safety/segmentation requirements; public maturity track.

