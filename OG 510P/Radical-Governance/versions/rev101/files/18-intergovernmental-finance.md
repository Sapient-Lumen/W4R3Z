# Intergovernmental Finance (Transfers, Tax Assignment, Equalisation)

Multi-level governance fails when the **money map** doesn’t match the **competence map**.
This memo defines a compact “fiscal interface” so scopes can share funding without creating hidden government, unfunded mandates, or bailout expectations.

**Anchor set (start here):**
- OECD (2025): see [BIB-OECD-IGFT-2025].
- IMF (2018): see [BIB-IMF-IGF-2018].
- World Bank (2007): see [BIB-WB-IGFT-2007].

---

## A. Core concepts (keep these definitions stable)
- **Expenditure assignment:** who is responsible for which services/mandates (see competence ledger in `34-competence-ledger-and-mandate-registry.md` (interfaces: `70-interoperability.md`)).
- **Revenue assignment:** who has access to which tax bases and what rate-setting authority.
- **Vertical imbalance (gap):** a level’s responsibilities exceed its own revenues.
- **Horizontal imbalance:** some jurisdictions have higher needs or lower revenue capacity than others.
- **Soft budget constraint:** lower levels over-borrow/under-tax because they expect rescues; this destroys accountability (see Rodden’s analysis of bailout expectations in the German Länder: [BIB-RODDEN-SBC-GERMANY-2006]).

---

## B. Minimum Viable Intergovernmental Finance (MV-IGF)
These are the smallest guarantees that make multi-level democracy *work* rather than blame-shift.

1) **No unfunded mandates**
- MUST: any higher-level standard or delegated mandate includes a **costing + funding channel** (grant, shared tax, or explicit local revenue authority).
- MUST: publish “mandate notes” in budgets (what changed; who pays; what happens if underfunded).

2) **A predictable, formula-based equalisation core**
- MUST: a **transparent formula** (published inputs, data sources, and weights).
- MUST: predictable timing (avoid political “grant churn”).
- SHOULD: equalise **capacity**, **needs**, or both — but explicitly state which (OECD 2025).

3) **Transfers are typed (don’t mix objectives)**
- **Equalisation (unconditional):** reduces baseline disparities; minimal strings; high transparency.
- **Spillover grants (conditional/matching):** used when benefits cross boundaries (e.g., transit, watershed).
- **Capital grants:** time-bounded, project-scoped; require lifecycle cost disclosure.
- **Stabilisation / emergency:** rules-based triggers where possible (disaster, sudden shocks).

**Beneficiary continuity rule (anti-hostage conditionality):** conditionality enforcement MUST be designed so that *final recipients* and *essential services* are not punished for higher-level disputes or noncompliance. Prefer targeted remedies (direct technical support, phased compliance plans, escrow/direct-to-provider routing) over blunt suspensions; if a holdback is used, publish the service-continuity backstop and appeal lane in the transfer register. **Tie “essential” to the service catalog**: impacted `TRF` enforcement actions SHOULD cite `SRV-*` IDs, and `ESS-1` services MUST have published continuity floors. Anchors: [BIB-EC-ROL-COND-REG-2021]; [BIB-IMF-SNG-FISCALRISKS-2022]; [BIB-WB-UNTILDEBT-2013].

4) **Hard budget constraints with a real resolution path**
- MUST: publish subnational borrowing, guarantees, and arrears in one place (debt registry).
- MUST: define *ex ante* what happens if a unit cannot pay (workout/insolvency path, service continuity plan).
- SHOULD: define essential-service continuity floors via the `SRV-*` catalog (`47-...`) so distress/workout actions can be audited against a published minimum, not improvised during crisis.
- MUST: ensure any distress/workout regime explicitly **protects essential public services** while restoring solvency (administrative, judicial, or hybrid models are all viable; the point is: *no chaos, no dark bailout*). Anchors: [BIB-OECD-SNG-INSOLVENCY-2018]; [BIB-IMF-SNG-FISCALRISKS-2022]; [BIB-WB-UNTILDEBT-2013].
- SHOULD: avoid discretionary bailouts; if extraordinary support occurs, require **loss-sharing + governance conditions**.

5) **Revenue autonomy floor**
- SHOULD: every general-purpose local unit has at least one meaningful own-source lever (rate-setting, fee authority, or shared tax with local discretion).
- Fails via: “grant dependency” → weak accountability and high capture risk.

6) **Legibility interface (public, audit-ready)**
- MUST: publish a **transfer register** (see schema below) and link it to the competence ledger.
- MUST: consolidated reporting that includes material functional authorities and SOEs (`07-...`, `15-...`, `13-...`).
- MUST: any pooled fund/transfer created via a compact is linkable (compact ID ↔ transfer ID) (`IOP-1`; see `19-compacts-and-cooperative-governance.md`).

---

## C. Transfer register (canonical schema)
A public transfer register keeps the *money map* aligned with the competence ledger.

**Canonical schema + conditionality discipline:** `35-transfer-register-and-conditionality.md`.

Minimum: publish `TRF` IDs, payer/recipient Unit IDs, purpose type, legal basis, formula/conditions, amounts/timing, and disputes/appeals.

---

## D. Design choices (quick decision guide)
### 1) Vertical vs horizontal funding
- **Vertical equalisation (funded by higher level):** simpler; risks politicisation.
- **Horizontal (donor jurisdictions contribute):** can improve “fairness optics”; risks political backlash.
- Many systems use hybrids (OECD 2025).

### 2) What to equalise
- **Revenue capacity:** equalise ability to raise funds at standard rates.
- **Expenditure needs:** equalise service need differences (age structure, geography, deprivation).
- **Both:** most robust, but more data + disputes (IMF 2018).

### 3) Conditionality discipline
- Use conditions for **spillovers and standards**, not as general patronage.
- Prefer **output definitions** over micromanaged inputs (reduces gaming and corruption surface).

---

## E. Failure modes + countermeasures (short list)
- **Blame shifting (“they cut our funding”)** → publish mandate notes + transfer register; tie funds to competence ledger.
- **Formula gaming / data manipulation** → independent statistics + audit trails; periodic rebasing.
- **Soft budget constraints** → debt registry + resolution framework; reduce ad hoc bailouts.
- **Fragmentation / hidden government** → consolidate functional authorities; require ledger entries and consolidated accounts (`15-...`, `70-...`).

---

## F. Cross-links (keep the archive small)
- Fiscal transparency and consolidated accounts: `07-fiscal-and-budgetary-governance.md`
- Functional authorities and off-book risks: `15-functional-authorities.md`
- Metropolitan arrangements (spillovers + land-use coupling): `16-metropolitan-governance.md`
- Boundary changes and reorganisation process: `17-jurisdiction-formation-and-boundaries.md`
- Interoperability primitives: `70-interoperability.md`
