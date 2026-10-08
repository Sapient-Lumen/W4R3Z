# Functional Authorities (Special Districts / Single-Purpose Bodies)

**Purpose:** map functional authority types and their interfaces so real power (not org charts) is traceable and corrigible.

See `14-scope-ladder.md` for the cross-scope map (what belongs where) and the common “kernel” each scope should carry.

Many “in-between” governance layers are not full general-purpose governments. They are **functional authorities**: bodies with a **narrow mandate** (water, transit, schools, drainage, waste, ports, housing finance, etc.) that cut across municipal boundaries.

They are often *the right abstraction* for scale economies and technical systems — and also a common source of **hidden government** (off-book debt, opaque procurement, weak democratic control).

Baseline note: in the U.S., the Census of Governments shows **special district governments** span many functions and are numerous enough to matter for legitimacy and fiscal risk (evidence for the “hidden government” problem): see [BIB-USCENSUS-SPECIALDIST-2022].

This memo defines a tight, reusable pattern for functional authorities that stays aligned with the archive’s stack (`02-design-toolkit.md`) and interfaces (`70-interoperability.md`). For metro/city-region composition patterns, see `16-metropolitan-governance.md`.

---

## Kernel anchors (do not repeat)
- **Person-facing invariants:** `98-persons-path-and-accessibility-invariants.md` (no AI/digital-only gates; oral/assisted options; safety).
- **Remedy is part of the interface:** `08-remedy-and-grievance.md`, `36-appeal-lanes-and-redress-registry.md` (contestability; time bounds; functional equivalents).
- **Protective legibility (transparency ≠ safety):** `99-protective-legibility-and-adoption-dynamics.md`.
- **Records + publication integrity:** `31-records-foi-and-government-memory.md`, `51-release-registry.md`.
- **Authority reality map:** `34-competence-ledger-and-mandate-registry.md`.

## Named tensions (design must surface these)
- **Clear responsibility vs overlap:** single throat to choke vs resilience and redundancy.
- **Expertise vs democratic control:** delegated competence vs public contestation.
- **Specialization vs fragmentation:** many agencies vs coherent person-facing journeys (`47-...`).
- **Emergency discretion vs reviewability:** fast action vs contestable receipts (`23-...`, `43-...`).

## 1) When functional authorities are appropriate
Create (or keep) a functional authority when **both** hold:
- **Scale / network effects:** the service is a network (pipes, rails, grid, basin) or benefits from unified standards and capital planning.
- **Cross-boundary spillovers:** problems cross municipal borders (commuter sheds, watersheds, air sheds, shared hazards).

Avoid functional authorities when the service is primarily **local preference** and not networked — default back to municipal delivery with neighborhood input.

**Creation/upgrade rule:** establishing (or materially expanding) an authority MUST be treated as a scope decision: publish a `DRR` tagged `DRR-TYPE: SCOPE` and update the competence ledger (see `IOP-10` in `02-design-toolkit.md` and `34-competence-ledger-and-mandate-registry.md`).

Polycentric design anchor: see [BIB-OSTROM-POLYCENTRIC-2010].

---

## 2) The core risks (why these bodies become pathological)
1) **Accountability gap:** voters often cannot see or sanction decisions (“low salience, high stakes”).
2) **Fiscal opacity:** debt and liabilities migrate into entities outside headline budgets (including SPVs).
   - Consolidation anchor: see [BIB-IMF-FTC-2019]
3) **Capture:** vendors, bondholders, and regulated incumbents shape policy; revolving doors become the de facto constitution.
4) **Fragmentation:** overlapping jurisdictions create blame-shifting and inequity across service areas.
5) **Regressive finance:** user fees and assessments hit the poor hardest unless explicitly designed otherwise.

A classic warning signal: “special districts” proliferate faster than consolidated reporting and oversight capacity.

---


## 2a) Proliferation control (the ledger is necessary, not sufficient)
- New authorities/SPVs SHOULD require a **portfolio impact note** in the `DRR-TYPE: SCOPE`: why an existing unit cannot host the function, what bodies could be merged instead, and what the consolidation/oversight plan is.
- Require periodic **authority portfolio reviews** (merge/federate/abolish) with published criteria and a public response loop (so “temporary SPVs” don’t become permanent dark government).
## 2b) Hardening a legacy authority (upgrade ladder)
Many jurisdictions inherit districts/SPVs that cannot be abolished quickly. Use a bounded upgrade ladder instead of creating new bodies:
1) **Inventory + ledger:** mint/confirm Unit ID, publish charter summary, board roster, and finance surface (including debt/guarantees).
2) **Receipt + register package:** open contracting (`CON-*`), audited statements, and decision receipts for tariffs/fees/enforcement; missing artifacts become `AL-LEG`/`LEGIBILITY-GAP` issues.
3) **Re-charter or merge:** if overlaps or fiscal opacity persist, require re-charter with hard boundaries, consolidation into public accounts, or merger/federation via compact.

**Rule:** SPVs/public benefit corporations performing public functions MUST be treated as functional authorities for ledger + finance + procurement + remedy purposes (prevents “outside the constitution” workarounds).

## 3) Minimum Viable Functional Authority (MVFA)
A functional authority MUST have, at minimum:

### A) A narrow charter with hard boundaries
- **Mandate:** one (or tightly related) function(s), explicit **non-powers**, and the interface to general-purpose governments.
- **Legal basis:** public, legible, and recorded in the competence ledger (`34-competence-ledger-and-mandate-registry.md`).
- **Sunset / re-charter:** periodic renewal (e.g., 8–12 years) with public performance review.

