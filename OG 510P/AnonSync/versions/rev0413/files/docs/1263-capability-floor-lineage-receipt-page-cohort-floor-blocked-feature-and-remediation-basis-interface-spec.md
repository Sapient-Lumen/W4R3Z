# Capability-floor lineage receipt page: cohort floor, blocked feature, and remediation basis interface spec

## Purpose

This receipt is the exportable proof for a capability-floor judgment.
It exists so the operator can answer later:

> why did the product refuse to claim more, which member set the floor, and what exactly had to change before the stronger claim became true?

## Receipt contents

The receipt must preserve:

- `capability_floor_id`
- subject ref
- issuance time
- byte-compatibility grade
- cohort major floor
- platform support floor
- product lane floor
- feature claim ceiling
- governing blockers
- strongest safe sentence
- blocked stronger sentence
- recommended remediations
- evidence freshness

## Human-readable summary

Example summary:

- `Bytes remain interoperable across this cohort, but the truthful feature envelope is capped by one Business-held v2 NAS member and one mixed-major linked family. Cohort-wide v3 management claims remain blocked until those blockers are resolved.`

## Hard rules

- the receipt must always separate `can still sync bytes` from `can safely claim feature parity`
- governing blockers must be named individually
- remediation steps must preserve whether each blocker is removable, permanent, or policy-held
- the blocked stronger sentence must survive export intact
