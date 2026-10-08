# 196 — Core glossary and terms of art

**Track:** Shared

This glossary defines **project-local meanings** of a small set of recurring terms.
It is intentionally short: if you need paragraphs to define a term, the term probably needs a dedicated spec.

## 196.1 Evidence primitives

- **Evidence object:** a JSON payload with a schema under `schemas/` (catalog: `EVIDENCE_OBJECT_CATALOG.md`).
- **EvidenceEnvelope:** the signed (or signable) wrapper around an evidence object (`173`, `176`).
- **Payload digest:** `sha256(JCS(payload))` recorded as `payload_digest` (`176`).
- **TBS digest:** “to-be-signed” digest for an envelope, computed over canonical fields (`176`).
- **Detached payload:** payload stored under `packet/objects/sha256-<hex>.json` and referenced by `payload_pointer` (`173`).

## 196.2 Publication and verification surfaces

- **Evidence packet:** a directory containing `manifest.json`, `envelopes/`, `objects/`, and optional notes (`173`, `92`).
- **Evidence API surface:** the minimum set of envelope kinds and registries a verifier must implement (`179`).
- **Verifier profile:** a small, stable capability claim (profile ID) a verifier can publish to indicate which kind sets it supports (`179`, `docs/VERIFIER_PROFILES.md`).
- **Publishable verifier output:** a privacy-safe report that can be cited publicly without leaking operator internals (`193`).
- **Comparability pins:** optional sha256s of stable registry bytes included in reports so two reports can prove they used the same rules (`99–100`, `tools/public_surface_pins.py`).

## 196.3 Comms as evidence

- **PublicNotice:** the canonical “official statement” envelope kind (`186`, schema: `schemas/PublicNotice.json`).
- **OfficialChannelDirectory:** a content-addressed directory of declared official public channels for a jurisdiction/election (published as evidence; `203`).
- **Rumor control:** Public notices that correct false claims using “myth → fact → how to verify” (`186`, `195`).
- **Status board:** a human-facing index over `PublicNotice` digests, not an authority separate from notices (`195`).
- **Parity:** the requirement that declared official channels show the same notice digests (anti targeted suppression) (`104`, `194`, `195`).
- **Stale pointer:** when caches/CDNs/proxies serve an older discovery payload (feed/directory/well-known) so users see outdated digests; treated as a split-view-adjacent risk and handled via explicit cache posture + parity snapshots (`205`, `201`).
- **OfficialSurfaceSecuritySnapshot:** a content-addressed snapshot of DNS/TLS/email anti-spoofing posture (CAA/DNSSEC/CT/DMARC/SPF/DKIM) published as evidence to make comms hardening auditable (`199`).
- **CAA / DNSSEC / CT monitoring / SPF / DKIM / DMARC:** standard domain/certificate/email controls used to reduce spoofing and detect mis-issuance (`37`, `199`).

## 196.4 Transparency and anti-equivocation

- **Transparency log:** an append-only public record of commitments (core primitive: `04`).
- **CommitLog Entry (CLE):** a minimal public commitment record (hash + coarse metadata) binding an authority to an evidence object without disclosing it (`261`).
- **Merkle tree:** hash-tree structure often used to implement append-only logs (enables compact proofs).
- **Inclusion proof / consistency proof:** cryptographic proofs that an entry is in a log and that the log history has not been rewritten (concept borrowed from Certificate Transparency; see `261`).
- **Witness gossip:** multi-vantage cross-checking to detect split-view and selective disclosure (`23`, `100`).
- **Receipt:** a verifiable acknowledgement/commitment from a transparency system or witness tier (`180–185`).
- **Selective disclosure:** withholding or showing different evidence to different audiences; treated as an attack surface (`180`, `100`, `104`).

## 196.5 Process terms

