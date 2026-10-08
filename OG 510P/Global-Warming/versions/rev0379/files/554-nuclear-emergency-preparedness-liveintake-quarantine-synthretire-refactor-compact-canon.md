# 554 — Nuclear emergency preparedness: live-intake quarantine, synthetic retirement, and replacement gate

## Purpose

Rev0347 closes the next operational gap after the rev0346 synthetic-payload dry run: the package can now receive live or anonymized evidence **without letting synthetic dry-run files, folders, public pages, or partial packets become readiness evidence**.

The new model is a replacement and quarantine lane:

`synthetic dry-run payload → synthetic-retirement ledger → live/anonymized intake quarantine → hash/custody/redaction/source-clock checks → candidate-for-adjudication only → CAP/retest/verifier → integrated claim kernel`.

## Hard rule

A folder, README, placeholder, synthetic payload, copied synthetic file, public notice, public meeting statement, preliminary finding, AAR paragraph, dashboard, PI page, MSEL event, extent-of-play statement, source ID, duplicate URL, redacted surrogate, warroom row, owner acknowledgement, packet skeleton, hash-only packet, or complete-looking local packet can demand, cap, route, contradict, or reopen a claim. It cannot automatically close local emergency-readiness evidence.

## Why this revision exists

Rev0346 intentionally seeded 24 synthetic packets. That proved the filesystem/hash/custody/redaction path, but it created a new risk: synthetic payloads could later be mistaken for real evidence, copied into live folders, or treated as a predecessor to closure.

Rev0347 makes that impossible by default. Synthetic payloads are explicitly retired only by a replacement packet that passes quarantine checks. A replacement packet still becomes only `candidate_for_adjudication_not_closure`, never automatic readiness closure.

## Operational route

1. Quarantine every live/anonymized packet before it can enter an adjudication docket.
2. Reject synthetic-to-real contamination, public-context-only evidence, hash-only files, redacted-only files, ownerless packets, custody gaps, stale clocks, and source-ID duplication.
3. Retain the loss cap until a replacement packet is adjudicated, retested where needed, independently verified, and passed through the public-claim kernel.
4. Keep the `REAL_BVPS_PUBLIC_ONLY` boundary: no real Beaver Valley readiness or unreadiness claim is made.

## New evidence surfaces

- `cube/nuclear-emergency-bvps-live-intake-quarantine-gate-rev0347.csv`
- `cube/nuclear-emergency-bvps-synthetic-payload-retirement-ledger-rev0347.csv`
- `cube/nuclear-emergency-bvps-live-replacement-minimum-packet-rev0347.csv`
- `cube/nuclear-emergency-bvps-quarantine-filesystem-materialization-rev0347.csv`
- `cube/nuclear-emergency-bvps-live-intake-validator-result-rev0347.csv`
- `cube/nuclear-emergency-bvps-live-intake-open-workorders-rev0347.csv`

## Claim boundary

This revision improves live-intake mechanics and synthetic-retirement controls. It does not import real June 2026 exercise evidence and does not claim that any site, jurisdiction, alerting authority, ORO, EOC/EOF/JIC, evaluator, controller, packet, or facility is ready, unready, green, failed, passed, certified, safe, sufficient, reasonable-assurance-ready, demonstrated, or closed.
