# Probe cohort selection fairness

**Track:** A (Deployable core)


## Why this matters
Multi-vantage evidence is only as credible as the *vantage cohort*.
Measurement platforms (e.g., volunteer-hosted probes) can be biased by region, network type, and volunteer demographics.

Goal: choose cohorts that are:
- **diverse** (geography, ASN, access type)
- **reproducible** (same inputs → same cohort)
- **fair** (no systematic under-coverage of targeted audiences)

## Threats
- attacker claims “your probes are all in Europe / all in big ISPs”
- selective suppression affects only under-sampled audiences
- probe cohort is quietly changed during election week

## Cohort policy
Define a signed `ProbeCohortPlan`:
- target N probes
- quotas by continent/country (or other jurisdictional grouping)
- quotas by ASN / ASN type (stub vs ISP)
- caps per organization
- minimum diversity score (topology-aware optional)

See `schemas/ProbeCohortPlan.json`.

## Practical selection strategies
- **Quota + round-robin**: simple, explainable.
- **Topology-aware diversity**: select dissimilar probes (RTT/AS-path features).
- **Two-cohort approach**:
  - a stable baseline cohort (comparability)
  - a rotating “canary cohort” (broader reach)

## Governance requirements
- **MUST** publish cohort plan before polls open.
- **MUST** anchor cohort plan hash into EPB.
- **MUST** treat mid-election cohort changes as incidents unless pre-authorized.

## References (see `references.md`)
- Work highlighting Atlas sampling bias and probe selection diversity methods.