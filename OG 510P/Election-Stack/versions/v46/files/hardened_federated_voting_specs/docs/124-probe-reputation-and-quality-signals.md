# Probe reputation and quality signals

**Track:** A (Deployable core)


This document specifies a *defensive* approach to scoring the trustworthiness and measurement quality of probes/vantage points.

It does **not** claim to “prove” a probe is honest. Instead, it provides:
- measurable **quality** indicators (noise/interference)
- measurable **health** indicators (stability/uptime)
- measurable **consensus** indicators (agreement with peers)

## Inputs

### I1. Bias awareness
Measurement infrastructures can be biased in geographic and AS distribution; any “representativeness” claim must be grounded in a cohort plan and audit report.

### I2. Interference awareness
Measurements can interfere with each other, impacting precision and synchrony. Quality scoring MUST incorporate concurrent-load proxies and variance patterns.

### I3. Platform security events
Platform security disclosures may indicate probe-transfer/administrative weaknesses; probe trust weighting MUST be updated accordingly.

## Reputation model (recommended)

Each probe gets a `ProbeReputationRecord` updated periodically:
- `availability_score` (fraction of successful scheduled checks)
- `stability_score` (latency/packet-loss variance over time)
- `consistency_score` (agreement with peer probes in similar geo/topology)
- `interference_score` (evidence of concurrent-measurement distortion)
- `integrity_flags` (platform security flags, suspicious changes in metadata, sudden ASN changes)
- `confidence` (low/medium/high; conservative default: low)

## Operational rules

**R-1:** Low-confidence probes MUST NOT be used as the sole basis for any “unreachability proof.”

**R-2:** If probes disagree significantly (bimodal results), the system MUST:
- produce a `CohortAuditReport` delta
- trigger additional corroboration using independent vantage sources

**R-3:** Reputation scoring code MUST be reproducible and versioned; scoring runs MUST be logged and hash-anchored in the evidence pipeline.

## Deliverables
- `ProbeReputationRecord.json` (schema)
- `tools/probe_reputation_scorer.py` (reference implementation skeleton)