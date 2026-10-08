# Industrial Policy & Supply-Chain Resilience Governance

**Purpose:** make “industrial strategy” (subsidies, procurement, domestic-content rules, strategic stockpiles, reshoring/nearshoring, export controls) **auditable and contestable** so it strengthens resilience without becoming a capture machine.

**Person served:** a person paying higher prices, losing a job, or living through shortages who needs to know *who decided what*, *why*, *who benefits*, and *how to contest or unwind it*.

## Core primitives

### 1) Mission / Capability Docket (MCD-*)
Every industrial-policy “mission” MUST have a short docket that can be audited.

**MCD fields (minimum):**
- **Capability target:** what capability, at what scale, by when (avoid vague “competitiveness”).
- **Threat model:** which failures this mitigates (single-supplier risk, geopolitical chokepoint, pandemic surge, grid fragility).
- **Scope + beneficiaries:** who is eligible; who is excluded; anti‑discrimination notes.
- **Counterfactuals:** why this is better than alternatives (trade diversification, demand reduction, standards, insurance).
- **Sunset + exit:** explicit unwind plan; what success/failure looks like; renewal requires evidence.
- **Capture defenses:** revolving-door constraints; disclosure; conflict-of-interest rules; independent evaluation hooks.
- **Join keys:** links to the spending rails (`REL-*`, `110`), project rails (`138`), and evaluation rails (`142`).

**Anchors:** EU NZIA governance patterns (`Regulation (EU) 2024/1735`) and its permitting / public procurement context are useful reference points for “mission dockets” even when jurisdictions differ. See [BIB-EU-NZIA-2024].

### 2) Dependency Map + Chokepoint Register (DMR-*)
Resilience begins with knowing where the brittle points are.

**DMR fields (minimum):**
- **Critical inputs:** components/materials/services; substitutability bands.
- **Supplier concentration:** “single point” dependencies and correlated risk.
- **Time-to-replace:** lead times and ramp constraints (months/years).
- **Mitigations:** diversify, stockpile, standards, redesign, mutual aid.
- **Disclosure posture:** publish aggregate where operational secrecy is needed (joins `77`).

**Evidence note:** policy should prefer *diversification and risk management* over blanket autarky when possible; see OECD’s resilience framing. [BIB-OECD-SUPPLY-RESILIENCE-2025]

### 3) Subsidy / Tax Credit Case File (STC-*)
If the state is paying (directly or via tax expenditure), it MUST be receipted.

**STC fields (minimum):**
- **Award basis:** criteria and scoring; ties to MCD-* target(s).
- **Terms:** jobs, wages, training, environmental performance, clawbacks, reporting cadence.
- **Guardrails:** restrictions and disclosure obligations (e.g., for advanced manufacturing credits).
- **Public value ledger:** who got what; what was promised; what was delivered (joins BRR-* in `138`).

**Anchors:** U.S. CHIPS implementation includes structured guardrails and tax-credit rulemaking that can be mined for “case file” fields and disclosure expectations. [BIB-US-CHIPS-48D-2024]

### 4) Procurement Preference Receipt (PPR-*)
Domestic-content or “Buy X” rules are *power* over markets; they must be contestable.

**PPR fields (minimum):**
- Rule version (`118`) + legal basis.
- Definition of “domestic content” and calculation method.
- Exceptions / waivers (and who can grant them) joined to `85`.
- Expected price effects and mitigation for vulnerable groups.
- Reciprocity / trade-compatibility notes where relevant.

### 5) Strategic Stockpile & Allocation Protocol (SSAP-*)
Stockpiles fail when allocation is ad hoc or politicized.

**SSAP fields (minimum):**
- Inventory classes; rotation/expiry discipline; audit cadence.
- Allocation tiers with reason codes + contest path (joins `140` queues).
- Surge triggers and deactivation rules (joins `23/112`).

## Circuit breakers (anti‑capture defaults)

- **CB‑IP1 “No blank-check mission”:** if an MCD-* lacks sunset + exit + evaluation hooks, spending is blocked (or auto‑escalated for independent review).
- **CB‑IP2 Concentration alarm:** if >X% of subsidy dollars flow to one firm/group in a sector, trigger a competition + capture review (joins `94`, `130`).
- **CB‑IP3 Clawback reality:** missed delivery milestones auto‑trigger clawback review; failure to pursue clawbacks must be justified publicly.
- **CB‑IP4 Waiver transparency:** waivers to procurement preferences must publish PPR-* within a fixed window (no silent exceptions).
- **CB‑IP5 “Industrial policy is fiscal policy”:** require a tax‑expenditure ledger entry and distributional note for credits/subsidies (joins `135`).

## Minimal metrics (publishable)
- Delivery vs. promise: jobs/wages/training, capacity built, lead times reduced.
- Price pass‑through and distributional impacts (especially on low‑income households).
- Dependency health: # of single‑point chokepoints; time‑to‑replace trend.
- Capture signals: concentration, revolving-door flags, lobbying intensity (where measurable).
- Clawback rate and waiver rate (and reasons).

## Joins (where this plugs in)
- Budget/procurement integrity: `110-budget-procurement-integrity.md`.
- Public investment + benefits realization: `138-public-investment-and-capital-projects-integrity.md`.
- Competition/market power: `94-competition-and-market-power-governance.md`.
- Sanctions/compliance: `131-compliance-and-sanctions-integrity.md` (export controls + restrictions).
- SCRM and critical infrastructure: `59` and `137`; cybersecurity SCRM practices can template DMR-* operationalization. [BIB-NIST-800-161R1-2024]

