# Identity, Credential, and Eligibility Systems Register (Make Access Gates Auditable)

**Purpose:** make access gates auditable without publishing identifiers—so exclusion/surveillance risks are bounded and correction/residual paths are visible.

Identity systems are not just “IT.” They are **access gates** for rights, services, mobility, and political voice. When the gate is opaque, exclusion becomes deniable; when the gate is over-joined, it becomes surveillance.

This memo defines a minimal **Identity & Credential Systems Register** keyed by stable `IDN` IDs, so identity proofing, credential issuance, and verification can be **audited, contested, and improved** without publishing personal identifiers.

**Limitation (EID/ID risk):** identity infrastructure is a high‑leverage tool that can exclude, surveil, or erase people. Designs SHOULD assume (a) some people cannot safely be legible, and (b) “one stable identifier for all life” is often politically and culturally contested. Prefer **purpose‑limited credentials**, avoid unnecessary cross‑system joining, and publish inclusion safeguards + error‑correction pathways (see `12-identity-and-recognition.md`, `33-data-protection-and-personal-data-governance.md`, and `77-sensitive-information-and-secrecy-governance.md`).


## Kernel anchors (do not repeat)
- **Recognition / identity politics:** `12-identity-and-recognition.md` (no AI-only gate; correction duties).
- **Person-facing invariants:** `98-persons-path-and-accessibility-invariants.md` (proof burdens; oral/assisted routes).
- **Data protection + correction:** `33-data-protection-and-personal-data-governance.md`.
- **Receipts + remedy:** `31-...` (DRR), `08-...` + ALR `36-...` (effective correction/appeal).
- **Protective legibility:** `99-protective-legibility-and-adoption-dynamics.md` (joinability can become surveillance).

## Named tensions (design must surface these)
- **Fraud control vs exclusion/dignity:** verification must not become a barrier to survival.
- **Joinability vs privacy:** eligibility joins can become targeting; publish limits and audit secondary use.
- **Standardization vs pluralism:** allow functional equivalents where they protect the governed.
- **Speed vs accuracy:** rapid determinations help; errors must have interim protection and fast correction.

## What `IDN` is (and is not)

- `IDN-*` identifies a **system/process**, not a person.
- `IDN-*` entries are about: identity proofing, credential types, trust frameworks, verification, revocation, and inclusion safeguards.
- Individual determinations remain **`DRR` receipts** (and appeals in `ALR`), with legal basis in `RULE` (as-of). (`08-...`, `39-...`, `36-...`)

## Minimal public register (IDN)

Each jurisdiction publishes an `IDN` register as part of the competence ledger ecosystem (`34-...`, `70-...`). Keep it small; every field must pay rent.

**Required fields**
- `IDN` (stable ID) + `UNIT` owner
- **Scope & purpose:** what decisions/services this gate controls (link to `PROG-*` / `PAR-*` when applicable)
- **Credential types supported:** what can be presented (e.g., CRVS record, physical credential, digital credential)
- **Proofing + assurance:** the stated assurance / proofing expectations (reference a published standard or local profile)
- **Assurance tiers in use:** which transactions require which assurance tier(s) (reference NIST IAL/AAL/FAL or a published local profile); include participation/voting where relevant.
- **Inclusion safeguards:** alternative enrollment paths, fee waivers, offline options, and exception handling
- **Residual / “no category fit” path:** what happens when a person’s situation does not match available categories; MUST route to authorized human adjudication (and emit a `DRR-*` with reasons + `AL-*` lane), not an algorithmic dead-end (see `47-...` and `98-persons-path-and-accessibility-invariants.md`).
- **Error correction:** correction path + deadlines; who can amend; audit log existence (link to `AL-*` lane); and (where feasible) how corrections propagate + what downstream systems are notified
- **Privacy & security:** link to `DPR-*` processing entry; retention; sharing rules; breach notification lane
- **Interoperability:** standards/protocols supported (e.g., VC, OIDC, etc.); constraints on cross-domain linking
- **Governance & procurement:** who governs; vendor/contract links (`CON-*`) and exit/portability provisions
- **Change log:** versioning and deprecations (retired IDs stay retired)

