# 110 — Budget + procurement integrity (money as power)

**Stack relation:** use `302-fiscal-state-budget-revenue-and-transfers-routing-guide.md` for the canonical route across the fiscal-state / budget / revenue / transfers family. This memo is the budget-readability / spending-allocation / procurement-capture front door; `07` is the broad fiscal-governance front door; `135` / `93` handle revenue-rule integrity and operational administration; `18` / `194` / `217` handle cross-scope finance, open budgets, and equalization design; `97` / `138` remain the capital-allocation and major-project neighbors.

**Purpose:** Treat *money flows* as a governance interface. If legitimacy is a protocol, fiscal decisions must be **readable**, **contestable**, and **hard to capture** at every scope.

## Minimal stack (portable across scopes)

**FIS-1 Readable public accounts**
- MUST: budget & spending published in a program/mission structure ordinary people can follow; quarterly execution updates; a public balance sheet.
- Anchor: see [BIB-IMF-FTC-2019].

**FIS-2 “Reason receipts” for money**
- MUST: for material allocations, publish a short *reason receipt* linking: (a) purpose, (b) criteria, (c) alternatives considered, (d) who benefits/loses, (e) conflict-of-interest checks, (f) evaluation plan.
- Interface: pairs with `106-legitimacy-protocols.md` (reasons + standing + contest windows).

**FIS-3 Pre-commitment + variance discipline**
- SHOULD: limited “off-cycle” spending; clear variance rules; automatic review when deviations exceed thresholds.
- Circuit breaker hook: see `105-institutional-circuit-breakers.md`.

**FIS-4 Open contracting baseline**
- MUST: publish the full contracting lifecycle (planning → tender → award → contract → implementation), with machine-readable fields where feasible.
- SHOULD: default open competition; exceptions require public justification; publish beneficial ownership where legal.
- Anchors: see [BIB-OECD-PROC], [BIB-OCP-OCDS], [BIB-EU-DIR-2014-24-OJ], [BIB-US-FAR-SUBPART-6-3].

**For AI/ADS procurements (special case):** treat “auditability + change control + evidence export” as *delivery requirements*, not optional compliance extras—vendors must support joinable logs, no-silent-swap change receipts, and contestability evidence packets. (See `146-ai-assurance-and-public-sector-ai-ops.md`; registry join: `42-...`.)

**FIS-5 Anti-capture procurement mechanics**
- SHOULD: rotating evaluation panels; red-team checks for bid-rigging patterns; debarment lists with due process; independent complaints channel.
- Minimal metrics: single-bid rate; time-to-award; change-order frequency; supplier concentration.

**FIS-6 Participatory allocation where stakes are local**
- SHOULD: reserve a bounded share of discretionary local spend for participatory budgeting (PB) with accessibility rules and auditability.
- Guardrails: do not PB safety-critical baselines; protect minority standing; publish tradeoffs.
- Anchor: see [BIB-WB-PB-GUIDE] (and cite local statutory basis where used).

## Transfer and seam rules
Money systems fail at boundaries (agency ↔ agency; local ↔ regional; public ↔ contracted).
- Apply `109-portability-and-cross-jurisdiction-continuity.md`: no “reset” of evidence; transfer-of-file protocol; continuity defaults.
- Require contract portability: records, case files, and service standards travel with the person.

## Failure modes → default fixes (compact)
- **“Black box budget”** → publish readable program structure + variance dashboard (FIS-1/3).
- **“Emergency exception becomes normal”** → exception register + auto-sunset + independent review (FIS-3 + `105`).
- **“Procurement theater”** → open contracting + publish justifications + single-bid alarms (FIS-4/5).
- **“PB as a PR layer”** → bounded share + binding rules + audit trail + minority standing (FIS-6 + `106/107`).

## Where this plugs in
- Capacity requirements: `02-design-toolkit.md` (CAP-2/3/4; add FIS-4/5/6).
- Legitimacy + tests: `106-legitimacy-protocols.md`, `107-governance-test-suite.md`.
- Time budgets & service promises (contracts must inherit them): `108-service-standards-and-time-budgets.md`.

**See also:** `163-integrity-stack-anti-corruption-rails.md` (end-to-end integrity stack).
