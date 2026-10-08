# 152. ADR process, claims, hazards, and evidence contracts

**Track:** Shared


This pack is intentionally “paranoid” and therefore sprawling. To keep it maintainable and auditable, adopt:

- **ADRs** (Architecture Decision Records) for decisions that change semantics or trust assumptions.
- A **claim/evidence matrix** so every important security claim points to a concrete artifact.
- A **hazard register** (or richer risk register) describing failure modes, triggers, detection, and mitigations.

## 152.1 ADR directory

Use `adr/NNNN-title.md` with:

- Status (Proposed/Accepted/Superseded)
- Context
- Decision
- Consequences
- Follow-ups

## 152.2 Claim/evidence matrix

Recommended: `../artifacts/claims/claim-evidence-matrix.csv` with columns:

- Claim ID
- Claim statement
- Threat addressed
- Evidence artifacts (files)
- Test/drill lane
- Owner
- Review cadence

## 152.3 Hazard register

You already have `../artifacts/risks/risk-register.csv`. If you want the TriKEM-style “hazard” structure, add:

- Hazard ID
- Preconditions
- Trigger signals
- Impact
- Detection artifacts
- Response playbook

## 152.4 Evidence bundle contracts

For high-stakes evidence (e.g., notarized bundles, ENR packages, drift alerts), define an **artifact contract**:

- required fields and file layout
- validation script
- interpretation rule (“pass means… under recorded conditions…”) 

This prevents evidence from becoming non-comparable across runs.

## Reference conventions

For machine-checkable references inside the claim/evidence matrix and hazard register, see `163-artifact-reference-conventions.md`.
