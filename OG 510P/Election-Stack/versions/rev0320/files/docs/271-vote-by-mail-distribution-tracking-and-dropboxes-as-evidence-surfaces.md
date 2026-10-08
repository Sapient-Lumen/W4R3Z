# 271 — Vote-by-mail distribution, tracking, and drop boxes as evidence surfaces

**Track:** Shared (cross-cutting)

This note defines **bounded, publishable evidence surfaces** for vote-by-mail (VBM) distribution and return logistics — including optional ballot tracking and drop boxes — without publishing voter-identifying data, precinct/style mappings, or operational details that would enable harassment or interference.

## Scope

Covers:
- outbound ballot materials (printing → packaging → mailing / hand distribution),
- inbound return channels (USPS, in-person return, drop box),
- optional ballot-tracking status feeds (public-facing),
- reconciliation at aggregate level (counts + hashes + attestations).

## Non-goals / stop conditions

Hard stop if a proposed artifact would:
- expose **voter PII** (names, addresses, signatures, identifiers, scan images),
- reveal **precise locations / collection routes / timing** that increase sabotage risk,
- enable mass challenge/harassment (lists of voters, signatures, “suspicious” ballots),
- disclose internal security controls (camera placements, alarm specs, keying plans).

When disclosure is compelled (PRR/FOIA), route through the archive’s **retention/access-bounds** patterns and publish only the minimum lawful response surface (see `docs/253-*`).

## Publishable evidence surfaces (digest-first)

### 1) VoteByMail Posture Statement (VBM-PS)
A short, public statement (1–2 pages) that commits to:
- channels offered (mail, in-person return, drop box if any),
- high-level eligibility and deadlines (jurisdiction-specific reference only),
- the *shape* of reconciliation reporting (what counts will be published, when),
- where authoritative updates live (PublicNotice feed / website).

**Publish:** PDF/HTML + hash commitment via CommitLog (`docs/261-*`) and CPP (`docs/265-*`).

### 2) Outbound Production & Distribution Ledger Digest (OPD-LD)
Append-only **aggregate** ledger per reporting interval:
- ballots printed (count),
- ballots packaged (count),
- ballots sent to USPS / carrier (count),
- undeliverable/returned-as-mail (count),
- replacement ballots issued (count, by reason bucket).

**Publish:** totals + timestamp + hash of the internal ledger snapshot (not the snapshot).

### 3) Return Channel Ledger Digest (RCLD-VBM)
Aggregate counts per interval:
- returned by mail (received),
- returned in-person (office),
- returned via drop box (if used),
- rejected/needs-cure buckets **only as counts** (reasons are policy surfaces; do not publish case details).

Bind these to:
- ENR snapshot/corrections discipline (`docs/252-*`),
- canvass/reconciliation (`docs/251-*`).

### 4) Drop Box Posture Statement (DB-PS) and Collection Ledger Digest (DB-CLD)
If drop boxes exist, publish:
- DB-PS: high-level controls in plain language (tamper-evident seals, custody discipline, surveillance posture described **without** camera placement details),
- DB-CLD: append-only **collection event digests** (counts + seal-status anomalies + custody attestations), with locations generalized (e.g., region/zone) if necessary.

Anchor to:
- EAC QSG on drop boxes and the GCC/SCC resource doc,
- CISA incident-focused drop box security best practices for incendiary devices.

### 5) Ballot Tracking Public Status Feed Digest (BT-PSFD)
If ballot tracking is offered, publish:
- a **status taxonomy** (e.g., sent, in transit, received, accepted, needs action),
- an interval digest of status transitions **as aggregate counts only**,
- a commitment to corrections logging if tracking statuses are revised.

Do **not** publish per-voter tracking events. If individual lookup exists, treat it as a separate authenticated system; this doc only defines what can be published safely.

## External anchors (cite-first, no bulk imports)

- **EAC Quick Start Guide: Ballot Drop Boxes** (design/operations considerations): https://www.eac.gov/sites/default/files/electionofficials/QuickStartGuides/Ballot_Drop_Boxes_EAC_Quick_Start_Guide_508.pdf
- **Elections GCC/SCC “Ballot Drop Box” resource document** (secure administration guidance): https://www.eac.gov/sites/default/files/electionofficials/vbm/Ballot_Drop_Box.pdf
- **CISA ballot drop box incendiary-device best practices** (risk-aware mitigation posture): https://www.cisa.gov/resources-tools/resources/ballot-drop-box-security-best-practices-incendiary-devices

See:
- `docs/245-external-standards-and-alignment-map.md` for how external anchors are referenced in this archive.
