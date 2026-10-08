# Results pipeline end-to-end (tabulation → public reporting → evidence)

**Track:** A (Deployable core)


> **Goal:** make Election Night Reporting (ENR) and all downstream public numbers **cryptographically attributable**, **internally consistent**, and **replayable** from published artifacts — while clearly separating **unofficial** from **certified** results.

This document specifies the **results pipeline** as a first-class security boundary. Attackers often prefer to compromise ENR (or its data feed) because it can create legitimacy crises without touching ballots.

## Non-negotiable invariants
1. **No silent divergence:** UI, API, and downloadable data must be derived from the *same* signed canonical object.
2. **Unambiguous official parameters:** every results object must bind to the election’s `ElectionParameterBundle` (EPB), including `bd_hash`, `disclosure_policy_hash`, and `crypto_policy_hash`.
3. **Replayability:** any observer can recompute every published number from the signed artifacts.
4. **Fail loud:** if an artifact is missing, unverifiable, or violates policy, public UIs must degrade to “UNVERIFIED / PARTIAL / DELAYED,” not show “confident” totals.
5. **Software independence preserved:** certified results and outcome disputes MUST have a paper/audit recovery path (see `09-audit-recovery.md`).

## Canonical data formats (recommended)
Use NIST Voting Common Data Formats for interoperability:
- **Cast Vote Records (CVR):** used for audits and comparisons. (`source: nist_sp1500_103_cvr_pdf`)
- **Election Results Reporting (ERR):** NIST SP 1500-100r2. (`source: nist_sp1500_100r2_err_pdf`)
- **Election Event Logging (EEL):** NIST SP 1500-101. (`source: nist_sp1500_101_eel_pdf`)

**If you do not use these formats**, you MUST provide an equivalent canonical schema + mapping manifest.

## Pipeline roles
- **Tabulation exporter**: produces signed tabulation outputs (CVR bundles or contest totals)
- **Results compiler**: converts exports into canonical `ERR` objects + produces ENR view objects
- **ENR publisher**: renders public UIs/APIs from the canonical `ERR`
- **Witnesses/monitors**: verify, diff, and co-sign checkpoints; produce alerts

## Pipeline objects

### A) Canonical Results Object (CRO)
The **single source of truth** for public reporting.

CRO MUST include:
- `election_id`, `epb_hash`
- `reporting_time` (informational)
- `results_format` (e.g., `NIST-ERR-1500-100r2`)
- `counts_status` / `report_detail_level` (where applicable)
- `reporting_units[]` and contest totals
- **content hash** computed over canonical bytes (see RFC 8785 for JSON canonicalization). (`source: rfc8785_txt`)

### B) ENR View Object (EVO)
A minimal object derived *only* from CRO (never hand-edited) for web rendering and APIs.

EVO MUST include:
- `cro_hash`
- `unofficial=true`
- user-facing context strings (“unofficial; subject to canvass/certification”)

### C) ResultsReleasePackage (RRP)
A content-addressed evidence bundle published at each reporting interval.

RRP MUST contain:
- `CRO` (ERR CDF JSON or XML)
- `EVO`
- `ENRUpdate` (see schema) describing delta from previous RRP
- `signatures/`:
  - signer certificate chain / public keys
  - signatures over CRO and RRP manifest
- `pbb_anchor`:
  - Merkle inclusion proof anchoring the RRP manifest hash into the PBB log
  - witness cosignatures for the checkpointed STH
- `provenance`:
  - exporter/compilers build identifiers
  - source input hashes (CVR bundle hash, device export hashes)
- `policy`:
  - `DisclosurePolicy` hash + a machine-checkable compliance report

## Normative pipeline flow

### Step 0: Pre-commit the “rules of reporting”
Before polls open:
- Publish and checkpoint EPB (includes BD hash + DisclosurePolicy hash).
- Publish a **Results API contract** (endpoints + fields + semantics), content-addressed and pinned.

### Step 1: Export tabulation inputs
- Exporter produces:
  - either `CVRBundle` (preferred for audits) or
  - `ContestTotalsBundle` + export logs
- Exporter signs export, produces `ExportAttestation` containing input IDs, output hash, device ID.

### Step 2: Compile CRO
- Results compiler ingests the exporter bundle(s), produces CRO in canonical format.
- Compiler produces `CompileAttestation` binding inputs → CRO hash.

### Step 3: Produce EVO + ENRUpdate
- EVO derived from CRO.
- ENRUpdate describes:
  - `prev_cro_hash`, `cro_hash`
  - delta metrics (new precincts reporting, ballot types added)
  - human explanation fields

### Step 4: Package + sign RRP
- Create `ResultsReleasePackage` with manifest hash.
- Sign CRO + manifest under a dedicated results-reporting key (NOT the tally key).

### Step 5: Anchor to PBB + witness checkpoint
- Submit manifest hash into PBB as a non-ballot log entry type.
- Require witness cosigning of STH checkpoints on a fixed cadence (e.g., every 2 minutes).

### Step 6: Publish
- ENR website, API, and downloads MUST be rendered from the CRO contained in the most recent **FINAL** checkpointed RRP.
- If the checkpoint is missing, UI MUST display a prominent “UNVERIFIED / DELAYED” state.

## Required monitors
Monitors MUST:
- validate signatures, inclusion proofs, and DisclosurePolicy compliance
- verify monotonicity constraints (counts do not decrease unless explicitly flagged)
- detect endpoint drift (UI/API mismatch, locale-specific mismatch)
- publish signed `DriftAlert` objects anchored into PBB

See `69-enr-drift-detection-and-alerting.md`.