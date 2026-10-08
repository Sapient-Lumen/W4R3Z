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
- a bounded log row in `artifacts/registries/drill-runs.csv` (run_id + scenario_id + pointers to the outputs below)
- a signed **ExerciseEvidenceBundle** (hash list of logs, screenshots, checkpoints)
- digest pins for any public packets created during the exercise (PublicNotice packets, parity snapshots, coverage/suppression reports, PacketVerificationReports)
- updated runbooks/checklists and measurable action items

## Checklist → capability rule (anti-theater)

A checklist or playbook is *not* a deployed capability unless it is exercised.

Therefore:
- if you add or materially change an operator checklist/playbook, also add/update a drill scenario (`artifacts/registries/drill-scenarios.csv`),
- specify the expected publishable outputs (AAR + packet pointers/digests),
- and schedule at least one tabletop run before treating it as “ready”.

Record the run as **planned** before it happens (status=`planned` with expected outputs), and mark it **completed** after the run with bounded pointers (AAR + notice IDs + packet digests; include TTR/MAPT log row IDs if applicable).

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

- **Human stress drills (required):**
  - Conflicting reports / information overload → `scenario_id: conflicting_reports_overload`
  - Political pressure to publish unverified claims → `scenario_id: political_pressure_unverified_claims`
  - Political pressure to prematurely expand scope (remote ballot return) → `scenario_id: premature_promotion_remote_return`
  - Forged “official statement” circulates (time-to-refute) → `scenario_id: forged_official_statement_time_to_refute`
  - Legibility-theater publication drop (exists-but-not-usable) → `scenario_id: legibility_theater_publication_drop`
  - (See `artifacts/registries/drill-scenarios.csv` for canonical pointers.)

## Pass/fail criteria (examples)
- **No false “RECORDED” receipts** in any outage scenario
- Fork proof is produced within N minutes of split-view detection
- Public statement issued within 30 minutes with correct uncertainty language
- TTR‑1 (signed verdict notice) and TTR‑2 (offline-verifiable refutation packet) recorded and compared against targets for any rumor/authenticity drill (`docs/240`; `artifacts/templates/time-to-refute-test-plan.md`); log row(s) in `artifacts/registries/time-to-refute-evaluations.csv`
- Evidence bundle published (or prepared) with correct hashes/checkpoints
- Fallback path executed without “unknown” states for voters
- **No unverified claim is published as fact** under political pressure (use epistemic tags + correction workflow).
- Rumor-control / authenticity verdict notice published with a digest and replay path within the deployment’s time-to-refute target (`194`, `240`).


## Interfaces to external exercise libraries
Where possible, adapt existing election security tabletop exercise packages and communications guides, but keep system-specific artifacts (PBB checkpoints, proofs, EPB hashes) as the “hard facts” that comms references.
