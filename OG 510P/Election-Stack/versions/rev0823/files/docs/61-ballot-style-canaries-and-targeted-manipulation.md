# 61 — Ballot-style canaries and targeted manipulation detection

**Track:** A (Deployable core)


This document addresses a specific high-impact threat:

> **Targeted manipulation**: an attacker serves a *different* ballot definition (or ballot style assignment) to a subset of voters.

This can happen even when the main bulletin board is correct, via:
- DNS/BGP diversion,
- compromised CDN edge,
- malicious browser extension,
- compromised registration/ballot-style service,
- selective censorship + replay.

## Design principle
Treat ballot definition integrity like transparency logs treat certificates:
- **publish**, **witness**, **gossip**, **prove equivocation**.

## Canary types
### A) Retrieval canaries (network diversity)
Monitors retrieve the EPB + BD bundle via:
- multiple ISPs/ASNs
- multiple regions
- different resolvers
- multiple client stacks

They record:
- endpoint reached
- EPB hash and inclusion proofs
- BD hash
- TLS/cert metadata (for incident forensics)

### B) Style-assignment canaries (ballot-style mapping)
Monitors validate that a set of canonical voter contexts map to the correct ballot style.
- Inputs: precinct/district identifiers.
- Outputs: ballot_style_id + contests list.

**MUST:** mapping results are deterministic and auditable.

### C) Voter-facing “hash pin” UI
Clients display:
- EPB short hash (e.g., first 10 chars)
- BD short hash
- witness checkpoint ID

This makes social verification possible (“my screen shows EPB 7f3a…; does yours?”).

## Evidence objects
When canaries detect variance, they MUST emit a signed evidence bundle:
- request transcript (sanitized)
- response payload hashes
- inclusion proofs
- witness checkpoint references

This bundle is designed to be court-usable and should be cross-anchored (see multi-log notarization doc).

## Response playbook (minimum)
1. **Stop-the-world** for the affected scope (precinct/region).
2. Publish evidence bundles immediately.
3. Move affected voters to **paper-of-record** fallback.
4. If variance suggests systemic compromise, invalidate EPB and re-run parameter ceremony.

## Coverage secrecy and post-election provability

Canaries are a detection surface. If attackers learn exactly which demographic/geographic combinations are covered, they can route around them.

Recommended pattern:
- publish *aggregate* representativeness metrics (docs/174), and
- publish a **commitment digest** to the full canary plan (salted hash of plan bytes) in a CoverageReport field:
  - `CoverageReport.commitments.canary_plan_commitment_sha256` (schema updated).

After the election (or upon court order), the plan can be revealed to auditors who can verify it matches the earlier commitment.

## Artifacts in this pack
- `artifacts/checklists/canary-monitoring-checklist.md`
- `artifacts/templates/public-status-page.md` (use to communicate incidents without ambiguity)

## References
- RFC 9162 (transparency log patterns).
- Routing security references (RPKI/ROV best practices; stealthy diversion threats).