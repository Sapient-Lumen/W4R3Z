# 273 — Ballot accounting and reconciliation as evidence surfaces

**Track:** Shared

Ballot accounting and reconciliation are where “trust me” becomes a ledger: *how many ballots existed*, *where they went*, *how many were cast/returned/accepted*, and *why counts changed* between election night and certification.

This doc defines **publishable, privacy-first digests** that support verification and oversight **without** exposing voter identities, ballot secrecy, facility layouts, or operational targeting details.

## Goals

- Make the **ballot lifecycle countable end-to-end** (issued → cast/returned → accepted → tabulated → stored → audited).
- Publish **bounded reconciliation artifacts** that are independently checkable.
- Compose with:
  - **CommitLog / transparency commitments** (`261-*`)
  - **canonicalization + signing + timestamping** (`265-*`)
  - **chain-of-custody + physical security digests** (`247-*`, `266-*`)
  - **mail ballot processing digests** (`272-*`)
  - **canvass & certification capsules** (`251-*`, `264-*`)

## Anti-bloat + safety rules

- Prefer **counts + reason codes + hashes** over raw images, scans, or voter-level exports.
- Never publish:
  - voter identifiers (names, DOB, address, voter ID, signature images)
  - ballot style → voter/precinct mappings beyond what is already legally public
  - detailed transport routes, schedules, or facility schematics
- If a request asks for raw ballot-level detail: route to **PRR bounds** (`253-*`) and apply stop conditions.

## Core evidence objects (minimal set)

All objects should be produced in **canonical form** (see `265-*`), then hashed and committed via **CommitLog entries** (`261-*`).

### 273.A — Ballot Inventory Snapshot (BIS)

**Purpose:** establish the baseline inventory of blank ballots/stock by ballot type and custody domain.

**Fields (publishable digest):**
- election_id, jurisdiction_id, ballot_type (in-person / mail / provisional / test / other)
- stock_class (printed ballots, blank stock, BOD media)
- counts: received, spoiled, issued, returned, unused, destroyed (if applicable)
- custody_domains: {site_class → count_bucket}
- `bis_hash` (hash of internal detailed inventory)

### 273.B — Ballot Accounting Ledger Digest (BALD)

**Purpose:** end-to-end reconciliation rollups, append-only across reporting phases.

**Phase buckets (suggested):**
- pre-election (stocking, L&A test decks separated)
- election day (issued + spoiled)
- post-election intake (mail return + drop box collections + provisional issuance)
- tabulation / export
- canvass adjustments
- audit outcomes

**Publishable BALD includes:**
- phase, timestamp, responsible office role
- totals per ballot type:
  - issued / cast / returned / accepted / rejected / challenged / cured / counted
- delta section: {metric, prior, new, reason_code, reference_id}
- `bald_hash` (hash of the internal detailed ledger)

### 273.C — Polling Place Ballot Statement Digest (PPBSD)

**Purpose:** reconcile on-site issued ballots, spoiled ballots, and equipment media counts without revealing precinct targeting detail.

**Publishable digest per site_class (not necessarily per location):**
- site_class (polling place / vote center / early vote) + reporting_date
- number_of_sites_reporting
- totals: check-ins, ballots_issued, ballots_cast, spoiled, provisional_issued
- exceptions summary (counts-only)
- `ppbsd_hash`

### 273.D — Central Count Intake Reconciliation Digest (CCIRD)

**Purpose:** bind intake batches (mail/dropbox) to processing and tabulation counts.

**Publishable digest:**
- batch_class (mail tray, dropbox collection, courier batch, etc.)
- counts: received_envelopes, accepted_for_verification, rejected_preverification
- verification rollups: accepted, rejected, pending_cure
- opening/scan-feed rollups: opened, duplicated, scanned, quarantined
- `ccird_hash`

### 273.E — Canvass Reconciliation Bridge (CRB)

**Purpose:** explain why “election night totals” differ from “certified totals”.

**Publishable digest:**
- prior_totals_ref (ENR snapshot id from `252-*`)
- current_totals_ref (canvass snapshot)
- delta buckets: late arrivals, curing outcomes, provisional adjudication, duplication/adjudication updates, error corrections
- links to reason-code dictionaries (from `254-*` and local JPSR knobs in `262-*`)
- `crb_hash`

## Reason codes and policy knobs

- Maintain a **stable Reason Code Dictionary** (RCD) for reconciliation deltas; reuse/align with adjudication and cure vocabularies (`254-*`, `251-*`).
- Maintain a **Jurisdictional Policy Surface Registry entry** (`262-*`) for:
  - acceptance windows, cure windows, signature verification rules, duplication standards, provisional eligibility decisions
  - when and how late-arriving ballots are handled

## Verification recipes (what outsiders can do)

A verifier should be able to:
1. Check **hash commitments** for each digest object in the CommitLog (`261-*`).
2. Validate signatures/timestamps (`265-*`).
3. Confirm that the **CRB deltas** sum to the certified totals.
4. Correlate high-level rollups with:
   - canvass/certification guidance and phases (EAC canvass guidance)
   - inbound mail ballot processes (EAC/CISA inbound ballot process)

## Primary anchors (cite-first)

- EAC: **Guide to the Canvass** (reconciliation, canvass stages, certification context).  
  xref: eac_electionofficials_postelection_guide_to_the_canvass_eac
- EAC/CISA: **Inbound Ballot Process** (intake + handling considerations).  
  xref: eac_electionofficials_vbm_inbound_ballot_process
- Brennan Center: **Best Practices for Ballot Accounting and Reconciliation** (historical checklist framing; not current authority).  
  xref: brennan_center_legacy_democracy_9_25_08_bestpracticeschecklist
- Elections Group: **Ballot Management Audit** (ballot accounting + reconciliation + custody implementation context; not locally hashed here).  
  xref: elections_group_content_uploads_2023_08_ballot_management_audit_230809
