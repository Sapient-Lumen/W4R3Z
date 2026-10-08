# Metropolitan Governance (The “City-Region” Problem)

**Purpose:** specify accountability interfaces for metro regions where harms cross municipal lines and blame-shifting is common.
**Person served:** a metro resident whose life crosses city lines (housing, transit, policing, work) who needs coordination without losing a clear, contestable chain of responsibility.

**From-below:** This helps you hold region‑wide systems accountable so “city‑region” problems don’t fall through jurisdiction cracks with no clear remedy.

See `14-scope-ladder.md` for the cross-scope map (what belongs where), `70-interoperability.md` for join-keys, and `71-interface-obligations-by-scope.md` for what each scope MUST publish.

Metropolitan areas behave like one economy and one ecology, but are often governed as **many** municipalities plus a thicket of **functional authorities**. This creates classic failure modes: fragmentation, duplicated bureaucracy, boundary arbitrage, and low-salience capture.

**Person-facing invariants:** metro arrangements must not create a “navigation tax.” For any person-facing determinations that cross municipal lines (transit fares/penalties, housing portability, utility service disputes, disaster aid routing), require **comprehension-tested receipts/notices**, **no-wrong-door** intake across member jurisdictions, and **portable remedy lanes** (`98-persons-path-and-accessibility-invariants.md`, `47-...`, `36-...`).

**Boundary note:** when the fix is a merger/split/annexation or a responsibility transfer, use `17-jurisdiction-formation-and-boundaries.md` for process and tests.

## Kernel anchors (do not repeat)

- **EXP pointer:** metro interfaces must reduce EXP-06 Complexity and EXP-02 Waiting (see `98-persons-path-and-accessibility-invariants.md`).
- **Person-facing invariants:** `98-persons-path-and-accessibility-invariants.md` (no AI/digital-only gates; oral/assisted options; safety).
- **Remedy is part of the interface:** `08-remedy-and-grievance.md`, `36-appeal-lanes-and-redress-registry.md` (contestability; time bounds; functional equivalents).
- **Protective legibility (transparency ≠ safety):** `99-protective-legibility-and-adoption-dynamics.md`.
- **Records + publication integrity:** `31-records-foi-and-government-memory.md`, `51-release-registry.md`.
- **Housing/land interface:** `62-land-and-housing-governance.md`.

## Named tensions (design must surface these)
- **Integration vs neighborhood autonomy:** region-wide systems vs local control.
- **Infrastructure optimization vs displacement:** service efficiency vs who pays the cost.
- **Fiscal capacity vs equity:** tax base differences vs equal access to basics.
- **Planning speed vs contestation:** delivery urgency vs democratic challenge.

## Anchor typologies (minimal)

For arrangement taxonomies and baseline evidence on fragmentation vs coordination, use:
- OECD typology and reform lessons: see [BIB-OECD-GOVCITY-2015].
- Metro mechanisms and finance/legitimacy trade-offs (cross-North/South): see [BIB-IDB-METROGOV-2019].
- Comparative case compendium (collaborative arrangements): see [BIB-WB-METROGOV-2020].

This memo is a *tight selection guide* for metropolitan governance arrangements that fits the archive’s stack and interfaces (`02-design-toolkit.md`, `70-interoperability.md`) and complements `30-regional.md` and `15-functional-authorities.md`.

---

## 1) What metro governance must solve (and what it should not)

### Must solve
- **Network goods:** transit, roads/corridors, water/waste systems, emergency coordination, housing-market and land-use spillovers (see `62-land-and-housing-governance.md`).
- **Externalities:** congestion, pollution/air-sheds, flood basins, spatial inequality and exclusionary zoning dynamics.
- **Scale + capital planning:** long-horizon capex, maintenance, and resilient standards.

### Should avoid by default
- becoming a full “shadow state” duplicating municipal services that are preference-sensitive and locally delivered (parks programming, minor permitting, etc.)
- proliferating opaque authorities rather than consolidating legibility (`15-...`, `70-...`)

---

## 2) Arrangement menu (use the smallest thing that works)

Think in **three** primitives (often combined):

1) **Inter-municipal compact (contractual coordination)**
- Best for: shared services, procurement, mutual aid, corridor standards, data interoperability.
- Limits: weak when distributional conflict is high or when stable capex + debt capacity is required.
- Spec: `19-compacts-and-cooperative-governance.md`.

