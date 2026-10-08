# 119 — OONI Corroboration (Supplementary)

**Track:** A (Deployable core)


OONI measurements can corroborate large-scale blocking events and help distinguish “local outage”
from “policy interference”. For this pack, OONI is **supplementary**: it cannot replace direct evidence
of reachability for your own endpoints, but it can strengthen narratives about regional censorship.

## Use cases
- Confirm that a jurisdiction shows elevated blocking of HTTPS/DNS generally
- Confirm that similar domains/services are blocked in the same ASN/country window
- Provide independent third-party context during disputes

## What not to do
- Do not treat OONI as a real-time SLA monitor.
- Do not over-interpret single measurements; prefer trends and multiple probes.
- Do not use OONI data to target or identify individuals.

## Implementation sketch
1. Query OONI API for relevant tests around time window W (country, ASN, domain category).
2. Extract aggregate indicators (block rate, anomaly rate) and store references in evidence bundle.
3. If possible, corroborate using at least one other source (RIPE Atlas, internal probes).

## Artifacts
- `schemas/OONICorroboration.json`
- Example: `artifacts/examples/ooni_corroboration_example.json`
- Tool: `tools/ooni_corroborator.py` (research/prototype; defaults to no-network schema-shaped pointers and never embeds raw measurement bodies)
