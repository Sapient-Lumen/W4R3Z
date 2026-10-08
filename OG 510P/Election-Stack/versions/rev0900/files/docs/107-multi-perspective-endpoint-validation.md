# Multi-perspective endpoint validation

**Track:** A (Deployable core)


## Problem
Routing/DNS attacks can divert some users to a fake endpoint that looks valid locally.

## Pattern
Validate endpoints from multiple independent perspectives:
- DNS answers
- TLS certificate chain / fingerprint
- HTTP response signatures

Emit signed `EndpointValidationReport` objects anchored to ATL.

## Normative requirements
- **MUST** validate from ≥ M distinct ASNs/regions.
- **MUST** pin expected artifacts (EPB hash, checkpoint hash).
- **MUST** treat inconsistent views as incidents.

## Artifact
- `schemas/EndpointValidationReport.json`
- `tools/endpoint_validator_skeleton.py`