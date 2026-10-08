# Certification & standards alignment (US-centric, adaptable)

**Track:** A (Deployable core)


## EAC / VVSG 2.0 alignment
- VVSG 2.0 provides security, accessibility, and functional requirements for voting systems. (`source: eac_vvsg2_test_assertions_v1_4_pdf`).
- EAC has a public process to solicit/evaluate/approve **E2E verifiable protocol** candidates. (`xref: eac_e2e_protocol_evaluation_process_page`).

This spec is written to be compatible with that direction:

Reference implementation/evaluation framing for E2E protocols (for review context, not normative here):
- EAC/NIST TGDC draft slides on E2E verifiable protocols (`source: eac_e2e_protocols_draft_tgdc_2023_pdf`).
- E2E verification artifacts are public and testable,
- critical security properties are explicit and auditable,
- operational controls are documented.

## Certification artifacts you should maintain
- traceability matrix: spec requirement → tests → evidence
- threat model → mitigations → residual risk
- penetration test + red team reports (with remediation)
- SBOMs + build provenance
- incident response plan and drill evidence
