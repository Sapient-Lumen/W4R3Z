# Contracting & Procurement Register (Open Contracting as an Interface)

**Purpose:** make contracting legible end‑to‑end (who paid whom, for what, under what terms) so corruption, failure, and capture are detectable and contestable.

Public procurement is one of the largest and most capture-prone state interfaces. The goal is not “more transparency” in the abstract, but a **joinable audit spine** that lets people answer:

- *Who decided to spend?* (`DRR` + `RULE`)
- *Who got paid for what?* (`CON` + joinable execution releases via `REL-*`)
- *What changed after award?* (amendments, scope changes, change orders)
- *How do I challenge this?* (`AL-*` lanes, including bid protests and supplier sanctions)
- *Is this tied to a transfer/compact/program?* (`TRF` / `CMP` / `PROG` / `CLM`)

This memo defines a minimal **Contracting & Procurement Register (CPR)** that can be implemented locally but interoperates across scopes.

For major capital projects, the CPR SHOULD join contracts to the capital project gate receipts and asset/portfolio context (see `97-public-investment-and-capital-project-governance.md` + `48-...`).

**Anchors:** [BIB-OCDS] (OCDS); [BIB-OECD-PROC]; [BIB-UNCAC]; [BIB-WB-PROC-REG-2025]. Optional beneficial ownership linkage: [BIB-BODS] and [BIB-FATF-BO-2023].

---


## Kernel anchors (do not repeat)
- **Receipts + reasons for spend:** `31-records-foi-and-government-memory.md` (DRR; RULE/RC; point-in-time).
- **Integrity / capture controls:** `22-public-integrity-and-procurement.md`, `79-conflict-of-interest-and-revolving-door-discipline.md`.
- **Remedy lanes:** `08-remedy-and-grievance.md`, ALR `36-...` (bid protest, supplier sanction appeal, public complaint).
- **Releases + audits:** `51-release-registry.md` (REL-* execution disclosures).
- **Protective legibility:** `99-protective-legibility-and-adoption-dynamics.md` (open ≠ safe; anti-retaliation where needed).
- Person-facing access + contestability for affected communities/workers: `98-persons-path-and-accessibility-invariants.md`.

## Named tensions (design must surface these)
- **Openness vs collusion/retaliation:** disclosure can enable cartel coordination or targeting; use phased/redacted release where justified.
- **Speed vs integrity:** crisis procurement needs throughput without becoming a capture portal.
- **Detail vs cognitive budget:** publish joinable essentials; avoid a “data lake” that hides the spine.
- **Competition vs continuity:** strict rules can kill delivery; exceptions must be receipted and reviewable.

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
| Capital / portfolio join (if applicable) | `AST-*` (asset) and/or `PROG-*` (portfolio/program) + any project gate `DRR-*` receipts (see `97-...`) |
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

**Legibility theater warning:** publication MUST include a **machine-readable feed** (CSV/JSON/OCDS) plus a short human summary. A large PDF alone is not compliance; it is functional opacity.

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
- **CLC-1 Receipt/record emission:** the vendor MUST support issuance of person-facing `DRR` receipts (or equivalent joinable records) for rights-affecting decisions and MUST log outcome reasons with `RC-*` (see `52-reason-codes-registry.md`) and remedy lane pointers (`AL-*`). Receipts MUST satisfy the **comprehension test** (`98-persons-path-and-accessibility-invariants.md`) and include a plain-language *what-next* path; where the vendor operates intake, it MUST preserve deadlines and provide **no-wrong-door** routing (see `08-...`, `47-...`).
- **CLC-2 Rule traceability:** operational policy artifacts that determine outcomes (manuals/scripts/config tables) MUST be inventoried in the PRR (often `GLAW`) and changes MUST be versioned and logged (no silent rewrites).
- **CLC-3 Audit + oversight access:** oversight bodies (audit/ombuds/IG) MUST have access to logs, cases, and technical details sufficient to test error, bias, and manipulation (even when public disclosure is limited). Confidentiality/trade‑secret claims MUST be narrow and reviewable and MUST NOT block access for authorized oversight or the disclosure of policy‑determining artifacts (rules, configs, thresholds) to those bodies.
- **CLC-4 Data portability + exit:** publish a workable exit plan for high-stakes systems (data export, schema documentation, transition support, escrow where appropriate) so “lock-in” can’t defeat accountability.
- **CLC-5 Incident/outage logging:** outages, degradations, and “manual override” modes that affect access MUST be logged and joinable (so outage-as-denial is contestable).
- **CLC-6 FOI/records continuity:** records created or held by the vendor in performing a public function MUST be captured/retained as official records under the jurisdiction’s records regime, and MUST be reachable via the FOI/RTI access pipeline (subject to lawful exemptions).
- **CLC-7 Evaluation cooperation:** where contracts support a `PROG-*`, vendors MUST support evaluation (data access, implementation logs, and response-to-evaluation duties as applicable).
- **CLC-8 Subcontractor transparency:** disclose material subcontractors for high-risk/`ESS-1` services and flow down the CLC pack (no accountability laundering via tiering).
- **CLC-9 Self-report + correction duty:** vendors MUST promptly disclose material legibility/integrity failures (missing receipts/logs, unlogged rule/config changes, data-release errors) and support corrective `DRR`/register updates; contracts MAY offer reduced penalties for timely self-report + correction (`ACC-8`).
- **CLC-10 Labour conditions (where labor‑intensive):** for contracts that procure labor-intensive work (works, care, cleaning, security, logistics), require compliance with wage/time/safety standards, flow down to subcontractors, and provide joinable reporting so violations can link to `DRR-*`/`ENF-*` and the `CON-*` object (procurement labor clause anchor: [BIB-ILO-C94-1949]).

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