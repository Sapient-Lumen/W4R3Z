# 89 — Controls Alignment (NIST CSF Election Infrastructure Profile + CISA/EAC Checklists)

**Track:** A (Deployable core)


## Goal
Translate the crypto/protocol design into **operational control families** election administrators already recognize.

This is NOT a certification claim. It is a mapping aid for risk owners.

## Inputs
- NIST: Cybersecurity Framework Election Infrastructure Profile (NIST VTS 200-1)
- EAC: Incident Response Checklist
- EAC: Election Night Reporting security checklist
- CISA: Incident response communications guide

## Mapping approach
- Map each major subsystem to CSF Functions (Identify / Protect / Detect / Respond / Recover).
- For each, point to concrete artifacts in this repo (runbooks, schemas, evidence bundles).

## Subsystem mapping (high level)
### PBB / transparency log
- Detect: fork proof, witness gossip, drift alerts
- Respond: emergency freeze policy
- Recover: paper-of-record + RLA path

### Eligibility / VRDB
- Protect: signed snapshots, revocation epochs
- Detect: mass-change alerts
- Recover: offline pollbook continuity

### ENR / public results
- Detect: drift detection, signed ENR chain
- Respond: status banners + signed statements

## Artifacts
See `78-nist-csf-election-profile-mapping.md` for detailed mapping; this doc adds operational cross-references to comms and exercise artifacts introduced after v14.