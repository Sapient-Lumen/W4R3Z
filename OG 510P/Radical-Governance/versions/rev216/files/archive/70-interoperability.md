# Interoperability (How Scopes Plug Together)

**Purpose:** keep joins **few and humane** so multi-unit governance can be traced end-to-end **without forcing the person to be the courier or to perform institutional joins**.

Governance fails at boundaries. This memo defines a **small interface set** so polycentric systems can behave like one system *when needed*—without requiring a single “master database.”

**Design rule:** keep interfaces **few, stable, and joinable**. If you need more than ~10 join‑key families in an implementation, refactor: treat `70` as the canonical map and use “only‑if‑applicable” add‑ons (`96-archive-governance.md`).

**Degraded interop rule (assume uneven adoption):** in the real world, some registers exist and others don’t; some units comply and others don’t. Interfaces MUST degrade gracefully: treat joins as **optional** where possible, publish an interface coverage/health snapshot as `REL-INTF-COVERAGE-*`, and **do not deny service or remedy** solely because a join‑key or upstream register is missing (provide a manual bridge via receipt/reference numbers).

## Kernel anchors (do not repeat)
- Complexity budget / keep interfaces few: `96-...`.
- Person-held receipts are the privacy-preserving join; do not offload institutional routing: `98-persons-path-and-accessibility-invariants.md`.
- Records + publication integrity for versioned joins (“as-of”): `31-...`, `53-...`.
- Protective legibility (joinability for contestation, not surveillance): `99-protective-legibility-and-adoption-dynamics.md`.

## Named tensions (design must surface these)
- Joinability for accountability vs privacy/surveillance risk.
- Joinability as an infrastructure property vs justice as an outcome (do not treat joins as the terminal goal).
- Standardization for interoperability vs plural institutions and local fit.
- Interoperability ambition vs **uneven adoption** (missing registers, noncompliant units, degraded channels).
- Entity resolution/dedup benefits vs false merges that create harm.
- “Once-only” proof vs the right to contest and correct upstream records.

## Version semantics & “as‑of” queries (canonical)

Any versioned object keyed by a stable ID (`RULE-*`, `REL-*`, `SRV-*`, …) MUST be **append‑only**: publish a new revision; never silently overwrite.

Minimum per‑revision fields: `REV` (monotonic), `PUBLISHED-AT` (when the public could know), `PUBLISHED-BY` (issuer `Unit ID`), `EFFECTIVE-FROM`/`EFFECTIVE-TO` (when it governs), `SUPERSEDES` (prior revision), and a one‑screen `CHANGELOG` (what changed and why; link the authorizing `DRR-*` when a formal decision triggered the change).

**Point‑in‑time retrieval:** implementations MUST support “give me the revision in force at date *t*” and “give me the revision the public could know at date *t*” for any versioned object.

Systems MUST support two “as‑of” queries: **effective as‑of** (“what governed date *t*?”) and **publication as‑of** (“what could an auditor know as of *t*?”). If `EFFECTIVE-FROM` precedes `PUBLISHED-AT`, require an explicit justification and flag for oversight review.

---
## One-screen join-key map (the MVGS interfaces)

**Core cross-scope join keys (expected almost everywhere)**
- `Unit ID` — who can act / issue artifacts (authority map). Home: `34-competence-ledger-and-mandate-registry.md`.
- `EID` — who a private counterparty is (vendor/grantee/lobby entity) without inventing a new global ID. See `EID` section below.
- `RULE-*` — what rule/instrument is in force (versioned). Home: `39-rulebook-and-instruments-registry.md`.
- `STD-*` — what technical standard applies (pinned versions + transitions). Home: `27-standards-and-technical-governance.md`.
- `DRR-*` — why a decision happened (receipt/record with links). Home: `31-records-foi-and-government-memory.md`.
- `AL-*` — where to appeal / get urgent protection (redress lane). Home: `36-appeal-lanes-and-redress-registry.md`.
- `OFR-*` — which oversight finding/case is at issue (follow‑through). Home: `55-oversight-findings-and-response-register.md`.
- `REL-*` — which public release/measure is being relied on (published “official fact”). Home: `51-release-registry.md`.

**Domain add-ons (use only if relevant; keep Interfaces ≤10 families)**
- `SRV-*` (service journey), `PROG-*` / `EVAL-*` (program + evaluation): `47`, `28`.
- Money flows: `CON-*` / `OCID` (contracts) and `GRT-*` / `TEX-*` (grants/subsidies/tax expenditures): `38`, `49`.
- Coercion & emergency edges (where they exist): `ENF-*` and `EMR-*`: `43`, `45`.
- Assets & infrastructure: `AST-*`: `48`.
- Participation events: `ENG-*`: `41`.
- Automated systems: `ADS-*` / `MOD-*`: `42`.
- Access-to-information requests: `FOI-*`: `31`.


## EID (entity identity as a bundle, not a global ID)

`EID` is a **counterparty identity bundle** for organizations and entities (vendors, grantees, lobby entities, shell companies) used to make integrity joins feasible **without pretending there is a single trusted global entity registry**.

- `EID` SHOULD carry multiple identifiers/evidence (e.g., registry number + jurisdiction, LEI where available, tax ID where lawful, beneficial owner statement IDs, address/contacts) plus a **verification status** and `AS-OF` timestamps (`22-...`, `38-...`, `46-...`, `49-...`).
- Implementations SHOULD invest in **entity resolution** (dedup + linkage) proportional to capture/corruption risk: manual review, match confidence, and a contestable correction path. Do not “auto-merge” on weak signals—false merges create real harm (see `81-...`, `33-...`, `99-...`).
- `EID` joins MUST remain auditable: record what evidence justified a linkage and when it changed; publish aggregates safely where required, and keep sensitive fields governed under the privacy/secrecy posture (`33-...`, `77-...`).

