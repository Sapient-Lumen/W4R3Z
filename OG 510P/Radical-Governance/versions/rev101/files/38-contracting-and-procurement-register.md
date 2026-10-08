# Contracting & Procurement Register (Open Contracting as an Interface)

Public procurement is one of the largest and most capture-prone state interfaces. The goal is not “more transparency” in the abstract, but a **joinable audit spine** that lets people answer:

- *Who decided to spend?* (`DRR` + `RULE`)
- *Who got paid for what?* (`CON` + joinable execution releases via `REL-*`)
- *What changed after award?* (amendments, scope changes, change orders)
- *How do I challenge this?* (`AL-*` lanes, including bid protests and supplier sanctions)
- *Is this tied to a transfer/compact/program?* (`TRF` / `CMP` / `PROG` / `CLM`)

This memo defines a minimal **Contracting & Procurement Register (CPR)** that can be implemented locally but interoperates across scopes.

**Anchors:** [BIB-OCDS] (OCDS); [BIB-OECD-PROC]; [BIB-UNCAC]; [BIB-WB-PROC-REG-2025]. Optional beneficial ownership linkage: [BIB-BODS] and [BIB-FATF-BO-2023].

---

## A. Object identity (joinability first)

### `CON` — Contract / procurement process ID
- Every procurement process MUST have a stable **`CON`** ID.
- Where using OCDS, the `CON` SHOULD be the **OCID** (or be machine-mapped to the OCID) so external tools can consume it.

**Minimum rule:** the `CON` ID MUST be present in (1) award notices, (2) execution/payment reporting, and (3) amendments/change orders.

**Budget/spend join (optional but high value):** if publishing budget/execution ledgers, use a consistent linkage pattern so contract spend can be joined to budget and execution lines (e.g., the OCDS budget/spend extension [BIB-OCDS-BUDGETSPEND-EXT] alongside fiscal ledger publication guidance like OFDP [BIB-GIFT-OFDP]).

---

## B. Minimal CPR record (one screen)

A CPR record SHOULD be one row (or one JSON object) keyed by `CON`, with linked documents.

| Field | Meaning |
|---|---|
| `CON` | stable ID (prefer OCID if OCDS) |
| Owning unit | Unit ID (competence ledger) |
| Legal basis | `RULE-*` authorizing procurement + any emergency authority (`EMR-*` if used) |
| `AUTH-DRR` | authorizing `DRR-*` (award decision) and any major amendment/change-order approvals (keeps reason-giving and remedy joinable; join rule in `70-...`) |
| Procurement method | open/limited/single-source; justification if non-open |
| Tender window | publish + close dates; bidder count; single-bid flag |
| Award | supplier (`EID` bundle; at least one authoritative registry ID); award value; award date; evaluation summary; (optional) BO statement references for high-risk awards |
| Contract terms | scope summary; duration; renewal options; key performance outputs |
| Amendments | list of amendments/change orders (date, value delta, scope delta, reason code) |
| Payments & delivery | payment totals; milestone status; completion/close-out result; and (when published) a pointer to the relevant execution/payment ledger release (`REL-*`) so payments can be joined to budgets and other spending lines (see `07-...`) |
| Integrity flags | conflict declarations; debarment/sanctions status; audit references (`OFR-*`) |
| Remedy | `AL-*` lanes (bid protest, FOI access, supplier sanctions appeal) |
| Links | `DRR-*` (award decision), `SRV-*` (services materially delivered/operated by the contract), `ADS-*`/`MOD-*` (if automated decisions are in scope), `TRF-*` (if funded by transfers), `PROG-*` and tested `CLM-*` (if part of a program), related permits (`PAR-*`) |

**Interface rule:** awards and major amendments SHOULD cite a `DRR` so reasons, evidence, and remedy are portable.

---

## C. Exceptions discipline (emergency and single-source)

When non-open procurement is used:
- MUST log a **justification** tied to `RULE`/`EMR` authority.
- MUST publish the record anyway, with redactions only as narrowly required.
- SHOULD require post-facto review (oversight finding `OFR-*`) when thresholds are exceeded.

---

## D. Supplier integrity linkage (minimal, not maximal)

