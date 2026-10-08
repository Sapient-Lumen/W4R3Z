# MPIC-style multi-perspective validation (election endpoints)

**Track:** A (Deployable core)


## Background
Multi-Perspective Issuance Corroboration (MPIC) is a pattern used to reduce the risk that a single network vantage is fooled during domain validation.

## Adaptation to election evidence endpoints
Use multi-perspective checks to validate:
- DNS records
- TLS endpoints
- HTTP message signatures
- pinned artifact hashes (EPB/checkpoints)

## Normative requirements
- **MUST** perform validation from ≥ M independent vantages.
- **MUST** treat disagreement as a security incident.
- **SHOULD** publish signed validation reports for public scrutiny.