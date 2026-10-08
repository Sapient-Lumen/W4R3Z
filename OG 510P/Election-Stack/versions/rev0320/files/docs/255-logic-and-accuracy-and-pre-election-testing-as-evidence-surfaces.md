# 255 — Logic & Accuracy (L&A) and pre-election testing as evidence surfaces

**Track:** Shared  
**Status:** Draft (operator‑usable, jurisdiction‑variable)  
**Last updated:** 2026-03-04

This note defines *minimal, publishable* evidence surfaces for **Logic & Accuracy (L&A)** testing and broader **pre-election testing** of election‑supporting technologies (EMS/ballot programming, e‑pollbooks, ballot‑on‑demand, ENR systems, etc.). The goal is to make “we tested it” **checkable** without leaking sensitive configuration details or producing data dumps.

## External anchors (cite-first; do not import large appendices)

- EAC **Complete Logic & Accuracy Testing Manual** (v1.4, revised 10‑2015): https://www.eac.gov/sites/default/files/eac_assets/1/28/Logic_and_Accuracy_Testing_Manual_Final_v1.4.pdf
- EAC **Logic & Accuracy Testing – Quick Start Guide**: https://www.eac.gov/sites/default/files/electionofficials/QuickStartGuides/Logic_and_Accuracy_Testing_EAC_Quick_Start_Guide_508.pdf
- EAC blog: **Guidance for Pre‑Election Testing on Election Supporting Technologies** (2025): https://www.eac.gov/blogs/new-eac-guidance-pre-election-testing-election-supporting-technologies
- CISA: **Best Practices for Securing Election Systems**: https://www.cisa.gov/best-practices-securing-election-systems
- (When relevant to your stack) EAC **VVSG 2.0** and **VVSG 2.0 Test Assertions**:  
  - https://www.eac.gov/sites/default/files/TestingCertification/Voluntary_Voting_System_Guidelines_Version_2_0.pdf  
  - https://www.eac.gov/sites/default/files/TestingCertification/VVSG%202.0%20Test%20Assertions%20v1.1.pdf

## Threats (what this surface is trying to prevent)

L&A / pre-election testing is one of the few moments where a jurisdiction can cheaply detect:
- **ballot definition errors** (contest mapping, rotation, language strings, layout),
- **scanner/mark‑sense interpretation failures** (calibration, timing marks, misreads),
- **tabulation/reporting defects** (aggregation logic, write‑in handling, over/under‑vote behavior),
- **configuration drift** between “tested” and “deployed”,
- and **procedure drift** (roles, chain‑of‑custody, observation, exception handling).

This spec *does not* try to standardize your L&A procedure. It standardizes what you can publish so third parties can verify that L&A occurred, was coherent, and matched the deployed configuration.

## Minimal publishable artifacts

### A. L&A Public Notice (LAN)

A one‑page announcement describing *when/where*, what components are covered, who may observe, and how challenges are recorded.

**Publishable fields (recommended):**
- jurisdiction + election identifier
- test scope (e.g., “precinct scanners, central count scanners, BMDs; ballot‑on‑demand; EMS programming checks; ENR pipeline checks”)
- observation rules (non‑interference; no photography of sensitive screens; no voter PII)
- contact channel for corrections

### B. L&A Test Deck Declaration (TDD)

A compact description of the test ballots/patterns, without dumping ballot images.

**Publishable fields:**
- deck identifier (e.g., `TDD-<election>-<date>-vX`)
- contest coverage statement (“every choice voted at least once; includes overvotes, undervotes, blanks, write‑ins per jurisdiction policy”)
- quantity statement (counts by ballot style / precinct grouping)
- hash list of the deck files (if digital) or hash of the scanned PDF packet used to print (if paper)

> **Anti-bloat rule:** publish **hashes + coverage statements**, not full decks.

### C. Expected Results Sheet (ERS)

A machine‑readable summary (CSV/JSON) of expected tallies for the deck.

**Publishable fields:**
- deck id
- expected totals by contest/option (and write‑in bucket handling if applicable)
- hash of the ERS file

### D. Configuration/Build Attestation (CBA)

A small attestation binding the tested build/config to the deployed build/config.

**Publishable fields:**
- system family + major/minor versions (no serials)
- ballot definition package id / EMS export id (hashed)
- device group identifiers (counts only: “247 precinct scanners, None BMDs …”)
- “sealed after test” statement + custody reference (see §E)

### E. Chain-of-Custody Pointer (CoC‑P)

A pointer to an internal custody ledger entry (do **not** publish serial numbers).

**Publishable fields:**
- custody event ids (opaque ids)
- custody roles (not names) and timestamps
- a redaction note (“device serials retained internally; available to authorized auditors”)

### F. Exceptions & Corrections Log (ECL)

An append‑only list of anomalies found during testing and how they were resolved.

**Publishable fields:**
- event id, date/time, component class (scanner/BMD/EMS/e‑pollbook/ENR)
- symptom code (reuse `SURFACE_ANOMALY_CODES.md` where possible)
- disposition (fixed / mitigated / accepted risk / deferred)
- linkage to a new hash of the corrected artifact (ballot definition package, etc.)

### G. L&A Results Snapshot Pack (LRSP)

A minimal bundle proving the run happened and matched ERS.

**Publishable fields:**
- snapshot id + timestamp + location label (non-sensitive)
- report hashes (results tapes / summary reports) **or** a hash of the exported results file
- “meets/does not meet ERS” boolean + delta summary (if not)

## Extended pre-election testing beyond classic L&A

Modern failures often occur in “supporting tech” layers (programming, check‑in, reporting). Keep the same publishable‑proof pattern:

- **EMS programming checks:** publish hashes for the ballot package + a short “ballot content verification checklist” attestation (no candidate data dumps).
- **E‑pollbooks:** publish a “sync + failover test attestation” and an exceptions log; do not publish voter records.
- **Ballot‑on‑demand:** publish calibration checklist hash + sample output verification statement; no ballot images.
- **ENR systems:** see `docs/252-election-night-reporting-and-unofficial-results-as-evidence-surfaces.md` (snapshots + corrections log).

## Stop conditions (dual-use / privacy / safety)

Do **not** publish:
- device serial numbers, seal numbers, or physical access procedures in detail,
- ballot images, tabulation databases, or EMS exports containing sensitive structure,
- voter registration records or any voter PII,
- step-by-step exploit or bypass instructions.

If a request demands these, route through `docs/253-public-records-requests-retention-and-access-bounds.md`.

## Integration points in this archive

- Ops custody + comms posture: `docs/247-ops-security-controls-comms-and-chain-of-custody.md`
- ENR snapshot/corrections patterns: `docs/252-election-night-reporting-and-unofficial-results-as-evidence-surfaces.md`
- Threat modeling ledger: `docs/249-threat-model-ledger-and-safe-red-teaming.md`
- Public capture/repro guidance: `docs/223-public-surface-capture-notes-and-reproducibility.md`
