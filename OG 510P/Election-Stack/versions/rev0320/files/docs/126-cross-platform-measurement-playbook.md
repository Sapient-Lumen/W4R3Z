# Cross-platform measurement playbook (corroboration without over-claiming)

**Track:** A (Deployable core)


Goal: corroborate availability/censorship claims using **independent measurement sources**, while respecting ethics and avoiding scan-like behavior.

## Principles

- Treat supplementary platforms as *context*, not oracle truth.
- Avoid broad scanning. Prefer **allow-listed targets**, modest rates, and public datasets/APIs.
- Publish the *raw result hashes* and the reduction code version.

## Recommended sources

### RIPE Atlas (primary)
- Active reachability/latency/DNS/HTTP measurements from diverse probes.
- Use cohort fairness + anti-capture controls.

### OONI (supplementary)
- Use OONI data as corroboration signals for interference/blocking patterns, with careful interpretation.

### Censorship measurement methodologies (background)
- Maintain a taxonomy of blocking techniques and measurement pitfalls to avoid false positives.

## Practical runbooks

### Runbook A: “Region X cannot reach evidence portal”
1. Trigger Atlas HTTP + DNS measurements from a cohort with strong diversity and anti-cluster constraints.
2. Fetch results in a bounded window; construct `UnreachabilityProof` with raw hashes.
3. Query OONI datasets for corroboration signals in the region/timeframe (if available).
4. Publish `DriftAlert`/`OutageAttestation` + URP anchored in the ATL/PBB.

### Runbook B: “Application-layer blocking suspected”
Use methods that distinguish DNS poisoning vs SNI/HTTP blocking vs TCP reset patterns. Prefer minimal tests; avoid disruptive payloads.

## Deliverables
- `OONICorroborationRecord` (existing schema) used as supplementary evidence
- playbook checklists and ethics guardrails used for every incident evidence bundle