# Ocean commons governance (seabed • high seas • Antarctica) — precautionary compacts

**Purpose:** specify a cross‑scope governance pattern for **global commons domains** where (a) impacts are hard to reverse, (b) enforcement is distributed, and (c) science uncertainty is weaponized to force through extraction.

**Anchors:** High Seas / BBNJ Agreement (in force Jan 2026) [BIB-BBNJ-UN-2023] [BIB-BBNJ-EU-2026]; International Seabed Authority “Mining Code” and draft exploitation rules [BIB-ISA-MININGCODE-2025]; Antarctic Treaty System Environmental Protocol (Madrid Protocol) [BIB-ATS-MADRID-1991]; precautionary approach (Rio Principle 15) [BIB-RIO-P15-1992].

---

## Design problem

Global commons regimes fail in repeatable ways:

- **Boundary fuzz + fragmented enforcement:** agreements exist, but ship flags, ports, insurers, and supply chains create loopholes.
- **Science as delay/cover:** uncertainty is used to argue both “wait forever” and “act now, we don’t know harm,” depending on who benefits.
- **License laundering:** authorizations issued in one lane are treated as legitimacy everywhere else.
- **Rent capture:** benefit‑sharing becomes a thin royalty while harms stay externalized.

This memo proposes a minimal spec for a **Precautionary Commons Compact (PCC)**: a joinable set of artifacts that make “no exploitation until rules exist” and “protection by default” operational across jurisdictions.

---

## Pattern: Precautionary Commons Compact (PCC)

A PCC is a multi‑party compact that binds *participants* (states, port authorities, registries, insurers, financiers, major buyers) to a shared **permit / monitoring / enforcement** interface.

### PCC-01: Default prohibition with explicit “go/no-go” gates
- **MUST** treat commercial extraction in high‑uncertainty commons as **prohibited by default** unless and until a published **Ruleset + Standards** package exists and has passed a “scope test docket” review (`IOP-10`, `14-scope-ladder.md`).  
- **MUST** define **gate conditions** as checklists with joinable evidence: baseline data, monitoring plan, liability/insurance, benefit‑sharing model, and reversal plan.
- **MUST** publish a `RULE-PCC-*` that states *what constitutes* an exploitation authorization (to prevent semantic laundering).

(This matches how the ISA continues to develop exploitation regulations while noting commercial exploitation is not yet approved in the absence of final regulations. [BIB-ISA-MININGCODE-2025])

### PCC-02: Protected-area and “no-take” designation as a first-class operation
- **MUST** support a fast path to designate protected zones with:
  - `DRR-TYPE: AREA` (designation decision + reasons + evidence docket),
  - `REG-AREA-*` (boundaries + allowed activities + enforcement hooks),
  - `REL-AREA-*` (funding + stewardship contracts).
- **SHOULD** separate the **scientific recommendation** step (technical body) from the **political adoption** step, but require a binding response rail (see `143-...` deliberation response patterns).

(The BBNJ Agreement explicitly creates a framework for area-based management tools including marine protected areas, plus EIAs. [BIB-BBNJ-UN-2023] [BIB-BBNJ-EU-2026])

### PCC-03: Environmental impact assessment (EIA) as a joinable *receipt stream*
- EIAs **MUST NOT** be PDFs in a drawer. They are `DRR` streams:
  - `DRR-EIA-0` scoping (what could go wrong, who is harmed),
  - `DRR-EIA-1` baseline + uncertainty map,
  - `DRR-EIA-2` mitigation plan + monitoring triggers,
  - `DRR-EIA-3` go/no-go decision with reason codes and appeal lane.
- **MUST** include **uncertainty‑handling policy**: what uncertainty blocks approval vs what triggers adaptive constraints (precautionary approach) [BIB-RIO-P15-1992].

### PCC-04: Distributed enforcement via chokepoints (ports, finance, insurance, buyers)
- **MUST** define and publish an `ENF-CHK-*` register of enforcement chokepoints:
  - port entry / services,
  - ship registry/flag services,
  - insurance and classification,
  - finance and settlement rails,
  - commodity buyers / processors.
- Participants **MUST** implement a shared `REG-PERMIT-*` verification API (even if only a signed JSON file) that returns:
  - permit validity, scope, expiry, monitoring status,
  - outstanding incidents (`INC-*`),
  - sanctions / exclusion list.

### PCC-05: Benefit-sharing that can’t be faked
- **MUST** publish a `REL-BEN-*` ledger: who received what, when, with what formula.
- **MUST** include “no undercutting” clauses: parties may not provide alternative authorizations that bypass PCC gates and still access PCC chokepoints.
- **SHOULD** treat benefit‑sharing as **two‑part**: (a) royalties, (b) a standing **commons stewardship fund** paying monitoring, protected areas, and restitution.

(The BBNJ regime includes benefit-sharing for marine genetic resources in areas beyond national jurisdiction. [BIB-BBNJ-UN-2023])

### PCC-06: Mineral resource bans as a clean governance move (Antarctica pattern)
- Where values are high and reversibility is low, the simplest safe regime is a **bright-line ban** enforced by shared chokepoints.  
- The Madrid Protocol prohibits Antarctic mineral resource activities except scientific research; treat this as a reference pattern for domains where extraction cannot be governed safely. [BIB-ATS-MADRID-1991]

### PCC-07: Dispute resolution that preserves the precautionary baseline
- **MUST** define a dispute lane where interim measures default to **harm prevention**:
  - standing injunctive capacity,
  - fast timeline,
  - independent technical advisory panel with conflict-of-interest constraints.
- **MUST** publish dispute outcomes as `DRR-DISPUTE-*` and link to any sanctions changes.

---

## Failure modes and countermeasures

- **Forum shopping:** counter with PCC-04 (chokepoint enforcement) and “no undercutting” (PCC-05).
- **Science capture:** require conflict disclosures + rotating panels + public methods; publish uncertainty maps and dissent logs (joinable to `DRR-EIA-*`).
- **Paper compliance:** monitor operational telemetry (AIS/port calls/supply chain receipts) and publish `INC-*` when required artifacts are missing (“absence is a signal”, `00-README.md`).
- **Extractive emergency:** prohibit “emergency exploitation” exceptions; if any derogation exists, bind it to `165` emergency rails (sunsets + renewal hearings + repair duty).

---

## Integration hooks

- Link PCC gates to `73-assurance-case-and-governance-safety-case.md` for high‑risk operations: the safety case is the spine; the PCC is the enforcement mesh.
- Use `136` polycentric federalism memo patterns for overlapping sovereignty: PCC is a compact across partially aligned actors, not a single sovereign.

**Related:** orbital commons (`148`), water basin compacts (`...`), climate retreat (`166`), illicit finance chokepoints (`...`).
