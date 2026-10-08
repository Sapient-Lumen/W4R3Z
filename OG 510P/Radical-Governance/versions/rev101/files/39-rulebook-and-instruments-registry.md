# Public Rules Register (PRR) & Rulebook Versioning (Making “the law” queryable)

The PRR is the **canonical inventory of enforceable norms** at a scope. It makes one question answerable with evidence:

> **What rule applies to me, right now, here — and how can I challenge it?**

This memo is a **spec** (joinable IDs, versioning, “as-of” queries, machine-readable options) and is intentionally narrow.

---

## A. Definitions (keep boundary disputes rare)

**Binding rule (“RULE”)**  
A norm that can be enforced against people (fines, permits, eligibility, sanctions, detention, seizure, rate/tariff enforcement).

**Guidance that functions like law (“GLAW”)**  
Non-binding in theory but enforced in practice (e.g., eligibility rules embedded in software or frontline scripts). If it is enforced, it MUST be discoverable in the PRR with a status flag.

**Operational policy / script (“OPS”)**  
Internal manuals, checklists, scripts, or configuration tables that materially determine outcomes (eligibility, permit conditions, tariffs, sanctions). If they shape decisions in practice, they MUST be inventoried in the PRR (often as `GLAW`) and linked to the system/service that uses them (`SRV-*`, `ADS-*`, `IDN-*`).

**Rulebook**  
The set of in-force `RULE` objects for a unit + all incorporated standards and referenced authorities, at a point in time.

**MVLL test (minimum viable legal legibility)**  
If a norm is enforced, it MUST be **findable** by ID with an effective date and an appeal lane.

---

## B. PRR — minimum schema (tight; don’t invent extra fields)

### Portable instrument kinds (keep the set small)
PRR entries SHOULD label the enforcement-facing **kind** of instrument so inventories can be reconciled across scopes.

Recommended values (use the nearest match; don’t proliferate synonyms):
- `STATUTE` / `REG` / `BYLAW` / `ORDER`
- `TARIFF` (rates/fees schedules)
- `POLICY` (operational policy manuals)
- `GUIDE` (non-binding guidance)
- `SCRIPT` / `CONFIG` (frontline scripts or software configuration tables)
- `RAC` (derivative “rules as code” implementation, subordinate to text)

| Field | Meaning |
|---|---|
| `RULE` ID | stable, resolvable identifier (`UNIT-RULE-SEQ`) |
| Title | human-readable title |
| Issuing `UNIT` | unit ID (must exist in competence ledger) |
| Instrument kind | one of the portable kinds above (e.g., `REG`, `TARIFF`, `SCRIPT`); if enforced but non-binding-in-theory, use `GUIDE`/`POLICY` and set status to `GLAW` |
| Authority chain | parent `RULE` IDs that authorize it (or constitutional basis) |
| Coverage | territory / service area reference where applicable |
| Status | proposed / in force / suspended / repealed / *GLAW* |
| Effective window | start + end (or open-ended) |
| Version | version ID + change log + links to prior versions |
| Authoritative text | canonical text (plus machine-readable form where feasible) |
| Plain summary | 3–7 bullets |
| Appeals / remedy | `AL-*` lane(s) (from ALR `36-...`) + time limits |
| Review / sunset | review date / sunset (if any) |
| Links | related rules, compacts, standards (`STD-*`), forms, ADS, permits |

**Non-negotiables**
- **Update SLA:** PRR is updated within a fixed window after enactment (e.g., 24–72 hours) with a published timestamp.
- **Diffs required:** every change publishes a diff summary (what changed; why; who authorized).
- **No “dark enforcement”:** enforcement actions MUST cite `RULE` IDs (and versions / “as-of” date) in `DRR`s (`31-...`).
- **Retire, don’t reuse:** repealed rule IDs remain resolvable (tombstones + history).

---

## C. “As-of” queries (prevent retroactive confusion)
PRR MUST support queries by:
- **date/time** (“show the rulebook as of 2026‑02‑01”), and
- **place/service area** (when coverage differs).

**Decision rule:** a rights-affecting `DRR` includes the **rule version(s)** used at decision time (or an “as-of” pointer). This is the minimum to make review and remedy meaningful.

---

## D. Machine-readable law (optional; never outranks the text)
Where feasible, publish a machine-readable representation for interchange and tooling (e.g., Akoma Ntoso / LegalDocML). The authoritative hierarchy is:

**canonical text > authenticated consolidations > machine representations > derived “rules as code”**

- If machine-readable outputs exist, they MUST link back to the canonical `RULE` ID + version.
- Tooling MUST be testable against the authoritative text (publish conformance tests / fixtures).

**Interchange anchors:** Akoma Ntoso (OASIS) and the LegalDocML workstream. See [BIB-OASIS-AKN-2018] and [BIB-OASIS-LEGALDOCML].

---

## E. “Rules as Code” (derivative interface; useful for eligibility & calculators)
If the public receives decisions via automated or semi-automated systems, publish a **derivative rule implementation** (RaC) only if:
- it is **traceable** to `RULE` IDs + versions,
- it has a public **test suite** (sample cases) and **change log**, and
- it never becomes the de facto source of truth.

This improves delivery while reducing “frontline discretion drift” and vendor lock-in. See [BIB-CIGI-RAC-2025].

---

## F. Implementation notes (keep it cheap)
- Start with **top enforcement surfaces**: permits, eligibility, fines, tariffs.
- Treat “binding guidance” as first-class: label it `GLAW` until clarified or repealed.
- Treat **OPS/script/config** artifacts as inventory targets: if they materially determine outcomes, they must be findable by `RULE` ID (often `GLAW`) and linked to the system/service that uses them (`SRV-*`/`ADS-*`/`IDN-*`).
- **OPS changes are policy changes:** when an OPS/script/config change is expected to alter outcomes (eligibility thresholds, enforcement priorities, queue rules), publish a new version and issue a `DRR` notice that cites the affected `RULE` IDs + the `SRV/ADS/IDN` surfaces.
- If you already publish law, *add joinability*: stable IDs, effective windows, and ALR lane links.
- If you have an API, document it (example reference: UK legislation.gov.uk OpenAPI). See [BIB-UK-LEGIS-OPENAPI].

---

## G. Cross-links (where this plugs in)
- Interop join-keys: `70-interoperability.md` (RULE as spine key)
- Decision receipts: `31-records-foi-and-government-memory.md` (DRR cites RULE+version)
- Remedy lanes: `36-appeal-lanes-and-redress-registry.md`
- Digital decisions: `06-digital-and-algorithmic-governance.md`
- Permissioning: `29-permissioning-and-approvals.md`
