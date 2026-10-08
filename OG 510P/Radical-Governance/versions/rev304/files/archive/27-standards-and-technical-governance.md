# Standards & Technical Governance (The Hidden Layer Between “Policy” and Reality)

**Purpose:** govern standards as power (who sets them, who benefits) and keep them contestable and update-disciplined.
**Person served:** someone affected by technical standards (safety, utilities, digital) who needs standard‑setting to be accountable, reviewable, and open to challenge.

**From-below:** This exposes the technical layer that shapes your life so standards don’t become unaccountable policy in disguise.

**EXP pointer:** counters `EXP-01` (Opacity) and `EXP-07` (Indifference) by making technical rules/standards legible, contestable, and tied to remedy (see `98-persons-path-and-accessibility-invariants.md`).

In practice, many “rules” are implemented as **technical standards** (protocols, data schemas, safety tests, audit formats, interoperability profiles).  
Across scopes (municipal → national → global), standards can become *de facto law* when:
- procurement requires them,
- regulators incorporate them by reference,
- platforms or infrastructure rely on them for access and compliance.

This memo defines a small reusable primitive: **Minimum Viable Standards Governance (MVSG)** plus a **Public Standards Register (PSR)** that makes standards *legible*, contestable, and compatible with the archive’s rule/evidence interfaces.

---

## Kernel anchors (do not repeat)
- **Person-facing invariants:** `98-persons-path-and-accessibility-invariants.md` (no AI/digital-only gates; oral/assisted options; safety).
- **Remedy is part of the interface:** `08-remedy-and-grievance.md`, `36-appeal-lanes-and-redress-registry.md` (contestability; time bounds; functional equivalents).
- **Protective legibility (transparency ≠ safety):** `99-protective-legibility-and-adoption-dynamics.md`.
- **Records + publication integrity:** `31-records-foi-and-government-memory.md`, `51-release-registry.md`.
- **Interoperability contracts:** `70-interoperability.md`, `71-interface-obligations-by-scope.md`.
- **Digital/AI governance:** `06-digital-and-algorithmic-governance.md`.

## Named tensions (design must surface these)
- **Standardization vs innovation:** stability for users vs experimentation.
- **Expert capture vs public contestation:** committee governance vs democratic legitimacy.
- **Openness vs security:** transparent specs vs abuse/attack surface.
- **Interoperability vs lock-in:** open interfaces vs vendor dependence (`22-...`).

## A. Failure modes (what goes wrong)

1) **Invisible rulemaking:** binding standards appear via procurement or “guidance”, bypassing public rulemaking.  
2) **Paywalled law:** incorporated standards are inaccessible (rights cannot be exercised).  
3) **Capture by vendors or incumbents:** committees become market-access chokepoints.  
4) **IP/royalty traps:** licensing blocks implementation or creates monopolies.  
5) **Standards drift:** revisions change obligations without clear transition, causing “silent compliance changes”.  
6) **Fragmentation:** competing profiles create interoperability failure and safety gaps.  
7) **Security debt:** old standards persist because replacement is disruptive and politically hard.

---

## B. Minimum Viable Standards Governance (MVSG)

### 1) Decision boundary: when a standard is “governance”
A standard MUST be treated as governance (and enter the PSR) when any of these are true:
- it is **required** for access to a public service, market, license, benefit, or infrastructure,
- it is referenced in **procurement** for essential services,
- it is incorporated by reference into a binding norm in the PRR (`39-...`),
- it materially affects **rights, safety, or eligibility**.

### 2) Openness + balance (anti-capture baseline)
For any standard treated as governance:
- **Open process:** public drafts, issue tracker (or equivalent), published change log.  
- **Balanced participation:** disclose materially affected constituencies; document outreach; prevent “single vendor stack”.  
- **Community representation (when applicable):** if a standard materially affects a defined community (geographic, indigenous, occupational) or frontline access to essential services, the process SHOULD include representatives nominated/recognized by that community and provide accessible participation (language, disability, time).
- **Conflict disclosure:** committee members disclose relevant financial ties; recusals for direct procurement conflicts.  
- **Appeals path:** a light, time-bounded appeal route for process violations or disproportionate burdens.

Anchors: IETF’s open process norms (RFC 2026) and W3C’s Process Document emphasize public review, consensus building, and documented transitions between maturity stages.  
- RFC 2026 (IETF standards process): [BIB-IETF-RFC2026]  
- W3C Process (2025): [BIB-W3C-PROCESS-2025]  
- W3C doc types + revision model: [BIB-W3C-STANDARDS-TYPES]