### B) Dual legitimacy (representation + member-government control)
Choose one:
- **Model 1: Member-compact authority** — board appointed by participating governments (with public rules), plus public hearings and duty-to-respond.
- **Model 2: Mixed board** — some members directly elected by the service area and some appointed by member governments.
- **Model 3: Elected board** — *only* if transparency, contestability, and finance discipline are strong enough to prevent “low-information capture”.

### C) Auditability as constitution
- Independent audit (`ACC-1`) with publish-by-default financial statements and management letters.
- Open contracting (`OPEN-2`) and vendor performance histories.
- Public tariff/fee book with reasoned decisions and appeal paths (`LAW-5`).

Fiscal transparency anchor: see [BIB-IMF-FTC-2019]  
Consolidation discipline anchor: IMF *Government Finance Statistics Manual 2014* (GFSM): see [BIB-IMF-GFSM-2014].

### D) Remedy and grievance
- A clear, accessible appeal path for billing, eligibility, permitting, enforcement, and service denials (`08-remedy-and-grievance.md`).
- “Stop-the-harm” powers must be reachable (ombuds/tribunal with deadlines).
- Person-facing determinations (tariffs, disconnection, fines, service denial) MUST issue **comprehension-tested** receipts/notices with no-wrong-door routing and safe filing/representation options (`98-persons-path-and-accessibility-invariants.md`, `13-...`).

---

## 4) Ideal pattern (bounded)
### 1) Charter + competence ledger entry (non-negotiable)
Every authority gets a **one-page public charter summary**:
- mandate / non-mandate
- governance model + board selection
- funding sources (fees, taxes, transfers)
- borrowing powers + limits
- audit + procurement rules
- appeal path + timelines
- dissolution / merger rules

### 2) Finance rules that prevent “hidden government”
- **Consolidation by default:** if government controls the authority or bears residual risk, its liabilities and contingent obligations are disclosed in consolidated public accounts (`CAP-2/3`; `07-fiscal-and-budgetary-governance.md`).
- **Borrowing guardrails:** debt service caps; stress tests; publish guarantees and termination liabilities (PPPs, leases, swaps).
- **No unfunded mandates:** member governments that impose duties must fund them (or explicitly publish who pays).

Public sector SPE/SPV risk framing: IMF discussion of special purpose entities: see [BIB-IMF-SPEPS-2005].  
PPP/SPV structure context: World Bank PPP Reference Guide v3: see [BIB-WB-PPP-RG3].

### 3) Participation that matches salience
Functional authorities often fail because participation is *optional* and *opaque*. The fix is to institutionalize:
- a service charter with measurable guarantees (uptime, response time, water quality, etc.)
- a public performance dashboard (`03-metrics-and-evidence.md`)
- a structured annual “tariff/plan hearing season” with duty-to-respond (`OPEN-*`, `DEC-2` where applicable)

### 4) Anti-capture package (tight)
- revolving-door cooling-off rules for executives + procurement leads
- procurement transparency with exception logs
- board meeting transparency, agenda and evidence packs published
- random integrity audits targeted at high-risk contracts (`ACC-2`, `OPEN-2`)

---

## 5) Interfaces (how these bodies plug into multi-level governance)

- **Fiscal interface:** revenue, transfers, and debt MUST be legible in consolidated accounts and the transfer register (see `18-intergovernmental-finance.md`).
Functional authorities MUST implement:
- **Competence ledger entry** (mandatory) — see schema in `70-interoperability.md`
- **Money interface:** publish mandates ↔ revenue ↔ transfers ↔ liabilities (`70-interoperability.md`)
- **Compact interface:** where multiple governments participate, treat the compact as first-class law (`IOP-1`; see `19-compacts-and-cooperative-governance.md`) and file it in the compact register (`70-...`).
- **Data interface:** shared registries, common identifiers, audit logs for critical decisions (`IOP-4/5/6`)
- **Remedy interface:** portable appeals when decisions affect people across boundaries (`LAW-5`)

OECD multi-level governance framing: see [BIB-OECD-MLG].

---

## 6) Minimal metrics (keep it small)
Prefer metric IDs from `03-metrics-and-evidence.md` packs; keep ≤10 total.
- visibility: consolidation coverage + time-to-publish audited statements [IPM-7]
- fiscal risk: debt + contingent liabilities [IPM-9] + fiscal risk statement completeness (incl. PPPs/guarantees) [IPM-8]
- integrity: procurement competitiveness [IPM-2] + vendor concentration [IPM-3] + audit closure [IPM-5] (track contract modifications as a local add-on)
- service outcomes: reliability/uptime [CAD-1] + equity of access [CAD-3]
- governance: participation breadth in tariff/plan processes [LRR-1] + decision transparency coverage [LRR-8]

Empirical caution on special districts and fiscal pools (example study): see [BIB-IJC-GREER-2018].  
Classic policy diagnosis (US): Advisory Commission on Intergovernmental Relations, *The Problem of Special Districts in American Government* (A-22): see [BIB-ACIR-A22-1964].

---

## 7) Design decision: merge, federate, or keep separate?
Use this rule of thumb:
- **Merge** when overlaps create blame-shifting and consolidated management is feasible.
- **Federate via compact** when technical systems must remain specialized but governance needs shared planning and fiscal visibility.
- **Keep separate** only when the authority’s charter boundaries are crisp, accountability is strong, and finance is fully legible.

The goal is not “more bodies” — it is **more legible capacity**.
