# 277 — Observability, metrics, and anomaly response as evidence surfaces

**Track:** Shared

Elections involve many coupled systems (registration, pollbooks, ballot build, ballot delivery, tabulation, reporting, audits).
“Observability” is how you show—without leaking sensitive details—that these systems were **operating within expected bounds**, that anomalies were **noticed**, and that responses were **timely, accountable, and reviewable**.

This document defines **publishable** (privacy-first, ops-safe) evidence surfaces for:
- operational **metrics** and **health** reporting,
- **anomaly detection** and triage,
- **outages** and **degraded mode** operation,
- post-incident **learning** that composes with `259` (incident disclosure) and `261/265` (commitments/proof packaging).

## Non-goals and hard stop conditions

Do **not** publish:
- network diagrams, IPs, device identifiers, software versions/build strings, admin endpoints, detailed alert rules,
- raw logs containing voter data, poll worker names, badge IDs, precise facility details, or timestamps granular enough to enable targeting,
- anything that meaningfully improves an attacker’s ability to evade detection.

If a record request seeks any of the above, route through `253` (PRR + access bounds) and publish only a safe digest.

## Core idea: “digest-first observability”

Publish **aggregates + hashes**, not internals.

- **Aggregates:** counts, rates, percentiles, “up/down” intervals, coarse time buckets (e.g., 30–60 min), and thresholds expressed qualitatively (“above baseline”).
- **Hashes:** commit to the internal, detailed telemetry bundle (metrics snapshots, log extracts, alert configs) using `265` (canonicalization + signing + timestamping).
- **Append-only:** publish updates as an append-only log (see `261` CommitLog Entry).

## Minimal publishable artifacts

### 277.A — Observability Posture Statement (OPS)
A short public posture statement covering:
- what is monitored (system classes, not endpoints),
- where monitoring is performed (logical boundary, not topology),
- how alerts are triaged (roles, duty rotation),
- how evidence is committed (CPP / hashes),
- what is **not** monitored (explicitly) to reduce false expectations.

### 277.B — Metrics Digest (MD)
A periodic (daily during peak; weekly otherwise) digest:
- availability by system class (pollbooks / EMS / scanners / ENR / voter portals),
- transaction volumes (check-ins, ballot requests, ballot accepts/rejects as aggregates),
- processing throughput (mail processing batches, scan-feed rollups),
- data quality indicators (schema validation failures, import/export error rates),
- “known degraded” windows with brief cause category.

**Format:** coarse time buckets + counts/rates/percentiles; no per-site or per-precinct breakout unless it is demonstrably safe.

### 277.C — Alert Ledger Digest (ALD)
An append-only ledger of alert **categories**, with:
- coarse timestamp bucket,
- category + severity band,
- disposition (acknowledged / mitigated / false positive / escalated),
- linkage to an Incident Disclosure Stub (IDS) when appropriate (`259`),
- a hash commitment to internal details.

### 277.D — Outage & Degraded-Mode Capsule (ODC)
A small capsule that can be published quickly:
- what is impacted (system class),
- what is *not* impacted (explicit),
- current status + next update time,
- verification pointers (official channels; do not link to private dashboards),
- digest/hash commitments for later audit.

Use this alongside `268` (rumor control) to minimize misinformation spread.

### 277.E — Monitoring Change Capsule (MCC)
When monitoring coverage changes (new metrics, new alerting, new tooling):
- describe at a high level what changed and why,
- publish a hash commitment to internal change packets (pairs with `256` change control),
- publish a “no regression” statement for continuity.

## Composition with other evidence surfaces

- **ENR snapshots (`252`) + CommitLog (`261`)**: MD/ALD can reference ENR correction events without re-publishing results.
- **Incident reporting (`259`)**: ALD entries can link to IDS/ITD digests when an operational anomaly becomes an incident.
- **COOP (`276`)**: ODC should specify which degraded-mode procedures are active (without revealing playbook internals).
- **Audits (`260`)**: metrics about audit execution (dates, progress percentages) can be published safely using MD.

## Minimal schema (copy/paste)

The following is a **suggested** high-level schema (publishable), designed to be canonicalized and signed per `265`:

- `ops_id` (stable identifier)
- `period` (date range; coarse buckets)
- `system_class` (enum)
- `metric_family` (availability|throughput|data_quality|alerts)
- `values` (aggregate counts/rates/percentiles)
- `notes` (bounded; no sensitive detail)
- `commitment` (hash + signing/timestamp metadata)
- `links` (CommitLog entry id; IDS id; ENR corrections log id)

## Primary anchors (cite-first)

- NIST SP 800-137 (Information Security Continuous Monitoring).  
  xref: nist_sp_800_137_final
- NIST SP 800-61 rev.3 (Incident Response).  
  xref: nist_sp800_61r3_pdf
- CISA election security best practices and operational guidance (overview hub).  
  xref: cisa_best_practices_securing_election_systems_page