The CPR SHOULD store **supplier identifiers** as `EID` bundles (at least one authoritative registry ID; tax IDs may be protected) and allow optional linkage to:
- beneficial ownership statements/entities (prefer BODS statement IDs; typically published in a joinable `REL-*` BO release), and/or
- a debarment/sanctions list with due-process appeal lanes (`AL-*`).
- `INF/INT` integrity joins where relevant (e.g., above-threshold procurement with logged influence interactions or conflicts) (see `46-influence-and-interests-register.md`).


**Constraint:** supplier sanctions MUST be contestable (lane published in ALR) and proportionate; “silent debarment” is prohibited.

---

## E. Contractual legibility clauses (CLC pack) — when government acts by contract

Outsourcing can create a **shadow state**: rights-affecting decisions and public records move into vendor systems where notice, remedy, and audit become harder. A CPR is not enough unless contracts *force the interface to exist*.

**Rule:** *delegation does not defeat legibility.* If a contract materially determines rights, money, or coercion, it MUST carry a minimal **Contractual Legibility Clause (CLC)** pack (see also [BIB-HUP-GOVBYCONTRACT-2009]).

**CLC pack (minimum; flow down to subcontractors):**
- **CLC-1 Receipt/record emission:** the vendor MUST support issuance of person-facing `DRR` receipts (or equivalent joinable records) for rights-affecting decisions and MUST log outcome reasons with `RC-*` and remedy lane pointers (`AL-*`).
- **CLC-2 Rule traceability:** operational policy artifacts that determine outcomes (manuals/scripts/config tables) MUST be inventoried in the PRR (often `GLAW`) and changes MUST be versioned and logged (no silent rewrites).
- **CLC-3 Audit + oversight access:** oversight bodies (audit/ombuds/IG) MUST have access to logs, cases, and technical details sufficient to test error, bias, and manipulation (even when public disclosure is limited). Confidentiality/trade‑secret claims MUST be narrow and reviewable and MUST NOT block access for authorized oversight or the disclosure of policy‑determining artifacts (rules, configs, thresholds) to those bodies.
- **CLC-4 Data portability + exit:** publish a workable exit plan for high-stakes systems (data export, schema documentation, transition support, escrow where appropriate) so “lock-in” can’t defeat accountability.
- **CLC-5 Incident/outage logging:** outages, degradations, and “manual override” modes that affect access MUST be logged and joinable (so outage-as-denial is contestable).
- **CLC-6 FOI/records continuity:** records created or held by the vendor in performing a public function MUST be captured/retained as official records under the jurisdiction’s records regime, and MUST be reachable via the FOI/RTI access pipeline (subject to lawful exemptions).
- **CLC-7 Evaluation cooperation:** where contracts support a `PROG-*`, vendors MUST support evaluation (data access, implementation logs, and response-to-evaluation duties as applicable).
- **CLC-8 Subcontractor transparency:** disclose material subcontractors for high-risk/`ESS-1` services and flow down the CLC pack (no accountability laundering via tiering).
- **CLC-9 Self-report + correction duty:** vendors MUST promptly disclose material legibility/integrity failures (missing receipts/logs, unlogged rule/config changes, data-release errors) and support corrective `DRR`/register updates; contracts MAY offer reduced penalties for timely self-report + correction (`ACC-8`).

**Publishing discipline:** CPR entries for CLC-scoped contracts SHOULD disclose whether the CLC pack is present (and whether any clauses are limited by law), so missing legibility becomes auditable.


## F. Minimal metrics (portable)

Keep metrics small; prefer ones that expose capture and delivery failure:
- share of value awarded via non-open methods
- share of single-bid awards
- share of spend under amended contracts; median amendment count
- on-time completion rate; close-out audit coverage

Hook these to the metrics pack (`03-metrics-and-evidence.md`) using [IPM-13].

---

## G. Where this plugs into the archive

- Integrity design: `22-public-integrity-and-procurement.md`
- Fiscal join: `07-fiscal-and-budgetary-governance.md`, `18-intergovernmental-finance.md`
- Records + remedy: `31-records-foi-and-government-memory.md`, `36-appeal-lanes-and-redress-registry.md`
- Interop rules: `70-interoperability.md`, roadmap: `80-implementation-roadmap.md`


Note: if procuring an automated decision system or model, link `ADS-*`/`MOD-*` and require auditability clauses (see `42-...`).
