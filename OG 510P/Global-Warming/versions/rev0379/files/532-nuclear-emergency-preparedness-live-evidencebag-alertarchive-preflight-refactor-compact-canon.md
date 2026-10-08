# 532 — Nuclear Emergency Preparedness Live Evidence Bag, Alert Archive, and Preflight Capture Refactor — Compact Canon

## Why this revision exists

Rev0324 proved that synthetic packet bundles can be imported without automatically closing readiness. Rev0325 tackles the next failure mode: when the real June 2026 exercise window arrives, the raw evidence may be lost, overwritten, redacted before it is hashed, or replaced by polished summaries. The cube now needs a live evidence-bag and alert-archive bridge that makes raw artifacts preservable, hashable, redaction-safe, and still unable to self-certify readiness.

## Operating rule

A live evidence bag may be accepted only as one of these states: `reject_closure_attempt`, `hold_no_upgrade`, `context_no_upgrade`, `accepted_reopen_signal`, or `candidate_for_adjudication_not_closure`. No state is automatic local closure.

Public alert archives, public message viewers, public schedules, public AAR text, public event notifications, and public fact sheets can corroborate timestamps, trigger a discrepancy, reopen a claim path, or demand local evidence. They cannot close local readiness rows.

## What changed

- Added an evidence-bag manifest schema with original hash, redacted-surrogate hash, source clock, chain-of-custody, sensitive-annex split, packet linkage, and counterevidence path fields.
- Added a minute-zero capture checklist for alert-originator, PIO/JIC, EOC scribe, controller/evaluator, AFN/school/LTC/hospital transport, route-control, CRC/decon, field monitoring, ingestion sampling, worker dosimetry, and EN58200 EOF non-regression evidence.
- Added an alert-archive triangulation table that separates local originator logs, IPAWS OPEN acknowledgements, EAS/WEA evidence, county alert-vendor records, FEMA IPAWS Message Viewer checks, OpenFEMA archived CAP records, and public-meeting/transcript sources.
- Added a CAP message validation profile so alert packets have field-level checks for identifier, sender, sent time, status, message type, scope, event, urgency, severity, certainty, instruction, area/geocode, references, and parameters.
- Added a live evidence-bag builder script and a deterministic validator fixture. The builder computes SHA-256 hashes and produces a manifest, packet JSON, sensitive-annex map, and public surrogate map. The validator proves the cube still rejects public-context closure, self-attested closure, missing hashes, custody gaps, and raw-log loss.

## Why it matters operationally

The most fragile artifacts are not usually polished AAR paragraphs. They are raw alert payloads, acknowledgement/error logs, clock provenance, screenshots before links change, evaluator observations before dispute resolution, and CAP/retest evidence before ownership blurs. Rev0325 makes absence of those artifacts a cap, not neutral missingness.

## What this revision still does not do

No real Beaver Valley readiness or unreadiness claim is made. `REAL_BVPS_PUBLIC_ONLY` remains public-context-only. The new scripts and tables are ready to receive actual/anonymized exercise evidence, but the package does not fabricate those packets.
