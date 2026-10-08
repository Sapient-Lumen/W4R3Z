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


## Certification ecosystem volatility (informative risk posture)

Certification and standards are part of the *real* security boundary: adversaries can exploit confusion about
“what standard applies,” “what was certified,” or “which lab/environment was used” to delay adjudication or undermine trust.

Minimum evidence posture (tight):
- Pin the exact standards and test-assertion versions you rely on (`source: eac_vvsg2_test_assertions_v1_4_pdf`).
- Treat certification claims as inputs that must be bound to evidence (hashes, dates, responsible parties), not as trusted premises.
- Keep official publication channels and results feeds auditable (`docs/203–205`, `docs/63`, `docs/68`).
- Prefer conservative operator guidance from election-security bodies as *informative baseline* (`xref: cisa_best_practices_securing_election_systems_page`).

See also: `adr/0003-institutional-volatility-as-threat.md`.
