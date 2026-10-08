# 148 — Challenge selection and coverage metrics

**Track:** A (Deployable core)


This document defines what it means for monitor inspections to have *meaningful coverage*.

## Coverage dimensions

Coverage is measured across:

1. **Targets**: endpoints / domains / jurisdictions / locales / API variants.
2. **Time**: continuous coverage through election phases (setup, voting, tally, audits).
3. **Perspective**: network vantage diversity (ASNs, regions), and implementation diversity (different watcher stacks).
4. **Artifact types**: inclusion proofs, consistency proofs, witness cosignatures, evidence bundles, alerts.

## Required metrics

Each reporting interval produces a signed `InspectionCoverageReport` containing:

- target sample size and selection parameters
- diversity metrics (ASN entropy, region distribution)
- challenge issuance rate and response rate
- missed-deadline counts and suppression reports
- cross-watcher agreement rate

## Minimum coverage SLOs (illustrative defaults)

- ≥ 2 independent watchers per monitor per day
- ≥ 95% responses within deadline (or signed suppression report)
- ≥ 80% of targets touched over rolling 7-day window
- no single ASN > 20% of the probe cohort for network-dependent checks

These values are policy choices; publish them pre-election and pin them into the EPB.

## Interactions with privacy

Coverage work can leak meta-information. Prefer:
- privacy-preserving submission layers (OHTTP/ODoH) for voter-facing flows
- public artifacts for monitor-facing flows
