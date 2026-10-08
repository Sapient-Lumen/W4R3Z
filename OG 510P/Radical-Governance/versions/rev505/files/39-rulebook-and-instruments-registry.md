# Public Rules Register (PRR) & Rulebook Versioning (Making “the law” queryable)

**Stack relation:** use `300-lawmaking-rulemaking-and-regulatory-change-routing-guide.md` for the canonical route across the lawmaking / rulemaking / regulatory-change family. This memo is the versioned PRR / rulebook substrate; `25` is the public legal-legibility front door; `118` is the generic rule-change-control front door; `215` is the legislative-process specialization; `317` is the primary-to-secondary-legislation seam; `320` is the incorporation-by-reference / external-material seam; `319` is the statute-book-maintenance / consolidation / repeal / revision seam; `318` is the quasi-law / guidance / shadow-law seam; `216` is the impact-assessment / ex-post-review specialization; `208` is the implementation / release-engineering neighbor.

**Purpose:** treat rules as versioned, citable objects so people can contest **what was in force when** and oversight can join decisions to legal basis.
**Person served:** a person subject to enforceable rules who needs to know what was in force (as‑of) and how to challenge it.

**From-below:** This makes rules queryable and timestamped so ‘the law’ can’t change without notice, reasons, and an appealable record.
**EXP pointer:** counters `EXP-01` (Opacity) by making rule bases and “as-of” instrument versions discoverable (`98-persons-path-and-accessibility-invariants.md`).
**Join constraints:** identifiers/joins using this artifact MUST follow `70-interoperability.md` (empowered use‑path + corrective action), stay purpose‑limited/minimized, and have a narrow alternative when joins are unsafe or missing (prefer person‑portable receipts/reference numbers). (See `101-claude-rev142-normative-requirements.md` (NR-14).)
**As-of & corrections:** This artifact is versioned and queryable “as-of”; corrections emit a citable update (`REL-*`) and must propagate to dependent records/systems (see `31`, `53`, `70`, `73`). (`101` NR-07, NR-15)

The PRR is the **canonical inventory of enforceable norms** at a scope. It makes one question answerable with evidence:

> **What rule applies to me, right now, here — and how can I challenge it?**

This memo is a **spec** (joinable IDs, versioning, “as-of” queries, machine-readable options) and is intentionally narrow.

---

## Kernel anchors (do not repeat)
- **Rules-in-force inventory:** `25-legal-legibility-and-rule-inventory.md` (public rule map).
- **Records + point-in-time:** `31-records-foi-and-government-memory.md` (as-of rule basis for DRR/REL).
- **Publication integrity:** `51-release-registry.md`, `53-publication-integrity-and-tamper-evident-logs.md`.
- **Secrecy exceptions:** `77-sensitive-information-and-secrecy-governance.md` (withholding receipts, not silent gaps).
- **Protective legibility:** `99-protective-legibility-and-adoption-dynamics.md` (joinability vs justice).
- Person-facing comprehension + access (rules must be retrievable and usable by the governed): `98-persons-path-and-accessibility-invariants.md`.

## Named tensions (design must surface these)
- **Accessibility vs precision:** plain-language summaries help; authoritative text must remain traceable.
- **Stability vs update:** frozen rules aid predictability; rapid updates can be necessary (must be logged, diffed, and contestable).
- **Publication vs security:** some instruments create operational risk; handle via typed withholding receipts (`77`).
- **Joinability vs privacy:** cross-linking can expose people; publish what is needed for contestation, not targeting.

## A. Definitions (keep boundary disputes rare)

**Binding rule (“RULE”)**
A norm that can be enforced against people (fines, permits, eligibility, sanctions, detention, seizure, rate/tariff enforcement).

**Guidance that functions like law (“GLAW”)**
Non-binding in theory but enforced in practice (e.g., eligibility rules embedded in software or frontline scripts). If it is enforced, it MUST be discoverable in the PRR with a status flag.

**Operational policy / script (“OPS”)**
Internal manuals, checklists, scripts, or configuration tables that materially determine outcomes (eligibility, permit conditions, tariffs, sanctions). If they shape decisions in practice, they MUST be inventoried in the PRR (often as `GLAW`) and linked to the system/service that uses them (`SRV-*`, `ADS-*`, `IDN-*`).
Route to `320-incorporation-by-reference-external-standards-dynamic-updates-and-public-access-rails.md` when the real question is not merely inventory, but whether and how legislation may import external standards, codes, rates, or other documents by reference. Route to `318-statutory-guidance-codes-of-practice-directions-manuals-and-shadow-law-rails.md` when the real question is not merely inventory, but the legal effect, publication duty, or constitutional status of guidance-like instruments themselves.

