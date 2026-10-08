# Antimonopoly & Market Structure Governance (Power as a Public Interface)

**Stack relation:** use `303-productive-state-utilities-market-structure-and-industrial-resilience-routing-guide.md` for the canonical route across the productive-state / utilities / market-structure / industrial-resilience family. This memo is the structural antimonopoly / contestability-engineering specialization; `94` is the broad competition-governance / enforcement front door; `13` is the public-interest regulation / utilities / SOE front door; `65` is the energy-sector specialization; `153` is the industrial-policy / supply-chain-resilience specialization.

**Purpose:** make **market power** (especially platform / network power) governable with **receipts, rails, and remedies**—without pretending that “competition” is automatic or that “regulation” is always wise.

**Person served:** people trapped by lock‑in (workers, small businesses, creators, end‑users) who need **exit paths, fair access, and contestable rules**.

**From-below:** treat market structure like any other high‑stakes system: publish the **rules of access**, log changes, and give affected people a **remedy lane**.

This memo defines a compact, cross‑scope pattern set for:
- **Structural competition** (preventing / unwinding concentration)
- **Contestability engineering** (portability + interoperability + open interfaces)
- **Utility rails** (when markets cannot reliably deliver non‑exclusion)
- **Anti‑capture operations** (transparent case files + bounded discretion)

---

## 1. Scope fit (where the levers live)

**Municipal / local:** zoning/permits + procurement + franchising + public options (wifi/transport/energy); *don’t* do national antitrust alone.

**Regional / state / province:** sector regulators (utilities, insurance); competition advocacy in regulation; labor monopsony enforcement.

**National:** merger control, dominance/monopolization enforcement, interoperability mandates, data portability duties, sector regulation.

**Transnational / treaty / bloc:** cross‑border digital markets, merger coordination, interoperability baselines, enforcement assistance.

**Rule:** the **highest scope that can bind the firm** must own the “hard levers” (merger, separation, access), while lower scopes run **procurement & public‑option rails**.

---

## 2. Core primitives (minimal but powerful)

### 2.1 Market Power Docket (MPD)
A continuously maintained docket for a market / sector:
- **Relevant market / substitutability** hypothesis (versioned)
- **Concentration & entry barriers** (with uncertainty)
- **Network effects / switching costs / multi‑homing constraints**
- **Data/control inputs** relevant to competition (where applicable)
- **Remedies considered** + why chosen (or why not)

MPD is to competition what a **Safety Case** is to hazards: it is contestable, versioned, and auditable.

### 2.2 Interoperability & Portability Rail (IPR)
A default remedy family that converts “switching” into an interface:
- **Portability**: export your contributed + observed data in usable form
- **Interoperability**: documented APIs / protocols enabling third‑party connection
- **Non‑degradation**: gatekeepers can’t sabotage interoperability via dark patterns
- **Security & privacy constraints**: scoped, justified, and reviewable

(These tools are widely discussed as pro‑competition measures for digital platforms.) [BIB-OECD-DATA-PORTABILITY-INTEROP-2021]

### 2.3 Access Duty Receipt (ADR)
When access is required (e.g., essential facility / platform rules), publish:
- eligibility criteria
- pricing terms (or pricing formula)
- safety/security requirements
- appeal lane
- change log

### 2.4 Merger Review Receipt (MRR)
For merger control, publish a plain‑language receipt:
- theory of harm(s)
- key evidence categories used
- remedies imposed (if any) and enforcement plan
- what would have changed the decision

(For U.S. agencies, the 2023 Merger Guidelines summarize frameworks they consider.) [BIB-US-DOJ-FTC-MERGER-GUIDELINES-2023]

### 2.5 Structural Remedy Ladder (SRL)
Escalation path (bounded discretion):
1) **Disclosure / transparency** (MPD + ADR + audits)
2) **Conduct remedies** (non‑discrimination, self‑preferencing bans)
3) **Interoperability/portability mandates** (IPR)
4) **Line‑of‑business restrictions** (separation of platform and commerce)
5) **Structural separation / divestiture** (if durable dominance persists)

