# 86 — Exercises & Gamedays Program (Operational Paranoia)

**Track:** A (Deployable core)


## Purpose
A system that is *cryptographically correct* can still fail catastrophically under real attack because the humans, comms, and operational dependencies (DNS, BGP, CDNs, identity proofing, vendors) fail.

This document defines an **exercise program** that produces measurable operational readiness:
- detect attacks quickly (no “silent failure”),
- communicate accurately without over-claiming,
- execute fallbacks (including paper-of-record paths),
- preserve court-usable evidence.

## Inputs
- Threat model (`01-threat-model.md`)
- Incident playbooks (`08-operations.md`, `72-status-page-and-communications-under-attack.md`)
- Evidence bundles (`37-public-evidence-and-disinformation-resilience.md`)

## Exercise types
1) **Tabletop exercises (TTX)** — decision-making, comms, escalation, legal posture.
2) **Gamedays** — controlled technical failures in staging or limited production.
3) **Red team / purple team** — adversarial validation of assumptions.
4) **Partner drills** — witnesses, trustees, VRDB operators, CDN/DNS/BGP providers.

## Cadence (minimum)
- **Quarterly TTX** (pre-election + post-election)
- **Monthly gameday** in non-election periods
- **Pre-election freeze drills**: 2 drills in the 6 weeks before opening
- **Election week**: daily comms+status rehearsal (15 minutes) with escalation tree

## Required roles
- Incident commander (IC)
- Comms lead (public statements)
- Legal liaison
- Federation operations lead
- Witness coordinator
- Trustee coordinator
- VRDB / eligibility lead
- Security lead (forensics)
- Product/UX lead (receipt truthfulness)

## Required outputs (artifacts)
Each exercise MUST produce:
- an **After Action Report (AAR)** (template in `artifacts/templates/after-action-report.md`)
- a signed **ExerciseEvidenceBundle** (hash list of logs, screenshots, checkpoints)
- updated runbooks/checklists and measurable action items

## Minimum scenario coverage
Within a 12-month cycle, cover at least:
- DDoS / outage + selective censorship evidence
- Split-view equivocation attempt (fork proof path)
- Witness quorum loss + degraded mode
- Trustee share compromise simulation + emergency freeze
- Eligibility issuer compromise / mass revocation attempt
- VRDB integrity incident (rollback attempt)
- ENR drift / fake-results injection
- Ballot-definition substitution attempt (split ballot styles)
- Supply-chain incident (malicious update / compromised CI)

## Pass/fail criteria (examples)
- **No false “RECORDED” receipts** in any outage scenario
- Fork proof is produced within N minutes of split-view detection
- Public statement issued within 30 minutes with correct uncertainty language
- Evidence bundle published (or prepared) with correct hashes/checkpoints
- Fallback path executed without “unknown” states for voters

## Interfaces to external exercise libraries
Where possible, adapt existing election security tabletop exercise packages and communications guides, but keep system-specific artifacts (PBB checkpoints, proofs, EPB hashes) as the “hard facts” that comms references.