- **Track A/B/C:** deployable core vs research annex vs North Star (`START_HERE.md`, `154`).
- **Claims contract:** what this archive asserts and what must be provable (`166`, `159`).
- **Non-claims:** explicit boundaries to prevent accidental overreach (`167`).
- **Epistemic tag:** a statement label (OBSERVED/MEASURED/REPORTED/INFERRED/UNKNOWN) plus confidence to prevent interpretation drift (`218`).
- **Proof obligation (PO):** a named, checkable thing that must be provable to justify a claim (`159`, `164`).
- **Release gate:** the checks that prevent silent drift and broken examples (`162`, `scripts/`).
- **Chain of custody:** an auditable record of who controlled election materials/systems, when, and under what controls; used as tamper-evidence and dispute-bounding (see `247`).
- **Incident response communications:** prepared templates + roles + timing for public updates during incidents; treated as a security control, not PR (see `247`).

## 196.X Continuity and contingency planning

- **COOP (Continuity of Operations):** planning and execution to keep essential election functions running during disruptions.
- **RTO / RPO:** recovery time objective / recovery point objective; in this archive we publish *classes/targets* without publishing runbook detail (`276`).
- **CPS (Continuity Posture Statement):** public, bounded continuity posture summary + commitment hash (`276`).
- **CPD (Continuity Plan Digest):** publishable digest of continuity plan scope, targets, and change linkage (`276`).
- **DMR (Degraded Mode Register):** bounded registry of acceptable degraded operations modes + verifier-visible outputs (`276`).
- **DID (Dependency Inventory Digest):** publishable digest of critical dependencies and single-point-of-failure flags, without topology (`276`).
- **CIC (Continuity Incident Capsule):** a PublicNotice-shaped, bounded update that declares the current operating mode and verification pointers (`276`).
## 196.6 Precinct closeout evidence

- **Poll / results tape (“poll tape”):** the printed closeout tape produced by a precinct scanner/BMD system, commonly used as a local, human-readable snapshot at close.
- **Precinct closeout micro-packet:** a small evidence packet containing poll-tape photos (and optionally seal/container photos + a closeout note) published and bound to a PublicNotice digest (`197`).
- **PrecinctCloseoutIndex:** content-addressed mapping of reporting unit ids → closeout packet manifest digests; chained updates make rollbacks detectable (kind `hfv.results.closeout_index`, `198`).
- **Closeout index:** a published mapping of reporting unit ids → closeout packet manifest digests, used to detect selective omission (`198`).

- **Well-known discovery** — A domain-first bootstrap surface (e.g., `/.well-known/election-stack.json`) that points to the latest directory/feed digests so outsiders can start from a single official domain (docs/204).

## 196.9 External anchor terms (for cross-reading)

