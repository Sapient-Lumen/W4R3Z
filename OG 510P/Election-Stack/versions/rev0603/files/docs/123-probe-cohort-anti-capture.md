# Probe cohort anti-capture (making “multi‑vantage evidence” hard to game)

**Track:** A (Deployable core)


This document hardens the *measurement/evidence* layer against a subtle but likely strategy:

> An attacker does not change the election cryptography; instead they try to ensure the **probe cohort** (or the paths to probes) are sufficiently **biased, controlled, or filtered** that “unreachability proofs” and parity monitoring miss the real incident — or become non-credible (“your probes are compromised / not representative”).

## Threats

### T1. Probe capture / hostile vantage points
A portion of probes are adversary-controlled (compromised devices, coerced hosts, malicious volunteers), producing *plausible* but wrong measurements.

### T2. Cohort manipulation by topology
The attacker doesn’t need to compromise probes; they can bias which probes are selected (e.g., only friendly ASNs, only certain regions) or ensure the “diverse” cohort has common-path dependencies (same upstreams).

### T3. Measurement platform exploitation
Measurement platform weaknesses (API flaws, device transfer bugs, firmware issues) allow a motivated attacker to influence where a probe runs or what it reports.

### T4. Measurement interference / quality degradation
Concurrent measurements can degrade precision/synchrony, and an attacker can “hide” censorship/outage effects inside noisy data.

## Requirements (normative)

**AC-1 (Cohort diversity):** Every `ProbeCohortPlan` MUST enforce diversity constraints across:
- country / region
- ASN (and ideally “organization”)
- access type (eyeballing: eyeball ISP vs datacenter vs academic)
- IPv4 and IPv6 reachability

**AC-2 (Cross-platform redundancy):** Critical assertions (e.g., “service unreachable from region X”) MUST be corroborated by at least **two independent vantage sources** when feasible:
- RIPE Atlas probes
- internal probes operated by independent stakeholders
- other public measurement platforms (e.g., OONI as supplementary context)

**AC-3 (Probe integrity signals):** Cohort selection MUST incorporate probe integrity/health signals (see `124-probe-reputation-and-quality-signals.md`). Probes with “unknown/low confidence” SHOULD be down-weighted or excluded.

**AC-4 (Platform security posture):** Operators MUST track platform security disclosures and apply policy updates (e.g., “probe transfer” incidents) to cohort selection and trust weighting.

**AC-5 (Adversarial cohort audit):** A signed `CohortAuditReport` MUST be produced on a schedule (at least: pre-election, mid-election, post-election) and anchored to the bulletin board.

## Practical mitigations

### M1. Probe reputation scoring (soft trust, not absolute trust)
Maintain a `ProbeReputationRecord` for each probe used, based on:
- long-term stability (availability/latency variance)
- agreement with other probes in similar topology/geo
- historical consistency across measurement types
- platform-provided metadata (hardware generation, “home-tag” where applicable)

### M2. Cohort “anti-cluster” selection
Augment simple diversity constraints with anti-clustering heuristics:
- avoid selecting probes that share the same upstream ASNs or IXPs (when known)
- cap selection from any single AS / organization

### M3. Evidence bundling that preserves raw inputs
Every `UnreachabilityProof` MUST include:
- raw measurement result hashes
- the cohort plan hash
- tool/version hashes (to make re-computation possible)

### M4. Interference-aware measurement windows
Use measurement planning that reduces self-interference (avoid launching overlapping heavy traceroutes/pings at the same probes, or annotate results with a “confidence index” / concurrent-load metadata).

## Output artifacts
- `ProbeCohortPlan` (signed and anchored)
- `CohortAuditReport` (signed and anchored)
- `ProbeReputationRecord` (signed, versioned; can be published as part of evidence bundles)