**Optional fields**
- independent evaluation / audit commitments (`EVAL-*` / `OFR-*`)
- revocation/credential status endpoints (if relevant)
- cross-boundary recognition agreements (`CMP-*`) and their constraints

## Join rules (how `IDN` connects to the rest of the archive)

1) **Any denial or restriction due to identity/eligibility MUST be contestable.**
   - The receipt (`DRR`) MUST cite: `RULE` basis (as-of), `AL-*` lane, and the relevant `IDN-*` gate used for proofing/verification.
   - If automation materially influenced the determination, also cite `ADS-*` / `MOD-*`. (`42-...`)
   - If an `ENG-*` participation process relies on identity/eligibility, the response `DRR` SHOULD cite the relevant `IDN-*` gate so contestation can target the gate (not just the outcome).

2) **Identity gates MUST not become stealth surveillance.**
   - `IDN` entries MUST declare prohibited joins (e.g., “no location tracking,” “no non-consensual cross-service correlation”).
   - Cross-boundary recognition SHOULD prefer *verifiable claims* over centralized databases where feasible, and SHOULD be governed by explicit compacts (`CMP-*`). (`19-...`, `70-...`)

3) **Procurement and funding must be legible.**
   - Identity systems and major upgrades MUST link the procurement process (`CON-*`) and any conditional transfers (`TRF-*`). (`38-...`, `35-...`)

## High-risk defaults (do-no-harm)

- **No irreversible harms without remedy:** if an identity failure blocks essential services, provide a time-limited fallback path pending correction/appeal.
- **No “category mismatch” dead‑ends:** category edge cases MUST have an escalation path to a person with authority to exercise judgment; treat repeated category-mismatch denials as a design defect and feed into category review.
- **No exclusion-by-default:** if documentation is missing, the system MUST offer alternative evidence paths and publish denial disparity audits.
- **Separation from enforcement:** identity infrastructure MUST not be repurposed for generalized policing or surveillance; any exception requires explicit legal basis + oversight finding. (Tie to `ENF-*` where coercion occurs.) (`43-...`, `05-...`)

## Metric hooks (use pack IDs; keep ≤10)
- **[IPM-18] Identity gate integrity:** coverage, denial disparities, correction time, fallback availability, and the share of denials attributable to **category mismatch / no-fit** (as a signal of broken categories).
- Also relevant: [LRR-3] [LRR-4] [DAG-6]

## Anchors
- NIST Digital Identity Guidelines (SP 800-63-4, Rev. 4) [BIB-NIST-800-63-4].
- OECD Recommendation on the Governance of Digital Identity [BIB-OECD-DIGID-REC].
- W3C Verifiable Credentials Data Model v2.0 [BIB-W3C-VC2] (when digital credentials are used).

## Person’s Path requirements (identity as the hardest gate)
Identity gates produce the sharpest `98` failure modes: **proof**, **error**, and **fear**. Treat accessibility as a design constraint, not an “outreach” add-on.

**Add these checks to every `IDN-*`:**
- **Comprehension-tested notices:** enrollment denials, revocations, and failed verifications MUST be understandable (plain language + translation), and MUST say *what to do next* (documents, alternatives, assistance), not just “ineligible.”
- **No-wrong-door + assisted navigation:** enrollment points and service counters SHOULD route identity problems to the correct lane (and help assemble evidence) rather than bouncing people between agencies.
- **Safe representation:** where filing can increase risk (domestic violence, policing, immigration, disability), support proxy/advocate flows and confidential channels; “must appear in person” SHOULD be exceptional and justified.
- **Offline-first fallback:** ensure low-tech alternatives (paper/phone/community verifier) exist for essential services when digital infrastructure fails or is unsafe.
