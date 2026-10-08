# 269 — Voter registration and list maintenance as evidence surfaces (VRDB integrity without PII dumps)

This module treats **voter registration databases (VRDBs)** and **list maintenance** as integrity-critical infrastructure while keeping the archive *privacy-first* and *anti-weaponization*.

It provides **publishable evidence surfaces** that help observers and auditors answer:

- Are registration systems operated with **integrity, availability, and confidentiality** expectations appropriate for election infrastructure?
- Is list maintenance performed **lawfully**, **consistently**, and with **bounded error**, without enabling targeted harassment or mass-challenge abuse?
- Are there stable ways to reconcile “what changed, when, and why” **without** publishing voter files?

Primary anchors (cite-first, do not import bulk):
- EAC: *Best Practices: Voter List Maintenance* (Mar 2023). https://www.eac.gov/sites/default/files/electionofficials/VoterList/Best_Practices_Voter_List_Maintenance_V1_508.pdf
- DOJ Civil Rights Division: *NVRA List Maintenance Guidance* (Sep 2024). https://www.justice.gov/crt/nvra-list-maintenance-guidance
- U.S. Code (NVRA §8): 52 U.S.C. § 20507. https://uscode.house.gov/view.xhtml?req=%28title%3A52+section%3A20507+edition%3Aprelim%29
- NIST: *Security of Voter Registration Databases* (VRDB security considerations). https://www.nist.gov/itl/voting/security-voter-registration-databases
- CISA: *Best Practices for Securing Election Systems* (enterprise/network posture for election infrastructure). https://www.cisa.gov/best-practices-securing-election-systems

---

## Design constraints

### Non-goals
- This module does **not** define who is eligible to vote, adjudicate residency, or specify state-by-state procedures.
- This module does **not** publish or request voter files, “full roll” exports, precinct/style mapping, or any PII.

### Hard stop conditions (do not proceed)
If a proposed artifact would:
- expose voter **names/addresses/DOB/IDs**, or allow re-identification by joining with public data,
- enable intimidation, targeted challenges, or harassment,
- provide detailed system configuration, network topology, or operational playbooks that materially increase attack capability,

…then it must **not** be included or published. Redirect to aggregate-only digests and policy declarations.

---

## Evidence surfaces

### 1) Voter Registration System Posture Statement (VR-SPS)
A short public statement, *bounded to what is safe to publish*, that:
- identifies the **system class** (state VRDB, county front-end, or integrated platform),
- states the **security objectives** (CIA) and administrative owner(s),
- states the **backup/restore posture** and “known outage” escalation contacts,
- points to the relevant **policy surfaces** in the JPSR (see `docs/262-*`).

**Publish:** text + a hash commitment to the internal “VRDB operations SOP” (CPP; see `docs/265-*`).

---

### 2) List Maintenance Policy Declaration (LMPD)
A public declaration of *policy posture* and authoritative references, including:
- legal anchor(s) used by the jurisdiction (e.g., NVRA §20507 and state law),
- high-level process description (sources, notice/cure steps if applicable),
- timing constraints (e.g., safeguards around federal election windows),
- error-handling posture (how false positives are minimized and remediated).

**Publish:** declaration + citation pointers, not case details.

---

### 3) Registration Change Ledger Digest (RCLD)
An **append-only**, periodic digest of changes to the registration record set, with:
- reporting period + jurisdiction,
- counts of adds/updates/inactivations/removals,
- coarse reason categories (move, death record match, felony status, voter request, undeliverable notice, etc. — jurisdiction-defined),
- a hash of the full internal ledger for that period.

This is the VRDB analogue of the ENR “corrections log” pattern: you can see *what changed and why, in aggregate*.

**Publish:** counts + reason-code dictionary + hash commitment.

---

### 4) List Maintenance Report Digest (LMRD)
A public, periodic report digest that includes:
- a compact “what we did” summary,
- the dataset sources used at a coarse level (e.g., NCOA, state DMVs, vital records; as applicable),
- QA checks performed (duplicate detection, sampling, back-out plan),
- a “known issues” section with remediations.

**Publish:** digest + hash commitment to the internal detailed report.

---

### 5) Access & Audit Log Digest (AALD)
A privacy-first, non-operational digest of access logging posture:
- confirmation that privileged access is logged and reviewed,
- periodic **review counts** (how many privileged accounts, how many changes reviewed),
- exception counts (break-glass events, emergency access).

**Publish:** counts + review cadence; do not publish account identifiers, schedules, or system topology.

---

## Composition with the rest of the archive

- **JPSR tie-in:** Add VRDB policy knobs (e.g., list maintenance cadence, notice method, challenge process) as entries in `docs/262-*` without state-by-state tables.
- **CPP tie-in:** Use canonicalization + signing + timestamping (see `docs/265-*`) for digests and declarations.
- **PRR tie-in:** Route “give us the voter file / full change logs” demands to `docs/253-*` (public records bounds + retention) and publish aggregate digests instead.
- **Threat model tie-in:** Put VRDB risks in the Threat Model Ledger (`docs/249-*`) at non-operational level (ransomware, unauthorized changes, availability attacks, data exfil).

---

## Minimal templates (one page each)

**VR-SPS**
- Jurisdiction:
- System class:
- Owner:
- Security objectives (CIA):
- Backup/restore posture:
- Logging posture:
- Public verification surfaces (CommitLog/CLE pointer):
- Hash commitment(s):

**RCLD**
- Period:
- Adds:
- Updates:
- Inactivations:
- Removals:
- Reason-code dictionary version:
- Hash commitment:
- Signature/timestamp reference:

**LMRD**
- Period:
- Process summary:
- Data sources (coarse):
- QA + rollback posture:
- Known issues + remediations:
- Hash commitment:
