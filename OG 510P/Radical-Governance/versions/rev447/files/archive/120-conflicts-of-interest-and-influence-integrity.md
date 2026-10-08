# Conflicts of interest & influence integrity

**Problem:** “Capture” often happens through **relationships**, **money**, and **career pathways**—not overt bribery. The system must make influence **legible**, conflicts **manageable**, and decisions **contestable**, without banning legitimate advocacy.

This memo defines a portable **Influence & Conflict Integrity Protocol (ICIP)** that can be adopted at any scope (municipal → national → transnational bodies) and plugs into:
- **Decision receipts** (`106`), **deliberation binding** (`111`), **record interfaces** (`115`), **budget/procurement integrity** (`110`), and **rule change control** (`118`).
- **Circuit breakers** (`105`) when influence risks exceed thresholds.

---

## ICIP primitives

### 1) Roles & coverage inventory
Maintain a **Role Coverage Ledger** for all decision-capable positions:
- `ROLE-*` stable IDs (from `113`) and **decision authorities** (what the role can approve/change).
- **Risk tiering** (e.g., procurement authority; licensing; enforcement; grants; rulemaking).

**Metric:** % of decision authority covered by ICIP (target: near-100% for high-risk authority).

### 2) Interests disclosure, in machine-readable form
Publish a **Public Interests Register** with typed entries and change logs:
- `DIR-*` (Disclosure Item Record): assets, outside roles, clients, gifts/hospitality, travel, significant liabilities, and close-family conflicts (scope-dependent).
- `DCR-*` (Disclosure Change Record): additions/edits with timestamps and reasons.

Rules:
- **Clocked updates**: new interests must be recorded within X days (see time budgets `108`).
- **Materiality thresholds** must be explicit and versioned (see `118`).

Anchors: UNCAC encourages systems to prevent/manage conflicts for public officials. [BIB-UNCAC] citeturn0search6turn0search17

### 3) Recusal and “conflict handling” receipts
For each decision, the official must either certify “no material conflict” or log a **Recusal / Handling Receipt**:
- `RHR-*` includes: conflict type, handling mode (recusal / disclosure-only / firewall / independent review), and a pointer to the decision receipt (`106`).
- **Non-recusal handling** must be justified with a reason receipt (e.g., “only qualified official”; “statutory duty”) and a compensating control (e.g., independent sign-off).

**Test:** Randomly sample decisions for conflict-handling conformance (pairs with `119`).

### 4) Influence transparency: “regulatory footprint”
Maintain a **Decision Influence Ledger** that can be joined to decision receipts:
- `LCR-*` (Lobbying Contact Record): who met whom, about what decision domain, date/time, participants, and disclosed client/interest.
- `AFR-*` (Advisory Footprint Record): external advisory bodies and consultees, including funding/selection basis.

This implements a “regulatory footprint” style approach promoted in OECD instruments. citeturn0search4turn0search0

### 5) Revolving door controls (cooling-off + transparency)
For high-risk roles, apply:
- **Cooling-off periods** before representing private interests back to the agency/sector.
- `COR-*` (Cooling-Off Record): role, duration, scope, waivers (if any) with reasons.
- **Waivers are exceptional** and must trigger heightened disclosure + independent approval.

GRECO and related integrity guidance commonly emphasize revolving-door risk management. citeturn0search1turn0search5

### 6) Gifts, hospitality, and travel
Maintain a **Gifts & Benefits Register**:
- `GBR-*`: benefit type, value estimate, donor, decision domains affected, acceptance basis (per rules), and disposition (returned/donated/accepted).
- Hard rule: gifts cannot be “laundered” via intermediaries; require **ultimate source** disclosure where feasible.

### 7) Political finance (if relevant to the scope)
Where elections/parties exist, create a **Political Finance Interface**:
- `PFR-*`: donors, amounts, channels, timing, and enforcement outcomes.
- **Pre-decision disclosure** for high-stakes periods is preferable to “after the fact” transparency.

(Political finance design is jurisdiction-specific; keep the interface stable and versioned.)

---

## Circuit breakers (when influence risk spikes)

Trigger `105`-style breakers when thresholds are met (examples):
- High value procurement/grant decisions with low competition.
- Repeated contacts by the same actor across a decision chain.
- Unresolved disclosures or overdue updates for key officials.

Breakers:
- **Pause & independent review**
- **Mandatory publication of influence ledger entries**
- **Interim continuity protections** for affected parties (`109`/`114`)
- **Auto-sunset** for emergency waivers (`112`)

---

## Minimal metrics (publishable)

1. **Disclosure freshness**: % of officials up to date within clock.
2. **Recusal conformance**: audited share of decisions with correct RHR linkage.
3. **Influence legibility**: share of major decisions with at least one LCR/AFR entry (or explicit “none”).
4. **Waiver rate**: cooling-off and gift-rule waivers per 1,000 officials; trend line.
5. **Outcome skew checks**: concentration of awards/licenses among top beneficiaries (pairs with `110`).

---

## Bibliography keys to add/use

- [BIB-OECD-LOB-2024] OECD Recommendation on Transparency and Integrity in Lobbying and Influence (2024). citeturn0search4
- [BIB-OECD-LOB-2010] OECD Principles for Transparency and Integrity in Lobbying (2010). citeturn0search8
- [BIB-UNCAC] UN Convention against Corruption (conflict-of-interest prevention guidance). citeturn0search6turn0search17
- [BIB-GRECO-REVOLVING] Council of Europe / GRECO materials on revolving doors and integrity in public office. citeturn0search1turn0search5
