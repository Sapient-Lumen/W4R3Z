# Land, Housing, and Commons Integrity

**Stack relation:** use `298-land-housing-commons-and-value-capture-routing-guide.md` for the canonical route across the land / housing / commons / value-capture cluster. This memo is the parcel / housing / commons integrity layer; `62` is the broad planning and housing-governance front door; `150` is the stewardship / anti-speculation institutional-carrier specialization; `198` is the value-capture and externalities fiscal specialization.

**Purpose:** Treat land use, housing access, and commons stewardship as *governance interfaces* where discretion, opacity, and delay convert into domination. This memo defines a compact, receipt‑bound protocol layer that scales from micro‑local (block, village, neighborhood) to metro, region, and state.

For **institutional rails** that can carry these interfaces in practice (e.g., CLTs/shared‑equity stewards and other commons units), see `150-land-commons-stewardship-anti-speculation.md`.

This document is intentionally *operational* and joins existing primitives:
- **Rule versioning:** `RCR-*` in [118-rulemaking-and-change-control.md](118-rulemaking-and-change-control.md)
- **Service clocks:** time budgets in [108-service-standards-and-time-budgets.md](108-service-standards-and-time-budgets.md)
- **Seam continuity:** portability in [109-portability-and-cross-jurisdiction-continuity.md](109-portability-and-cross-jurisdiction-continuity.md)
- **Dispute / coordination:** [114-interjurisdictional-dispute-and-coordination.md](114-interjurisdictional-dispute-and-coordination.md)
- **Budget / procurement integrity:** [110-budget-procurement-integrity.md](110-budget-procurement-integrity.md)
- **Legibility budgets:** [134-legibility-and-complexity-budgets.md](134-legibility-and-complexity-budgets.md)
- **Remedy lanes:** [08-remedy-and-grievance.md](08-remedy-and-grievance.md)

---

## Core artifacts

### 1) Parcel & Commons Registry Cards (PCR / CCR)

Minimum publishable units:

- **PCR-*** (Parcel Card): unique `parcel_id`, boundary reference, legal basis, current rights bundle, restrictions, encumbrances, responsible authority, and links to all decisions affecting the parcel.
- **CCR-*** (Commons Card): resource boundary, stewardship authority, access rules, monitoring rules, sanction ladder, revenue/maintenance plan, and contest/appeal routes.

**Invariant L-1 (linkability):** Every land/housing decision must reference *exact* PCR/CCR identifiers and the rule versions in force at decision time (see **past‑rule replay** in `118`).

### 2) Land Use Decision Receipts (LDR)

- **LDR-***: “why + under which rule version + who had standing + what evidence + what alternatives considered + what mitigations + what contest window.”
- Must include **impact deltas** at a minimum: displacement risk, cost-to-comply, travel/time impact, environmental externalities, and accessibility changes.

**Invariant L-2 (anti‑silent change):** No effective change to permissible uses, densities, eligibility, or fee schedules without an `RCR-*` link and an `LDR-*` published within the notice window.

### 3) Housing Allocation Receipts (HAR)

Where housing is scarce (public housing, vouchers, shelters, relocation units, disaster housing):

- **HAR-***: eligibility test applied, queue position (privacy-preserving), priority basis, any discretionary overrides, and a clocked decision trail.
- Join to **status receipts**: `CSR-*` in [125-identity-membership-and-civil-status.md](125-identity-membership-and-civil-status.md).

**Invariant H-1 (no invisible discretion):** Overrides are allowed only with explicit grounds, bounded categories, and auditability.

### 4) Displacement & Relocation Protocol (DRP)

Applies to evictions, buyouts, rezoning displacement, infrastructure projects, and disaster recovery:

- **DRP-***: displacement trigger, notice, interim protection, relocation options, compensation basis, continuity of services, and post-move remediation.
- **Provisional continuity default:** if the responsible authority misses the relocation clock, **interim housing / benefits continue** until resolved (joins `108` and `109`).

**Invariant D-1 (continuity over seam):** Transfers between agencies/jurisdictions cannot reset eligibility, evidence, or clocks.

### 5) Land Value Capture & Compensation Discipline (LVC)

When governance actions create windfalls or harms:

- Publish a **Value Delta Note** attached to each `LDR-*`:
 - `windfall_estimate`, `harm_estimate`, methodology, and uncertainty bounds.
- Define a **capture channel** (tax/fee/exaction) and a **compensation channel** (relocation, payments, service credits).

**Invariant V-1 (symmetry):** If the system can impose costs, it must define an explicit compensation lane for comparable harms.

---

## Minimal rights floors (scope-agnostic)

- **Standing floor:** affected residents, tenants, adjacent parcels, and commons users have standing.
- **Contest floor:** a real contest window with time budgets and escalation triggers.
- **Legibility floor:** “person path” to understand and challenge a land/housing decision must fit within complexity budgets (`134`).
- **Safety floor:** reporting corruption or coercion in housing/land processes routes through protected disclosure (`121`) and influence integrity (`120`).

---

## Capture surfaces & circuit breakers

### Common capture patterns
- Zoning/permit discretion as a bribe surface
- “Emergency” exemptions becoming permanent
- Opaque queues / priority manipulation
- Vendor lock-in in housing services or registries
- Jurisdictional ping‑pong during relocation / eligibility

### Circuit breakers (trigger table)
- **CB-L1:** unexplained decision time > budget → *auto escalation + interim protection*
- **CB-L2:** decision affects >X people or increases rents/fees >Y% → *mandatory independent review window*
- **CB-L3:** repeated overrides / waivers by same official → *audit trigger + recusal review*
- **CB-L4:** registry integrity incident → *freeze high-impact transactions until reconciliation*

(Implement using the circuit-breaker framework in `105`.)

---

## Minimal metrics (publishable)

- **Decision latency:** median/95p for permits, allocations, relocation.
- **Override rate:** % of `HAR-*` or `LDR-*` with discretionary override.
- **Displacement outcomes:** % relocated within target window; % with service continuity failures.
- **Appeal outcomes:** reversal rate and common error classes.
- **Complexity burden:** median steps/time to understand + contest a decision.

---

## References (add keys in bibliography)

- [BIB-UN-HOUSING-RIGHT] — UN CESCR General Comment No. 4 (Right to adequate housing) + No. 7 (Forced evictions).
- [BIB-OSTROM-GOVERNING-COMMONS] — Elinor Ostrom, *Governing the Commons*.
- [BIB-HENRYGEORGE-LVT] — Land value tax / value capture foundations (Henry George; modern summaries).
- [BIB-OECD-LANDUSE] — OECD land use / housing policy work (zoning, affordability, land governance).
- [BIB-WB-LANDGOV] — World Bank land governance / land administration guidance.

