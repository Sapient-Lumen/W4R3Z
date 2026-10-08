# Certification & standards alignment (US-centric, adaptable)

**Track:** A (Deployable core)


## EAC / VVSG 2.0 alignment
- VVSG 2.0 provides security, accessibility, and functional requirements for voting systems.
- EAC has a public process to solicit/evaluate/approve **E2E verifiable protocol** candidates.

This spec is written to be compatible with that direction:
- E2E verification artifacts are public and testable,
- critical security properties are explicit and auditable,
- operational controls are documented.

## Certification artifacts you should maintain
- traceability matrix: spec requirement → tests → evidence
- threat model → mitigations → residual risk
- penetration test + red team reports (with remediation)
- SBOMs + build provenance
- incident response plan and drill evidence