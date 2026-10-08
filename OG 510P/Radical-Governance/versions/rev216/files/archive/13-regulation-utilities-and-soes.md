# Regulation, Utilities, and State-Owned Enterprises (SOEs)

**Purpose:** keep *market power* and *critical services* (water, energy, telecom, transport, finance-adjacent infrastructure) aligned with the public interest **without** turning regulation into capture, arbitrary discretion, or surveillance.

This memo is a cross-scope primitive: municipalities regulate concessions and utilities; nations regulate markets and network industries; supranational bodies coordinate standards and competition; global systems coordinate baseline rules and cooperation.

See also: `65-energy-and-decarbonization-governance.md` (mitigation pipeline built from these same regulatory/utility interfaces); `94-competition-and-market-power-governance.md` (market power governance spine).

## Kernel anchors (do not repeat)
- Regulation is person-facing: notices, service disputes, and safe complaint intake must work without lawyers/AI: `98-persons-path-and-accessibility-invariants.md`, `82-service-standards-and-minimum-service-guarantees.md`, `47-service-catalog-and-access-journeys-register.md`.
- Integrity/anti-capture wiring for regulators and SOEs: `22-public-integrity-and-procurement.md`, `79-conflict-of-interest-and-revolving-door-discipline.md`.
- Protective legibility (publish enforceable facts without enabling retaliation): `99-protective-legibility-and-adoption-dynamics.md`.

## Named tensions (design must surface these)
- **Affordability vs sustainability:** cost recovery competes with universal access and non-disconnection protections.
- **Reliability vs market discipline:** emergency continuity duties conflict with strict contract logic.
- **Transparency vs capture/retaliation:** disclosures must be usable and safe for workers/complainants.


---

## Minimum viable regulatory state (MVRS)

1) **Regulatory inventory (what exists)**
- MUST: a public list of regulators, mandates, covered sectors, major powers, and appeal routes.
- MUST: a canonical **Public Rules Register** with stable IDs, effective dates, and change logs (binding guidance included when enforced). See `25-legal-legibility-and-rule-inventory.md`.
- SHOULD: a **Public Standards Register (PSR)** for governance-grade technical standards referenced by rules, regulators, or essential procurement; PRR Rule IDs that incorporate standards SHOULD point to PSR `STD-*` IDs. See `27-standards-and-technical-governance.md`.
- MUST: identify *natural monopoly / network* services and *high externality* sectors.

2) **Rulemaking quality baseline**
- MUST: publish draft rules and allow public comment (“notice-and-comment”).
- SHOULD: regulatory impact assessment (RIA) for major rules; publish assumptions and distributional impacts.
- SHOULD: ex-post review triggers (sunsets or review clauses) for major rules.

3) **Independent regulator pattern (when discretion is large)**
- SHOULD: fixed-term leadership; protected removal rules; conflict-of-interest + revolving-door rules.
- SHOULD: budget/fee model insulated from day-to-day political retaliation (with audit).
- MUST: publish decisions, reasons, evidence, and metrics; protect confidential info with narrow rules.
- MUST: for customer/licensee‑affecting determinations (tariffs/bills, disconnection, fines, license conditions/denials), issue a `DRR-*` receipt that cites `RULE-*` (as‑of) + `RC-*` and names the `AL-*` lane—written to pass the **comprehension test** (`98-persons-path-and-accessibility-invariants.md`) and reachable via a **no‑wrong‑door** intake (`08-...`, `47-...`).
- MUST: meaningful appeal / review (see `LAW-5`, `08-remedy-and-grievance.md`).

4) **Utilities & concessions governance**
- MUST: transparent tariffs/rates (or contract payments), service-quality metrics, and outage/incident reporting. For `ESS-1` utilities, publish the customer-facing service definition (`SRV-*`) and minimum service guarantees (`82-...`), including tail-wait and dignity expectations.
- SHOULD: require a joinable **Asset & Infrastructure Register** for regulated network assets (condition grades, inspection cadence, and maintenance backlog) keyed by `AST-*` and linked to affected `SRV-*` where defined (see `48-asset-and-infrastructure-register.md`; anchors: [BIB-OECD-INFRA-2020]; [BIB-ISO-55000]).
- SHOULD: for major capital expansions, use stage-gated approvals and change-control receipts so capex promises remain auditable (see `97-public-investment-and-capital-project-governance.md`).
- SHOULD: publish concession/operator ownership and (for private operators) beneficial ownership disclosures, linked to relevant contract/concession IDs; use an open schema for exchange where feasible (see [BIB-BODS]; `22-public-integrity-and-procurement.md`).
- SHOULD: universal service policy (access/affordability) with explicit funding mechanism.
- SHOULD: resilience requirements (redundancy, cybersecurity, disaster plans) with after-action reporting.

