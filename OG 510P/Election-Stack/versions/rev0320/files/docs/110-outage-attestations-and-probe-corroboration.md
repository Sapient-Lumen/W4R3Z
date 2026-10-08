# Outage attestations and probe corroboration

**Track:** A+C (Core + North Star)


## OutageAttestation
A signed claim that a specific endpoint/artifact class was unreachable or split-delivered.

Fields include:
- affected endpoints
- time window
- probe evidence references (hashes)
- mitigation actions taken

See `schemas/OutageAttestation.json`.

## Corroboration
Attach:
- internal probe results
- external multi-vantage results (e.g., RIPE Atlas)

## Normative requirements
- **MUST** include at least one corroborating source independent of the affected operator.
- **MUST** hash raw probe result sets and publish reduction method.
- **MUST** anchor attestations into ATL within MAAD.