# 274 — CVR, ballot images, and public election-data release governance

**Track:** Shared  
**Status:** Draft (deployable patterns, jurisdiction-specific knobs)  
**Purpose:** Enable *auditable* transparency while preventing privacy leakage, harassment, or operational compromise.

This spec defines a **Data Release Governance (DRG)** pattern for publishing (or responding to records requests for) election data such as:
- **Cast Vote Records (CVRs)** (ballot-level, machine-interpreted selections),
- **ballot images** (scanned images of marked ballots),
- supporting exports (results, manifests, style catalogs, adjudication logs).

It is designed to compose with:
- **CommitLog / transparency logs** (`261`),
- **proof packaging (CPP)** (`265`),
- **public records / retention bounds** (`253`),
- **audit publication packs** (`260`),
- **ballot accounting & reconciliation** (`273`),
- **adjudication evidence surfaces** (`254`).

---

## Design constraints (non‑negotiable)

1. **No voter PII.** Do not publish anything that directly identifies a voter, or that can reasonably be joined to identify a voter.
2. **Prevent ballot secrecy leakage.** Ballot‑level releases can re-identify choices when combined with auxiliary data (small precincts, unique vote patterns, timestamped check-in, etc.).
3. **No operational targeting.** Avoid releasing details that increase the attack surface (facility topology, schedules, device identifiers that aid targeting, etc.).
4. **Publish digests before payloads.** Prefer **hash commitments + metadata + verification recipes** over raw datasets.
5. **Jurisdictional knobs are explicit.** Do not imply that one policy fits all states/localities.

---

## Threats & failure modes to actively defend against

- **Re-identification / vote-buying / coercion** from ballot-level releases (especially with ranked-choice, write-ins, or rare patterns).
- **Harassment / doxxing** of election workers enabled by excessive granularity.
- **Narrative manipulation** by cherry-picking or “forensic” overclaims based on misunderstood fields.
- **Operational compromise** via release of device serials, network details, or detailed facility procedures.
- **Integrity confusion** when datasets are released without provenance, versions, and change logs.

---

## The Data Release Governance (DRG) pattern

### DRG‑0: Data Release Posture Statement (DRPS)
A short, publishable statement that answers:
- what classes of election data may be released (and why),
- what is *never* released,
- what redaction / aggregation principles apply,
- the authoritative legal/jurisdictional references (via `262` JPSR pointers),
- the verification pathway (how the public checks integrity).

> **Publishable proof:** DRPS itself + CommitLog entry hash.

### DRG‑1: Data Release Request Capsule (DRRC)
For each release (proactive publication or PRR response):
- request scope (high-level),
- decision basis (cite-only; no long legal analysis),
- a **Release Plan**: what will be included, excluded, aggregated, delayed, or transformed.

> **Publishable proof:** DRRC + CommitLog entry hash.

### DRG‑2: Privacy Risk Screen (PRS)
A short risk screen that records:
- whether data is **ballot-level** vs **aggregated**,
- whether it includes rare-pattern fields (write-ins, RCV rankings, timestamps, batch IDs),
- the **minimum safe aggregation** level,
- whether **differential privacy** (or other formal privacy) is used,
- the “stop conditions” invoked (see below).

> **Publishable proof:** PRS summary + hash commitment to internal analysis notes (if any).

### DRG‑3: Provenance & Version Capsule (PVC)
For any dataset released:
- generator system class (scanner export, EMS export, audit tool export),
- software/config baseline reference (hashes via `256`, `265`, `261`),
- export timestamp window (coarse),
- schema version (e.g., NIST CVR CDF version),
- transformations applied (redactions, aggregation, DP parameters if applicable),
- **append-only corrections log** pointer (pairs with ENR corrections patterns in `252`).

> **Publishable proof:** PVC + file hashes + signature/timestamp.

### DRG‑4: Release Artifact Pack (RAP)
A minimal package layout:

- `README.md` (human: what this is / isn’t)
- `MANIFEST.sha256`
- `SIGNATURES/` (optional)
- `PVC.json` (canonicalized) + `PVC.sig` + `PVC.tsr` (timestamp) (optional)
- `DATA/` (only if release payload is approved)
- `TRANSFORMS/` (scripts or declarative rules, if safe to publish)

> **Publishable proof:** RAP hashes + signatures + inclusion proofs (if using a transparency log).

---

## Stop conditions (hard gates)

If any of these apply, default to **digest-only** publication and/or stronger aggregation:

- Ballot-level data that can be joined to **timestamps**, **pollbook logs**, **sequence numbers**, **batch IDs**, or **small geography**.
- Ballot images containing **write-ins**, distinctive marks, or metadata that materially increases re-identification risk.
- Any dataset that exposes **device serials**, operational schedules, or facility procedures beyond generic posture.
- Requests framed as **equipment access** or “full forensic imaging” without a security-controlled legal basis.
- Anything likely to enable **harassment, intimidation, or targeting**.

---

## Recommended default stances (tight and practical)

- Prefer **comparison audits** and publish **audit packs** (`260`) over publishing raw CVRs/ballot images.
- If publishing CVRs, publish with:
  - strong provenance (PVC),
  - **coarse geography** (or none),
  - removal/aggregation of rare-pattern fields,
  - a clear “misinterpretation hazards” section in `README.md`.
- Treat ballot images as **high-risk**; publish only with an explicit PRS, redaction/aggregation posture, and strong reason.

---

## Primary anchors (cite-first)

- **NIST SP 1500-103 (CVR CDF):** defines CVR common data format and interoperability context.  
  xref: nist_sp1500_103_cvr_pdf
- **NIST GCR 24-058 (CDF implementation guidance):** practical guidance for using CDFs (incl. CVR) across systems.  
  xref: nist_gcr_2024_24_058_nist_gcr_24_058
- **Bipartisan Policy Center (ballot images + CVRs public):** tradeoffs and implications for transparency vs privacy/ops burden.  
  xref: bpc_making_ballot_images_and_cast_vote_records_public
- **Science Advances (2025):** shows privacy risks from granular election data and ballot-level releases.  
  xref: science_doi_10_1126_sciadv_adt1512
- **Brennan Center (records/equipment access):** how to respond to access demands while protecting security.  
  xref: brennan_center_research_reports_responsibilities_officials_regarding_acc
- **EAC VVSG 2.0:** voting system requirements; includes voter privacy / secrecy principles context.  
  xref: eac_testingcertification_voluntary_voting_system_guidelines_version_2_0
