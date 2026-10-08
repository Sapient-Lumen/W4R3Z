# Mutual Recognition of Credentials, Licenses, and Status (Portable Proof Without Dossiers)

**Cross-stack note:** use `296-status-identity-portability-and-mobility-routing-guide.md` for the canonical route across the status / identity / portability / mobility cluster. This memo is the mutual-recognition specialization; `12` is the person-recognition front door; `125` is the civil-status / membership specialization; `109` is the portability / continuity specialization; `67` is the migration / border-status specialization; `158` is the family-unity neighbor; `287` is the digital-implementation family neighbor.

**Purpose:** let people use legitimate credentials across jurisdictions (education, work, mobility, benefits) **without** forcing repeated re‑proving, over‑disclosure, or capture by gatekeepers.

**Person served:** the person who moves (or works across borders) and is told “we don’t recognize that here”, losing access to work, services, or rights despite valid proof.

**From-below:** if recognition is denied, you get a **recognition denial receipt**, a **time-bound review**, a **human path**, and a **provisional access lane** when denial would cause severe harm.

**See also:** `160-digital-identity-credentials-privacy-utility.md` (wallet/claims basics), `109-portability-and-cross-jurisdiction-continuity.md` (continuity), `182-polycentric-governance-and-compacts.md` (compacts), `195-dispute-resolution-escalation-and-odr-rails.md` (no‑wrong‑door disputes), `68-education-and-skills-governance.md` (qualifications), `67-migration-and-mobility-governance.md` (status), `93-tax-and-revenue-administration.md` (cross‑jurisdiction identifiers).

---

## Core claim

Modern life requires a person to prove the same facts repeatedly:
- identity attributes (name, age, residency),
- qualifications (degrees, licenses),
- status (work authorization, disability determination, benefits eligibility),
- entitlements (insurance coverage, tax residency).

Without mutual recognition, systems drift toward:
- **re-proofing churn** (administrative burden as exclusion),
- **dossier inflation** (collecting far more than needed),
- **gatekeeper capture** (incumbents blocking entrants),
- **shadow markets** (forged documents and brokers).

**Goal:** recognition that is (1) *portable*, (2) *minimal‑disclosure*, (3) *contestable*, and (4) *revocable with due process*.

---

## Minimum viable architecture

### A. Mutual Recognition Compacts (MRC)
Recognition should be governed explicitly as a **compact** between issuers and relying parties.

Each compact defines:
- **scope:** which credential classes are covered (e.g., driver eligibility, nursing license, university degree, residency attestation).
- **schema + semantics:** what each claim means (avoid “same name, different meaning”).
- **assurance profile:** acceptable proofing/authentication levels (anchor to NIST identity guidance where relevant) [BIB-NIST-800-63-4].
- **verification method:** verifiable credentials / attestations (issuer-signed) and how revocation is checked [BIB-W3C-VC-DM-2-0].
- **privacy constraints:** minimal disclosure, purpose binding, pairwise identifiers, and relying-party governance (see `160`).
- **error + dispute rails:** clocked review, escalation, and cross‑jurisdiction dispute handling (`195`).
- **anti-capture rules:** no arbitrary local monopoly on recognition; transparent equivalency mappings.

### B. Evidence-first, dossier-last
Relying parties MUST prefer **cryptographically verifiable claims** (or equivalent signed attestations) over “submit your full file”.

- Ask for **one fact** where possible (e.g., *licensed to practice medicine in jurisdiction X*) not an education history.
- Support **selective disclosure** and **attribute-based proofs** (e.g., age ≥ 18).

Anchors: W3C Verifiable Credentials model [BIB-W3C-VC-DM-2-0]; modern digital identity assurance guidance [BIB-NIST-800-63-4].

### C. A recognition “fallback path” for the real world
Even good systems fail.

Every recognition process MUST include:
- **assisted/human path** (language/disability/low‑tech),
- **provisional recognition** when denial would cause severe harm (time‑boxed, with safeguards),
- **repair lane** for issuer mistakes (fast correction without starting over).

---

## Required artifacts (joinable)

### 1) Mutual Recognition Compact Register — `MRC-*`
A public register of:
- credential classes covered,
- participating issuers and relying-party classes,
- assurance profiles and required checks,
- change history (no silent tightening).

**Rule:** a jurisdiction can reject recognition only if it can point to a published `MRC-*` rule or a published exception.

### 2) Recognition Decision Receipt — `RDR-*`
When a person presents a credential and a decision is made (accept/reject/conditional), the system emits:
- credential class + issuer ID,
- claims requested (and justification),
- verification checks performed (and outcomes),
- decision + reason codes,
- next steps + deadlines + appeal lane (`AL-*`).

### 3) Equivalency Map — `EQM-*`
For each credential class, publish:
- equivalency rules (what counts as “same”),
- known non-equivalencies (with reasons),
- transition policies (grandfathering, bridging courses).

**Anti-capture requirement:** equivalency rules must be reviewable by independent bodies and affected professions/users.

### 4) Revocation + Suspension Feed — `REV-*`
Where revocation matters (licenses, status), publish a privacy-preserving revocation check mechanism:
- avoid global correlators;
- publish only what relying parties need to validate current standing.

(For mDL-style credentials, note the existence of standardized reader/issuer interfaces in ISO/IEC 18013-5.) [BIB-ISO-18013-5]

---

## Safety and abuse defenses

### S1. Coercion and forced presentation
Some contexts (domestic abuse, trafficking, coercive employers) require **non-disclosure-by-default**.

Systems SHOULD support:
- “safe mode” wallets (reduced disclosures),
- *in-person* alternative verification,
- limits on who can demand presentation,
- penalties for improper relying-party requests.

### S2. Discrimination and exclusion via equivalency
Equivalency maps can be weaponized to exclude outsiders.

Defenses:
- publish denial distributions and outcomes (audit for bias),
- require written justification for new non-equivalency,
- periodic review with minority docket rights.

### S3. Vendor lock-in
Compacts MUST require open interfaces and portability:
- people can change wallet providers (`160`),
- issuers can change vendors without breaking verifiers,
- schema changes are versioned with transition windows.

---

## Implementation notes (tight)

Start with one high-impact use case where denial causes major harm:
- professional license recognition,
- benefits eligibility across regions,
- student qualification recognition.

Ship in this order:
1) publish `EQM-*` and `MRC-*` (rules and scope),
2) add `RDR-*` receipts at decision time,
3) implement verifiable claims + revocation checks,
4) add cross‑scope dispute escalation (`195`) and audit loops (`183`).

---

## References (external anchors)

- NIST Digital Identity Guidelines (SP 800-63-4) [BIB-NIST-800-63-4].
- W3C Verifiable Credentials Data Model v2.0 [BIB-W3C-VC-DM-2-0].
- ISO/IEC 18013-5:2021 (mobile driving licence interfaces) [BIB-ISO-18013-5].
