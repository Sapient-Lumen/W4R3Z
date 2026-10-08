# Mandates & Jurisdiction Scope Integrity

**Goal:** prevent “mission creep,” jurisdiction ping‑pong, and covert power shifts by making **who may do what** legible, versioned, and contestable—across micro‑local to global scopes.

This memo defines a minimal **Mandate Integrity Protocol (MIP)** that can be applied to agencies, councils, regulators, courts, platform-governance bodies, and intergovernmental compacts.

---

## Core primitives (receipts + registries)

### 1) Mandate Card (`MC-*`) — publish the *authority surface*
Every public body (or delegated actor) MUST publish a short **Mandate Card**:

- `MC.id`, `MC.version`, `MC.effective_from`
- **Authority sources:** constitution/statute/treaty/compact/court order (`RID-*` links if available; see `118-rulemaking-and-change-control.md`)
- **Competences:** what the body may decide / enforce / spend / collect
- **Non‑competences:** explicit “cannot do” list (anti‑creep)
- **Decision interfaces:** what receipt types it emits (e.g., `DRR-*`, `CFR-*`, `FER-*`)
- **Geography + persons covered:** jurisdictional bounds
- **Cross‑body dependencies:** required handoffs/approvals; dispute resolver (`CRD-*`, see `114-interjurisdictional-dispute-and-coordination.md`)
- **Transparency floor:** what must be public; what may be withheld and why (`115-information-integrity-and-record-interfaces.md`)
- **Appeal / contest lane:** where challenges go and the contest window

**Rule:** if it cannot fit on one page, it is not a Mandate Card.

### 2) Delegation / outsourcing receipt (`DLG-*`) — when authority is moved
Whenever authority is delegated to another body (or to a private/non‑state provider), the delegator MUST publish a **Delegation Receipt**:

- scope of delegated power; duration; renewal conditions
- oversight hooks (audit/inspection, reporting cadence) (`130-audit-and-inspection-integrity.md`)
- enforcement boundaries (what the delegate may not do)
- data-sharing purposes + limits (`127-data-governance-and-privacy-interfaces.md`)
- grievance lane: who is accountable to the person (no “not my department”)

### 3) Scope Change Receipt (`SCR-*`) — version control for power shifts
Any meaningful change to competence/jurisdiction MUST emit a **Scope Change Receipt**:

- what changed, why, who proposed, what alternatives were considered
- who gains/loses power and which people are affected
- effective date + **non‑retroactivity default** (unless explicitly justified)
- required updates: Mandate Card version bump; interface registry update (`128-interoperability-interfaces-and-standards.md`)
- contest window + standing

### 4) Overlap & gap register (`OGR-*`) — seams are named, not denied
Maintain a living **Overlap/Gaps Register**:

- overlaps (two+ bodies can act) and gaps (no one can act)
- “seam owner” for each overlap/gap (temporary if needed)
- interim continuity default so the person is not harmed during institutional argument (`109-portability-and-cross-jurisdiction-continuity.md`)

---

## Operating rules (minimal, high leverage)

### Rule A — Subsidiarity as an evidence claim, not a slogan
If a higher scope claims authority over a lower scope, it MUST publish an evidence‑based `SCR-*` showing why the lower scope cannot meet person‑facing floors (capacity, spillovers, rights protection). Tie to metrics (`03-metrics-and-evidence.md`).

### Rule B — “No ping‑pong” duty
If an issue falls within a body’s **possible** competence, it MUST:
1) issue an acknowledgment receipt and interim protection if needed, and  
2) either resolve the case, or issue a time‑bounded `CRD-*` routing decision with continuity preserved.

(See: `114-interjurisdictional-dispute-and-coordination.md`, `108-service-standards-and-time-budgets.md`.)

### Rule C — One accountable face to the person
For any person’s case, there MUST be a single **Accountable Case Owner** (may coordinate behind the scenes). The person should never be forced to re‑file across seams.

### Rule D — Authority cannot hide in software
If automated systems materially shape outcomes, the Mandate Card MUST name:
- the algorithmic decision register entries (`ADR-*`) and
- the contest lane and correction mechanisms.

(See: `115-information-integrity-and-record-interfaces.md`, `127-data-governance-and-privacy-interfaces.md`.)

---

## Minimal publishable metrics

- % of bodies with current `MC-*` (and last update date)
- # of `SCR-*` per quarter; share with contest initiated
- overlap/gap count and median time‑to‑resolution in `OGR-*`
- “ping‑pong” incidence rate (cases re-routed 2+ times)
- delegation inventory coverage (% of delegated functions with `DLG-*`)

---

## Implementation notes (tight)

- Start by issuing Mandate Cards for the **top 20** bodies that most affect daily life (benefits, housing, policing, licensing, immigration, health, taxation, schools).
- Treat the Mandate Card as the **front page** of every body’s public presence; everything else links outward.
- When in doubt, prefer **bounded authority + strong continuity** over sprawling authority.

---

## References (anchors)

- Subsidiarity principle (EU Treaty Article 5): [BIB-EU-TEU-ART5].  
- Institutional mandates & authority as governance surface (WDR 2017 framing): [BIB-WDR2017].  
- Delegation and oversight basics (public sector accountability/audit): [BIB-ISSAI-100].  