**Rulebook**
The set of in-force `RULE` objects for a unit + all incorporated standards and referenced authorities, at a point in time.

**MVLL test (minimum viable legal legibility)**
If a norm is enforced, it MUST be **findable** by ID with an effective date, a **person‑readable summary**, and an appeal lane.

---

## B. PRR — minimum schema (tight; don’t invent extra fields)

### Portable instrument kinds (keep the set small)
PRR entries SHOULD label the enforcement-facing **kind** of instrument so inventories can be reconciled across scopes.

Recommended values (use the nearest match; don’t proliferate synonyms):
- `CONSTITUTION` / `CHARTER` / `TREATY` (top-tier instruments; see change discipline in `58-constitutional-change-and-amendment-discipline.md`)
- `STATUTE` / `REG` / `BYLAW` / `ORDER`
- `TARIFF` (rates/fees schedules)
- `PLAN` (binding plans/land-use and housing strategies that materially govern approvals; treat updates as publishable and diffable)
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
| Plain summary (person‑readable) | 3–7 bullets; MUST be understandable to a primary‑school literacy reader in the relevant language(s) (see `98-persons-path-and-accessibility-invariants.md`); provide translations and an offline/printable form |
| Appeals / remedy | `AL-*` lane(s) (from ALR `36-...`) + time limits |
| Review / sunset | review date / sunset (if any) + renewal standard / evidence docket pointer (for high-impact rules) |
| Links | related rules, compacts, standards (`STD-*`), forms, ADS, permits |

**Non-negotiables**
- **Update SLA:** PRR is updated within a fixed window after enactment (e.g., 24–72 hours) with a published timestamp.
- **Diffs required:** every change publishes a diff summary (what changed; why; who authorized).
- **Usable packaging (anti‑theater):** the PRR MUST offer low‑bandwidth and printable views for high‑enforcement rules (the “rules card”: what it means, what triggers it, and how to challenge) and MUST not rely on massive PDFs as the only interface (see `25-...` and `98-persons-path-and-accessibility-invariants.md`).
- **No “dark enforcement”:** enforcement actions MUST cite `RULE` IDs (and versions / “as-of” date) in `DRR`s (`31-...`).
- **Retire, don’t reuse:** repealed rule IDs remain resolvable (tombstones + history).

- **Waiver legibility:** if an instrument authorizes waivers/variances/exemptions, the PRR entry MUST point to the enabling clause and (when material) to a `REL-*` exception log; otherwise state `WAIVERS: NONE`.
 - See: `85-waivers-variances-and-exceptions-discipline.md`.

---

## C. “As-of” queries (prevent retroactive confusion)
PRR MUST support queries by:
- **date/time** (“show the rulebook as of 2026‑02‑01”), and
- **place/service area** (when coverage differs).

**Decision rule:** a rights-affecting `DRR` includes the **rule version(s)** used at decision time (or an “as-of” pointer). This is the minimum to make review and remedy meaningful.

**Cross-artifact rule:** if a `DRR` cites `AL-*`, `STD-*`, `ADS-*`, or other versioned objects, the referenced register SHOULD support the same point‑in‑time retrieval so a reviewer can reconstruct the full “decision environment” as of that date (see `70-interoperability.md`).

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
- In low‑literacy / low‑connectivity contexts, publish “rules cards” in **pictorial/voice‑friendly** form (posters, radio scripts, call‑in lines) keyed to the same `RULE` IDs.
- If you have an API, document it (example reference: UK legislation.gov.uk OpenAPI). See [BIB-UK-LEGIS-OPENAPI].

---

## G. Cross-links (where this plugs in)
- Omission / nonfeasance visibility: publish a periodic **rule activity** snapshot (`REL-*`) joinable by `RULE` (counts of determinations/enforcement where applicable) so *failure to act / failure to enforce* becomes measurable rather than deniable (see [TM-30]). (See `101-claude-rev142-normative-requirements.md` (NR-02).)
- Interop join-keys: `70-interoperability.md` (RULE as spine key)
- Decision receipts: `31-records-foi-and-government-memory.md` (DRR cites RULE+version)
- Remedy lanes: `36-appeal-lanes-and-redress-registry.md`
- Digital decisions: `06-digital-and-algorithmic-governance.md`
- Permissioning: `29-permissioning-and-approvals.md`
