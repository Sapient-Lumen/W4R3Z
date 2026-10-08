# Audience-targeted suppression and parity

**Track:** A (Deployable core)


## Problem
Attackers can selectively suppress or mutate evidence for specific:
- regions / ASNs
- languages
- device classes

This creates “it worked for me” disputes.

## Parity property
At time t, for each artifact class (checkpoint, bundle, drift alert, revocation notice):
- all audiences should see the same **content-addressed hash** within bounded delay.

## Mechanism
- periodic **ParityProbes** from diverse vantages
- emit signed **ParityReport** objects, anchored into PBB/ATL

See:
- `schemas/ParityProbeResult.json`
- `schemas/ParityReport.json`

## Normative requirements
- **MUST** probe UI and API endpoints, not just one.
- **MUST** include locale variants in probe set.
- **MUST** publish ParityReports on a fixed schedule.
- **MUST** define parity SLOs and escalation triggers.

## Escalation
- If parity fails: publish a DriftAlert-like statement, rotate mirrors, and (if needed) freeze intake.