**Known limitation:** cross-register joins may require entity resolution (dedup/matching). Invest in verification proportional to capture/corruption risk; do not pretend the join is automatic.

### Minimal `EID` bundle (portable)
- legal name + aliases
- jurisdiction of registration + registration number(s) (or local equivalent)
- legal form + status (active/dissolved)
- stable internal reference (for de-dup) + last verified date
- minimal contact channel for official notice (avoid personal data where possible)

### Beneficial ownership join pattern (optional, high value)
Where BO registries exist, link `EID` → BO artifact (or disclosure statement) with verification status, `AS-OF`, and a redaction posture for vulnerable persons (`77-...`).

Home: `38-contracting-and-procurement-register.md`, `49-grants-subsidies-and-tax-expenditures-register.md`, and the secrecy discipline in `77-...`.

---

## Artifact invariants (minimum fields all scopes should enforce)

Any joinable public artifact (`RULE/STD/DRR/REL/OFR/...`) SHOULD carry a minimal “join spine” so it can be traced across scopes:

- **ID** (stable), **issuer `Unit ID`**, **scope** (jurisdiction + program/service where relevant)
- **timestamps** (issued / effective / last-updated) and **version** (or hash)
- **basis links** (e.g., `DRR-*` links to `RULE-*`, `RC-*`, and `AL-*`; `REL-*` links to method note + source `DRR-*` where applicable)
- **publication integrity pointer** (tamper-evident log / point-in-time capture). Home: `53-publication-integrity-and-tamper-evident-logs.md`
- **privacy/redaction posture** for sensitive fields (do not centralize what can be verified locally). Home: `33-data-protection-and-personal-data-governance.md`, `77-sensitive-information-and-secrecy-governance.md`, `99-protective-legibility-and-adoption-dynamics.md`

---


## No person join-key (privacy by design)

The archive intentionally does **not** define a global person identifier.

- The affected person (or advocate) can integrate *their own narrative* by holding receipts (`DRR-*`) and lane pointers (`AL-*`) for verification/contestation (`98-persons-path-and-accessibility-invariants.md`).
- Institutions MUST NOT offload internal routing/handoffs onto the person (no “bring this paper to that office”; see `71-...` and `47-...`).
- Implementations SHOULD avoid default cross-service person linkage when a local, purpose-limited check suffices (`33-...`, `77-...`).
- Where longitudinal analysis is needed, prefer **aggregates** and consented/minimal linking—not default surveillance.

---

## Correction propagation (fix once; stop cascading errors)

- When a source record is corrected, downstream systems that relied on it SHOULD be notified and update within a deadline; publish exceptions.
- High-stakes correction receipts SHOULD name downstream notification/ack status so people aren’t told "fixed" while harms persist.

Home: `33-data-protection-and-personal-data-governance.md`, `44-identity-credential-and-eligibility-systems-register.md`, `98-persons-path-and-accessibility-invariants.md`.

---


## Why `DRR` is the keystone (decision receipts as capability tokens)

The archive’s theory of change is **legibility → contestation → accountability**. `DRR-*` is the smallest artifact that makes that real:
- it gives the affected person something to **hold**
- it gives oversight something to **aggregate**
- it gives implementers something to **debug**

**Keep DRR types small.** Prefer a compact set such as:
- `DRR-TYPE: SERVICE` (benefit/permit/eligibility/billing)
- `DRR-TYPE: ENFORCEMENT` (coercion/custody/sanctions-adjacent)
- `DRR-TYPE: EXCEPTION` (waiver/variance/emergency deviation)
- `DRR-TYPE: COMPETENCE` (mandate/boundary dispute ruling)
- `DRR-TYPE: INCIDENT` (serious incident / artifact-absence incident)

If you need finer distinctions, use `RC-*` (portable reason codes) and `AO-*` (appeal outcomes), not a proliferating DRR taxonomy (`52-reason-codes-registry.md`, ALR `36-...`).

**DRR taxonomy maintenance rule:** if `DRR-TYPE` grows beyond ~15 values (or minimum fields diverge significantly), start an RFC to split a subset into a new ID family while keeping backwards‑compatible links from `DRR-*` (see `96-...`).

---

## Boundary conflicts (when mandates overlap)

Overlaps are normal in polycentric systems; the failure is **unlogged conflict** that becomes informal domination.

Minimum discipline:
- disputes about “who decides” MUST produce a `DRR-TYPE: COMPETENCE` record and land in the competence ledger (`34`) with a cited rule basis (`RULE-*`) and an appeal lane (`AL-*`)
- where scope reassignment is considered, run the subsidiary test (`54-subsidiarity-and-scope-assignment-test.md`) and log changes (`35-transfer-register-and-conditionality.md`, `92-boundary-change-checklist.md`)

---

## Degraded mode (paper-first still interoperates)

Interoperability is not “digital.” In low-infrastructure contexts, the same join keys can be carried via:
- numbered paper receipts (`DRR-*`), posted rules (`RULE-*`), and public noticeboards/radio summaries (`REL-*`)
- mobile ombuds / traveling offices for `AL-*` access (`98-persons-path-and-accessibility-invariants.md`, `80-implementation-roadmap.md`)

The interface set is intentionally portable across implementation profiles.

