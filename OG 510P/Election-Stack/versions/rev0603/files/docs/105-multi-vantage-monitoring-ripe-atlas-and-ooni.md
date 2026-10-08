# Multi-vantage monitoring: RIPE Atlas and OONI

**Track:** A (Deployable core)


## Goal
Generate **portable evidence** that an endpoint was unreachable, delayed, or split-delivered.

## Primary platform: RIPE Atlas
Use Atlas to run targeted, non-invasive checks from many ASNs/regions:
- DNS resolve
- HTTPS fetch
- ping/traceroute

Outputs feed:
- `UnreachabilityProof` (`schemas/UnreachabilityProof.json`)
- `AvailabilityProbeResult` (`schemas/AvailabilityProbeResult.json`)

## Supplementary platform: OONI
Use OONI open data as context:
- evidence of censorship events in a region
- do not over-claim causality

## Normative requirements
- **MUST** define allowed target list (no scanning).
- **MUST** cap rate/volume and follow platform terms.
- **MUST** hash raw results and publish reduction code version.

## Tools
- `tools/atlas_urp_generator.py`
- `tools/ooni_corroborator.py`