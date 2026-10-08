# Mapping to NIST CSF Election Infrastructure Profile

**Track:** A (Deployable core)


This document maps the spec pack controls to NIST’s Cybersecurity Framework Election Infrastructure Profile (NIST VTS 200-1).

## Components mapped
- VRDB transparency + snapshots → Identify/Protect (asset mgmt, access control), Detect (anomalies), Recover (restoration)
- PBB + witness gossip → Detect (integrity monitoring), Respond (analysis), Recover (evidence)
- ENR results pipeline → Protect (authenticity), Detect (drift), Respond (comms), Recover (corrections)

## Deliverable
A traceability matrix that links:
- CSF categories/subcategories
- our requirements (MUST/SHOULD)
- artifacts (checklists, schemas, drills)