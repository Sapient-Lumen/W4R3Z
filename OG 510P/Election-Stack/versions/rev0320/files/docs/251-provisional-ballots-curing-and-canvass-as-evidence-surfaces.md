# 251 — Provisional ballots, ballot curing, and canvass as evidence surfaces (minimal, privacy-first)

**Track:** Shared

This document treats three “ballot resolution” processes as **integrity evidence surfaces**:

- **Provisional ballots** (fail-safe ballots when eligibility cannot be confirmed at time of voting),
- **Ballot curing** (fixing correctable defects, often signature-related, under jurisdiction rules),
- **Canvass / certification** (the structured reconciliation and finalization process).

The goal is **not** to standardize law. It is to define *minimal publishable artifacts* that let observers verify process claims **without leaking voter PII** or enabling intimidation.

## 251.1 Non-goals and stop conditions

**Non-goals**
- Not legal guidance; rules vary by state/locality.
- Not an endorsement of any specific signature-comparison method or threshold.
- Not a recipe for challenging ballots; this pack is anti-weaponization.

**Stop conditions**
- If a proposed artifact would expose voter identity, address, signature images, DOB, or any uniquely identifying ballot envelope marks: **do not publish it**.
- If an artifact could be used to target voters/workers (doxxing, harassment): **do not publish it**.
- If a process claim depends on vendor/proprietary internals that cannot be independently checked: downgrade the claim or publish only *interface-level* evidence.

## 251.2 Minimal artifacts (publishable, bounded)

The following are intended to be **small, hashable, and replayable**.

### A) Provisional ballot accountability snapshot
Publish **aggregate counts** and **reasons** (at the jurisdiction’s normal reporting granularity), plus pointers to the governing standards used.

Minimum fields:
- election_id, jurisdiction_id
- provisional_issued_count
- provisional_counted_count
- not_counted_by_reason: { reason_code → count }
- voter_lookup_available: yes/no (HAVA requires voter ability to learn status)
- last_updated_at, report_digest

Anchor: EAC emphasizes clarity/uniformity and publicizing how many provisional ballots were issued/counted and reasons for not counting.

### B) Cure policy declaration (jurisdiction-specific)
Publish the **policy surface**, not case details:

Minimum fields:
- eligible_defects (enumerated)
- notification_channels (mail/text/email/portal/in-person)
- cure_deadline_rule (text + citation pointer)
- accepted_cure_methods (ID verification, affidavit, signature update, etc.)
- accessibility/language accommodations (pointer to 248)
- operator_roles_and_separation (who reviews vs who contacts)
- change_log_digest (policy versioning)

Anchor: EAC/CISA describe signature verification + cure processes and operational considerations.

### C) Cure processing metrics (aggregate, time-bucketed)
Publish **process metrics** to make discriminatory or chaotic handling visible without exposing voters.

Minimum fields:
- notifications_sent_by_channel (counts)
- cures_received_by_channel (counts)
- cured_and_accepted_count
- cured_but_rejected_count (by reason)
- median_time_to_notify, median_time_to_resolve
- exception_counts (e.g., unreachable, language assistance requested)

For “how many states do this” / definitional context, keep external pointers only (do not copy tables).

### D) Canvass reconciliation ledger (minimal)
Publish a reconciliation summary with explicit “what changed” accounting.

Minimum fields:
- ballots_cast_total (by mode, if available)
- ballots_tabulated_election_night
- ballots_added_after_election_night (by class: late-arriving eligible, cured, provisional counted, duplication/remake, adjudication)
- ballots_removed_after_election_night (by class: rejected provisional, rejected late-arriving, duplicates resolved, etc.)
- batch_count / precinct_count reconciliation totals (as applicable)
- anomalies_and_disposition_count (aggregate)
- certification_event_digest(s) (what was certified, when, by whom)

Context pointer: canvassing/certification are widely misunderstood; use explanatory material as a *citation*, not as a normative source.

## 251.3 Evidence minimization patterns (how to publish safely)

- Prefer **counts, reason codes, and timestamps** over scans/photos.
- Prefer **hash commitments** to internal working papers (sealed) over publication.
- Use **“reason code registries”**: stable, documented reason codes so counts are comparable across updates.
- Publish **delta reports** (“what changed since last update”) to prevent rumor amplification.

## 251.4 Integration hooks (where this plugs into the stack)

- Pair A/B/C/D artifacts with `PublicNotice` when communicating updates (see `186`, `195`).
- Treat policy declarations as “official surface” content-addressed payloads (see `203`, `199`).
- Feed high-level metrics into the Threat Model Ledger (see `249`) as *signals* (not accusations).

## 251.5 Open questions (kept tight)

- What is the minimum cross-jurisdiction reason-code set that remains non-prescriptive?
- Which metrics best detect inequitable curing outcomes without re-identification risk?
- How should observers verify “uniformity” claims when counties differ materially?


## Primary anchors

- [EAC — Provisional Voting](https://www.eac.gov/research-and-data/provisional-voting)
- [EAC — Signature Verification & Cure Process (PDF)](https://www.eac.gov/sites/default/files/electionofficials/vbm/Signature_Verification_Cure_Process.pdf)
- [NCSL — Canvassing and Certification of Ballots](https://www.ncsl.org/resources/details/elections-defined-canvassing-and-certification-of-ballots)
- [NCSL — Ballot Curing](https://www.ncsl.org/resources/details/elections-defined-ballot-curing-provides-safeguard)