5) **SOE governance (when the state owns operators)**
- SHOULD: explicit ownership policy; professional boards; clear separation between ownership and regulation.
- MUST: financial disclosure and consolidated reporting (tie to `CAP-3` fiscal risk).
- SHOULD: “competitive neutrality” where SOEs compete with private firms (level playing field).

6) **Competition & procedural fairness**
- SHOULD: competition agency transparency and procedural fairness norms (publication of standards, due process, predictable remedies).

---

## Failure modes (and targeted countermeasures)

**Capture / revolving door**
- Signals: closed-door rules; consultant-written regulations; “regulatory dark matter” (guidance that functions as law).
- Countermeasures: `ACC-5` influence transparency; publish meetings; conflict rules; open consultation logs; audit of enforcement selectivity.

**Tariff opacity / hidden cross-subsidies**
- Countermeasures: publish tariff models and assumptions; independent review; public dashboards.

**Overregulation / licensing abuse**
- Countermeasures: inventory + repeal/review discipline (`OPEN-7`); risk-tier permissioning (notify/audit vs permit) with time bounds, a public Permit/Approval Register (PAR), and careful use of deemed approval (`LAW-7`; see `29-permissioning-and-approvals.md`).

**SOE politicisation + hidden liabilities**
- Countermeasures: `CAP-8` SOE governance; `CAP-3` fiscal risk disclosure; publish guarantees and contingent liabilities; professionalised ownership entity.

**Competition enforcement arbitrariness**
- Countermeasures: procedural fairness, transparency, appeal rights, published guidelines.

---

## Minimal metrics (portable set)
Prefer metric IDs from `03-metrics-and-evidence.md` packs; keep ≤10 total.
- Rulemaking openness: drafts + comments + published response log [REG-1].
- Review discipline: sunsets/reviews included and completed on time [REG-2].
- Utility performance: reliability/outage + affordability burden; customer complaint-to-remedy time [REG-4] / [REG-3].
- Network asset health (where relevant): maintenance backlog + condition trend for critical utility assets [CAD-7] (keyed by `AST-*` when AIR exists).
- SOE disclosure & state support transparency: audited financials + guarantees/state support disclosure [REG-5] (and consolidation timeliness where relevant) [IPM-7].
- Market power: concentration watch list + decision transparency (local add-on; align with concentration triggers) [IPM-3].

---

## Cross-scope notes (where this shows up)

**Municipal**
- concession contracts, zoning/permits, municipal utilities → publish tariffs/terms and grievance pathways; avoid vendor lock-in.

**Regional**
- network coordination (power, water, transport), watershed authorities → compacts with common standards + dispute channels (`IOP-1`).

**National**
- independent regulators for high-discretion sectors; competition authority; SOE ownership entity; fiscal risk consolidation.

**Supranational**
- mutual recognition requires minimum regulator competence + remedy; standards alignment; cross-border competition cooperation.

**Global**
- baseline norms (transparency, procedural fairness, cooperation) and capacity support; avoid one-size-fits-all, focus on interoperable minimums.

---

## Anchors (start here)
- OECD Recommendation on Regulatory Policy and Governance (OECD/LEGAL/0390): see [BIB-OECD-RPG-0390].
- World Bank Global Indicators of Regulatory Governance (methodology): see [BIB-WB-GIRG].
- OECD Guidelines on Corporate Governance of State-Owned Enterprises (2024): see [BIB-OECD-SOE-2024].
- ICN Recommended Practices for Investigative Process (procedural fairness / transparency): [BIB-ICN-INVPROC-2019]
- AI use in rulemaking (transparency/record rules): see [BIB-GFI-AI-RULEMAKING-2025].