- **VVSG (Voluntary Voting System Guidelines):** U.S. EAC voting system guidelines used for testing/certification; referenced as an external anchor (see `245`).
- **CDF (Common Data Format):** an interoperability format family for election data (e.g., ballot definition, CVR, results); referenced as an external anchor (see `245`).
- **CVR (Cast Vote Record):** a ballot-level electronic record of voter selections produced by vote-capture devices (e.g., scanners); useful for tabulation and some audits, but privacy-sensitive when released at fine granularity (see `274`).  
- **Ballot image:** a digital scan/picture of a marked ballot; typically higher privacy risk than CVRs because it can contain distinctive marks, write-ins, and artifacts (see `274`).  
- **DRG (Data Release Governance):** this archive’s posture + procedures for publishing or responding to requests for election datasets (CVRs, ballot images, etc.) using digest-first proofs and explicit stop-conditions (see `274`).
- **RLA (Risk-Limiting Audit):** a post-election audit method that uses statistics + paper audit trails to bound the chance of confirming an incorrect outcome; referenced as an external anchor (see `245`).
- **Risk limit:** the maximum (pre-specified) probability that an RLA will fail to correct an incorrect reported outcome (smaller is stronger). (See: [NIST “A Gentle Introduction to Risk-Limiting Audits”](https://www.nist.gov/document/gentle-introduction-risk-limiting-audits))
- **Ballot manifest:** the accounting list that maps physical ballots/batches to identifiers used for random selection; manifest accuracy is audit-critical. (See: [EAC Post-Election Tabulation Audit Guide (2024)](https://www.eac.gov/sites/default/files/2024-11/Post_Election_Tabulation_Audit_Guide_508.pdf))
- **Ballot-polling audit:** an RLA method that samples ballots and interprets votes directly without using CVRs. (See: [NIST “A Gentle Introduction to Risk-Limiting Audits”](https://www.nist.gov/document/gentle-introduction-risk-limiting-audits))
- **Ballot-level comparison audit:** an RLA method that compares hand interpretation of sampled ballots to the system’s corresponding CVRs (requires trustworthy ballot–CVR linkage). (See: [NIST “A Gentle Introduction to Risk-Limiting Audits”](https://www.nist.gov/document/gentle-introduction-risk-limiting-audits))
- **Audit Publication Pack (APP):** this archive’s minimal publishable artifact set for audits (hashes + digests proving selection/custody/discrepancies/escalation without leaking ballots/PII).


## 196.X Assurance vocabulary (minimal)

- **Assurance case:** a structured argument that a system deserves trust for a stated scope and threat model, backed by checkable evidence.
- **Claim tree (GSN-like):** a shallow “goal / subgoal / evidence” decomposition that keeps the assurance case maintainable without heavy notation.
- **Evidence minimization:** discipline of storing only what is needed to *reproduce* and *verify* claims (hashes, scripts, schemas, and pointers), avoiding bulky annexes.
- **Threat model ledger (TML):** a compact, maintained crosswalk from assets → threat classes → surfaces → controls → publishable proofs → residual risk.
- **Threat-informed defense:** using observed adversary behaviors (e.g., ATT&CK tactics/techniques) to prioritize controls and detection, without embedding exploit steps.
- **Safe red-teaming:** authorized, scoped testing that produces defensive improvements while filtering dual-use details from publication.

## 196.X Accessibility and language access

- **ADA:** Americans with Disabilities Act; requires state/local election officials to provide full and equal opportunity to vote, including accessible polling places and accessible processes.
- **HAVA:** Help America Vote Act; among other provisions, requires accessible voting systems for voters with disabilities in federal elections (at least one accessible voting system per polling place).
- **VAEHA:** Voting Accessibility for the Elderly and Handicapped Act; requires accessible polling places or alternate means in federal elections.
- **VRA Section 203:** Voting Rights Act language-minority protections; requires covered jurisdictions to provide language assistance.
- **WCAG (2.x):** Web Content Accessibility Guidelines (W3C); common benchmark for accessibility of voter-facing web properties.


## 196.X Ballot resolution surfaces (provisional / cure / canvass)

- **Provisional ballot:** a fail-safe ballot cast when eligibility cannot be determined at the time of voting; counted only if eligibility is confirmed under jurisdiction rules.
- **Ballot curing:** a process that allows voters to correct certain defects (often signature-related) so an otherwise valid ballot can be accepted, under defined deadlines and methods.
- **Canvass:** the structured reconciliation/finalization process in which totals are checked, eligible late-counted ballots are incorporated, and results are finalized/certified.

## 196.X Observation roles (minimal)

- **Poll watcher / observer:** an authorized person who may observe steps in the election process, subject to jurisdiction rules; in this archive, observer evidence must be non-interfering and non-PII by default (`250`).
- **Challenger:** an authorized person who may raise procedural challenges/objections under defined rules; challenges should be recorded as procedural facts with disposition, not as performative narratives (`250`).
- **Observation surface:** a place/process step where authorized observation occurs (polling place, processing, tabulation, canvass); treated as an evidence surface (`237`, `250`).
- **ENR (Election Night Reporting):** software/systems used to aggregate and publish *unofficial* results (e.g., via an official website), distinct from tabulation systems (`252`).  
- **Unofficial results:** preliminary results published before certification; expected to change during canvass and ballot-resolution processes (`251`, `252`).  
- **Corrections log:** an append-only public record of changes to unofficial results, with timestamps, scope, and reason codes (`252`).  
- **URSP (Unofficial Results Snapshot Pack):** a minimal bundle of a results snapshot + hash + metadata suitable for public comparison and provenance (`252`).

## Public records request (PRR)
A request for government records under FOIA or a state public records law. In this archive, PRRs are treated as an **attack surface** and an **evidence surface**: we publish *logs + response packets + hashes*, not bulk sensitive records.

## RetentionAttestation
A publishable statement (plus hashes of inventories) that certain election record categories are being retained for required windows, without publishing those records.

## 52 U.S.C. §20701 (Federal election records retention)
U.S. federal election records retention statute (commonly referenced as a **22‑month** retention floor for elections involving federal candidates). Treat as a floor; state/local overlays may add requirements.


## Adjudication
Human review of flagged items (e.g., scanner exceptions, ambiguous marks) to determine how votes are interpreted **per jurisdiction rules**. Transparency should be **aggregate + procedure** oriented, not per-ballot narrative.

## Voter intent standard
The legal/administrative rule set for interpreting marks on a paper ballot when the mark is unclear or irregular (varies by jurisdiction).

## Ballot duplication (replication)
Process of copying selections from a damaged/defective ballot onto a new ballot that can be scanned/tabulated, with strict chain-of-custody and reconciliation.

## Reason-code dictionary (RCD)
A stable set of coded reasons used to summarize adjudication/duplication dispositions in an auditable, privacy-preserving way.

## Configuration Baseline Attestation (CBA)
A publishable statement that a named system scope is operating on a specific approved configuration baseline, expressed as **IDs + hashes**, not configs.

## Change Control Packet (CCP)
A minimal record of an approved change window: what changed (at a high level), why, who authorized (roles), rollback plan summary, and before/after baseline identifiers.

## Software/Firmware Update Packet (SUP)
A minimal record of a deployed software/firmware update: vendor identifiers, package hashes/signature-verification class, deployment scope/dates (aggregate), and post-update verification performed.

## Emergency Patch Decision Record (EPDR)
A minimal record for time-sensitive changes: trigger, decision authority (roles), risk tradeoff summary, compensating controls (high-level), and follow-up verification plan.

## Configuration Drift Ledger (CDL)
A periodic, aggregated statement indicating whether observed baselines match approved baselines (match/mismatch/unknown) and pointers to remediation records.


## 196.7 Pre‑election testing surfaces

- **L&A (Logic & Accuracy):** pre-election procedures intended to confirm the configured system can record and report votes as expected (`255`).
- **LAN (L&A Public Notice):** the public announcement of an L&A test scope/time/place and observation rules (`255`).
- **TDD (Test Deck Declaration):** a minimal description of the L&A test ballot patterns + hashes, not ballot images (`255`).
- **ERS (Expected Results Sheet):** machine-readable expected tallies for the test deck, published with a hash (`255`).
- **LRSP (L&A Results Snapshot Pack):** minimal hash-bound proof that a test run occurred and matched ERS (or shows deltas) (`255`).

- **SBOM (Software Bill of Materials):** an inventory of software components/dependencies, used to improve transparency and vulnerability response; often shared under controlled access (`257`).
- **SSDF (Secure Software Development Framework):** NIST SP 800-218 recommended secure software development practices; used here as an external anchor for vendor expectations (`257`).
- **SLSA (Supply-chain Levels for Software Artifacts):** a framework describing build integrity controls and provenance/attestation concepts; used here as an external anchor for build provenance (`257`).
- **VTP (Vendor Transparency Packet):** digest-first statement of what transparency artifacts were requested/received from vendors (SBOM/provenance/support/vuln disclosure) (`257`).
- **CIS (Component Inventory Snapshot):** minimal “what is installed” inventory at a time, published as counts/version ranges + digests (`257`).
- **PBAA (Provenance & Build Assurance Attestation):** a small statement that build provenance was required and verified, without publishing sensitive internals (`257`).
- **VHR (Vulnerability Handling Record):** a publishable record of tracking/closing a vulnerability affecting a component, linked to change-control artifacts (`257`).
- **DRA (Decommission & Replacement Attestation):** digest-first record that components were decommissioned/replaced, with before/after inventory digests (`257`).

## 196.X Training and exercises (integrity controls)

## Tabletop exercise (TTX)
A facilitated, discussion-based exercise where participants walk through roles, decisions, and communications under a hypothetical scenario. Used to test plans without touching live systems.

## Inject
A piece of scenario information introduced during an exercise (e.g., “the website is down”, “a rumor spreads”). **Do not publish inject details** when they would reveal sensitive pathways.

## Hotwash
An immediate, informal after-action discussion held right after an exercise to capture what worked and what failed.

## After-action report (AAR) / Improvement plan (IP)
A summary of strengths/gaps and a tracked list of corrective actions (owners, due dates, status). In this archive, the publishable form is an **AAR+Improvement Ledger**: aggregate, privacy-first, and hashes-first.

## 196.X Incident reporting and disclosure (bounded)

- **IDS (Incident Disclosure Stub):** a minimal public statement that an incident class occurred, with coarse scope and update commitments, published without operational details (`259`).
- **ITD (Incident Timeline Digest):** an append-only hash chain over high-level timeline events; the public artifact is the hashes + coarse labels, not internal notes (`259`).
- **ENL (External Notification Ledger):** a publishable ledger of *who was notified* (by category) and when, without disclosing sensitive contents (`259`).
- **PCP (Public Communications Packet):** a bounded set of public communications artifacts for incident periods (known/unknown, actions, where to verify official updates) (`259`).

## 196.Y Jurisdictional policy surfaces

- **Policy surface:** a jurisdiction-set decision (“knob”) that materially affects access, outcomes, or verifiability (e.g., cure window, audit rule).
- **JPSR (Jurisdictional Policy Surface Registry):** a bounded, change-controlled registry of policy surfaces with authoritative citations and links to required evidence artifacts (`262`).
- **PSR (PolicySurfaceRecord):** one record in the JPSR (stable ID, scope/authority/owner, authoritative references, and linked evidence surfaces).


## Ballot design / ballot building evidence surfaces

- **ACDD (Authoritative Contest Definition Digest):** a signed digest (hash + metadata) of the authoritative contest-definition input set used to generate ballot styles (`263`).
- **BSMD (Ballot Style Manifest Digest):** a digest of the set of ballot styles (style IDs + included contests + language variants) without precinct mapping disclosure (`263`).
- **BPP (Ballot Proof Packet):** the bounded proofing bundle (rendered proofs + checklist + issue log + fix confirmations), typically published as a digest with an aggregate issue summary (`263`).
- **PAL (Proof Approval Ledger):** append-only approvals record that links role-based approvals to hashes of proof packets and style manifests (`263`).
- **PERA (Print/Export Release Attestation):** attestation that printed/exported ballots match the approved proofs, linked by hashes (`263`).


## Recount

A **recount** is a post-election re-tabulation or re-examination of ballots/votes under a jurisdiction’s rules (automatic threshold-triggered or requested). In this archive, recounts have bounded, publishable **evidence surfaces** (declaration, custody attestations, change ledger) without ballot-level disclosures. See `264-recounts-contests-and-certification-disputes-as-evidence-surfaces.md`.

## Election contest / challenge (administrative)

A **contest/challenge** here means a structured, rule-governed claim that an election outcome or process step should be reconsidered (often through an elections board process). This is distinct from “general controversy” or informal allegations; the evidence surface is the **docket digest** (status + authority + bounded claim summary) and not raw case files.

## Certification dispute

A **certification dispute** is any formal condition where certification is delayed, stayed, or partially contested (administrative or judicial). The publishable surface is a **Certification Status Capsule (CSC)** that distinguishes unofficial results (ENR) from certified results, and states what is pending and when updates will occur.


## Canonicalization

**Canonicalization** is producing a deterministic byte representation of data so that hashing and signing are stable across implementations. For JSON, this archive points to **JCS (JSON Canonicalization Scheme)**. ([RFC 8785](https://datatracker.ietf.org/doc/rfc8785/))

## CPP (Crypto-Proof Packaging)

**CPP** is the archive’s minimal envelope for publishable commitments: canonicalize → hash → sign → timestamp → (optional) transparency log. See `265-canonicalization-signing-timestamping-and-proof-packaging.md`.

## RFC 3161 / trusted timestamp token

**RFC 3161 TSP** is a protocol for obtaining a signed timestamp token from a Time Stamping Authority over a hash, providing evidence that some data existed at or before a time without revealing the data. ([RFC 3161](https://www.ietf.org/rfc/rfc3161.txt))

## Transparency log inclusion proof / consistency proof

A **transparency log** is an append-only log (often Merkle-tree based) that can provide:
- an **inclusion proof** (a commitment is in the log), and
- a **consistency proof** (the log only ever appended, never rewrote history). ([RFC 6962](https://www.rfc-editor.org/rfc/rfc6962.html))

## PSPS (Physical Security Posture Statement)

**PSPS** is a minimal, publishable statement of baseline physical-security posture (controlled areas definition, role-based access model, two-person integrity where used, seal custody model), paired with a hash commitment to the detailed internal procedures. See `266-physical-security-and-access-control-as-evidence-surfaces.md`.

## CALD (Controlled Access Log Digest)

**CALD** is an append-only, publishable digest of access events for controlled areas (time window + role class + reason code + hash pointers), designed to support checkability and incident reconstruction without publishing sensitive access details or staff identities. See `266-physical-security-and-access-control-as-evidence-surfaces.md`.

## KCCA (Key / Credential Control Attestation)

**KCCA** is a minimal publishable attestation describing custody and rotation of physical keys and access credentials using role tags (not names). See `266-physical-security-and-access-control-as-evidence-surfaces.md`.

## SIS (Seal Inventory Snapshot)

**SIS** is a periodic snapshot of tamper-evident seal materials (class + counts + anomalies) with a hash commitment to the internal seal ledger. See `266-physical-security-and-access-control-as-evidence-surfaces.md`.

## FIC (Facility Incident Capsule)

**FIC** is a bounded public capsule for physical incidents affecting election facilities (what is known/unknown, affected asset classes, next verification steps) that can optionally link to the incident disclosure surfaces (`259`). See `266-physical-security-and-access-control-as-evidence-surfaces.md`.

## Two-person integrity

**Two-person integrity** (sometimes “two-person rule”) means certain sensitive actions require two authorized individuals present/participating, reducing single-actor risk and improving accountability.

## Personnel security / insider risk (bounded)

- **PSPS:** Personnel Security Posture Statement — public posture statement (policy level) without rosters or screening playbooks.
- **RABMD:** Role/Access Boundary Map Digest — publishable digest of role-to-capability boundaries with CPP hash commitments to internal mappings.
- **ARL:** Access Review Ledger — append-only log of periodic access reviews (counts + exceptions by code).
- **TCD:** Training & Credentialing Digest — publishable proof that training occurred without naming individuals.
- **ICIC:** Insider-Concern Intake Capsule — public proof that a concern channel exists and is used responsibly (no case details).
- **THHC:** Threat & Harassment Handling Capsule — bounded public artifact for worker threats (privacy-first, no identifying details).

## RumorControlPack (RCP)

**RCP** is a small, content-addressed correction packet that binds a claim identifier to a minimal correction, safe verification pointers, and signed provenance (via CPP). See `268-rumor-control-and-mis-disinformation-response-as-evidence-surfaces.md`.

## RumorControl index (RCI)

**RCI** is an append-only index of rumor-control entries (CID → status → RCP digest + validity window) published as a verifiable public surface. See `268-rumor-control-and-mis-disinformation-response-as-evidence-surfaces.md`.

## Claim identifier (CID)

**CID** is a deterministic identifier for a claim/correction so independent parties can refer to the same item without coordination (computed from a canonicalized claim string; avoids named individuals and fine-grained location targeting). See `268-rumor-control-and-mis-disinformation-response-as-evidence-surfaces.md`.


## Voter Registration Database (VRDB)

A system (often state-run) that stores and manages voter registration records. VRDBs typically contain sensitive information and require a balanced posture across **confidentiality, integrity, and availability** (CIA). See NIST’s VRDB security considerations: https://www.nist.gov/itl/voting/security-voter-registration-databases

## List maintenance

The process of adding, updating, and removing voter registration records to keep lists accurate and current, typically governed by the National Voter Registration Act (NVRA) and state law. See EAC best practices (Mar 2023): https://www.eac.gov/sites/default/files/electionofficials/VoterList/Best_Practices_Voter_List_Maintenance_V1_508.pdf

## National Voter Registration Act (NVRA) Section 8

The federal statutory framework that governs certain aspects of list maintenance for federal elections (often referenced as **52 U.S.C. § 20507**). Primary text: https://uscode.house.gov/view.xhtml?req=%28title%3A52+section%3A20507+edition%3Aprelim%29

## Registration Change Ledger Digest (RCLD)

A privacy-first, **aggregate-only** digest of VRDB record changes (adds/updates/inactivations/removals) over a reporting period, typically published with a hash commitment (CPP) to an internal detailed ledger. See `269-voter-registration-and-list-maintenance-as-evidence-surfaces.md`.

## List Maintenance Report Digest (LMRD)

A short, publishable digest describing list maintenance activities, data-source categories, QA/rollback posture, and known issues — published with hash commitments rather than raw voter data. See `269-voter-registration-and-list-maintenance-as-evidence-surfaces.md`.

## Electronic pollbook (EPB / e-pollbook)

A digital system used at voting locations to identify eligible voters, manage check‑in, and (often) assist with ballot style issuance and reporting. In many jurisdictions EPBs synchronize across sites to prevent duplicate crediting and to support real-time operational awareness. See EAC ESTEP EPB program overview: https://www.eac.gov/election-technology/estep-program/electronic-poll-books

## Check‑In Transaction Ledger Digest (CTLD)

A privacy-first, aggregate-only, append-only digest of check-in activity (counts, buckets, exception totals) published with hash commitments to enable reconciliation without exposing voter identifiers. See `270-electronic-pollbooks-and-voter-checkin-as-evidence-surfaces.md`.

## Sync Integrity Ledger Digest (SILD)

An aggregate-only digest that summarizes EPB synchronization health (cycles, failures, latency buckets, conflict counts) without exposing endpoints or topology. See `270-electronic-pollbooks-and-voter-checkin-as-evidence-surfaces.md`.

## Ballot Style Assignment Digest (BSA‑D)

A publishable digest that summarizes ballot style issuance at a safe aggregation level and links issuance rules to change control, without publishing ballot-style-to-precinct mappings. See `270-electronic-pollbooks-and-voter-checkin-as-evidence-surfaces.md`.

## Outage / Queue Capsule (OQC)

A bounded public capsule describing EPB outages or queue events (coarse timeline, declared operational mode, next verification step) designed to improve transparency without amplifying rumors or exposing sensitive operational details. See `270-electronic-pollbooks-and-voter-checkin-as-evidence-surfaces.md`.


## Vote-by-mail (VBM)

A voting channel where ballots are delivered to eligible voters outside the polling place (typically by mail) and returned via mail or approved return options. In this archive, VBM evidence surfaces focus on **logistics integrity and reconciliation** without publishing voter-identifying data. See `271-vote-by-mail-distribution-tracking-and-dropboxes-as-evidence-surfaces.md`.

## Ballot drop box

A secured receptacle designated for voters to return completed ballots. Security posture commonly relies on custody procedures, tamper-evident seals, surveillance posture, and collection discipline. This archive treats drop boxes as a **return-channel evidence surface** with publishable digests (not routes, timing, or camera placement). See `271-vote-by-mail-distribution-tracking-and-dropboxes-as-evidence-surfaces.md`.

## Outbound Production & Distribution Ledger Digest (OPD-LD)

An append-only, aggregate-only digest of outbound ballot production and distribution events (printed/packaged/handed to carrier/undeliverable/replacements), published with hash commitments to internal ledgers. See `271-vote-by-mail-distribution-tracking-and-dropboxes-as-evidence-surfaces.md`.

## Return Channel Ledger Digest (RCLD-VBM)

An aggregate-only digest of ballot returns by channel (mail/in-person/drop box) and high-level outcome buckets, published with hash commitments and linked to canvass reconciliation surfaces. See `271-vote-by-mail-distribution-tracking-and-dropboxes-as-evidence-surfaces.md`.

## Ballot Tracking Public Status Feed Digest (BT-PSFD)

A publishable, aggregate-only digest of ballot-tracking status transitions using a stable status taxonomy; explicitly excludes per-voter event disclosure. See `271-vote-by-mail-distribution-tracking-and-dropboxes-as-evidence-surfaces.md`.

## Intake Batch Digest (IBD)

A publishable, aggregate-only digest of returned-mail-ballot intake batches (counts, channel class, custody handoffs by role class), with hash commitments to internal intake logs. See `272-mail-ballot-intake-verification-and-processing-as-evidence-surfaces.md`.

## Verification Rollup Digest (VRD)

An aggregate-only rollup of envelope verification outcomes (accepted / rejected / needs-cure) by stable reason codes, with change-controlled definitions and hash commitments. See `272-mail-ballot-intake-verification-and-processing-as-evidence-surfaces.md`.

## Rejection Reason-Code Dictionary (RRCD)

A small, change-controlled dictionary defining the reason codes used in verification rollups (VRD). Changes should be committed (e.g., via `261`) and governed by change control (`256`). See `272-mail-ballot-intake-verification-and-processing-as-evidence-surfaces.md`.

## Opening Session Ledger (OSL)

A per-session aggregate ledger for envelope opening/extraction (counts, timestamps, role classes present, anomalies), explicitly excluding per-envelope/per-ballot identifiers. See `272-mail-ballot-intake-verification-and-processing-as-evidence-surfaces.md`.

## Scanner Feed Digest (SFD)

Counts-only digest of ballots scanned and scan exceptions (by code), plus cryptographic commitments (hashes) to internal scan logs — without releasing results. See `272-mail-ballot-intake-verification-and-processing-as-evidence-surfaces.md`.

## Processing → Canvass Bridge Digest (PCBD)

A small reconciliation bridge tying intake/verification/opening/scanning aggregates to canvass reconciliation and ENR corrections surfaces. See `272-mail-ballot-intake-verification-and-processing-as-evidence-surfaces.md`.


## Ballot Inventory Snapshot (BIS)

Publishable, counts-only digest of blank ballot/stock inventory by ballot type and custody domain, with hash commitments to internal detailed inventories. See `273-ballot-accounting-and-reconciliation-as-evidence-surfaces.md`.

## Ballot Accounting Ledger Digest (BALD)

Append-only, phase-bucketed reconciliation rollups for issued/returned/accepted/count totals with delta reason codes and hash commitments to internal ledgers. See `273-ballot-accounting-and-reconciliation-as-evidence-surfaces.md`.

## Canvass Reconciliation Bridge (CRB)

A publishable digest explaining why unofficial election-night totals differ from canvass/certified totals, expressed as bounded delta buckets with references to ENR snapshots and stable reason codes. See `273-ballot-accounting-and-reconciliation-as-evidence-surfaces.md`.

## Interoperability and data release

- **CDF (Common Data Format):** NIST Voting common data formats for exchanging election information across systems.
- **ERR CDF:** NIST Election Results Reporting Common Data Format.
- **EML (Election Markup Language):** OASIS XML-based election/voter services interoperability standard.
- **Schema Registry Digest (SRD):** A small, signed, hash-anchored declaration of the schemas/profiles a jurisdiction uses and how they relate.

## Observability Posture Statement (OPS)

A short public statement describing **what classes of systems are monitored**, how triage is organized (roles, not names), and how detailed telemetry is committed via hashes/signatures (see `265`). It is intentionally **non-topological** (no endpoint details). See `277-observability-metrics-and-anomaly-response-as-evidence-surfaces.md`.

## Metrics Digest (MD)

A publishable, aggregate-only report of operational health (availability, throughput, data quality) by **system class**, using coarse time buckets and without site/precinct breakdown unless demonstrably safe. See `277-observability-metrics-and-anomaly-response-as-evidence-surfaces.md`.

## Alert Ledger Digest (ALD)

An append-only, publishable ledger of alert **categories** and dispositions (acknowledged/mitigated/escalated) with hash commitments to internal details. See `277-observability-metrics-and-anomaly-response-as-evidence-surfaces.md`.

## Outage & Degraded-Mode Capsule (ODC)

A compact public notice describing an outage or degraded mode (what’s impacted / not impacted, status, next update time) plus commitments for later verification. See `277-observability-metrics-and-anomaly-response-as-evidence-surfaces.md`.