### 3) IP and implementability (no royalty traps by default)
- **Default:** the standard SHOULD be implementable by multiple parties without discriminatory barriers.
- If licensing commitments exist, the PSR entry MUST state: licensing model, patent disclosure mechanism, and implementer obligations.
- Prefer “open standards” principles (due process, broad consensus, transparency, balance, openness, and implementer-friendly terms).
Anchors: OpenStand principles and IETF’s affirmation (RFC 6852).  
- OpenStand principles: [BIB-OPENSTAND]  
- RFC 6852 (affirmation of OpenStand): [BIB-IETF-RFC6852]

### 3b) International baseline principles (useful even outside trade)
Many regimes borrow a shared vocabulary for “good” standards processes: transparency, openness, impartiality/consensus, effectiveness/relevance, coherence, and attention to development constraints.
- WTO TBT Committee: principles for international standards: [BIB-WTO-TBT-PRINCIPLES]
- WTO TBT Agreement Annex 3 (Code of Good Practice): [BIB-WTO-TBT-LEGAL]

### 4) Conformance: standards without tests are aspirational
A governance-grade standard MUST have:
- a **conformance statement** (what it means to comply),
- a **test suite** or validation method, or a plan + timeline for one,
- a minimal “profile” mechanism for interoperability (avoid N variants).

### 5) Versioning + transitions (no silent compliance changes)
- Every adoption MUST specify a **version pin** and an **effective date**.
- Major changes MUST include a **transition plan** (overlap window, deprecation date, backward-compatibility notes).
- Emergency updates are allowed, but MUST be logged as emergency measures (`23-...`) if they change rights/safety obligations.

### 6) Incorporation by reference (avoid “paywalled law”)
If a public authority incorporates a standard by reference:
- the referenced version MUST be **freely accessible** (or a legally equivalent public access mechanism),
- the authority MUST publish a **plain-language compliance summary** for affected users,
  - the summary MUST pass the comprehension test under `98-persons-path-and-accessibility-invariants.md` (what changed, who is affected, what to do next, by when) and include a discoverable remedy lane (`AL-*`) plus an offline contact path.
- the incorporation MUST appear in the PRR with a Rule ID (`25-...`) that points to the PSR entry.

---

## C. Public Standards Register (PSR) — minimum schema

The PSR is the standards analogue of the PRR and PDRR.

| Field | Meaning |
|---|---|
| Standard ID (`STD-*`) | stable identifier (e.g., `UNITID-STD-SEQ`) |
| Title + scope | what the standard covers; what it does *not* cover |
| Origin | SDO/body (IETF/W3C/ISO/IEC/etc) or local committee |
| Governance status | informative / recommended / required / incorporated / procurement-required |
| Version pin | version/date; maturity status if applicable |
| Conformance | compliance statement + test/validator link |
| Licensing/IP | implementer obligations + disclosure mechanism |
| Transition | deprecation/overlap window + effective dates |
| Affected domains | safety, rights, eligibility, infrastructure |
| Linkages | related Rule IDs (PRR), data Release IDs (PDRR), ADS entries (ADS register) |
| Appeal/issue route | where to raise issues + escalation path |

**MVSG rule:** any “required” or “incorporated” standard MUST have a PSR entry.

---

## D. Interface hooks (how this plugs into the archive)

- **Legal legibility:** PRR Rule IDs MUST reference PSR `STD-*` IDs when incorporating by reference.
- **Interoperability:** standards used as system interfaces SHOULD be referenced as `STD-*` IDs (not vague prose).
- **Digital governance:** ADS and public digital rails SHOULD prefer PSR-tracked standards and publish profiles.
- **Evidence:** data-method standards (schemas, metadata rules) should be PSR-tracked and referenced from Release IDs (`26-...`).

---

## E. Minimal metrics (use existing packs; avoid new ones)

Suggested choices (≤6 total for standards-heavy scopes):
- **[REG-1]** Rulemaking openness (treat governance-grade standards as “major rules” for openness accounting).
- **[REG-2]** Review discipline (standards pins + deprecation on time).
- **[DAG-1]** ADS register coverage (if standards affect ADS inputs/outputs).
- **[CAD-2]** Service reliability / delivery (where standards affect service uptime or correctness).
- **[LRR-5]** Reasons & explainability coverage (if standards shape eligibility decisions).

---

## F. Cross-scope implications (small)

- **Municipal/Regional:** PSR matters most for procurement-bound standards (utilities, transit, housing, permitting).
- **National:** treat incorporated standards as binding norms; prohibit paywalled law; set baseline licensing/appeals rules.
- **Supranational/Global:** standards bodies are major governance venues; insist on openness, balance, and transition discipline as preconditions for mutual recognition.

### Standards note: machine-readable law & rule registers
- If publishing enforceable norms, consider open, interoperable legal-document standards (Akoma Ntoso / LegalDocML) for interchange and tooling; see [BIB-OASIS-AKN-2018] and [BIB-OASIS-LEGALDOCML].
- If exposing PRR via API, publish stable OpenAPI docs (example reference: [BIB-UK-LEGIS-OPENAPI]).
