# Adversarial cohort audits (prove your probes are not a monoculture)

**Track:** A (Deployable core)


This document defines `CohortAuditReport` and how to generate it so “your probes are biased/controlled” becomes a *testable claim*.

## Audit questions

1. **Representativeness:** Does the cohort cover the jurisdictions and networks we need?
2. **Correlation risk:** Do “diverse” probes share hidden common dependencies (same upstreams)?
3. **Integrity drift:** Did probe metadata change unexpectedly (ASN/geo/host tag)?
4. **Platform events:** Did the measurement platform disclose incidents affecting probe integrity or administration?
5. **Measurement load:** Were probes affected by interference from concurrent measurements?

## Minimum audit content (normative)

A `CohortAuditReport` MUST include:
- the referenced `ProbeCohortPlan` hash
- distribution stats: country, ASN, network type buckets
- “anti-cluster” stats: top-k ASNs, max share thresholds
- a list of excluded probes with reasons (low confidence, integrity flags, interference)
- references to any platform security disclosures relevant to the audit window
- hash pointers to raw data used for the audit

## Red-team “cohort capture” exercises
During pre-election drills, run scenarios where:
- 30–40% of probes are assumed adversary-controlled
- selected ASNs are filtered / re-routed
- evidence endpoints are split-view

Then confirm:
- detection probability meets target (see `122-detection-probability-simulation-harness.md`)
- audits identify the failure modes and trigger cross-platform corroboration

## Deliverables
- `CohortAuditReport.json` (schema)
- `tools/cohort_audit_reporter.py` (reference skeleton)