2) **Metro functional authority (single-purpose, network-good body)**
- Best for: transit operators, regional water boards, basin/drainage authorities, ports/airports, MPO-like planning + funding bodies.
- Limits: can become “hidden government” unless aggressively audited and integrated into competence + fiscal reporting (`15-...`, `07-...`, `70-...`).

3) **Metro general-purpose government (two-tier / regional layer)**
- Best for: sustained redistribution and land-use/housing externalities where bargaining fails; metropolitan planning with enforceable powers.
- Limits: higher legitimacy requirements; risk of remoteness; requires clear mandate boundaries with municipalities (`30-...`).

---

## 3) Selection tests (a practical decision procedure)

Use this as a “subsidiarity-with-teeth” filter (`01-principles.md`):

### A) Spillover severity test
- **Low spillover:** compact (1)
- **Medium spillover but networked:** authority (2)
- **High spillover + distributional conflict:** two-tier (3) or authority (2) with strong redistribution/land-use hooks

### B) Capital intensity + balance-sheet test
If the problem requires sustained capex and debt capacity:
- prefer (2) or (3) **only if** consolidated reporting and audit can be enforced (IMF Fiscal Transparency Code anchor: see [BIB-IMF-FTC-2019].)

### C) Democratic salience test
If residents cannot easily identify “who did this”:
- require direct legitimacy upgrades (e.g., direct election, clear appointment + recall/sanction rules, strong transparency and remedy path)
- otherwise, default away from (2) proliferation

### D) Land-use coupling test
If transport/housing outcomes depend on land-use decisions:
- either (3), or (2) with **explicit conditionality** (funding tied to zoning/housing targets) and a published enforcement ladder.

---

## 4) Minimum Viable Metro Governance (MVMG)

A metro area SHOULD be able to start small and harden as needed.

**MVMG-1 Metro Compact Office**
- maintains the **metro competence map** (subset view of the competence ledger) (see `34-competence-ledger-and-mandate-registry.md`).
- maintains the metro **compact register** (so agreements are legible and reviewable)
- publishes the metro capital plan and performance dashboard (transport, housing, safety, climate resilience)
- runs a compact arbitration / dispute pathway (tie into `08-remedy-and-grievance.md`)

**MVMG-2 One “backbone” metro body for the main network good**
Pick the dominant binding constraint:
- transit/corridors, or water/basin, or housing-land-use coordination.

This body MUST:
- appear in the competence ledger (`34-competence-ledger-and-mandate-registry.md`)
- publish contracts, outcomes, and board votes (`OPEN-1/2`)
- have independent audit + procurement controls (`ACC-1/3`)
- have enforceable grievance + review (`08-...`)

**MVMG-3 Consolidated metro accounts**
- publish a consolidated view of metro entities (including special districts) and fiscal risks (`07-...`) (special districts evidence: [BIB-USCENSUS-SPECIALDIST-2022]).
- “no off-book metro” rule: any SPV/PPP requires disclosure and consolidation logic.

---

## 5) Anti-pathology rules (what keeps metro governance from turning toxic)

- **No invisible powers:** every metro body is listed in the competence ledger with mandates, overrule conditions, funding responsibility, and remedy path (`34-competence-ledger-and-mandate-registry.md`).
- **No duplication without justification:** new metro bodies must publish what they replace and why (sunset old entities).
- **Hard sunset + review:** every new authority has a default sunset, renewal requires evidence (`03-metrics-and-evidence.md`).
- **Prevent low-salience capture:** meeting transparency + influence transparency + audit closure rates are non-optional (`ACC-*`, `OPEN-*`).
- **Exit is not enough:** municipalities can’t “exit” a network externality; design must include enforceable fairness rules and rights protection.

---

## 6) Interfaces (how metro plugs into the ladder)

- **Fiscal interface:** metro bodies must have explicit revenue/transfer channels and appear in consolidated reporting (see `18-intergovernmental-finance.md`, `07-fiscal-and-budgetary-governance.md`).

- **Downward:** service charters and neighborhood co-design loops for local delivery (do not centralize what can stay local).
- **Sideways:** standardized compacts for shared services and corridor standards (`IOP-1`).
- **Upward:** regional/national standards for rights, equalization, and catastrophic risk (see `30-...`, `40-...`).
