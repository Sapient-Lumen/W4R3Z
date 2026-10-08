# 90 — Exercise Scenario Library (Election Ops Reality)

**Track:** A (Deployable core)


## Overview
This library provides scenario “cards” for tabletop exercises and gamedays.

Each scenario includes:
- Trigger
- Technical reality (what can actually happen)
- Decision points
- Required public artifacts (hashes/checkpoints)
- Pass/fail criteria

## Scenario cards

### S1 — DDoS + selective ballot dropping
- Trigger: spike traffic, certain ASN/regions can’t reach gateways
- Reality: receipts may show PENDING but never RECORDED
- Decision: when to declare degraded vs incident; when to freeze intake
- Artifacts: missed-deadline evidence, status page statement, checkpoint gaps

### S2 — Split-view (equivocation) attempt
- Trigger: witnesses see different STHs for same tree size
- Reality: log operator compromised or partitioned
- Decision: declare incident, instruct verifiers to reject non-quorum checkpoints
- Artifacts: ForkProof, witness-gossip transcript, public statement

### S3 — Ballot definition substitution
- Trigger: canary detects different BD hash served to subset
- Reality: targeted manipulation by CDN/DNS or app update
- Decision: freeze, republish EPB, advise voters, reissue ballots
- Artifacts: BD hash diff, EPB inclusion proof, canary evidence bundle

### S4 — VRDB rollback attempt
- Trigger: VRDB snapshot hash regresses; mass precinct mapping changes
- Reality: integrity incident or operational error
- Decision: switch to signed offline pollbooks, investigate, publish diffs
- Artifacts: snapshot chain, change alert, comms pack

### S5 — ENR drift + fake results injection
- Trigger: public website shows totals that fail verifier check
- Reality: CDN or CMS compromise, misconfigured feed, or malicious insider
- Decision: disable ENR, publish signed ResultsReleasePackage + guidance
- Artifacts: drift alert, anchored canonical results object

### S6 — Credential recovery fraud wave
- Trigger: spike in recovery requests from targeted region
- Reality: social engineering, coercion, or compromised proofing vendor
- Decision: tighten proofing, enable in-person rapid issuance, publish advisory
- Artifacts: recovery event log, mass-incident checklist outputs

## Templates & schemas
- Exercise plan: `schemas/ExercisePlan.json`
- After action: `schemas/AfterActionReport.json`
- Templates: `artifacts/templates/after-action-report.md`