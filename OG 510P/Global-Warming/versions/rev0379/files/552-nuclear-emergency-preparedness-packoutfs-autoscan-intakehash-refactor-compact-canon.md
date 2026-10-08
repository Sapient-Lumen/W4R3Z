# 552 — Nuclear emergency preparedness: packout filesystem materialization, autoscan, intake hashing and redaction pairing preflight

Revision: rev0345  
Created: 2026-06-05T12:04:00-04:00  
Scope: `REAL_BVPS_PUBLIC_ONLY`; no real-site readiness or unreadiness claim.

## Why this revision exists

Rev0344 merged the evidence warroom and event-day packout, but the package still had a practical field defect: `cube/nuclear-emergency-bvps-evidence-bag-folder-map-rev0343.csv` described 240 required packet subfolders while the actual packet skeletons were mostly packet-level README directories. That is not enough for a live capture operation.

Rev0345 materializes the filesystem and adds autoscan/hash/redaction-pairing machinery. The point is operational: an event-day packet owner should have somewhere concrete to put the original, redacted surrogate, custody record, and QA/adjudication note, and the cube should immediately classify empty folders as **not evidence**.

## Hard rule

A folder, README, placeholder, label, public notice, public meeting statement, preliminary finding, AAR paragraph, dashboard, PI page, MSEL event, extent-of-play statement, source ID, duplicate URL, redacted surrogate, warroom status row, owner acknowledgement, packet skeleton, or complete-looking local packet can demand, cap, route, contradict, or reopen a claim. It cannot automatically close local emergency-readiness evidence.

## Operational route

`packet cutline → physical folder materialization → autoscan/hash index → redaction/surrogate pairing check → custody/QA check → loss-cap board → adjudication docket → CAP/retest/verifier → integrated claim kernel`

## What changed

- Materialized all 240 required `raw/`, `redacted/`, `custody/`, and `qa/` packet subfolders.
- Added non-evidence README placeholders to preserve folders inside the zip.
- Added a scanner that counts payloads, detects missing subfolders, and keeps loss caps active when only skeletons exist.
- Added a redaction/surrogate pairing autocheck and placeholder hash index.
- Added an owner-grouped operator clipboard so the warroom can act without reading the entire cube.

## Claim boundary

No real/anonymized June 2026 exercise packets are imported. All 60 must-capture packets are `skeleton_ready_no_evidence` and remain loss-capped. This revision does not claim Beaver Valley, Pennsylvania, West Virginia, Ohio, any county, ORO, evaluator, controller, alerting authority, EOC/EOF/JIC, or facility is ready, unready, green, failed, passed, certified, safe, sufficient, reasonable-assurance-ready, demonstrated, or closed.