### 2.6 Contestability Budget (CB‑M)
A requirement that major sectors publish:
- **switching cost audits**
- **time‑to‑switch targets** (service standards for exit)
- **lock‑in incident ledger** (complaints/metrics)

---

## 3. Institutions (roles and separation)

### 3.1 Competition Authority (CA)
- owns MPDs for priority markets
- runs merger control + abuse/dominance cases
- maintains a public **Case File Registry** (redactions justified)

### 3.2 Sector Regulators (SR)
- enforce ADRs in regulated sectors
- can impose IPR where sector‑specific safety needs exist
- coordinate with CA via a **Dispute & Coordination Lane** (`114-...`)

### 3.3 Public Option / Utility Operator (PO)
When market structure can’t reliably provide non‑exclusion:
- create a **utility rail** (open access) for baseline services
- PO must be governed using the archive’s utility integrity patterns (`137-...`, `164-...`)

### 3.4 Competition Advocacy Unit (within CA)
Reduce “anti‑competitive by regulation” outcomes:
- review proposed rules for entry barriers and capture risks
- publish short “competition impact notes”

(Competition advocacy toolkits emphasize strengthening these practices.) [BIB-ICN-ADVOCACY-TOOLKIT]

---

## 4. Operations (make it hard to quietly entrench power)

### 4.1 Interface governance as competition governance
- mandatory **Interface Registry** for designated gatekeepers (`128-...`)
- change receipts + deprecation clocks
- conformance tests for interoperability claims

DMA‑style regimes explicitly require interoperability in certain contexts (and publish guidance/decisions). [BIB-EC-DMA-INTEROP-QA-2025]

### 4.2 “No silent swap” rule
If a platform changes ranking, access, pricing, or APIs:
- publish a change receipt
- provide migration guidance
- provide a remedy lane for impacted parties

(See also `115-...` record interfaces; `118-...` rulemaking change control.)

### 4.3 Data control in merger review
Require MPDs/MRRs to explicitly analyze:
- control of key datasets
- whether data advantages foreclose rivals
- potential competition effects

(Comparative authority experience is compiled by ICN members.) [BIB-ICN-MWG-DATA-MARKETPOWER-2024]

### 4.4 Anti‑monopsony (labor and supplier power)
Treat concentrated buyer power as a governance hazard:
- require **fair dealing** duties where a platform is a dominant buyer
- create collective bargaining safe harbors / duty‑to‑respond (`123-...`)

---

## 5. Threat model (how this fails)

**Capture / revolving door:** enforcement becomes selective or performative. Counter: `120-...`, `113-...`, `163-...`.

**Weaponized antitrust:** “competition” rhetoric used to punish enemies or entrench incumbents. Counter: MPD transparency + appeal + bounded discretion (SRL).

**Security/privacy pretext:** interoperability blocked by vague “integrity” claims. Counter: require narrowly tailored, reviewable constraints (ADR + IPR).

**Over‑remedy / brittle rules:** mandated interfaces ossify innovation. Counter: versioned standards + experimentation lanes + sunset reviews (`118-...`, `133-...`).

---

## 6. Minimum viable package (MVP)

1) Stand up MPDs for **3 priority markets** (choose by harm + lock‑in).
2) Publish IPR baseline: portability + interoperability spec template.
3) Require MRRs for major merger decisions.
4) Add “no silent swap” change receipt discipline for gatekeepers.
5) Create an inter‑agency coordination lane (CA ↔ SR) with deadlines (`114-...`).

---

## 7. Evidence anchors (keys)

- [BIB-OECD-DATA-PORTABILITY-INTEROP-2021]
- [BIB-OECD-MARKETPOWER-DIGITAL-2022]
- [BIB-US-DOJ-FTC-MERGER-GUIDELINES-2023]
- [BIB-EC-DMA-INTEROP-QA-2025]
- [BIB-ICN-MWG-DATA-MARKETPOWER-2024]
- [BIB-ICN-ADVOCACY-TOOLKIT]
