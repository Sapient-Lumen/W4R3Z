# Vendor & supply-chain oversight for election infrastructure

**Track:** A+C (Core + North Star)


This doc converts “supply chain is Tier‑0” into procurement and operational artifacts for:
- VRDB services
- ENR sites and CDNs
- PBB/witness nodes
- verifier implementations
- credential issuance tooling

## Why paranoia is warranted
Election ecosystems rely heavily on third parties: hosting, DNS, CDN, managed security, development vendors, and equipment suppliers. A single upstream compromise can become a systemic incident.

## Baseline expectations
- SBOMs for all deployed software and major dependencies
- reproducible builds for client/verifier binaries when feasible
- secure update framework (TUF profile) for all distributed software
- segregated environments for election management components
- least privilege for vendor remote access; time-bounded approvals; full logging

## Checklist highlights
- third-party risk management (TPRM) requirements embedded in RFPs
- incident notification SLA + forensic cooperation clause
- escrow of build recipes + pinned dependency manifests
- independent security assessment / red team window

## References
- CISA supply chain guidance for election infrastructure
- CIS/Electionline supply chain whitepapers and vendor oversight practices