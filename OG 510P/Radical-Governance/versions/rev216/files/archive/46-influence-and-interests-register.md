# Influence & Interests Register (INF/INT) (Making Influence Joinable)

**Purpose:** make influence (meetings, gifts, conflicts, intermediaries) joinable to decisions/contracts—while minimizing retaliation/doxxing risk (`99`).

Integrity failures are often *boundary failures*: decisions are quietly shaped by meetings, gifts, conflicts, intermediaries, or revolving-door arrangements that never become part of the official record. The goal here is a compact, portable register pattern that makes influence **discoverable**, **contestable**, and **joinable** to decisions and contracts—without doxxing.

**Anchor set (start here):**
- OECD Recommendation on Public Integrity: see [BIB-OECD-PI].
- OECD Recommendation on Transparency and Integrity in Lobbying: see [BIB-OECD-LOB].
- OECD Guidelines for Managing Conflict of Interest in the Public Service: see [BIB-OECD-COI].
- UNCAC prevention + procurement baselines: see [BIB-UNCAC].
- See `79-conflict-of-interest-and-revolving-door-discipline.md` for a minimal portable discipline (waivers, recusals, cooling-off as joinable receipts).

---


## Kernel anchors (do not repeat)
- **From-below usability:** these artifacts MUST remain comprehensible and actionable via the person’s path (assisted/offline options; no insider knowledge). (`98-persons-path-and-accessibility-invariants.md`)
- **COI + revolving door:** `79-conflict-of-interest-and-revolving-door-discipline.md`.
- **Procurement integrity:** `22-public-integrity-and-procurement.md`, CPR `38-...` (joinable spend + interests).
- **Records + remedy:** `31-...` (DRR), `08-...` + ALR `36-...` (challenge and enforcement).
- **Publication discipline:** `51-...` (release formats; point-in-time).
- **Protective legibility:** `99-protective-legibility-and-adoption-dynamics.md` (disclosure can enable harassment/retaliation).

## Named tensions (design must surface these)
- **Transparency vs harassment/retaliation:** disclose enough to deter capture without enabling targeting.
- **Disclosure burden vs access:** rules must not exclude legitimate participation by small actors.
- **Anti-corruption vs association rights:** regulate influence without criminalizing civic life.
- **Detail vs cognitive budget:** prioritize joinable essentials; avoid “everything disclosed, nothing seen.”

## A. Objects and IDs (keep the set small)
- **`INF-*` Influence interaction**: any *material* contact intended to shape a public decision (meeting, call, message, event invitation, sponsored travel, gift/hospitality above threshold, etc.).
- **`INT-*` Interests / COI declaration**: structured declaration (and lifecycle) for a covered role, including recusals and management actions.

**Design rule:** publish **role IDs and org/entity IDs**, not personal contact details. The public interface is about *influence on decisions*, not surveillance of people.

---

## B. Influence Interactions Register (`INF`) — minimum public schema
Start with a simple CSV; graduate to a register with change logs.

| Field | Meaning |
|---|---|
| `INF-ID` | stable ID |
| Date | occurrence date (time optional) |
| Covered role | role/office ID (not private contact info) |
| External party | organization / lobby entity / client (`EID` bundle where available) |
| Channel | meeting/call/written/other |
| Topic | short topic tags + (when known) linked `DRR-*` / `PAR-*` / `CON-*` |
| Outcome type | info request / recommendation / commitment / other |
| Disclosure status | complete / partial / redacted (with reason) |
| Links | related object IDs (`DRR`/`PAR`/`CON`/`TRF`/`ENG`/`RULE` as-of) |
| Notes (optional) | short non-sensitive summary |

**Thresholds (local):**
- define a **gift/hospitality threshold** (and always log above it);
- define **decision classes** that require ex parte disclosure by default (permits, enforcement discretion, large procurement, zoning/land-use, grants).

---

## C. Interests / COI Register (`INT`) — minimum public schema
A two-layer pattern works best:
- **Public:** status + categories + recusals (without sensitive personal details).
- **Protected:** full detail under strict access controls + audit logs (see `33-...`).

| Field | Meaning |
|---|---|
| `INT-ID` | stable ID |
| Covered role | role/office ID + coverage rule |
| Declaration date | filed date + period covered |
| Categories | structured categories (holdings, outside roles, gifts, family ties, etc.) |
| Status | filed / overdue / verified / under review / sanctioned / closed |
| Cooling-off / exit restrictions (if applicable) | restriction categories + end date; waiver pointer (`DRR` when granted) |
| Management actions | recusal(s), divestment, blind trust, role change (link to `DRR-*` when it alters authority) |
| Links | related `INF-*` disclosures; related contracts `CON-*` where conflicts exist |

---

## D. Interface rules (how this plugs into the archive’s join graph)
**IR-1 Decision disclosure rule (default):**
- For decision classes where **ex parte influence** is plausible, the issuing `DRR` MUST include a “contact disclosure” field:
  - either `INF-*` IDs (if any), or `INF: NONE DECLARED`.
- If a decision is informed by formal participation, prefer linking `ENG-*` (and keep `INF-*` for non-public influence channels).

**IR-2 Recusal and authority rule:**
- If a conflict triggers **recusal** or **authority reassignment**, issue a `DRR` (typically `DRR-KIND: DEC` with `DRR-TYPE: INTEGRITY`) that cites the relevant `INT-*` and updates the competence ledger where necessary.

**IR-3 Procurement linkage (anti-capture):**
- Above threshold, awards and major amendments SHOULD be cross-checked for:
  - relevant `INF-*` interactions with procuring officials; and
  - unresolved `INT-*` conflicts.
- Contracts already live in CPR (`38-...`); `INF/INT` are the *integrity joins*.

**IR-4 Remedy and enforcement:**
- Provide explicit appeal lanes (`AL-*`) for:
  - register non-compliance (missing/late disclosures),
  - ethics determinations, and
  - sanctions (supplier debarment, official discipline).
(See `36-...` and `08-...`.)

**IR-5 Revolving door and waiver discipline:**
- Entry/exit restrictions, cooling-off determinations, and waivers MUST be recorded as joinable integrity receipts (`DRR-TYPE: INTEGRITY`) that cite the relevant `INT-*` (and `INF-*` when contact will occur).
- No silent exceptions: waivers are time-bounded decisions with an appeal lane.
(See `79-conflict-of-interest-and-revolving-door-discipline.md`.)

---

## E. Privacy and abuse-resistance (minimum)
- **Publish roles, not personal contact details.**
- Use **`EID` bundles** for external parties where possible; otherwise publish org name.
- Record **redaction reasons** as codes (e.g., safety, ongoing investigation), and treat redactions as reviewable decisions (`DRR` + `AL-*`).
- Keep public notes short; move sensitive detail to protected layers with audit logs (`DPR-*` where applicable).
- **Do not weaponize disclosure:** the goal is accountability for **decision influence**, not doxxing or chilling participation. Avoid requirements that force vulnerable community advocates to publish personal identifiers; prefer organization/role-level disclosure and representative channels (`99`).
- **Retaliation-aware intake:** allegations of undisclosed influence or coercive lobbying SHOULD have confidential filing options and safe representation; treat intimidation as a defect and track it as an integrity risk (`08`, `36`, `98`).
---

## F. Minimal implementation path (ship this without a new bureaucracy)
1) Start with **monthly disclosure CSVs** (INF + INT status).
2) Add stable IDs + change logs (no silent edits).
3) Require `DRR` receipts to cite `INF/INT` on the high-risk decision classes.
4) Add enforcement: late filing → auto-notice; repeated noncompliance → ethics lane.
