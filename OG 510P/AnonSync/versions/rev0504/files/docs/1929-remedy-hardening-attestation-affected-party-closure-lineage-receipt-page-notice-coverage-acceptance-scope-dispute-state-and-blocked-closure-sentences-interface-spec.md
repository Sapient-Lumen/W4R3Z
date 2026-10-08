# Remedy-hardening-attestation affected-party-closure lineage receipt page — notice coverage, acceptance scope, dispute state, and blocked closure sentences

## Purpose

This page is the durable one-receipt summary for the closure phase.
It lets a later operator read one artifact and know exactly how far the case progressed from operational remediation into affected-party delivery, acknowledgement, acceptance, uncontested lapse, or contest.

## Receipt fields

- receipt identifier
- case identifier
- source downstream-effects receipt identifier
- current affected-party-closure class
- required materially affected cohort
- named reached cohort
- named acknowledged cohort
- named accepted cohort
- named contested cohort
- unknown or unreachable cohort flag
- open objection windows summary
- lapsed objection windows summary
- reopen risk summary
- highest honest closure sentence
- blocked stronger closure sentence
- evidence bundle references
- issued-at timestamp

## Primary sentence block

The receipt must begin with exactly two lines:

- **Highest honest closure sentence**
- **Blocked stronger closure sentence**

## Required sections

1. **Who materially had to be told**
2. **Who was actually reached**
3. **Who acknowledged, accepted, contested, or stayed silent**
4. **Which objection windows remain live or reopened**
5. **Why the next stronger closure sentence is still blocked**

## Hard rules

The receipt must never let:

- `operational remediation complete` impersonate `case closed`
- `one delivered notice` impersonate `all materially affected parties reached`
- `no visible contest` impersonate `uncontested closure`
- `acknowledged` impersonate `accepted`
- `accepted by one cohort` impersonate `global final closure`
