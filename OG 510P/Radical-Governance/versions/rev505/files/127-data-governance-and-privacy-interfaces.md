# Data Governance & Privacy Interfaces (Purpose, Access, Sharing)

**Stack relation:** use `301-digital-governance-data-interoperability-and-algorithmic-assurance-routing-guide.md` for the canonical route across the digital-governance / data / interoperability / algorithmic-assurance family. This memo is the data-rights / purpose-limitation / sharing-interface front door; `06` is the broad digital-public-systems front door; `128` is seam / interoperability / conformance governance; `152` is the ex ante public-AI-governance front door; `33` remains the broader privacy / due-process neighbor.

**Purpose:** make personal-data power **legible, bounded, and contestable** across agencies, vendors, and automation—without requiring “trust us.”

**Person served:** a person whose life is shaped by data decisions (eligibility, enforcement, profiling, risk flags) and who needs to know **what data exists, why, who used it, and how to challenge misuse**.

**From-below:** this memo turns opaque “data handling” into **receipts + clocks + appeal lanes** that a person (or advocate) can use.

**Scope:** applies to any public body (or delegated provider) that collects, uses, shares, or retains personal data, including algorithmic assistance.

---

## Core idea
Treat data handling as **governance interfaces** that must emit **receipts** and attach to **remedy**.

A data system is compliant only if a person can:
1) discover *what* data exists about them (or about a decision that affected them),
2) see *why* it exists and *who* used/shared it,
3) contest misuse/misclassification, and
4) get a bounded-time correction or protection.

---

## Minimal artifacts (portable)

### 1) Data Asset Card (`DATA-*`)
For every dataset/system containing personal data (including vendor systems), publish or maintain a discoverable **Data Asset Card**:
- **DATA-ID** (stable), steward/owner, operator (incl. vendor), scope/jurisdiction.
- **Purpose(s)** (enumerated, bounded) + **legal basis**.
- **Data categories** (plain language) + collection sources.
- **Decision coupling:** which decisions use it (link to `PROG-*`, `RULE-*`, `ADR-*` where relevant).
- **Retention** + deletion cadence; archive/transfer rules.
- **Sharing map:** allowed recipients + join-keys; emergency exceptions.
- **Sensitivity tier** and protective legibility constraints (`99`, `77`).

**MUST:** purposes are bounded; “general government use” is not a purpose.

### 2) Purpose Declaration Receipt (`PDR-*`)
Any *material* use of personal data for a decision or enforcement posture MUST emit a **Purpose Declaration Receipt** joinable to the Decision Receipt (`DRR-*`):
- DATA-ID(s) used
- purpose code
- rule / policy basis (Rule ID where possible)
- whether automated assistance occurred (link to `ADR-*` if applicable)

### 3) Access Log Receipt (`ALR-*`)
Any access to personal data by staff or system MUST be logged with a retrievable record:
- who/what (role/service account)
- when
- DATA-ID
- purpose code
- case/ticket/join key
- whether exported/copied

**MUST:** the person can request a **bounded view** of ALR entries relevant to them, subject to safety constraints (e.g., active investigations) with a withholding receipt (`WHR-*`) and review lane.

### 4) Sharing Receipt (`SHR-*`)
Any transfer of personal data across boundaries (agency→agency, agency→vendor, vendor→subvendor, cross-border) MUST emit a Sharing Receipt:
- sender/recipient identities
- DATA-ID(s) and fields/categories shared
- purpose + legal basis
- retention/deletion obligations downstream
- onward-sharing prohibition or map
- dispute/incident contact + remedy lane

**MUST:** sharing defaults to **minimum necessary fields** and MUST include a purpose-limited contract term when delegated (`38`, `78`).

### 5) Correction & status protection (`COR-*`)
A person MUST have a reachable path to:
- correct factual errors,
- contest derived flags/scores, and
- obtain interim protection where the data issue risks deprivation (benefits, liberty, housing, safety).

**MUST:** decisions relying on disputed data must disclose the dispute status and provide a fast lane (`AL-*`) where delay would be irreparable (`108`, `08`).

---

## Guardrails (non-negotiables)

### Purpose limitation & non-reset transfers
- **MUST:** purposes are enumerated; new purposes require change control (`118`) and, where material, a future-impact review (`122`).
- **MUST:** when cases transfer across jurisdictions, evidence/data MUST NOT “reset” (non-reset rule), and essential services must have provisional continuity (`109`, `114`, `125`).

### Delegation & vendor control
- **MUST:** delegated processing requires a contract-visible purpose map + audit rights + incident notification clocks (`38`, `105`).
- **MUST:** subprocessing/onward transfers require `SHR-*` and are discoverable.

### Safety / protective legibility
- **MUST:** publication of cards/logs uses protective legibility (avoid doxxing/target lists) (`99`, `77`).
- **MUST:** refusal/withholding requires a withholding receipt + review lane; secrecy is not a silent default.

---

## Minimal metrics (publishable)
- % of person-impacting decisions that include `PDR-*` joinable to `DRR-*`.
- median time to correction (`COR-*`) and to ALR disclosure.
- # of `SHR-*` transfers by purpose; % with minimum-necessary-field certification.
- incident rate: unauthorized access / sharing; median time to containment + notice.

---

## Composition pointers
- Pair with `115-information-integrity-and-record-interfaces.md` (stable pointers + disclosure clocks + ADR).
- Pair with `120-conflicts-of-interest-and-influence-integrity.md` when data access overlaps with lobbying/capture.
- Pair with `125-identity-membership-and-civil-status.md` when data controls membership/status.

---

## Reference anchors (see bibliography)
- Privacy/data protection baseline: [BIB-COE-108PLUS], [BIB-GDPR].
- Government privacy guidance: [BIB-OECD-PRIVACY-2013].
- Operational privacy engineering: [BIB-NIST-PRIVACY-FRAMEWORK].
