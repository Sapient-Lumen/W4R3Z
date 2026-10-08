# 531 — Nuclear Emergency Preparedness Packet Dry-Run, Adjudication, Loss-Cap, and Root-Schema Refactor — Compact Canon

## Purpose

This revision closes the gap between a packet catalog and an executable packet intake path. Rev0323 defined the field-packet templates. Rev0324 adds a dry-run import bundle, row-level field values, validator output, chain-of-custody timeline checks, adjudication-board docket, evidence-loss default caps, and public-claim gates.

The governing rule is deliberately conservative:

> A packet can be imported only as **rejected**, **hold/no-upgrade**, **context/no-upgrade**, **accepted reopen signal**, or **candidate for adjudication, not closure**. No packet auto-closes a local emergency-preparedness readiness row.

## Priority risk addressed

The riskiest near-term failure is no longer a missing registry. It is that field evidence collected around the June 2026 Beaver Valley exercise could be incomplete, unhashable, unverifiable, or converted into a readiness claim before CAP/retest and independent verification exist. Rev0324 therefore makes the dry-run import path strict enough to reject common false closures: public schedules, public AAR paragraphs, public ETE tables, public mass-care numbers, unverified revised templates, self-attested retests, missing acknowledgment/error logs, custody gaps, and public event-notification text.

## New operational surfaces

- `cube/nuclear-emergency-bvps-packet-dryrun-bundle-catalog-rev0324.csv`
- `cube/nuclear-emergency-bvps-packet-field-values-dryrun-rev0324.csv`
- `cube/nuclear-emergency-bvps-packet-import-validation-rev0324.csv`
- `cube/nuclear-emergency-bvps-packet-to-blocker-adjudication-queue-rev0324.csv`
- `cube/nuclear-emergency-bvps-evidence-chain-of-custody-timeline-dryrun-rev0324.csv`
- `cube/nuclear-emergency-bvps-chain-of-custody-break-audit-rev0324.csv`
- `cube/nuclear-emergency-bvps-evidence-loss-default-cap-application-rev0324.csv`
- `cube/nuclear-emergency-bvps-public-claim-state-after-dryrun-rev0324.csv`
- `cube/nuclear-emergency-bvps-packet-closure-negative-control-rev0324.csv`
- `tools/import_nuclear_emergency_bvps_packet_bundle_rev0324.py`

## Query-route refactor

The current query path is now:

`packet template -> row-level field values -> validator -> chain-of-custody audit -> adjudication queue -> evidence-loss cap -> public-claim gate -> no auto-closure`

This is intentionally narrower than a readiness score. It is an intake and triage path.

## Audit correction

Rev0323 fixed `cube/schema.json`, but the root-level `schema.json` still reported rev0322. Rev0324 fixes that root-schema lag and adds a validation check to prevent the package-level schema and cube-level schema from diverging again.

## Claim boundary

`REAL_BVPS_PUBLIC_ONLY` remains public-context-only. Synthetic dry-run rows prove the import machinery; they do not claim that Beaver Valley, Pennsylvania, West Virginia, Ohio, any county, or any facility is ready or unready.
