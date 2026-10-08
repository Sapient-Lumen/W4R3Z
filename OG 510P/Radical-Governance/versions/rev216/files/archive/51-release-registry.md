# Release Registry & Publication Objects (`REL-*`)

**Purpose:** make official releases versioned, joinable, and contestable so public evidence can be used without guesswork.

A **release** is any official publication that claims to describe reality (“what happened / what is the state of the world”), or that
is required to make authority and money **auditable**: datasets, statistical bulletins, budget tables, contract/grant disclosures,
evaluation reports, algorithmic impact summaries, enforcement reports, etc.

This file defines a **Public Data / Document Release Register (PDRR)** and the stable ID family `REL-*` used across the archive.

**Why this exists:** many “open data” programs fail because releases are **not joinable** (no stable IDs, no versioning, no methods, no contestation lane).
`REL-*` is the smallest interface that makes releases usable for audit, remedy, and learning.

**Anchors (high-trust):** official statistics norms ([BIB-UNFPOS], [BIB-OECD-GSP]); catalog/metadata standards ([BIB-W3C-DCAT-3], [BIB-SDMX-3-0]);
provenance ([BIB-W3C-PROV-O]); content provenance ([BIB-C2PA-2-3]).

## Kernel anchors (do not repeat)
- Publication integrity (tamper-evident, as-of access): `53-...`.
- Records custody + FOI pipeline: `31-...`.
- Interop join keys (REL links to RULE/DRR/etc.): `70-...`.
- Protective legibility: publish what enables contestation, not surveillance: `99-protective-legibility-and-adoption-dynamics.md`.
- Person-facing use (receipts cite releases; comprehension/access): `98-persons-path-and-accessibility-invariants.md`.

## Named tensions (design must surface these)
- Openness for accountability vs misuse/harassment/retaliation risk.
- Timeliness vs validation (publish fast vs publish right).
- Machine-readability vs human comprehension/context.
- Transparency vs operational/security risk (esp. in coercive domains).

---
## A) What counts as a `REL-*` release
Mint a `REL-*` when *any* of the following are true:
- it is cited as evidence in a `DRR-*` (decision record/receipt), **or**
- it publishes a baseline or outcome for a `CLM-*` claim, `EVAL-*` evaluation, or `PROG-*` program, **or**
- it discloses money/relationships (contracts, grants, subsidies, lobbying meetings) needed for integrity auditing, **or**
- it is a “canonical” series (budget tables, service performance dashboards, safety statistics, ecological indicators).

Do **not** mint a new `REL-*` for trivial website edits; use normal web change logs unless the content is relied upon for decisions.

---

## B) Minimum public schema (one screen)
A release must be discoverable and verifiable even when the underlying data is gated.

| Field | Meaning |
|---|---|
| `REL-*` | stable release ID |
| Issuing unit | Unit ID + accountable role |
| Title + type | e.g., dataset / report / bulletin / dashboard / disclosure packet |
| Coverage | geography + time window (and population/units where relevant) |
| Subject tags | ≤6 tags (use existing vocab where possible; see `27-standards-and-technical-governance.md`) |
| Link(s) | canonical URL(s) + mirrors + file hashes |
| Format + schema | file format(s) (machine-readable where possible) + schema/codebook reference; if PDF-only, publish a structured extract or justify |
| Method note | short method summary + link to full method; include definitional choices |
| Revision policy + log | what can change; how revisions are labeled; no silent edits; use canonical `REV`/`PUBLISHED-AT`/`EFFECTIVE-*` semantics (`70-...`) |
| Access class | public / gated / confidential; if gated, publish existence metadata + how to request access (`FOI-*` / lane in `AL-*`) |
| Contestation lane | where method disputes / correction requests go (`AL-*`) |
| Related joins | cite relevant IDs (`CLM-*`, `EVAL-*`, `PROG-*`, `CON-*`, `GRT-*`, `TEX-*`, `ADS-*`, `ENF-*`, `DRR-*`) |
| Privacy / security note (when needed) | cite `DPR-*` or risk assessment summary if release involves personal/sensitive data |

Machine readability is a first-class requirement: contestation increasingly depends on automation (including citizen-side AI). Prefer open, structured formats (CSV/JSON) with explicit schemas; if the public-facing artifact is narrative (PDF/report), publish the corresponding structured extract.


### B2) Optional fields (stats-grade / high-stakes releases)
These fields are optional, but strongly recommended for canonical series and anything used in rights-/resource-affecting decisions:
- **Update cadence + publication lag** (so timeliness is measurable).
- **Uncertainty / data quality note** (even if qualitative).
- **`REVISION-OF` link + per-version changelog entry** (no silent rebases).
- **Status flag**: provisional / final / superseded / withdrawn.

**Verification:** every release SHOULD publish a checksum/signature; see `53-publication-integrity-and-tamper-evident-logs.md` for bundle + transparency-log options. If a platform supports content credentials, include them ([BIB-C2PA-2-3]).

---

## C) Types (keep the set small)
Use a small controlled list so analytics is possible:
- `REL-TYPE: STATS` (official stats / series)
- `REL-TYPE: BUDGET` (budget + execution tables)
- `REL-TYPE: DISCLOSURE` (contracts/grants/lobbying/beneficial ownership)
- `REL-TYPE: EVAL` (evaluation report + annexes)
- `REL-TYPE: SAFETY` (safety incidents, enforcement reporting)
- `REL-TYPE: TECH` (model cards / system impact summaries)
- `REL-TYPE: OTHER` (only if unavoidable)

---

## D) Release discipline (anti-propaganda rules)
- **Equal access:** no privileged pre-release to insiders; if embargoed for operational reasons, log the embargo terms and recipients.
- **Methods are first-class:** definitional disputes must be routed to a named lane and cannot be buried in footnotes.
- **Revision honesty:** corrections must be issued as new versions; keep prior versions accessible unless a court-ordered restriction exists.
- **Joinability to decisions:** when a `REL-*` is used in a `DRR-*`, the `DRR-*` MUST cite the release *as-of* a specific version/time.

---

## E) Minimal operating model (who runs PDRR)
- A small **Release Steward** function (can sit with records/FOI or statistics) ensures IDs, versioning, and logs exist.
- Audit/oversight SHOULD test “missing release” incidents (see `32-oversight-institutions-and-follow-through.md`).

See also: `26-epistemic-infrastructure-and-public-knowledge.md` (why shared facts collapse); `31-records-foi-and-government-memory.md` (records/FOI joins);
`38-contracting-and-procurement-register.md` and `49-grants-subsidies-and-tax-expenditures-register.md` (money disclosures).